import sqlite3
from pathlib import Path
from dotenv import load_dotenv

from utils import lru_session_datasets


load_dotenv()
db_name = Path.cwd() / "data" / "NoM.db"
db_name.parent.mkdir(parents=True, exist_ok=True)

def _execute(query: str, data: tuple=()):
    with sqlite3.connect(db_name, timeout=30.0) as conn:
        curs = conn.cursor()
        curs.execute("""PRAGMA foreign_keys=ON""")
        curs.execute("""PRAGMA journal_mode=WAL""")

        curs.execute(query, data)
        fetchall = curs.fetchall()
        lastrowid = curs.lastrowid

        return (fetchall, lastrowid)

def init_users():
    query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash BLOB NOT NULL
        );
    """

    _execute(query)

def init_linked_datasets():
    query = """
        CREATE TABLE IF NOT EXISTS linked_datasets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path_to_file TEXT NOT NULL
        );
    """

    _execute(query)

def init_session_datasets():
    query = """
        CREATE TABLE IF NOT EXISTS session_datasets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path_to_file TEXT NOT NULL,
            last_action_time INTEGER NOT NULL
        );
    """

    _execute(query)

def init_models():
    query = """
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path_to_file TEXT NOT NULL,
            model_type TEXT NOT NULL,
            train_date INTEGER NOT NULL,
            description TEXT NOT NULL,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            dataset_id INTEGER REFERENCES linked_datasets(id) ON DELETE SET NULL
        );
    """

    _execute(query)

def init_all():
    init_users()
    init_linked_datasets()
    init_session_datasets()
    init_models()

def get_user_data(username: str):
    query = """
        SELECT *
        FROM users
        WHERE username = (?)
    """
    fetchall, lastrowid = _execute(query, (username,))

    return fetchall[0] if fetchall else None

def add_user(username: str, password_hash: bytes):
    query = """
        INSERT INTO users
        (username, password_hash) VALUES (?, ?)
    """
    fetchall, lastrowid = _execute(query, (username, password_hash))

    return lastrowid

def get_linked_dataset_data(dataset_id: int):
    query = """
        SELECT *
        FROM linked_datasets
        WHERE id = (?)
    """
    fetchall, lastrowid = _execute(query, (dataset_id,))

    return fetchall[0] if fetchall else None

def add_linked_dataset(name: str, path_to_file: str):
    query = """
        INSERT INTO linked_datasets
        (name, path_to_file) VALUES (?, ?)
    """
    fetchall, lastrowid = _execute(query, (name, path_to_file))

    return lastrowid

def get_session_dataset_data(dataset_id: int):
    query = """
        SELECT *
        FROM session_datasets
        WHERE id = (?)
    """
    fetchall, lastrowid = _execute(query, (dataset_id,))

    return fetchall[0] if fetchall else None

def add_session_dataset(name: str, path_to_file: str, time: int):
    query = """
        INSERT INTO session_datasets
        (name, path_to_file, last_action_time) VALUES (?, ?, ?)
    """
    fetchall, lastrowid = _execute(query, (name, path_to_file, time))
    lru_session_datasets._set_dataset(lastrowid, path_to_file)

    return lastrowid

def get_model_data(model_id: int):
    query = """
        SELECT *
        FROM models
        WHERE id = (?)
    """
    fetchall, lastrowid = _execute(query, (model_id,))

    return fetchall[0] if fetchall else None

def add_model(name: str, path_to_file: str, user_id: int, model_type: str, train_date: int, description: str, dataset_id: int):
    query = """
        INSERT INTO models
        (name, path_to_file, user_id, model_type, train_date, description, dataset_id) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    fetchall, lastrowid = _execute(query, (name, path_to_file, user_id, model_type, train_date, description, dataset_id))

    return lastrowid