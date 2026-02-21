import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
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
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    device_id = data[CONF_DEVICE_ID]
    device_type = data[CONF_DEVICE_TYPE]
    sn8 = data.get(CONF_SN8, "")
    sn = data.get(CONF_SN, "")
    device_name = data.get("device_name", f"Midea Device {device_id}")
    
    device_type_int = int(device_type, 16) if isinstance(device_type, str) else device_type
    
    device_mapping = get_device_mapping(device_type_int, sn8)
    entities_config = device_mapping.get("entities", {})
    
    select_config = entities_config.get("select", {})
    if select_config:
        entities = []
        for select_id, config in select_config.items():
            name = config.get("name", select_id)
            options = config.get("options", {})
            if isinstance(options, dict):
                option_list = list(options.keys())
            else:
                option_list = options
            entities.append(
                MideaSelectEntity(
                    coordinator, device_id, device_type, sn, sn8, device_name,
                    select_id, name, option_list
                )
            )
        async_add_entities(entities)

class MideaSelectEntity(MideaBaseEntity, SelectEntity):
    def __init__(
        self,
        coordinator: MideaCoordinator,
        device_id: int,
        device_type: str,
        sn: str,
        sn8: str,
        device_name: str,
        select_id: str,
        name: str,
        options: list[str],
    ):
        super().__init__(coordinator, device_id, device_type, sn, sn8, device_name, select_id)
        self._select_id = select_id
        self._options = options
        self._attr_translation_key = select_id
        self._attr_options = options
    
    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data or {}
        value = data.get(self._select_id, 0)
        try:
            index = int(value)
        except (TypeError, ValueError):
            index = 0
        if 0 <= index < len(self._options):
            return self._options[index]
        return self._options[0] if self._options else None
    
    async def async_select_option(self, option: str) -> None:
        if option in self._options:
            index = self._options.index(option)
            await self.coordinator.async_set_control(self._select_id, index)
