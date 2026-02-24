import socket
import json
import threading
import logging
from pathlib import Path
from typing import Any, Optional

import lupa.lua51

from midealocal.security import LocalSecurity
from midealocal.packet_builder import PacketBuilder

_LOGGER = logging.getLogger(__name__)

class LuaRuntime:
    def __init__(self, file_path: str, lua_default_dir: str):
        self._runtime = lupa.lua51.LuaRuntime()
        
        lua_dir = str(Path(file_path).parent).replace("\\", "/")
        lua_default_dir = str(lua_default_dir).replace("\\", "/")
        
        self._runtime.execute(
            f'package.path = "{lua_default_dir}/?.lua;{lua_dir}/?.lua;" .. package.path'
        )
        
        try:
            self._runtime.execute('require "cjson"')
        except Exception:
            pass
        try:
            self._runtime.execute('require "bit"')
        except Exception:
            pass
        
        with open(file_path, "r", encoding="utf-8") as f:
            self._runtime.execute(f.read())
        
        self._lock = threading.Lock()
        self._json_to_data = self._runtime.eval(
            "function(param) return jsonToData(param) end"
        )
        self._data_to_json = self._runtime.eval(
            "function(param) return dataToJson(param) end"
        )

    def json_to_data(self, json_value: str) -> str:
        with self._lock:
            return self._json_to_data(json_value)

    def data_to_json(self, data_value: str) -> str:
        with self._lock:
            return self._data_to_json(data_value)

class MideaCodec(LuaRuntime):
    def __init__(self, file_path: str, lua_default_dir: str, sn: str = None, subtype: int = 0):
        super().__init__(file_path, lua_default_dir)
        self._sn = sn or ""
        self._subtype = subtype

    def build_query(self, query: dict = None) -> str:
        return self.json_to_data(json.dumps({
            "deviceinfo": {"deviceSN": self._sn, "deviceSubType": self._subtype},
            "query": query or {}
        }))

    def build_control(self, control: dict) -> str:
        return self.json_to_data(json.dumps({
            "deviceinfo": {"deviceSN": self._sn, "deviceSubType": self._subtype},
            "control": control,
            "status": {}
        }))

    def decode_status(self, full_message_hex: str) -> Optional[dict]:
        result = self.data_to_json(json.dumps({
            "deviceinfo": {"deviceSN": self._sn, "deviceSubType": self._subtype},
            "msg": {"data": full_message_hex}
        }))
        if result:
            return json.loads(result).get("status")
        return None

class DeviceController:
    def __init__(
        self,
        device_id: int,
        ip_address: str,
        port: int,
        token: str,
        key: str,
        codec: MideaCodec
    ):
        self._device_id = device_id
        self._ip = ip_address
        self._port = port
        self._token = token
        self._key = key
        self._codec = codec
        self._security: Optional[LocalSecurity] = None
        self._sock: Optional[socket.socket] = None
        self._lock = threading.Lock()
        self._connected = False

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        with self._lock:
            try:
                self._disconnect_internal()
                self._security = LocalSecurity()
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(10)
                self._sock.connect((self._ip, self._port))
                handshake = self._security.encode_8370(bytes.fromhex(self._token), 0x0)
                self._sock.send(handshake)
                response = self._sock.recv(256)
                auth_data = response[8:72]
                self._security.tcp_key(auth_data, bytes.fromhex(self._key))
                self._connected = True
                _LOGGER.debug("Connected to device %s at %s", self._device_id, self._ip)
                return True
            except Exception as e:
                _LOGGER.error("Failed to connect to device %s: %s", self._device_id, e)
                self._connected = False
                return False

    def close(self):
        with self._lock:
            self._disconnect_internal()

    def _disconnect_internal(self):
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _send_and_receive(self, data_hex: str, retry: int = 2) -> Optional[bytes]:
        with self._lock:
            for attempt in range(retry):
                try:
                    if not self._connected:
                        self._connect_internal()
                    
                    data_bytes = bytes.fromhex(data_hex)
                    packet = PacketBuilder(self._device_id, data_bytes).finalize()
                    encrypted = self._security.encode_8370(bytes(packet), 0x6)
                    self._sock.send(encrypted)
                    response = self._sock.recv(4096)
                    packets, _ = self._security.decode_8370(response)
                    if packets:
                        data = packets[0]
                        encrypted_data = data[40:-16]
                        return self._security.aes_decrypt(encrypted_data)
                except socket.timeout:
                    _LOGGER.warning(
                        "Timeout for device %s, retry %d/%d",
                        self._device_id, attempt + 1, retry
                    )
                    self._connect_internal()
                except Exception as e:
                    _LOGGER.error(
                        "Error for device %s: %s, reconnecting...",
                        self._device_id, e
                    )
                    self._connect_internal()
            return None

    def _connect_internal(self):
        self._disconnect_internal()
        try:
            self._security = LocalSecurity()
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((self._ip, self._port))
            handshake = self._security.encode_8370(bytes.fromhex(self._token), 0x0)
            self._sock.send(handshake)
            response = self._sock.recv(256)
            auth_data = response[8:72]
            self._security.tcp_key(auth_data, bytes.fromhex(self._key))
            self._connected = True
        except Exception as e:
            _LOGGER.error("Reconnect failed for device %s: %s", self._device_id, e)
            self._connected = False

    def get_status(self, query: dict = None) -> dict[str, Any]:
        query_hex = self._codec.build_query(query)
        decrypted = self._send_and_receive(query_hex)
        if decrypted:
            return self._codec.decode_status(decrypted.hex()) or {}
        return {}

    def set_control(self, attr: str | dict, value: Any = None) -> dict[str, Any]:
        if isinstance(attr, dict):
            control = attr
        else:
            control = {attr: value}
        control_hex = self._codec.build_control(control)
        self._send_and_receive(control_hex, retry=1)
        return {}
