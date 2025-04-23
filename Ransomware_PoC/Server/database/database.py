import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'server.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Crear tabla de agentes
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            mac TEXT NOT NULL,
            so TEXT NOT NULL,
            private_key TEXT NOT NULL,
            pay_status BOOLEAN NOT NULL DEFAULT FALSE,
            timestamp TEXT NOT NULL 
        )
    ''')
    # Crear tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Insertar un usuario por defecto 
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES ('hacker', 'hacker123')")

    conn.commit()
    conn.close()
