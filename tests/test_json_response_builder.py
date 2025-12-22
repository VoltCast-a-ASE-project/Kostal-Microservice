import pytest
from datetime import date

import app.json_response_builder as jb


@pytest.fixture
def gen():
    return {"state": "1000", "attributes": {"unit_of_measurement": "W"}}

@pytest.fixture
def cons():
    return {"state": "800", "attributes": {"unit_of_measurement": "W"}}

@pytest.fixture
def cap():
    return {"state": "75", "attributes": {"unit_of_measurement": "%"}}


def test_build_live_json(gen, cons, cap):
    r = jb.build_live_json(gen, cons, cap)
    assert r["inverter"] == "Kostal"
    assert r["realtime_data"]["current_generation"]["unit"] == "W"
    assert r["realtime_data"]["current_generation"]["value"] == "1000"
    assert r["realtime_data"]["current_consumption"]["value"] == "800"
    assert r["realtime_data"]["battery_capacity"]["unit"] == "%"


def test_build_interval_json(gen, cons):
    r = jb.build_interval_json(gen, cons)
    assert r["inverter"] == "Kostal"
    assert r["lfdata"]["total_generation"]["unit"] == "W"
    assert r["lfdata"]["total_consumption"]["value"] == "800"


def test_build_history_json_with_simple_objects():
    today = type("X", (), {"unit": "kWh", "values": [1, 2]})()
    d30 = type("X", (), {"unit": "kWh", "values": [10]})()
    d365 = type("X", (), {"unit": "kWh", "values": [100]})()

    r = jb.build_history_json(today, d30, d365)
    assert r["historic_data"]["energy_consumption_today"]["values"] == [1, 2]
    assert r["historic_data"]["energy_consumption_30Days"]["values"] == [10]
    assert r["historic_data"]["energy_consumption_365Days"]["values"] == [100]


# ---- Mock functions: make randint deterministic ----
def test_build_mock_live_json(monkeypatch):
    # randint wird 3x aufgerufen -> feste Werte liefern
    seq = iter([111, 222, 33])
    monkeypatch.setattr(jb, "randint", lambda a, b: next(seq))

    r = jb.build_mock_live_json()
    assert r["inverter"] == "MOCK"
    assert r["realtime_data"]["current_generation"]["value"] == 111
    assert r["realtime_data"]["current_consumption"]["value"] == 222
    assert r["realtime_data"]["battery_capacity"]["value"] == 33


def test_build_mock_interval_json(monkeypatch):
    seq = iter([1234, 5678])
    monkeypatch.setattr(jb, "randint", lambda a, b: next(seq))

    r = jb.build_mock_interval_json()
    assert r["inverter"] == "MOCK"
    assert r["lfdata"]["total_generation"]["value"] == 1234
    assert r["lfdata"]["total_consumption"]["value"] == 5678


def test_mock_today_consumption(monkeypatch):
    # 24 Werte, immer 500
    monkeypatch.setattr(jb, "randint", lambda a, b: 500)

    hd = jb._mock_today_consumption()
    assert hd.unit == "W"
    assert len(hd.values) == 24
    assert hd.values[0]["time"] == "00:00"
    assert hd.values[-1]["time"] == "23:00"
    assert all(v["value"] == 500 for v in hd.values)


def test_mock_last_days(monkeypatch):
    monkeypatch.setattr(jb, "randint", lambda a, b: 9000)

    hd = jb._mock_last_days(3)
    assert hd.unit == "W"
    assert len(hd.values) == 3

    # Prüfe: datum-strings + alle values = 9000
    assert all("date" in x and "value" in x for x in hd.values)
    assert all(x["value"] == 9000 for x in hd.values)


def test_build_mock_historic_json(monkeypatch):
    # randint wird oft aufgerufen -> einfach konstant machen
    monkeypatch.setattr(jb, "randint", lambda a, b: 777)

    r = jb.build_mock_historic_json()
    assert "historic_data" in r
    assert r["historic_data"]["energy_consumption_today"]["unit"] == "W"
    assert len(r["historic_data"]["energy_consumption_today"]["values"]) == 24
    assert len(r["historic_data"]["energy_consumption_30Days"]["values"]) == 30
    assert len(r["historic_data"]["energy_consumption_365Days"]["values"]) == 365
