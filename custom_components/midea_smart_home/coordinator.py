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
    ):
        self.controller = controller
        self.device_name = device_name
        self.calculate_config = calculate_config or {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"Midea Smart Home {device_name}",
            update_interval=timedelta(seconds=update_interval),
        )

    def _evaluate_expression(self, expression: str, data: dict) -> Any:
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+|[+\-*/()]', expression)
        result_expr = ""
        for token in tokens:
            if re.match(r'^[a-zA-Z_]', token):
                if token in data:
                    result_expr += str(data[token])
                else:
                    result_expr += "0"
            else:
                result_expr += token
        try:
            return eval(result_expr)
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
                    data[lvalue] = result
                    _LOGGER.debug(f"Calculated {lvalue} = {result}")
        
        return data

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.hass.async_add_executor_job(
                self.controller.get_status
            )
            return self._apply_calculations(data)
        except Exception as e:
            raise UpdateFailed(f"Failed to update device status: {e}") from e

    async def async_set_control(self, attr: str, value: Any) -> dict[str, Any]:
        await self.hass.async_add_executor_job(
            self.controller.set_control, attr, value
        )
        await self.async_request_refresh()
        return self.data
