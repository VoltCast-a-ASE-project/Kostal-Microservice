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

def build_history_json(consumption: dict) -> dict:
    return {
        "inverter": INVERTER_NAME,
        "historic_data": {
            "energy_consumption": {
                "unit": consumption.get("attributes", {}).get("unit_of_measurement"),
                "value": consumption["state"]
            },
            "timeperiod": ""
        }
    }
