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

