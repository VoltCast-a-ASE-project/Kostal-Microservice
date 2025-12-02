import types
import pytest
from app.json_response_builder import (
    build_live_json,
    build_interval_json,
    build_history_json,
)

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
    result = build_live_json(gen, cons, cap)

    assert result["inverter"] == "Kostal"
    assert result["realtime_data"]["current_generation"]["value"] == "1000"
    assert result["realtime_data"]["battery_capacity"]["unit"] == "%"


def test_build_interval_json(gen, cons):
    result = build_interval_json(gen, cons)

    assert result["inverter"] == "Kostal"
    assert result["lfdata"]["total_generation"]["value"] == "1000"
    assert result["lfdata"]["total_consumption"]["unit"] == "W"


@pytest.mark.parametrize(
    "today, days_30, days_365, expected_today_values",
    [
        (
            types.SimpleNamespace(unit="kWh", values=[1, 2]),
            types.SimpleNamespace(unit="kWh", values=[10]),
            types.SimpleNamespace(unit="kWh", values=[100]),
            [1, 2],
        ),
        (
            types.SimpleNamespace(unit="kWh", values=[]),
            types.SimpleNamespace(unit="kWh", values=[]),
            types.SimpleNamespace(unit="kWh", values=[]),
            [],
        ),
    ],
)
def test_build_history_json(today, days_30, days_365, expected_today_values):
    result = build_history_json(today, days_30, days_365)

    assert result["historic_data"]["energy_consumption_today"]["values"] == expected_today_values
