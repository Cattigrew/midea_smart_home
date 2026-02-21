from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MideaCoordinator

class MideaBaseEntity(CoordinatorEntity[MideaCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MideaCoordinator,
        device_id: int,
        device_type: str,
        sn: str,
        sn8: str,
        device_name: str,
        entity_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_type = device_type
        self._sn = sn
        self._sn8 = sn8
        self._entity_key = entity_key
        
        device_type_int = int(device_type, 16) if isinstance(device_type, str) else 0
        device_type_code = f"T0x{device_type_int:02X}" if device_type_int else device_type
        
        device_display_name = f"{device_name} ({sn8})" if sn8 else device_name
        
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{entity_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device_id))},
            name=device_display_name,
            manufacturer="Midea",
            model=sn8 if sn8 else device_type_code,
            serial_number=sn,
        )
