
from fastapi import FastAPI
from app.ha_client import HAClient
from app.kostal_service import KostalService
from app.data_collector import EnergyDataCollector
from app.inverter_db import init_db
import logging

app = FastAPI()

ha_client = HAClient()
kostal_service = KostalService(ha_client)
data_collector = EnergyDataCollector(ha_client)
log = logging.getLogger("uvicorn.info")

@app.on_event("startup")
def startup_event():
    init_db()
    log.info("SQLite DB initialized")
    # Start automatic data collection
    data_collector.start_collection(interval_seconds=15)

@app.on_event("shutdown")
async def shutdown_event():
    data_collector.stop_collection()

@app.get("/kostal/realtimedata")
async def realtime_data():
    return await kostal_service.get_realtime_data()

@app.get("/kostal/lfdata")
async def lf_data():
    return await kostal_service.get_lf_data()

@app.get("/kostal/historicaldata")
async def historic_data():
    return await kostal_service.get_historical_data()