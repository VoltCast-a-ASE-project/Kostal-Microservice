
from fastapi import FastAPI, Request, Response
from app.ha_client import HAClient
from app.json_response_builder import build_mock_live_json, build_mock_interval_json, build_mock_historic_json
from app.kostal_service import KostalService
from app.data_collector import EnergyDataCollector
from app.inverter_db import init_db, get_inverter, add_inverter, update_inverter, delete_inverter
from app.kostal_service import KostalService
import logging

app = FastAPI()
log = logging.getLogger("uvicorn.info")

USE_MOCK = True

@app.on_event("startup")
def startup_event():
    if USE_MOCK:
        app.state.ha_client = None
        app.state.kostal_service = KostalService(ha_client=None)
        log.info("MOCK MODE - no DB init, no data collection")
        return

    app.state.ha_client = HAClient()
    app.state.kostal_service = KostalService(app.state.ha_client)
    app.state.data_collector = EnergyDataCollector(app.state.ha_client)

    init_db()
    log.info("SQLite DB initialized")
    app.state.data_collector.start_collection(interval_seconds=15)


@app.on_event("shutdown")
async def shutdown_event():
    if not USE_MOCK:
        app.state.data_collector.stop_collection()


@app.get("/kostal/realtimedata")
async def realtime_data():
    if USE_MOCK:
        return build_mock_live_json()
    return await app.state.kostal_service.get_realtime_data()


@app.get("/kostal/lfdata")
async def lf_data():
    if USE_MOCK:
        return build_mock_interval_json()
    return await app.state.kostal_service.get_lf_data()


@app.get("/kostal/historicaldata")
async def historic_data():
    if USE_MOCK:
        return build_mock_historic_json()
    return await app.state.kostal_service.get_historical_data()

@app.get("/kostal/{username}")
async def api_get_inverter(username: str):
    data = get_inverter(username)
    if not data:
        return Response("Not found", status_code=404)
    return data


@app.post("/kostal")
async def api_add_inverter(request: Request):

    body = await request.json()
    print(body)

    if not add_inverter(body):
        return Response("Internal Server Error: Failed to add inverter data to database", status_code=500)

    return Response("Added inverter to database", status_code=200)

@app.put("/kostal")
async def api_update_inverter(request: Request):

    body = await request.json()

    if not update_inverter(body):
        return Response("Internal Server Error: Failed to update inverter data", status_code=500)

    return Response("Updated inverter data", status_code=200)


@app.delete("/kostal/user/{user}")
async def api_delete_inverter(user: str):

    if not delete_inverter(user):
        return Response("Internal Server Error: Failed to delete inverter", status_code=500)

    return Response("Deleted inverter for user", status_code=200)
