import logging

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    VacuumActivity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DEVICE_ID, CONF_DEVICE_TYPE, CONF_SN, CONF_SN8, DOMAIN
from .coordinator import MideaCoordinator
from .device_mapping import get_device_mapping
from .entity import MideaBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up vacuum entities for Midea devices."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id_str, data in entry_data.items():
        if device_id_str == "device_list":
            continue
        coordinator = data.get("coordinator")
        if not coordinator:
            continue
        device_id = data[CONF_DEVICE_ID]
        device_type = data[CONF_DEVICE_TYPE]
        sn8 = data.get(CONF_SN8, "")
        sn = data.get(CONF_SN, "")
        device_name = data.get("device_name", f"Midea Device {device_id}")

        device_type_int = int(device_type, 16) if isinstance(device_type, str) else device_type

        device_mapping = get_device_mapping(device_type_int, sn8)
        entities_config = device_mapping.get("entities", {})

        vacuum_config = entities_config.get(Platform.VACUUM, {})
        if vacuum_config:
            for vacuum_id, config in vacuum_config.items():
                entities.append(
                    MideaVacuumEntity(
                        coordinator, device_id, device_type, sn, sn8, device_name,
                        vacuum_id, config
                    )
                )

    async_add_entities(entities)


class MideaVacuumEntity(MideaBaseEntity, StateVacuumEntity):
    def __init__(
        self,
        coordinator: MideaCoordinator,
        device_id: int,
        device_type: str,
        sn: str,
        sn8: str,
        device_name: str,
        vacuum_id: str,
        config: dict,
    ):
        super().__init__(coordinator, device_id, device_type, sn, sn8, device_name, vacuum_id)
        self._vacuum_id = vacuum_id
        self._config = config
        self._key_battery_level = config.get("battery_level")
        self._key_status = config.get("status")
        self._key_fan_speeds = config.get("fan_speeds", {})

    @property
    def supported_features(self):
        features = VacuumEntityFeature(0)
        features |= VacuumEntityFeature.STOP
        features |= VacuumEntityFeature.PAUSE
        features |= VacuumEntityFeature.START
        features |= VacuumEntityFeature.RETURN_HOME
        features |= VacuumEntityFeature.FAN_SPEED
        features |= VacuumEntityFeature.STATUS
        features |= VacuumEntityFeature.BATTERY
        return features

    @property
    def battery_level(self):
        """Return the battery level of the vacuum cleaner."""
        if self._key_battery_level:
            data = self.coordinator.data or {}
            battery = self._get_nested_value(data, self._key_battery_level)
            if battery is not None:
                try:
                    return int(battery)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def status(self):
        """Return the status of the vacuum cleaner."""
        if self._key_status:
            data = self.coordinator.data or {}
            return self._get_nested_value(data, self._key_status)
        return None

    @property
    def state(self):
        """Return the state of the vacuum cleaner."""
        status = self.status
        if not status:
            return None

        status_mapping = {
            "work": VacuumActivity.CLEANING,
            "auto_clean": VacuumActivity.CLEANING,
            "charging_on_dock": VacuumActivity.DOCKED,
            "on_base": VacuumActivity.DOCKED,
            "charge_finish": VacuumActivity.DOCKED,
            "stop": VacuumActivity.IDLE,
            "sleep": VacuumActivity.IDLE,
            "clean_pause": VacuumActivity.PAUSED,
            "charge_pause": VacuumActivity.PAUSED,
            "charging": VacuumActivity.RETURNING,
            "error": VacuumActivity.ERROR,
        }

        return status_mapping.get(status, status)

    @property
    def fan_speed(self):
        """Return the current fan speed."""
        return self._dict_get_selected(self._key_fan_speeds)

    @property
    def fan_speed_list(self):
        """Return the list of available fan speeds."""
        return list(self._key_fan_speeds.keys())

    async def async_start(self):
        """Start or resume the cleaning task."""
        if self._key_status:
            await self.coordinator.async_set_control(self._key_status, "work")

    async def async_stop(self):
        """Stop the vacuum cleaner."""
        if self._key_status:
            await self.coordinator.async_set_control(self._key_status, "stop")

    async def async_pause(self):
        """Pause the cleaning task."""
        if self._key_status:
            await self.coordinator.async_set_control(self._key_status, "pause")

    async def async_return_to_base(self):
        """Return the vacuum cleaner to its base."""
        if self._key_status:
            await self.coordinator.async_set_control(self._key_status, "charge")

    async def async_set_fan_speed(self, fan_speed: str):
        """Set the fan speed."""
        new_status = self._key_fan_speeds.get(fan_speed)
        if new_status is not None:
            await self.coordinator.async_set_controls(new_status)

    def _get_nested_value(self, data: dict, key):
        """Get nested value from device data."""
        if not key or not data:
            return None
        if isinstance(key, str):
            return data.get(key)
        return None

    def _dict_get_selected(self, options_dict: dict):
        """Get the currently selected option from a dict of options."""
        if not options_dict:
            return None
        data = self.coordinator.data or {}
        for key, value in options_dict.items():
            if isinstance(value, dict):
                match = True
                for k, v in value.items():
                    if data.get(k) != v:
                        match = False
                        break
                if match:
                    return key
        return None
