from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, PERCENTAGE, UnitOfTime

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.COVER: {
                "updown": {
                    "open_value": "up",
                    "close_value": "down",
                    "stop_value": "pause",
                }
            },
            Platform.NUMBER: {
                "light_brightness": {
                    "min": 20,
                    "max": 100,
                    "step": 1,
                    "unit_of_measurement": PERCENTAGE,
                    "translation_key": "lightness"
                },
                "custom_height": {
                    "min": 0,
                    "max": 100,
                    "step": 10,
                },
                "custom_timing": {
                    "min": 0,
                    "max": 180,
                    "step": 5,
                    "unit_of_measurement": UnitOfTime.MINUTES
                }
            },
            Platform.SWITCH: {
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "laundry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "offline_voice_function": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            }
        }
    },
    "default_laundry_rack": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.COVER: {
                "updown": {
                    "open_value": "up",
                    "close_value": "down",
                    "stop_value": "pause",
                }
            },
            Platform.NUMBER: {
                "light_brightness": {
                    "min": 20,
                    "max": 100,
                    "step": 1,
                    "unit_of_measurement": PERCENTAGE,
                    "translation_key": "lightness"
                },
                "custom_height": {
                    "min": 0,
                    "max": 100,
                    "step": 10,
                },
                "custom_timing": {
                    "min": 0,
                    "max": 180,
                    "step": 5,
                    "unit_of_measurement": UnitOfTime.MINUTES
                }
            },
            Platform.SWITCH: {
                "light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "laundry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "offline_voice_function": {
                    "device_class": SwitchDeviceClass.SWITCH,
                }
            }
        }
    }
}
