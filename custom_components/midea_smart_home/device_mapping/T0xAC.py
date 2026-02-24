from homeassistant.const import Platform, UnitOfTemperature, PRECISION_HALVES, \
    CONCENTRATION_PARTS_PER_MILLION, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "comfort_power_save": "off",
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "comfort": {"comfort_power_save": "on"},
                        "boost": {"strong_wind": "on"}
                    },
                    "swing_modes": {
                        "off": {"wind_swing_lr": "off", "wind_swing_ud": "off"},
                        "both": {"wind_swing_lr": "on", "wind_swing_ud": "on"},
                        "horizontal": {"wind_swing_lr": "on", "wind_swing_ud": "off"},
                        "vertical": {"wind_swing_lr": "off", "wind_swing_ud": "on"},
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fresh_air_remove_odor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "aux_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
            }
        }
    },
    "21293193": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "query_all"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "smart_mode"},
                    },
                    "preset_modes": {
                        "auto": {"water_model_temperature_auto": "on", "temperature_control_switch": 0},
                        "manual": {"water_model_temperature_auto": "off", "temperature_control_switch": 0},
                        "link": {"water_model_temperature_auto": "on", "temperature_control_switch": 1}
                    },
                    "target_temperature": "effluent_temperature",
                    "pre_mode": "mode",
                    "min_temp": 25,
                    "max_temp": 60,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.NUMBER: {
                "temperature": {
                    "min": 16,
                    "max": 30,
                    "step": 0.5,
                    "translation_key": "heating_target_temperature",
                },
            },
            Platform.SWITCH: {
                "out_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "translation_key": "water_model_go_out",
                },
                "mute_voice": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "eco": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "temperature_control_switch": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                    "translation_key": "room_temp_ctrl",
                },
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    },
    "22259015": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type": "run_status"}, {"query_type": "module_30"}, {"query_type": "module_31"}, {"query_type": "module_32"}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[indoor_humidity]",
                    "rvalue": "[humidity_value]"
                },
                {
                    "lvalue": "[indoor_temperature]",
                    "rvalue": "[t1_temp]"
                },
                {
                    "lvalue": "[co2_value]",
                    "rvalue": "[co2_concentration]"
                },
                {
                    "lvalue": "[pm25_value]",
                    "rvalue": "[dust_co2]"
                }
            ],
            "set": []
        },
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "comfort_power_save": "off",
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "comfort": {"comfort_power_save": "on"},
                        "boost": {"strong_wind": "on"}
                    },
                    "swing_modes": {
                        "off": {"wind_swing_lr": "off", "wind_swing_ud": "off"},
                        "both": {"wind_swing_lr": "on", "wind_swing_ud": "on"},
                        "horizontal": {"wind_swing_lr": "on", "wind_swing_ud": "off"},
                        "vertical": {"wind_swing_lr": "off", "wind_swing_ud": "on"},
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "aux_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "elec_dust_remove": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "auto_comfort_fresh_air": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "auto_fresh_off_co2": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "comfort_fresh_air": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "manul_humi":{
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "remove_arofene":{
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "disinfect":{
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.NUMBER: {
                "manul_humi_value": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "min": 40,
                    "max": 70,
                    "step": 1,
                    "unit_of_measurement": "%",
                },
                "auto_purifier_on_pm": {
                    "device_class": SensorDeviceClass.PM25,
                    "min": 75,
                    "max": 180,
                    "step": 1,
                    "unit_of_measurement": "µg/m³",
                }
            },
            Platform.SELECT: {
                "fresh_air_fan_speed": {
                    "options": {
                        "低速": {"fresh_air_fan_speed": 40},
                        "中速": {"fresh_air_fan_speed": 60},
                        "高速": {"fresh_air_fan_speed": 80},
                        "全速": {"fresh_air_fan_speed": 100}
                    }
                },
                "fresh_air_setting_mode": {
                    "options": {
                        "内外循环": {"fresh_air_setting_mode": 0},
                        "外循环": {"fresh_air_setting_mode": 1}
                    },
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "co2_value": {
                    "device_class": SensorDeviceClass.CO2,
                    "unit_of_measurement": CONCENTRATION_PARTS_PER_MILLION,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
                "pm25_value": {
                    "device_class": SensorDeviceClass.PM25,
                    "unit_of_measurement": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                    "state_class": SensorStateClass.MEASUREMENT,
                },
            }
        }
    },
    ("22019031", "22019035", "22019045"): {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"fresh_air"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}, {"query_type":"outdoor_temperature"}],
        "centralized": [],
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "comfort_power_save": "off",
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "comfort": {"comfort_power_save": "on"},
                        "boost": {"strong_wind": "on"}
                    },
                    "swing_modes": {
                        "off": {"wind_swing_lr": "off", "wind_swing_ud": "off"},
                        "both": {"wind_swing_lr": "on", "wind_swing_ud": "on"},
                        "horizontal": {"wind_swing_lr": "on", "wind_swing_ud": "off"},
                        "vertical": {"wind_swing_lr": "off", "wind_swing_ud": "on"},
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fresh_air_remove_odor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1],
                },
                "dry": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "prevent_straight_wind": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": [0, 1]
                },
                "aux_heat": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "outdoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "fresh_air_temp": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                }
            }
        }
    },
    "23096653": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[total_elec_value]",
                    "rvalue": "float([total_elec]) / 1000"
                },
            ],
        },
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "boost": {"strong_wind": "on"}
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "fengguan_remove_odor": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "rationale": ["on", "off"],
                    "translation_key": "disinfect",
                },
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
                }
            },
            Platform.SELECT: {
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "total_elec_value": {
                    "device_class": SensorDeviceClass.ENERGY,
                    "unit_of_measurement": "kWh",
                    "state_class": SensorStateClass.TOTAL_INCREASING
                }
            }
        }
    },
    "23096633": {
        "rationale": ["off", "on"],
        "queries": [{}, {"query_type":"run_status"}, {"query_type":"indoor_humidity"}, {"query_type":"indoor_temperature"}],
        "centralized": [],
        "calculate": {
            "get": [
                {
                    "lvalue": "[total_elec_value]",
                    "rvalue": "float([total_elec]) / 1000"
                },
            ],
        },
        "entities": {
            Platform.CLIMATE: {
                "thermostat": {
                    "power": "power",
                    "hvac_modes": {
                        "off": {"power": "off"},
                        "heat": {"power": "on", "mode": "heat"},
                        "cool": {"power": "on", "mode": "cool"},
                        "auto": {"power": "on", "mode": "auto"},
                        "dry": {"power": "on", "mode": "dry"},
                        "fan_only": {"power": "on", "mode": "fan"}
                    },
                    "preset_modes": {
                        "none": {
                            "eco": "off",
                            "cool_power_saving": 0,
                            "strong_wind": "off"
                        },
                        "eco": {"eco": "on", "cool_power_saving": 1},
                        "boost": {"strong_wind": "on"}
                    },
                    "fan_modes": {
                        "silent": {"wind_speed": 20},
                        "low": {"wind_speed": 40},
                        "medium": {"wind_speed": 60},
                        "high": {"wind_speed": 80},
                        "full": {"wind_speed": 100},
                        "auto": {"wind_speed": 102}
                    },
                    "target_temperature": ["temperature", "small_temperature"],
                    "current_temperature": "indoor_temperature",
                    "pre_mode": "mode",
                    "aux_heat": "ptc",
                    "min_temp": 17,
                    "max_temp": 30,
                    "temperature_unit": UnitOfTemperature.CELSIUS,
                    "precision": PRECISION_HALVES,
                }
            },
            Platform.SWITCH: {
                "power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
                "ptc": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "aux_heat",
                }
            },
            Platform.SELECT: {
                "new_wind_model_intake_enable": {
                    "options": {
                        "off": {"new_wind_model_intake_switch": "off"},
                        "low": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "40"},
                        "medium": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "60"},
                        "high": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "80"},
                        "full": {"new_wind_model_intake_switch": "on", "new_wind_model_intake_wind": "100"}
                    }
                },
                "new_wind_model_exhaust_enable": {
                    "options": {
                        "off": {"new_wind_model_exhaust_switch": "off"},
                        "silent": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "20"},
                        "high": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "80"},
                        "full": {"new_wind_model_exhaust_switch": "on", "new_wind_model_exhaust_wind": "100"}
                    }
                },
                "follow_body_sense": {
                    "options": {
                        "on": {"follow_body_sense": "on", "follow_body_sense_enable": 1},
                        "off": {"follow_body_sense": "off", "follow_body_sense_enable": 1},
                    }
                }
            },
            Platform.SENSOR: {
                "mode": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "indoor_temperature": {
                    "device_class": SensorDeviceClass.TEMPERATURE,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "indoor_humidity": {
                    "device_class": SensorDeviceClass.HUMIDITY,
                    "unit_of_measurement": "%",
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "total_elec_value": {
                    "device_class": SensorDeviceClass.ENERGY,
                    "unit_of_measurement": "kWh",
                    "state_class": SensorStateClass.TOTAL_INCREASING
                }
            }
        }
    },
}
