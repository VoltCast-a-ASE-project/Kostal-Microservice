import os
from app import inverter_db
from app.ha_client import HAClient
from app.json_response_builder import (
    build_live_json,
    build_interval_json,
    build_history_json,
)
from app.inverter_db import get_last_30_days, get_last_365_days
from app.inverter_db import  get_today_consumption



class KostalService:
    """Service for fetching Kostal inverter data from Home Assistant."""

    def __init__(self, ha_client: HAClient):
        """Initialize the service with a Home Assistant client."""
        self.ha = ha_client
        self.db = inverter_db

    async def get_realtime_data(self):
        """Fetch current generation, consumption, and battery capacity data."""
        current_generation = await self.ha.get_entity_state(os.getenv("CURRENT_GENERATION"))
        current_consumption = await self.ha.get_entity_state(os.getenv("CURRENT_CONSUMPTION"))
        battery_capacity   = await self.ha.get_entity_state(os.getenv("BATTERY_SOC"))
        return build_live_json(current_generation, current_consumption, battery_capacity)

    async def get_lf_data(self):
        """Fetch low frequent generation and consumption data."""
        total_generation   = await self.ha.get_entity_state(os.getenv("TOTAL_GENERATION"))
        total_consumption  = await self.ha.get_entity_state(os.getenv("TOTAL_CONSUMPTION"))
        return build_interval_json(total_generation, total_consumption)

    @staticmethod
    async def get_historical_data():
        """Retrieve historical consumption data for today, last 30 days, and last 365 days."""
        today_data = get_today_consumption()
        days_30_data = get_last_30_days()
        days_365_data = get_last_365_days()
        return build_history_json(today_data, days_30_data,days_365_data)
