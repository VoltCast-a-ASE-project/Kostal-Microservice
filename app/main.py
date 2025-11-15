from dotenv import load_dotenv
from fastapi import FastAPI
from app.ha_client import HAClient
import logging
import os
load_dotenv()

app = FastAPI()
ha_client = HAClient()
log = logging.getLogger("uvicorn.info")

@app.get("/kostal/batterysoc")
async def battery_soc():
    state = await ha_client.get_entity_state(os.getenv("BATTERY_SOC"))
    log.info(f"BATTERY_SOC: {state}")
    return {
            "entity_id": state["entity_id"],
            "battery_soc": state["state"],
#            "attributes": state["attributes"],
            "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/batterypowerin")    #Batterieladung
async def battery_power():
    state = await ha_client.get_entity_state(os.getenv("BATTERY_POWER_IN"))
    log.info(f"BATTERY_POWER: {state}")
    return {
        "entity_id": state["entity_id"],
        "battery_power_in": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/batterypowerout")
async def battery_power_out():
    state = await ha_client.get_entity_state(os.getenv("BATTERY_POWER_OUT"))
    log.info(f"BATTERY_POWER_OUT: {state}")
    return{
        "entity_id": state["entity_id"],
        "battery_power_out": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/totaldcinput")
async def total_dc_input():
    state = await ha_client.get_entity_state(os.getenv("TOTAL_DC_INPUT"))
    log.info(f"TOTAL_DC_INPUT: {state}")
    return{
        "entity_id": state["entity_id"],
        "TOTAL_DC_INPUT": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/homepower")
async def home_power():
    state = await ha_client.get_entity_state(os.getenv("HOME_POWER"))
    log.info(f"HOME_POWER: {state}")
    return{
        "entity_id": state["entity_id"],
        "HOME_POWER": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/totalhomeconsumption")
async def total_home_consumption():
    state = await ha_client.get_entity_state(os.getenv("TOTAL_HOME_CONSUMPTION"))
    log.info(f"TOTAL_HOME_CONSUMPTION: {state}")
    return{
        "entity_id": state["entity_id"],
        "TOTAL_HOME_CONSUMPTION": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/totalenergytogrid")
async def total_energy_to_grid():
    state = await ha_client.get_entity_state(os.getenv("TOTAL_ENERGY_TO_GRID"))
    log.info(f"TOTAL_ENERGY_TO_GRID: {state}")
    return{
        "entity_id": state["entity_id"],
        "TOTAL_ENERGY_TO_GRID": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }
@app.get("/kostal/totalenergyfromgrid")
async def total_energy_from_grid():
    state = await ha_client.get_entity_state(os.getenv("TOTAL_ENERGY_FROM_GRID"))
    log.info(f"TOTAL_ENERGY_FROM_GRID: {state}")
    return{
        "entity_id": state["entity_id"],
        "TOTAL_ENERGY_FROM_GRID": state["state"],
        "unit_of_measurement": state.get("attributes", {}).get("unit_of_measurement")
    }

@app.get("/hello")
async def root():
    return {"message": "Hello World"}