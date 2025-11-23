import os
from app.ha_client import HAClient
from app.json_response_builder import (
    build_live_json,
    build_interval_json,
    build_history_json,
)

class KostalService:
    def __init__(self, ha_client: HAClient):
        self.ha = ha_client

    async def get_realtime_data(self):
        current_generation = await self.ha.get_entity_state(os.getenv("CURRENT_GENERATION"))
        current_consumption = await self.ha.get_entity_state(os.getenv("CURRENT_CONSUMPTION"))
        battery_capacity   = await self.ha.get_entity_state(os.getenv("BATTERY_SOC"))
        return build_live_json(current_generation, current_consumption, battery_capacity)

    async def get_lf_data(self):
        total_generation   = await self.ha.get_entity_state(os.getenv("TOTAL_GENERATION"))
        total_consumption  = await self.ha.get_entity_state(os.getenv("TOTAL_CONSUMPTION"))
        return build_interval_json(total_generation, total_consumption)

    async def get_historical_data(self):
        consumption = await self.ha.get_entity_state(os.getenv("TOTAL_ENERGY_TO_GRID"))
        return build_history_json(consumption)
