import logging
import os
import base64
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_IP,
    CONF_KEY,
    CONF_LUA_FILE,
    CONF_PORT,
    CONF_SN,
    CONF_SN8,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEVICE_TYPES,
    DEVICE_TYPES_ZH,
    DOMAIN,
    PLATFORMS,
    CJSON_LUA,
    BIT_LUA,
    LUA_COMMON_PATH,
)
from .coordinator import MideaCoordinator
from .device import DeviceController, MideaCodec
from .device_mapping import get_device_mapping

_LOGGER = logging.getLogger(__name__)

def _write_lua_file(file_path: str, content: str) -> bool:
    try:
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(content)
        return True
    except PermissionError as e:
        _LOGGER.error(f"Failed to create {file_path}: {e}")
        return False

def _ensure_lua_files(lua_path: str) -> tuple:
    cjson = os.path.join(lua_path, "cjson.lua")
    bit = os.path.join(lua_path, "bit.lua")
    
    cjson_lua = base64.b64decode(CJSON_LUA.encode("utf-8")).decode("utf-8")
    bit_lua = base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8")
    
    return cjson, bit, cjson_lua, bit_lua

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    lua_path = hass.config.path(LUA_COMMON_PATH)
    os.makedirs(lua_path, exist_ok=True)
    
    cjson, bit, cjson_lua, bit_lua = await hass.async_add_executor_job(
        _ensure_lua_files, lua_path
    )
    
    if not os.path.exists(cjson):
        success = await hass.async_add_executor_job(_write_lua_file, cjson, cjson_lua)
        if success:
            _LOGGER.info("Created cjson.lua at %s", cjson)
    
    if not os.path.exists(bit):
        success = await hass.async_add_executor_job(_write_lua_file, bit, bit_lua)
        if success:
            _LOGGER.info("Created bit.lua at %s", bit)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = entry.data
    
    device_id = data[CONF_DEVICE_ID]
    ip_address = data[CONF_IP]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    token = data[CONF_TOKEN]
    key = data[CONF_KEY]
    lua_file = data[CONF_LUA_FILE]
    sn = data.get(CONF_SN, "")
    sn8 = data.get(CONF_SN8, "")
    device_type = data.get(CONF_DEVICE_TYPE)
    
    lua_common_dir = Path(hass.config.config_dir) / LUA_COMMON_PATH
    
    codec = MideaCodec(lua_file, str(lua_common_dir), sn=sn, subtype=0)
    controller = DeviceController(
        device_id=device_id,
        ip_address=ip_address,
        port=port,
        token=token,
        key=key,
        codec=codec,
    )
    
    if not await hass.async_add_executor_job(controller.connect):
        _LOGGER.error("Failed to connect to device %s at %s", device_id, ip_address)
        return False
    
    device_type_int = int(device_type, 16) if isinstance(device_type, str) else 0
    device_mapping = get_device_mapping(device_type_int, sn8)
    calculate_config = device_mapping.get("calculate", {})
    
    language = hass.config.language or "en"
    if language.startswith("zh"):
        device_name = DEVICE_TYPES_ZH.get(device_type_int, f"设备 {device_type}")
    else:
        device_name = DEVICE_TYPES.get(device_type_int, f"Device {device_type}")
    
    update_interval = entry.options.get("update_interval", 1)
    coordinator = MideaCoordinator(
        hass,
        controller,
        f"Device_{device_id}",
        update_interval=update_interval,
        calculate_config=calculate_config,
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "controller": controller,
        CONF_DEVICE_ID: device_id,
        CONF_DEVICE_TYPE: device_type,
        CONF_SN8: sn8,
        CONF_SN: sn,
        "device_name": device_name,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        controller = data["controller"]
        await hass.async_add_executor_job(controller.close)
    
    return unload_ok

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
