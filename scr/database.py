import sqlite3
import uuid
import hashlib
from datetime import datetime

DB_NAME = "water_tracker.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        weight_kg REAL DEFAULT 70.0,
        activity_level TEXT DEFAULT 'moderate',
        daily_goal_ml INTEGER DEFAULT 2500,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Water intake table (now references users.user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS water_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        intake_ml INTEGER NOT NULL,
        note TEXT,
        logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    conn.commit()
    conn.close()


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_user_id() -> str:
    """Generate a unique user ID with prefix."""
    return "USR-" + str(uuid.uuid4())[:8].upper()


def create_user(username: str, email: str, password: str,
                full_name: str = "", weight_kg: float = 70.0,
                activity_level: str = "moderate") -> dict:
    """
    Register a new user.
    Returns dict with success/error info.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check duplicates
    cursor.execute("SELECT 1 FROM users WHERE username=? OR email=?", (username, email))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "error": "Username or email already exists."}

    user_id = generate_user_id()
    password_hash = hash_password(password)

    # Calculate recommended daily goal based on weight & activity
    daily_goal_ml = calculate_daily_goal(weight_kg, activity_level)

    cursor.execute("""
    INSERT INTO users (user_id, username, email, password_hash, full_name,
                       weight_kg, activity_level, daily_goal_ml)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, email, password_hash, full_name,
          weight_kg, activity_level, daily_goal_ml))

    conn.commit()
    conn.close()
    return {"success": True, "user_id": user_id}


def authenticate_user(username_or_email: str, password: str) -> dict | None:
    """
    Verify credentials and return user dict or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)

    cursor.execute("""
    SELECT user_id, username, email, full_name, weight_kg,
           activity_level, daily_goal_ml, created_at
    FROM users
    WHERE (username=? OR email=?) AND password_hash=?
    """, (username_or_email, username_or_email, password_hash))

    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a user record by user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT user_id, username, email, full_name, weight_kg,
           activity_level, daily_goal_ml, created_at
    FROM users WHERE user_id=?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id: str, full_name: str,
                        weight_kg: float, activity_level: str):
    """Update user profile and recalculate daily goal."""
    daily_goal_ml = calculate_daily_goal(weight_kg, activity_level)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET full_name=?, weight_kg=?, activity_level=?, daily_goal_ml=?
    WHERE user_id=?
    """, (full_name, weight_kg, activity_level, daily_goal_ml, user_id))
    conn.commit()
    conn.close()
    return daily_goal_ml


# ─── Intake helpers ────────────────────────────────────────────────────────────

def calculate_daily_goal(weight_kg: float, activity_level: str) -> int:
    """
    Estimate daily water goal in ml.
    Base: 35 ml/kg.  Activity multipliers applied.
    """
    base = weight_kg * 35
    multipliers = {
        "sedentary": 0.9,
        "light": 1.0,
        "moderate": 1.1,
        "active": 1.2,
        "very_active": 1.35,
    }
    return int(base * multipliers.get(activity_level, 1.0))


def log_intake(user_id: str, intake_ml: int, note: str = ""):
    """Log a water intake entry for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    date_today = datetime.today().strftime("%Y-%m-%d")
    logged_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO water_intake (user_id, intake_ml, note, logged_at, date)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, intake_ml, note, logged_at, date_today))
    conn.commit()
    conn.close()


def get_today_total(user_id: str) -> int:
    """Get total ml consumed today."""
    conn = get_connection()
    cursor = conn.cursor()
    date_today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT COALESCE(SUM(intake_ml), 0) FROM water_intake
    WHERE user_id=? AND date=?
    """, (user_id, date_today))
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_intake_history(user_id: str, days: int = 7) -> list:
    """Get last N days of intake records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT intake_ml, note, logged_at, date
    FROM water_intake
    WHERE user_id=?
    ORDER BY logged_at DESC
    LIMIT 200
    """, (user_id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records


def get_daily_totals(user_id: str, days: int = 7) -> list:
    """Get per-day totals for the last N days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, SUM(intake_ml) as total_ml
    FROM water_intake
    WHERE user_id=?
    GROUP BY date
    ORDER BY date DESC
    LIMIT ?
    """, (user_id, days))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records


# Run migrations on import
create_tables()
