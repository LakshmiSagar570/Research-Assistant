import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "data", "app.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = [info[1] for info in cur.execute("PRAGMA table_info(users)").fetchall()]
    print("Existing users table columns:", cols)
    if "college" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN college TEXT DEFAULT ''")
        print("Added college column")
    if "department" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN department TEXT DEFAULT ''")
        print("Added department column")
    conn.commit()
    conn.close()
    print("Database migration successfully applied.")
else:
    print("No local app.db file found yet; it will be created on server startup.")
