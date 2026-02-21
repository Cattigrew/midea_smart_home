from importlib import import_module
from pathlib import Path
import logging

_LOGGER = logging.getLogger(__name__)

DEVICE_MAPPINGS = {}

# 动态加载所有设备映射文件
def load_device_mappings():
    """加载所有设备映射文件"""
    mapping_dir = Path(__file__).parent
    
    # 确保目录存在
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

# 初始化时加载设备映射
load_device_mappings()

def get_device_mapping(device_type, sn8: str = ""):
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
    
    if sn8 and sn8 in mapping:
        return mapping[sn8]
    
    if "default" in mapping:
        return mapping["default"]
    
    return mapping
