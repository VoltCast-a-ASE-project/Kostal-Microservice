import sqlite3
import pytest
from unittest.mock import AsyncMock, MagicMock

import app.data_collector as edc


class DummyScheduler:
    def __init__(self):
        self.jobs = []
        self.started = False
        self.running = False

    def add_job(self, func, trigger, seconds, id, replace_existing):
        self.jobs.append((func, trigger, seconds, id, replace_existing))

    def start(self):
        self.started = True
        self.running = True

    def shutdown(self):
        self.running = False


@pytest.fixture
def ha_mock():
    return AsyncMock(spec=edc.HAClient)


def test_start_collection_adds_job_and_starts_scheduler(monkeypatch, ha_mock):
    monkeypatch.setattr(edc, "AsyncIOScheduler", DummyScheduler)

    collector = edc.EnergyDataCollector(ha_mock)
    collector.start_collection(30)

    scheduler = collector.scheduler
    assert scheduler.started is True


def test_start_collection_uses_given_interval(monkeypatch, ha_mock):
    monkeypatch.setattr(edc, "AsyncIOScheduler", DummyScheduler)

    collector = edc.EnergyDataCollector(ha_mock)
    collector.start_collection(45)

    scheduler = collector.scheduler
    assert scheduler.jobs[0][2] == 45


@pytest.mark.asyncio
async def test_fetch_and_store_calls_ha_and_store(monkeypatch, ha_mock):
    ha_mock.get_entity_state.return_value = {
        "state": "1.5",
        "attributes": {"unit_of_measurement": "kWh"},
    }

    store_mock = MagicMock()
    monkeypatch.setattr(edc, "_store_to_db", store_mock)
    monkeypatch.setenv("CURRENT_CONSUMPTION", "sensor.power")

    collector = edc.EnergyDataCollector(ha_mock)
    await collector.fetch_and_store()

    store_mock.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_and_store_logs_error_on_exception(monkeypatch, ha_mock):
    ha_mock.get_entity_state.side_effect = Exception("fail")

    log_mock = MagicMock()
    monkeypatch.setattr(edc, "log", log_mock)
    monkeypatch.setenv("CURRENT_CONSUMPTION", "sensor.power")

    collector = edc.EnergyDataCollector(ha_mock)
    await collector.fetch_and_store()

    log_mock.error.assert_called_once()


def test_stop_collection_shuts_down_when_running(monkeypatch, ha_mock):
    monkeypatch.setattr(edc, "AsyncIOScheduler", DummyScheduler)

    collector = edc.EnergyDataCollector(ha_mock)
    collector.scheduler.running = True

    collector.stop_collection()

    assert collector.scheduler.running is False


def test_store_to_db_inserts_row(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    def fake_get_connection():
        return conn

    monkeypatch.setattr(edc, "get_connection", fake_get_connection)

    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE historic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            epoch INTEGER NOT NULL,
            unit TEXT NOT NULL,
            value REAL NOT NULL
        )
        """
    )
    conn.commit()

    edc._store_to_db(epoch=1234567890, unit="kWh", value=2.5)

    cur.execute("SELECT epoch, unit, value FROM historic_data")
    row = cur.fetchone()
    conn.close()

    assert row["value"] == 2.5
