import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.ha_client import HAClient
from app.inverter_db import get_connection
import os

log = logging.getLogger("uvicorn.info")

class EnergyDataCollector:
    def __init__(self, ha_client: HAClient):
        self.ha = ha_client
        self.scheduler = AsyncIOScheduler()
        self.consumption_entity = os.getenv("CURRENT_CONSUMPTION")


    def start_collection(self, interval_seconds: int):
        self.scheduler.add_job(
            self.fetch_and_store,
            'interval',
            seconds=interval_seconds,
            id='energy_collection',
            replace_existing=True
        )
        self.scheduler.start()
        log.info(f"Started data collection every {interval_seconds} seconds")


    async def fetch_and_store(self):
        try:
            data = await self.ha.get_entity_state(self.consumption_entity)
            value = float(data["state"])
            unit = data.get("attributes", {}).get("unit_of_measurement")
            print("unit", unit)
            epoch = int(datetime.now().timestamp())

            _store_to_db(epoch, unit, value)

            log.info(f" Stored consumption: {value} {unit} at {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            log.error(f"✗ Error collecting data: {e}")

    def stop_collection(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            log.info(" Stopped data collection")


def _store_to_db(epoch: int, unit: str, value: float):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO historic_data (epoch, unit, value)
                    VALUES (?, ?, ?)
                    """, (epoch, unit, value))
        conn.commit()