from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock

class FakeKostalService:
    async def get_realtime_data(self):
        return {"inverter": "Kostal", "realtime_data": {"status": "ok"}}

    async def get_lf_data(self):
        return {"inverter": "Kostal", "lfdata": {"status": "ok"}}

    async def get_historical_data(self):
        return {"inverter": "Kostal", "historic_data": {"status": "ok"}}


def override_service():
    return FakeKostalService()


def test_realtime_data(monkeypatch):
    monkeypatch.setattr("app.main.kostal_service", FakeKostalService())

    client = TestClient(app)
    response = client.get("/kostal/realtimedata")

    assert response.status_code == 200
    assert response.json()["realtime_data"]["status"] == "ok"


def test_lf_data(monkeypatch):
    monkeypatch.setattr("app.main.kostal_service", FakeKostalService())

    client = TestClient(app)
    response = client.get("/kostal/lfdata")

    assert response.status_code == 200
    assert response.json()["lfdata"]["status"] == "ok"


def test_historical_data(monkeypatch):
    monkeypatch.setattr("app.main.kostal_service", FakeKostalService())

    client = TestClient(app)
    response = client.get("/kostal/historicaldata")

    assert response.status_code == 200
    assert response.json()["historic_data"]["status"] == "ok"


def test_lifespan_calls_init_db_and_starts_and_stops_collector(monkeypatch):
    fake_init_db = MagicMock()
    fake_collector = MagicMock()

    monkeypatch.setattr("app.main.init_db", fake_init_db)
    monkeypatch.setattr("app.main.data_collector", fake_collector)

    with TestClient(app) as client:
        fake_init_db.assert_called_once()
        fake_collector.start_collection.assert_called_once_with(interval_seconds=15)

    fake_collector.stop_collection.assert_called_once()
