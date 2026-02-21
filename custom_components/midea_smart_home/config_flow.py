import base64
import logging
import socket
from ipaddress import IPv4Network
from pathlib import Path
from typing import Any

import ifaddr
import voluptuous as vol
from aiohttp import ClientSession
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    BIT_LUA,
    CJSON_LUA,
    CONF_ACCOUNT,
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_IP,
    CONF_KEY,
    CONF_LUA_FILE,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SN,
    CONF_SN8,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEVICE_TYPES,
    DOMAIN,
    LUA_COMMON_PATH,
    LUA_DEVICE_PATH,
)

_LOGGER = logging.getLogger(__name__)

DISCOVERY_TIMEOUT = 5.0

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_ACCOUNT): str,
    vol.Required(CONF_PASSWORD): str,
})

def get_lua_storage_path(hass_config_dir: str) -> Path:
    return Path(hass_config_dir) / LUA_DEVICE_PATH

def get_lua_common_path(hass_config_dir: str) -> Path:
    return Path(hass_config_dir) / LUA_COMMON_PATH

def get_lua_file_path(hass_config_dir: str, device_type: int, sn8: str = "") -> Path:
    if sn8:
        return get_lua_storage_path(hass_config_dir) / f"T0x{hex(device_type)[2:].upper()}_{sn8}.lua"
    return get_lua_storage_path(hass_config_dir) / f"T0x{hex(device_type)[2:]}.lua"

def discover_devices(timeout: float = DISCOVERY_TIMEOUT) -> dict:
    from midealocal.security import LocalSecurity
    
    BROADCAST_MSG = bytes([
        0x5A, 0x5A, 0x01, 0x11, 0x48, 0x00, 0x92, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x7F, 0x75, 0xBD, 0x6B, 0x3E, 0x4F, 0x8B, 0x76,
        0x2E, 0x84, 0x9C, 0x6E, 0x57, 0x8D, 0x65, 0x90,
        0x03, 0x6E, 0x9D, 0x43, 0x42, 0xA5, 0x0F, 0x1F,
        0x56, 0x9E, 0xB8, 0xEC, 0x91, 0x8E, 0x92, 0xE5,
    ])
    
    nets = []
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            if ip.is_IPv4 and ip.network_prefix < 32:
                local_network = IPv4Network(f"{ip.ip}/{ip.network_prefix}", strict=False)
                if local_network.is_private and not local_network.is_loopback:
                    addr = str(local_network.broadcast_address)
                    if addr not in nets:
                        nets.append(addr)
    
    if not nets:
        return {}
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    
    for addr in nets:
        try:
            sock.sendto(BROADCAST_MSG, (addr, 6445))
        except Exception:
            pass
    
    devices = {}
    security = LocalSecurity()
    
    while True:
        try:
            data, addr = sock.recvfrom(512)
            if len(data) < 40:
                continue
            
            if data[:2].hex() == "8370" and data[8:10].hex() == "5a5a":
                inner_data = data[8:-16]
            elif data[:2].hex() == "5a5a":
                inner_data = data
            else:
                continue
            
            device_id = int.from_bytes(inner_data[20:26], "little")
            if device_id in devices:
                continue
            
            encrypt_data = inner_data[40:-16]
            if len(encrypt_data) < 16:
                continue
            
            reply = security.aes_decrypt(encrypt_data)
            if len(reply) < 41:
                continue
            
            sn = reply[8:40].decode("utf-8", errors="ignore").rstrip('\x00')
            ssid_len = reply[40]
            ssid = reply[41:41+ssid_len].decode("utf-8", errors="ignore")
            
            sn8 = sn[9:17] if len(sn) > 17 else ""
            
            device_type = 0
            if "_" in ssid:
                type_str = ssid.split("_")[1]
                try:
                    device_type = int(type_str, 16)
                except Exception:
                    pass
            
            devices[device_id] = {
                CONF_DEVICE_ID: device_id,
                CONF_IP: addr[0],
                CONF_DEVICE_TYPE: device_type,
                CONF_SN: sn,
                CONF_SN8: sn8,
            }
        except socket.timeout:
            break
        except Exception:
            continue
    
    sock.close()
    return devices

class MideaLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    def __init__(self):
        self._discovered_devices: dict = {}
        self._selected_device: dict = {}
        self._account: str = None
        self._password: str = None
        self._session: ClientSession = None
        self._preset_cloud = None
        self._user_cloud = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        
        if user_input is not None:
            self._account = user_input.get(CONF_ACCOUNT)
            self._password = user_input.get(CONF_PASSWORD)
            return await self.async_step_discover()
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "note": "请输入美的美居账号密码，用于下载设备 Lua 文件"
            },
        )

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self._discovered_devices = await self.hass.async_add_executor_job(
            discover_devices, 3.0
        )
        
        if not self._discovered_devices:
            return self.async_show_form(
                step_id="discover",
                errors={"base": "no_devices_found"},
                description_placeholders={"note": "局域网中未发现设备"},
            )
        
        device_options = {
            str(did): f"{did} - {info[CONF_IP]} ({DEVICE_TYPES.get(info[CONF_DEVICE_TYPE], hex(info[CONF_DEVICE_TYPE]))})"
            for did, info in self._discovered_devices.items()
        }
        
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_options),
            }),
        )

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return await self.async_step_discover()
        
        device_id = int(user_input["device"])
        self._selected_device = self._discovered_devices[device_id]
        
        await self.async_set_unique_id(str(device_id))
        self._abort_if_unique_id_configured()
        
        return await self.async_step_get_token()

    async def async_step_get_token(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=f"Midea | {self._account}",
                data={
                    CONF_DEVICE_ID: self._selected_device[CONF_DEVICE_ID],
                    CONF_IP: self._selected_device[CONF_IP],
                    CONF_PORT: DEFAULT_PORT,
                    CONF_DEVICE_TYPE: hex(self._selected_device.get(CONF_DEVICE_TYPE)),
                    CONF_SN: self._selected_device.get(CONF_SN, ""),
                    CONF_SN8: self._selected_device.get(CONF_SN8, ""),
                    CONF_ACCOUNT: self._account,
                    CONF_TOKEN: user_input.get(CONF_TOKEN),
                    CONF_KEY: user_input.get(CONF_KEY),
                    CONF_LUA_FILE: user_input.get(CONF_LUA_FILE),
                },
            )
        
        token = None
        key = None
        lua_file = None
        
        self._session = ClientSession()
        
        try:
            from midealocal.cloud import get_midea_cloud, get_preset_account_cloud
            
            preset = get_preset_account_cloud()
            self._preset_cloud = get_midea_cloud(
                cloud_name=preset["cloud_name"],
                session=self._session,
                account=preset["username"],
                password=preset["password"],
            )
            
            if await self._preset_cloud.login():
                device_id = self._selected_device[CONF_DEVICE_ID]
                keys = await self._preset_cloud.get_cloud_keys(device_id)
                if keys:
                    method = list(keys.keys())[0]
                    token = keys[method]["token"]
                    key = keys[method]["key"]
                    _LOGGER.info("Got token/key for device %s", device_id)
            
            user_cloud = get_midea_cloud(
                cloud_name="美的美居",
                session=self._session,
                account=self._account,
                password=self._password,
            )
            
            if await user_cloud.login():
                _LOGGER.info("User account login success")
                self._user_cloud = user_cloud
                
                # 下载通用Lua文件
                lua_common_dir = get_lua_common_path(self.hass.config.config_dir)
                await self._download_common_lua_files(lua_common_dir)
                
                # 下载设备特定的Lua文件
                device_type = self._selected_device.get(CONF_DEVICE_TYPE)
                sn = self._selected_device.get(CONF_SN, "")
                sn8 = self._selected_device.get(CONF_SN8, "")
                lua_storage_dir = get_lua_storage_path(self.hass.config.config_dir)
                lua_storage_dir.mkdir(parents=True, exist_ok=True)
                
                lua_file = await self._download_lua_file(
                    user_cloud, device_type, sn, sn8, lua_storage_dir
                )
            else:
                _LOGGER.warning("User account login failed")
        except Exception as err:
            _LOGGER.error("Failed to get token/key or lua: %s", err)
        finally:
            await self._session.close()
        
        device_type = self._selected_device.get(CONF_DEVICE_TYPE)
        sn8 = self._selected_device.get(CONF_SN8, "")
        lua_file_path = get_lua_file_path(self.hass.config.config_dir, device_type, sn8)
        
        if not lua_file and lua_file_path.exists():
            lua_file = str(lua_file_path)
        
        return self.async_show_form(
            step_id="get_token",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=token or ""): str,
                vol.Required(CONF_KEY, default=key or ""): str,
                vol.Required(CONF_LUA_FILE, default=lua_file or ""): str,
            }),
            description_placeholders={
                "device_id": str(self._selected_device[CONF_DEVICE_ID]),
                "ip": self._selected_device[CONF_IP],
                "sn8": self._selected_device.get(CONF_SN8, ""),
            },
        )

    async def _download_lua_file(
        self, cloud, device_type: int, sn: str, sn8: str, storage_dir: Path
    ) -> str | None:
        def _write_lua_file(file_path: Path, content: str) -> bool:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except Exception as e:
                _LOGGER.error("Error writing Lua file %s: %s", file_path, e)
                return False

        def _read_lua_file(file_path: Path) -> str | None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return None

        try:
            if sn8:
                lua_file_path = storage_dir / f"T0x{hex(device_type)[2:].upper()}_{sn8}.lua"
            else:
                lua_file_path = storage_dir / f"T0x{hex(device_type)[2:]}.lua"
            
            if lua_file_path.exists():
                _LOGGER.info("Lua file already exists: %s", lua_file_path)
                return str(lua_file_path)
            
            downloaded_path = await cloud.download_lua(
                path=str(storage_dir),
                device_type=device_type,
                sn=sn,
            )
            
            if downloaded_path and Path(downloaded_path).exists():
                content = await self.hass.async_add_executor_job(_read_lua_file, Path(downloaded_path))
                
                if content:
                    modified = content.replace(
                        "if ((dataType ~= 0x02) and (dataType ~= 0x03) and (dataType ~= 0x04)) then         return nil     end",
                        ""
                    )
                    
                    success = await self.hass.async_add_executor_job(_write_lua_file, lua_file_path, modified)
                    
                    if downloaded_path != str(lua_file_path):
                        Path(downloaded_path).unlink()
                    
                    if success:
                        _LOGGER.info("Downloaded Lua file for device type 0x%s, sn8: %s", hex(device_type)[2:], sn8)
                        return str(lua_file_path)
            else:
                _LOGGER.warning("download_lua returned no path")
        except Exception as err:
            _LOGGER.error("Failed to download Lua file: %s", err)
        return None

    async def _download_common_lua_files(
        self, storage_dir: Path
    ) -> bool:
        def _write_lua_file(file_path: Path, content: str) -> bool:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except Exception as e:
                _LOGGER.error("Error creating Lua file %s: %s", file_path, e)
                return False

        try:
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            common_files = {
                "bit.lua": base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8"),
                "cjson.lua": base64.b64decode(CJSON_LUA.encode("utf-8")).decode("utf-8"),
            }
            
            for file_name, content in common_files.items():
                file_path = storage_dir / file_name
                
                if file_path.exists():
                    _LOGGER.info("Common Lua file already exists: %s", file_path)
                    continue
                
                success = await self.hass.async_add_executor_job(
                    _write_lua_file, file_path, content
                )
                if success:
                    _LOGGER.info("Created common Lua file: %s", file_name)
            
            return True
        except Exception as err:
            _LOGGER.error("Failed to create common Lua files: %s", err)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return MideaLocalOptionsFlowHandler(config_entry)

class MideaLocalOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        options = self._config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval",
                    default=options.get("update_interval", 1),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
            }),
        )
