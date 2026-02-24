import asyncio
import logging
import re
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .device import DeviceController

_LOGGER = logging.getLogger(__name__)


class MideaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        controller: DeviceController,
        device_name: str,
        update_interval: int = 1,
        calculate_config: dict = None,
        queries: list = None,
        centralized: list = None,
        default_values: dict = None,
        device_type: int = 0,
    ):
        self.controller = controller
        self.device_name = device_name
        self.calculate_config = calculate_config or {}
        self.queries = queries or [{}]
        self.centralized = centralized or []
        self.default_values = default_values or {}
        self._last_control_state: dict[str, Any] = {}
        self.device_type = device_type
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"Midea Smart Home {device_name}",
            update_interval=timedelta(seconds=update_interval),
        )

    def _evaluate_expression(self, expression: str, data: dict) -> Any:
        def replace_var(match):
            var_name = match.group(1)
            if var_name in data:
                return str(data[var_name])
            return "0"
        
        result_expr = re.sub(r'\[([a-zA-Z_][a-zA-Z0-9_]*)\]', replace_var, expression)
        
        preserve_functions = ['float', 'int', 'str', 'bool']
        result_expr = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', 
                           lambda m: str(data[m.group(1)]) if m.group(1) in data and m.group(1) not in preserve_functions else m.group(1), 
                           result_expr)
        
        try:
            return eval(result_expr, {"__builtins__": {"float": float, "int": int, "str": str}})
        except Exception as e:
            _LOGGER.warning(f"Failed to evaluate expression '{expression}': {e}")
            return None

    def _apply_calculations(self, data: dict) -> dict:
        if not data:
            return data
        
        get_calculations = self.calculate_config.get("get", [])
        for calc in get_calculations:
            lvalue = calc.get("lvalue")
            rvalue = calc.get("rvalue")
            if lvalue and rvalue:
                result = self._evaluate_expression(rvalue, data)
                if result is not None:
                    if lvalue.startswith('[') and lvalue.endswith(']'):
                        actual_lvalue = lvalue[1:-1]
                    else:
                        actual_lvalue = lvalue
                    data[actual_lvalue] = result
                    _LOGGER.debug(f"Calculated {actual_lvalue} = {result}")
        
        return data

    def _apply_default_values(self, data: dict) -> dict:
        for attr, default_value in self.default_values.items():
            if attr not in data or data[attr] is None:
                data[attr] = default_value
        return data

    def _handle_t0xd9_db_location_selection(self, data: dict, value: str) -> None:
        if value == "left":
            data["db_location"] = 1
        elif value == "right":
            data["db_location"] = 2

    def _adjust_t0xd9_db_location_based_on_position(self, data: dict) -> int:
        db_position = data.get("db_position", 1)
        current_location = data.get("db_location", 1)
        
        if db_position == 1:
            calculated_location = current_location
        elif db_position == 0:
            calculated_location = 2 if current_location == 1 else 1
        else:
            calculated_location = current_location
        
        data["db_location"] = calculated_location
        return calculated_location

    def _sync_t0xd9_location_selection(self, data: dict, location: int) -> None:
        if location == 1:
            data["db_location_selection"] = "left"
        elif location == 2:
            data["db_location_selection"] = "right"

    def _adjust_t0xd9_control_status(self, data: dict, running_status: str) -> None:
        if running_status == "start":
            control_status = "start"
        else:
            control_status = "pause"
        data["db_control_status"] = control_status

    def _apply_t0xd9_special_handling(self, data: dict, is_control: bool = False, control_attrs: dict = None) -> None:
        if self.device_type != 0xD9:
            return
        
        if is_control and control_attrs:
            if "db_location_selection" in control_attrs:
                self._handle_t0xd9_db_location_selection(data, control_attrs["db_location_selection"])
            else:
                self._adjust_t0xd9_db_location_based_on_position(data)
        else:
            if "db_running_status" in data:
                self._adjust_t0xd9_control_status(data, data["db_running_status"])
            
            if "db_location" in data:
                self._sync_t0xd9_location_selection(data, data["db_location"])

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            all_data = {}
            
            for query in self.queries:
                actual_query = query.copy() if isinstance(query, dict) else query
                
                if self.device_type == 0xD9 and isinstance(actual_query, dict):
                    calculated_location = self._adjust_t0xd9_db_location_based_on_position(all_data)
                    self._sync_t0xd9_location_selection(all_data, calculated_location)
                
                data = await self.hass.async_add_executor_job(
                    self.controller.get_status, actual_query
                )
                if data:
                    all_data.update(data)
            
            result = self._apply_default_values(all_data)
            result = self._apply_calculations(result)
            
            self._apply_t0xd9_special_handling(result)
            
            for key, value in self._last_control_state.items():
                if key not in result:
                    result[key] = value
            return result
        except Exception as e:
            raise UpdateFailed(f"Failed to update device status: {e}") from e

    async def async_set_control(self, attr: str | dict, value: Any = None) -> dict[str, Any]:
        if isinstance(attr, dict):
            control = attr
        else:
            control = {attr: value}
        
        full_control = {}
        for key in self.centralized:
            if key in self.data:
                full_control[key] = self.data[key]
        full_control.update(control)
        
        if self.device_type == 0xD9:
            if "db_location_selection" in control:
                self._handle_t0xd9_db_location_selection(full_control, control["db_location_selection"])
            else:
                self._adjust_t0xd9_db_location_based_on_position(full_control)
        
        await self.hass.async_add_executor_job(
            self.controller.set_control, full_control
        )
        
        self._last_control_state.update(control)
        
        await asyncio.sleep(0.5)
        await self.async_request_refresh()
        return self.data

    async def async_set_controls(self, controls: dict) -> dict[str, Any]:
        """Set multiple control attributes at once."""
        return await self.async_set_control(controls)
