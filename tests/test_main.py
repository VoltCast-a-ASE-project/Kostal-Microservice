import pytest
from fastapi.testclient import TestClient
import app.main as main


@pytest.fixture
def client():
    return TestClient(main.app)


# ---------- Helpers ----------
class DummyCollector:
    def __init__(self):
        self.started = False
        self.stopped = False

    def start_collection(self, interval_seconds: int):
        self.started = True

    def stop_collection(self):
        self.stopped = True


class LiveOkService:
    async def get_realtime_data(self):
        return {"ok": "realtime"}

    async def get_lf_data(self):
        return {"ok": "lf"}

    async def get_historical_data(self):
        return {"ok": "history"}


class FallbackService:
    async def get_lf_data(self):
        return {"fallback": "lf"}

    async def get_historical_data(self):
        return {"fallback": "history"}


# ---------- Startup / Shutdown ----------
def test_startup_mock_branch(monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", True)

    called = {"init": False}
    monkeypatch.setattr(main, "init_db", lambda: called.__setitem__("init", True))
    monkeypatch.setattr(main, "KostalService", lambda ha_client=None: object())

    main.startup_event()

    assert called["init"] is True
    assert main.app.state.ha_client is None


def test_startup_live_success(monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "init_db", lambda: None)
    monkeypatch.setattr(main, "HAClient", lambda: object())
    monkeypatch.setattr(main, "KostalService", lambda _c: object())

    dummy = DummyCollector()
    monkeypatch.setattr(main, "EnergyDataCollector", lambda _c: dummy)

    main.startup_event()
    assert dummy.started is True


def test_startup_live_valueerror(monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "init_db", lambda: None)

    def raise_valueerror():
        raise ValueError("missing")

    monkeypatch.setattr(main, "HAClient", raise_valueerror)

    main.startup_event()
    assert getattr(main.app.state, "data_collector", None) is None


@pytest.mark.asyncio
async def test_shutdown_live_stops_collector(monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    dummy = DummyCollector()
    main.app.state.data_collector = dummy

    await main.shutdown_event()
    assert dummy.stopped is True


@pytest.mark.asyncio
async def test_shutdown_mock_does_nothing(monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", True)
    # darf nicht crashen
    await main.shutdown_event()


# ---------- GET /kostal/realtimedata ----------
def test_realtime_mock(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", True)
    monkeypatch.setattr(main, "build_mock_live_json", lambda: {"inverter": "MOCK"})
    r = client.get("/kostal/realtimedata")
    assert r.status_code == 200
    assert r.json()["inverter"] == "MOCK"


def test_realtime_live_ok(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "HAClient", lambda: object())
    monkeypatch.setattr(main, "KostalService", lambda _c: LiveOkService())

    r = client.get("/kostal/realtimedata")
    assert r.status_code == 200
    assert r.json() == {"ok": "realtime"}


def test_realtime_live_valueerror_to_503(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)

    def raise_valueerror():
        raise ValueError("HA_REST_URL is missing!")

    monkeypatch.setattr(main, "HAClient", raise_valueerror)

    r = client.get("/kostal/realtimedata")
    assert r.status_code == 503


def test_realtime_live_exception_to_500(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "HAClient", lambda: object())

    class BadService:
        async def get_realtime_data(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(main, "KostalService", lambda _c: BadService())

    r = client.get("/kostal/realtimedata")
    assert r.status_code == 500


# ---------- GET /kostal/lfdata ----------
def test_lf_mock(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", True)
    monkeypatch.setattr(main, "build_mock_interval_json", lambda: {"inverter": "MOCK", "lfdata": {}})
    r = client.get("/kostal/lfdata")
    assert r.status_code == 200
    assert "lfdata" in r.json()


def test_lf_live_ok(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "HAClient", lambda: object())
    monkeypatch.setattr(main, "KostalService", lambda _c: LiveOkService())

    r = client.get("/kostal/lfdata")
    assert r.status_code == 200
    assert r.json() == {"ok": "lf"}


def test_lf_live_valueerror_to_503(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)

    def raise_valueerror():
        raise ValueError("HA_TOKEN is missing!")

    monkeypatch.setattr(main, "HAClient", raise_valueerror)

    r = client.get("/kostal/lfdata")
    assert r.status_code == 503


def test_lf_live_exception_fallback_to_state_service(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    main.app.state.kostal_service = FallbackService()
    monkeypatch.setattr(main, "HAClient", lambda: object())

    class BadService:
        async def get_lf_data(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(main, "KostalService", lambda _c: BadService())

    r = client.get("/kostal/lfdata")
    assert r.status_code == 200
    assert r.json() == {"fallback": "lf"}


# ---------- GET /kostal/historicaldata ----------
def test_history_mock(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", True)
    monkeypatch.setattr(main, "build_mock_historic_json", lambda: {"inverter": "MOCK"})
    r = client.get("/kostal/historicaldata")
    assert r.status_code == 200


def test_history_live_ok(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    monkeypatch.setattr(main, "HAClient", lambda: object())
    monkeypatch.setattr(main, "KostalService", lambda _c: LiveOkService())

    r = client.get("/kostal/historicaldata")
    assert r.status_code == 200
    assert r.json() == {"ok": "history"}


def test_history_live_valueerror_to_503(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)

    def raise_valueerror():
        raise ValueError("HA_TOKEN is missing!")

    monkeypatch.setattr(main, "HAClient", raise_valueerror)

    r = client.get("/kostal/historicaldata")
    assert r.status_code == 503


def test_history_live_exception_fallback_to_state_service(client, monkeypatch):
    monkeypatch.setattr(main, "USE_MOCK", False)
    main.app.state.kostal_service = FallbackService()
    monkeypatch.setattr(main, "HAClient", lambda: object())

    class BadService:
        async def get_historical_data(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(main, "KostalService", lambda _c: BadService())

    r = client.get("/kostal/historicaldata")
    assert r.status_code == 200
    assert r.json() == {"fallback": "history"}


# ---------- GET /kostal/{username} ----------
def test_get_inverter_404(client, monkeypatch):
    monkeypatch.setattr(main, "get_inverter", lambda u: None)
    r = client.get("/kostal/unknown")
    assert r.status_code == 404


def test_get_inverter_200(client, monkeypatch):
    monkeypatch.setattr(main, "get_inverter", lambda u: {"username": u})
    r = client.get("/kostal/inverter/Philipp2")
    assert r.status_code == 200
    assert r.json()["username"] == "Philipp2"


# ---------- POST /kostal ----------
def test_post_add_200(client, monkeypatch):
    monkeypatch.setattr(main, "add_inverter", lambda body: True)
    r = client.post("/kostal/inverter", json={"username": "u", "name": "n", "ip_address": "ip", "token": "t"})
    assert r.status_code == 200


def test_post_add_500(client, monkeypatch):
    monkeypatch.setattr(main, "add_inverter", lambda body: False)
    r = client.post("/kostal/inverter", json={"username": "u", "name": "n", "ip_address": "ip", "token": "t"})
    assert r.status_code == 500


# ---------- PUT /kostal ----------
def test_put_update_200(client, monkeypatch):
    monkeypatch.setattr(main, "update_inverter", lambda body: True)
    r = client.put("/kostal/inverter", json={"username": "u"})
    assert r.status_code == 200


def test_put_update_500(client, monkeypatch):
    monkeypatch.setattr(main, "update_inverter", lambda body: False)
    r = client.put("/kostal/inverter", json={"username": "u"})
    assert r.status_code == 500


# ---------- DELETE /kostal/user/{user} ----------
def test_delete_200(client, monkeypatch):
    monkeypatch.setattr(main, "delete_inverter", lambda u: True)
    r = client.delete("/kostal/inverter/user/Philipp2")
    assert r.status_code == 200


def test_delete_500(client, monkeypatch):
    monkeypatch.setattr(main, "delete_inverter", lambda u: False)
    r = client.delete("/kostal/inverter/user/Philipp2")
    assert r.status_code == 500
