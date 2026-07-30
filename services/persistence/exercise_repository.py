import sqlite3
import streamlit as st 
from pathlib import Path

_DB_PATH = str(Path(__file__).parent.parent / "data.db")

@st.cache_resource
def _get_connection():
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           username TEXT UNIQUE NOT NULL,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            exercise_name TEXT NOT NULL,
            reps INTEGER NOT NULL DEFAULT 0,
            sets INTEGER NOT NULL DEFAULT 0,
            time INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

def get_user(username):
    conn = _get_connection()
    return conn.execute("""
    SELECT * FROM users WHERE username = ?
    """, (username,)).fetchone()

def create_user(username):
    conn = _get_connection()
    with conn:
        conn.execute("""
           INSERT INTO users (username) VALUES (?)
        """, (username,))

    return get_user(username)

def get_or_create_user(username):
    user = get_user(username)
    if user is None:
        user = create_user(username)
    return user

def add_exercise(user_id, exercise_name, reps, sets, time):
    if not user_id or user_id == 0:
        username = st.session_state.get("username")
        if username:
            user = get_or_create_user(username)
            user_id = user["id"]
        else:
            user_id = 1

    conn = _get_connection()
    with conn:
        existing = conn.execute("""
           SELECT * FROM exercises
           WHERE user_id = ? AND exercise_name = ? AND DATE(created_at) = DATE('now') 
        """, (user_id, exercise_name)).fetchone()

        if existing:
            conn.execute("""
               UPDATE exercises
               SET reps = reps + ?, sets = sets + ?, time = time + ?
               WHERE id = ?
            """, (reps, sets, int(time), existing['id']))
        else:
            conn.execute("""
               INSERT INTO exercises (user_id, exercise_name, reps, sets, time)
               VALUES (?, ?, ?, ?, ?)
            """, (user_id, exercise_name, reps, sets, int(time)))

def get_users_exercise(user_id=None, username=None):
    if not user_id or user_id == 0:
        username = username or st.session_state.get("username")
        if username:
            user = get_user(username)
            if user:
                user_id = user["id"]

    conn = _get_connection()
    if user_id:
        return conn.execute("""
           SELECT * FROM exercises
           WHERE user_id = ?
           ORDER BY created_at DESC
        """, (user_id,)).fetchall()
    else:
        return conn.execute("""
           SELECT * FROM exercises
           ORDER BY created_at DESC
        """).fetchall()

get_users_exercises = get_users_exercise
