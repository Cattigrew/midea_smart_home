from homeassistant.const import Platform, UnitOfTemperature, UnitOfPower, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.SWITCH: {
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Child Lock",
                    "translation_key": "child_lock"
                },
                "screen_close": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Screen Close",
                    "rationale": ["off", "on"]
                },
                "auto_power_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Auto Power Off"
                },
                "humidification": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Humidification",
                    "rationale": ["off", "no_change"]
                },
                "voice": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Voice",
                    "rationale": ["close_buzzer", "open_buzzer"]
                }
            },
            Platform.CLIMATE: {
                "electric_heater": {
                    "name": "Electric Heater",
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"}
                    },
                    "preset_modes": {
                        "left_warm": {"gear": 1},
                        "right_warm": {"gear": 2},
                        "full_on": {"gear": 3}
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "cur_temperature",
                    "min_temp": 5,
                    "max_temp": 35,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_WHOLE
                }
            },
            Platform.SENSOR: {
                "power_statistics": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": UnitOfPower.WATT,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "name": "Power Consumption"
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "name": "Current Temperature"
                }
            }
        }
    },
    "570667EC": {
        "rationale": ["off", "on"],
        "entities": {
            Platform.SWITCH: {
                "lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Child Lock",
                    "translation_key": "child_lock"
                },
                "screen_close": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Screen Close",
                    "rationale": ["off", "on"]
                },
                "auto_power_off": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Auto Power Off"
                },
                "humidification": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Humidification",
                    "rationale": ["off", "no_change"]
                },
                "voice": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "name": "Voice",
                    "rationale": ["close_buzzer", "open_buzzer"]
                }
            },
            Platform.CLIMATE: {
                "electric_heater": {
                    "name": "Electric Heater",
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on"}
                    },
                    "preset_modes": {
                        "left_warm": {"gear": 1},
                        "right_warm": {"gear": 2},
                        "full_on": {"gear": 3}
                    },
                    "target_temperature": "temperature",
                    "current_temperature": "cur_temperature",
                    "min_temp": 5,
                    "max_temp": 35,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_WHOLE
                }
            },
            Platform.SENSOR: {
                "power_statistics": {
                    "device_class": SensorDeviceClass.POWER,
                    "unit_of_measurement": UnitOfPower.WATT,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "name": "Power Consumption"
                },
                "cur_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "name": "Current Temperature"
                }
            }
        }
    }
}
