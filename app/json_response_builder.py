from random import randint

INVERTER_NAME = "Kostal"

def build_live_json(generation: dict, consumption: dict, capacity: dict) -> dict:
    return {
        "inverter": INVERTER_NAME,
        "realtime_data": {
            "current_generation": {
                "unit": generation.get("attributes", {}).get("unit_of_measurement"),
                "value": generation["state"]
            },
            "current_consumption": {
                "unit": consumption.get("attributes", {}).get("unit_of_measurement"),
                "value": consumption["state"]
            },
            "battery_capacity": {
                "unit": capacity.get("attributes", {}).get("unit_of_measurement"),
                "value": capacity["state"]
            }
        }
    }

def build_mock_live_json():
    return {
        "inverter": "MOCK",
        "realtime_data": {
            "current_generation": {
                "unit": "W",
                # Using randint for mock/test inverter values
                "value": randint(0, 3500)
            },
            "current_consumption": {
                "unit": "W",
                # Using randint for mock/test inverter values
                "value": randint(300, 5000)
            },
            "battery_capacity": {
                "unit": "%",
                # Using randint for mock/test inverter values
                "value": randint(10, 100)
            }
        }
    }


def build_interval_json(generation: dict, consumption: dict) -> dict:
    return {
        "inverter": INVERTER_NAME,
        "lfdata": {
            "total_generation": {
                "unit": generation.get("attributes", {}).get("unit_of_measurement"),
                "value": generation["state"]
            },
            "total_consumption": {
                "unit": consumption.get("attributes", {}).get("unit_of_measurement"),
                "value": consumption["state"]
            }
        }
    }

def build_mock_interval_json():
    return {
        "inverter": "MOCK",
        "lfdata": {
            "total_generation": {
                "unit": "kWh",
                # Using randint for mock/test inverter values
                "value": randint(1000, 6000)
            },
            "total_consumption": {
                "unit": "kWh",
                # Using randint for mock/test inverter values
                "value": randint(1500, 7000)
            }
        }
    }

def build_history_json(today_data,days_30_data,days_365_data) -> dict:
    return {
        "historic_data": {
            "energy_consumption_today": {
                "unit": today_data.unit,
                "values": today_data.values
            },
            "energy_consumption_30Days": {
                "unit": days_30_data.unit,
                "values": days_30_data.values
            },
            "energy_consumption_365Days": {
                "unit": days_365_data.unit,
                "values": days_365_data.values
            }
        }
    }

