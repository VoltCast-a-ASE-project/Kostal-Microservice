from fastapi.testclient import TestClient
from app.main import app

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


def test_lf_data(monkeypatch):
    monkeypatch.setattr("app.main.kostal_service", FakeKostalService())

    client = TestClient(app)
    response = client.get("/kostal/lfdata")

    assert response.status_code == 200


def test_historical_data(monkeypatch):
    monkeypatch.setattr("app.main.kostal_service", FakeKostalService())

    client = TestClient(app)
    response = client.get("/kostal/historicaldata")

    assert response.status_code == 200



