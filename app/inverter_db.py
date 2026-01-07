from collections import defaultdict
from pathlib import Path
import time
from datetime import datetime
import sqlite3
from sqlite3 import DatabaseError

DB_PATH = Path(__file__).parent / "database.db"

class HistoricalData:
    """Container for historical energy data with unit and time-series values."""

    def __init__(self, unit: str, values: list):
        """Initialize with measurement unit and data values."""
        self.unit = unit
        self.values = values

def get_connection():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for historic data and inverter configuration."""
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inverter (
            username TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            token TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_inverter(username: str):
    """Retrieve inverter configuration for a specific username."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM inverter WHERE username = ?", (username,))
            row = cur.fetchone()
            return dict(row) if row else None
    except DatabaseError:
        return None


def add_inverter(data) -> bool:
    """Add new inverter configuration to the database."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO inverter (username, name, ip_address, token) VALUES (?, ?, ?, ?)",
                (data["username"], data["name"], data["ip_address"], data["token"])
            )
            conn.commit()
        return True
    except DatabaseError:
        return False


def update_inverter(data) -> bool:
    """Update existing inverter configuration in the database."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE inverter
                SET name = ?, ip_address = ?, token = ?
                WHERE username = ?
            """, (data["name"], data["ip_address"], data["token"], data["username"]))
            conn.commit()
            return cur.rowcount > 0
    except DatabaseError:
        return False


def delete_inverter(username: str) -> bool:
    """Delete inverter configuration for a specific username."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        DELETE
                        from inverter
                        WHERE username = ? """, (username,))
            conn.commit()
        return True
    except DatabaseError:
        return False


def get_token() -> str:
    """Retrieve the inverter's authentication token from the database."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT token FROM inverter")
            data = cur.fetchall()
            return data[0][0] if data else ""
    except DatabaseError as e:
        print(e)
        return ""

def get_ipadress() -> str:
    """Retrieve the inverter's IP address from the database."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ip_address FROM inverter")
            data = cur.fetchall()
            return data[0][0] if data else ""
    except DatabaseError as e:
        print(e)
        return ""




def get_today_consumption():
    """Retrieve energy consumption data for the current day."""
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
    """Retrieve aggregated daily energy consumption for the last 30 days."""
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
    """Retrieve aggregated daily energy consumption for the last 365 days."""
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
    """Get epoch timestamp for today's midnight (00:00:00)."""
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return int(today_midnight.timestamp())

def get_today_end_epoch():
    """Get epoch timestamp for today's end (23:59:59)."""
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 23, 59, 59)
    return int(today_midnight.timestamp())


def _format_time_value_data(rows):
    """Format database rows into time-value pairs for intraday data."""
    return [
        {
            "time": _epoch_to_time_string(row["epoch"]),
            "value": row["value"]
        }
        for row in rows
    ]

def _epoch_to_time_string(epoch):
    """Convert epoch timestamp to HH:MM time string."""
    return datetime.fromtimestamp(epoch).strftime("%H:%M")

def _aggregate_by_date(rows):
    """Aggregate consumption values by date and return sorted date-value pairs."""
    per_day = defaultdict(float)
    for row in rows:
        date_str = datetime.fromtimestamp(row["epoch"]).strftime("%Y-%m-%d")
        per_day[date_str] += row["value"]

    return [
        {"date": date, "value": round(per_day[date], 2)}
        for date in sorted(per_day.keys())
    ]


