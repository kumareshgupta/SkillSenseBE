# backend/db_handler.py
import sqlite3

DB_NAME = "participants.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            contact TEXT,
            experience TEXT,
            current_skill TEXT,
            wish_to_upskill TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_participant(name, email, contact, experience, current_skill, wish_to_upskill):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO participants (name, email, contact, experience, current_skill, wish_to_upskill)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, contact, experience, current_skill, ",".join(wish_to_upskill)))
    conn.commit()
    conn.close()
