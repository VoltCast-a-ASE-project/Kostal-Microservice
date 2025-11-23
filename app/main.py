
from fastapi import FastAPI
from app.ha_client import HAClient
from app.kostal_service import KostalService
import logging

app = FastAPI()

ha_client = HAClient()
kostal_service = KostalService(ha_client)

log = logging.getLogger("uvicorn.info")

@app.get("/kostal/realtimedata")
async def realtime_data():
    return await kostal_service.get_realtime_data()

@app.get("/kostal/lfdata")
async def lf_data():
    return await kostal_service.get_lf_data()

@app.get("/kostal/historicaldata")
async def historic_data():
    return await kostal_service.get_historical_data()
