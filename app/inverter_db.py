from collections import defaultdict
from pathlib import Path
import time
from datetime import datetime
import sqlite3

DB_PATH = Path(__file__).parent / "database.db"

class HistoricalData:
    def __init__(self, unit: str, values: list):
        self.unit = unit
        self.values = values

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            epoch INTEGER NOT NULL,
            unit TEXT NOT NULL,
            value REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_today_consumption():
    start_epoch = get_today_start_epoch()
    end_epoch = get_today_end_epoch()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT epoch, unit, value
                    FROM historic_data
                    WHERE epoch >= ? AND epoch <= ?
                    ORDER BY epoch ASC
                    """, (start_epoch,end_epoch))
        rows = cur.fetchall()

    if not rows:
        return HistoricalData(unit="", values=[])

    unit = rows[0]["unit"]
    values = _format_time_value_data(rows)

    return HistoricalData(unit=unit, values=values)


def get_last_30_days():
    now_epoch = int(time.time())
    cutoff = now_epoch - 30 * 24 * 3600

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT epoch, unit, value
                    FROM historic_data
                    WHERE epoch >= ?
                    ORDER BY epoch ASC
                    """, (cutoff,))
        rows = cur.fetchall()

    if not rows:
        return HistoricalData(unit="", values=[])

    unit = rows[0]["unit"]
    values = _aggregate_by_date(rows)

    return HistoricalData(unit=unit, values=values)


def get_last_365_days():
    now_epoch = int(time.time())
    cutoff = now_epoch - 365 * 24 * 3600

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT epoch, unit, value
                    FROM historic_data
                    WHERE epoch >= ?
                    ORDER BY epoch ASC
                    """, (cutoff,))
        rows = cur.fetchall()
    if not rows:
        return HistoricalData(unit="", values=[])

    unit = rows[0]["unit"]
    values = _aggregate_by_date(rows)

    return HistoricalData(unit=unit, values=values)


def get_today_start_epoch():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return int(today_midnight.timestamp())

def get_today_end_epoch():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 23, 59, 59)
    return int(today_midnight.timestamp())


def _format_time_value_data(rows):
    return [
        {
            "time": _epoch_to_time_string(row["epoch"]),
            "value": row["value"]
        }
        for row in rows
    ]

def _epoch_to_time_string(epoch):
    return datetime.fromtimestamp(epoch).strftime("%H:%M")

def _aggregate_by_date(rows):
    per_day = defaultdict(float)
    for row in rows:
        date_str = datetime.fromtimestamp(row["epoch"]).strftime("%Y-%m-%d")
        per_day[date_str] += row["value"]

    return [
        {"date": date, "value": round(per_day[date], 2)}
        for date in sorted(per_day.keys())
    ]


