from importlib import import_module
from pathlib import Path
import logging

_LOGGER = logging.getLogger(__name__)

DEVICE_MAPPINGS = {}

def load_device_mappings():
    """加载所有设备映射文件"""
    mapping_dir = Path(__file__).parent
    
    if not mapping_dir.exists():
        _LOGGER.error(f"设备映射目录不存在: {mapping_dir}")
        return
    
    try:
        files = list(mapping_dir.iterdir())
        
        for file in files:
            if file.name.endswith('.py') and file.name != '__init__.py':
                try:
                    module_name = f"{__package__}.{file.stem}"
                    module = import_module(module_name)
                    
                    if hasattr(module, 'DEVICE_MAPPING'):
                        device_type = int(file.stem.replace('T0x', ''), 16)
                        DEVICE_MAPPINGS[device_type] = module.DEVICE_MAPPING
                        _LOGGER.info(f"成功加载设备映射: {file.stem} -> 设备类型: 0x{device_type:X}")
                except Exception as e:
                    _LOGGER.error(f"加载设备映射文件 {file.name} 失败: {e}", exc_info=True)
    except Exception as e:
        _LOGGER.error(f"遍历设备映射目录失败: {e}", exc_info=True)

load_device_mappings()

def get_device_mapping(device_type: int, sn8: str = "") -> dict:
    """获取指定设备类型的映射
    
    Args:
        device_type: 设备类型（如 0xFB）
        sn8: 设备型号代码（8位），用于获取特定设备的映射
    
    Returns:
        设备映射字典，优先返回 sn8 对应的映射，不存在则返回 default
    """
    mapping = DEVICE_MAPPINGS.get(device_type, {})
    
    if not mapping:
        return {}
    
    if sn8:
        if sn8 in mapping:
            return mapping[sn8]
        for key in mapping:
            if isinstance(key, tuple) and sn8 in key:
                return mapping[key]
    
    if "default" in mapping:
        return mapping["default"]
    
    return mapping

def get_queries(device_type: int, sn8: str = "") -> list:
    """获取设备的查询配置"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("queries", [{}])

def get_centralized(device_type: int, sn8: str = "") -> list:
    """获取设备的集中控制属性列表"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("centralized", [])

def get_default_values(device_type: int, sn8: str = "") -> dict:
    """获取设备的属性默认值"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("default_values", {})

def get_calculate(device_type: int, sn8: str = "") -> dict:
    """获取设备的计算配置"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("calculate", {})

def get_entities(device_type: int, sn8: str = "") -> dict:
    """获取设备的实体配置"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("entities", {})

def get_rationale(device_type: int, sn8: str = "") -> list:
    """获取设备的开关逻辑"""
    mapping = get_device_mapping(device_type, sn8)
    return mapping.get("rationale", ["off", "on"])
