from random import randint
from datetime import datetime, timedelta


from app.inverter_db import HistoricalData

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
                "value": randint(0, 3500)
            },
            "current_consumption": {
                "unit": "W",
                "value": randint(300, 5000)
            },
            "battery_capacity": {
                "unit": "%",
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
                "value": randint(1000, 6000)
            },
            "total_consumption": {
                "unit": "kWh",
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

def build_mock_historic_json() -> dict:
    today = _mock_today_consumption()
    days_30 = _mock_last_days(30)
    days_365 = _mock_last_days(365)
    return build_history_json(today, days_30, days_365)

def _mock_today_consumption() -> HistoricalData:
    return HistoricalData(
        "W",
        [{"time": f"{h:02d}:00", "value": randint(150, 800)} for h in range(24)]
    )

def _mock_last_days(days: int) -> HistoricalData:
    today = datetime.now().date()
    return HistoricalData(
        "W",
        [{"date": str(today - timedelta(days=i)), "value": randint(4000, 12000)}
         for i in range(days)]
    )

