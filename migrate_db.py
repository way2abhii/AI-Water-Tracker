"""One-time migration script to update existing water_tracker.db schema."""
import sqlite3

conn = sqlite3.connect("water_tracker.db")
cur = conn.cursor()

# ── water_intake table ─────────────────────────────────────────────────────
cur.execute("PRAGMA table_info(water_intake)")
intake_cols = [r[1] for r in cur.fetchall()]
print("water_intake columns:", intake_cols)

if "note" not in intake_cols:
    cur.execute("ALTER TABLE water_intake ADD COLUMN note TEXT DEFAULT ''")
    print("  + Added: note")

if "logged_at" not in intake_cols:
    cur.execute("ALTER TABLE water_intake ADD COLUMN logged_at TEXT DEFAULT '2024-01-01 00:00:00'")
    print("  + Added: logged_at")

# ── users table ─────────────────────────────────────────────────────────────
cur.execute("PRAGMA table_info(users)")
user_cols = [r[1] for r in cur.fetchall()]
print("users columns:", user_cols)

# (create_tables() in database.py will create it if missing; nothing extra needed)

conn.commit()
conn.close()
print("Migration complete.")
