import sqlite3
from utils import helpers, lru_session_datasets as lru_sd

db_name = "data/NoM_db.db"

def _execute(query: str, data: tuple=()):
    with sqlite3.connect(db_name, timeout=30.0) as conn:
        curs = conn.cursor()
        curs.execute("""PRAGMA foreign_keys=ON""")
        curs.execute("""PRAGMA journal_mode=WAL""")

        curs.execute(query, data)
        return (curs.fetchall(), curs.lastrowid)

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
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            dataset_id INTEGER REFERENCES linked_datasets(id) ON DELETE CASCADE
        );
    """

    _execute(query)

def init_all():
    init_users()
    init_linked_datasets()
    init_session_datasets()
    init_models()

@helpers.return_data_control
def get_user_data(username: str):
    query = """
        SELECT *
        FROM users
        WHERE username = (?)
    """

    return _execute(query, (username,))

def add_user(username: str, password_hash: bytes):
    query = """
        INSERT INTO users
        (username, password_hash) VALUES (?, ?)
    """
    return _execute(query, (username, password_hash))[1]

@helpers.return_data_control
def get_linked_dataset_data(id: int):
    query = """
        SELECT *
        FROM linked_datasets
        WHERE id = (?)
    """
    return _execute(query, (id,))

def add_linked_dataset(name: str, path_to_file: str):
    query = """
        INSERT INTO linked_datasets
        (name, path_to_file) VALUES (?, ?)
    """
    return _execute(query, (name, path_to_file))[1]

@helpers.return_data_control
def get_session_dataset_data(id: int):
    query = """
        SELECT *
        FROM session_datasets
        WHERE id = (?)
    """
    return _execute(query, (id,))

def add_session_dataset(name: str, path_to_file: str, time: int):
    query = """
        INSERT INTO session_datasets
        (name, path_to_file, last_action_time) VALUES (?, ?, ?)
    """
    lru_sd.lru_session_datasets._with_path(path_to_file)

    return _execute(query, (name, path_to_file, time))[1]

@helpers.return_data_control
def get_model_data(id: int):
    query = """
        SELECT *
        FROM models
        WHERE id = (?)
    """
    return _execute(query, (id,))

def add_model(name: str, path_to_file: str, user_id: int, model_type: str, train_date: int, description: str, dataset_id: int):
    query = """
        INSERT INTO models
        (name, path_to_file, user_id, model_type, train_date, description, dataset_id) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    return _execute(query, (name, path_to_file, user_id, model_type, train_date, description, dataset_id))[1]