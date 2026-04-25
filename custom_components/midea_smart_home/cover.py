import logging
from typing import Any, Optional

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MideaCoordinator
from .entity import MideaBaseEntity, iter_midea_device_configs

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities = []

    for coordinator, device_id, device_type, sn, sn8, device_name, model, device_mapping in iter_midea_device_configs(
        hass, entry
    ):
        entities_config = device_mapping.get("entities", {})
        cover_config = entities_config.get(Platform.COVER, {})

        if cover_config:
            for cover_key, config in cover_config.items():
                entities.append(
                    MideaCoverEntity(
                        coordinator, device_id, device_type, sn, sn8, device_name,
                        cover_key, config, model
                    )
                )

    async_add_entities(entities)


class MideaCoverEntity(MideaBaseEntity, CoverEntity):

    def __init__(
        self,
        coordinator: MideaCoordinator,
        device_id: int,
        device_type: str,
        sn: str,
        sn8: str,
        device_name: str,
        entity_key: str,
        config: dict,
        model: Optional[str] = None,
    ):
        super().__init__(
            coordinator, device_id, device_type, sn, sn8, device_name, entity_key, model,
            platform_name="cover", config=config
        )
        self._entity_key = entity_key
        self._open_value = config.get("open_value", "open")
        self._close_value = config.get("close_value", "close")
        self._stop_value = config.get("stop_value", "stop")
        self._position_key = config.get("position_key")

        device_class = config.get("device_class")
        if device_class:
            self._attr_device_class = device_class

        features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        if self._position_key:
            features |= CoverEntityFeature.SET_POSITION
        self._attr_supported_features = features

    @property
    def is_closed(self) -> Optional[bool]:
        if self._position_key:
            position = self._get_nested_value(self._position_key)
            if position is not None:
                try:
                    return int(position) == 0
                except (ValueError, TypeError):
                    pass
        return None

    @property
    def current_cover_position(self) -> Optional[int]:
        if self._position_key:
            position = self._get_nested_value(self._position_key)
            if position is not None:
                try:
                    return int(position)
                except (ValueError, TypeError):
                    pass
        return None

    @property
    def is_opening(self) -> bool:
        value = self._get_nested_value(self._entity_key)
        return value == self._open_value

    @property
    def is_closing(self) -> bool:
        value = self._get_nested_value(self._entity_key)
        return value == self._close_value

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_control(self._entity_key, self._open_value)

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_control(self._entity_key, self._close_value)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_control(self._entity_key, self._stop_value)

    async def async_set_cover_position(self, position: int, **kwargs: Any) -> None:
        if self._position_key:
            await self.coordinator.async_set_control(self._position_key, position)
