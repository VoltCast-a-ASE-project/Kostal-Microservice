import pytest
from fastapi.testclient import TestClient
from app.main import app

class FakeKostalService:
    async def get_realtime_data(self):
        return {"status": "ok"}

    async def get_lf_data(self):
        return {"status": "ok"}

    async def get_historical_data(self):
        return {"status": "ok"}


@pytest.fixture(autouse=True)
def setup_fake_service():
    app.state.kostal_service = FakeKostalService()


def test_realtime_data():
    client = TestClient(app)
    r = client.get("/kostal/realtimedata")
    assert r.status_code == 200


def test_lf_data():
    client = TestClient(app)
    r = client.get("/kostal/lfdata")
    assert r.status_code == 200


def test_historical_data():
    client = TestClient(app)
    r = client.get("/kostal/historicaldata")
    assert r.status_code == 200
