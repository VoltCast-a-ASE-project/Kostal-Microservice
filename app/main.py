from dotenv import load_dotenv
from fastapi import FastAPI

from app.json_response_builder import build_live_json, build_interval_json, build_history_json
from app.ha_client import HAClient
import logging
import os
load_dotenv()
app = FastAPI()
ha_client = HAClient()
log = logging.getLogger("uvicorn.info")

@app.get("/kostal/realtimedata")
async def realtime_data():
    current_generation = await current_dc_generation()
    current_consumption = await current_home_consumption()
    battery_capacity = await battery_soc()
    return build_live_json(current_generation, current_consumption, battery_capacity)

async def current_home_consumption():
     return await ha_client.get_entity_state(os.getenv("CURRENT_CONSUMPTION"))

async def current_dc_generation():
    return await ha_client.get_entity_state(os.getenv("CURRENT_GENERATION"))

async def battery_soc():
    return await ha_client.get_entity_state(os.getenv("BATTERY_SOC"))


@app.get("/kostal/lfdata")
async def lf_data():
    total_generation = await total_dc_generation()
    total_consumption = await total_home_consumption()
    return build_interval_json(total_generation, total_consumption)


async def total_home_consumption():
    return await ha_client.get_entity_state(os.getenv("TOTAL_CONSUMPTION"))

async def total_dc_generation():
    return await ha_client.get_entity_state(os.getenv("TOTAL_GENERATION"))

@app.get("/kostal/historicaldata")
async def historic_data():
    consumption = await total_energy_to_grid()
    return build_history_json(consumption)

async def total_energy_to_grid():
   return await ha_client.get_entity_state(os.getenv("TOTAL_ENERGY_TO_GRID"))
