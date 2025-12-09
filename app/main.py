
from fastapi import FastAPI
from app.ha_client import HAClient
from app.json_response_builder import build_mock_live_json, build_mock_interval_json
from app.kostal_service import KostalService
from app.data_collector import EnergyDataCollector
from app.inverter_db import init_db
from app.kostal_service import KostalService
import logging
app = FastAPI()

ha_client = None
kostal_service = None
data_collector = None

log = logging.getLogger("uvicorn.info")

USE_MOCK = True

@app.on_event("startup")
def startup_event():
    if USE_MOCK:
        log.info("MOCK MODE - no DB init, no data collection")
        return

    ha_client = HAClient()
    kostal_service = KostalService(ha_client)
    data_collector = EnergyDataCollector(ha_client)

    init_db()
    log.info("SQLite DB initialized")
    data_collector.start_collection(interval_seconds=15)

@app.on_event("shutdown")
async def shutdown_event():
    if not USE_MOCK:
        data_collector.stop_collection()

@app.get("/kostal/realtimedata")
async def realtime_data():
    if USE_MOCK:
        return build_mock_live_json()
    return await kostal_service.get_realtime_data()

@app.get("/kostal/lfdata")
async def lf_data():
    if USE_MOCK:
        return build_mock_interval_json()
    return await kostal_service.get_lf_data()

@app.get("/kostal/historicaldata")
async def historic_data():
    if USE_MOCK:
        return await KostalService.get_historical_data()
    return await kostal_service.get_historical_data()