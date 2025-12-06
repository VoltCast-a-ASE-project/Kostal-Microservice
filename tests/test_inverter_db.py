import sqlite3
import pytest

from app.inverter_db import (
    init_db,
    get_today_consumption,
    get_last_30_days,
    get_last_365_days,
    _format_time_value_data,
    _aggregate_by_date,
    HistoricalData,
)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "test_database.db"
    monkeypatch.setattr("app.inverter_db.DB_PATH", path)
    init_db()
    return path


@pytest.fixture
def conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _insert_row(conn, epoch, value, unit="kWh"):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO historic_data (epoch, unit, value) VALUES (?, ?, ?)",
        (epoch, unit, value),
    )
    conn.commit()


def _freeze_time(monkeypatch, timestamp):
    monkeypatch.setattr("app.inverter_db.time.time", lambda: timestamp)


def test_init_db_creates_table(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='historic_data'"
    )
    row = cur.fetchone()
    conn.close()
    assert row[0] == "historic_data"


def test_get_today_consumption_returns_historicaldata(conn, monkeypatch):
    monkeypatch.setattr("app.inverter_db.get_today_start_epoch", lambda: 0)
    monkeypatch.setattr("app.inverter_db.get_today_end_epoch", lambda: 100)

    _insert_row(conn, epoch=10, value=1.2)

    result = get_today_consumption()
    assert isinstance(result, HistoricalData)


def test_get_today_consumption_values_have_time_and_value(conn, monkeypatch):
    monkeypatch.setattr("app.inverter_db.get_today_start_epoch", lambda: 0)
    monkeypatch.setattr("app.inverter_db.get_today_end_epoch", lambda: 100)

    _insert_row(conn, epoch=10, value=1.2)

    result = get_today_consumption()
    assert list(result.values[0].keys()) == ["time", "value"]


def test_get_last_30_days_returns_historicaldata(conn, monkeypatch):
    _freeze_time(monkeypatch, 1_000_000)
    _insert_row(conn, epoch=900_000, value=1.0)

    result = get_last_30_days()
    assert isinstance(result, HistoricalData)


def test_get_last_30_days_values_have_date_and_value(conn, monkeypatch):
    _freeze_time(monkeypatch, 1_000_000)
    _insert_row(conn, epoch=900_000, value=1.0)

    result = get_last_30_days()
    assert list(result.values[0].keys()) == ["date", "value"]


def test_get_last_365_days_returns_historicaldata(conn, monkeypatch):
    _freeze_time(monkeypatch, 1_000_000)
    _insert_row(conn, epoch=500_000, value=2.5)

    result = get_last_365_days()
    assert isinstance(result, HistoricalData)


def test_format_time_value_data_returns_list_of_dicts():
    rows = [{"epoch": 60, "value": 1.0}]
    result = _format_time_value_data(rows)
    assert list(result[0].keys()) == ["time", "value"]


def test_aggregate_by_date_returns_date_and_value():
    rows = [{"epoch": 1_000_000, "value": 2.0}]
    result = _aggregate_by_date(rows)
    assert list(result[0].keys()) == ["date", "value"]
