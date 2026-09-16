import os
import mysql.connector
import pytest
from fastapi.testclient import TestClient

from app import db as db_module
from app.main import app

TEST_DB_CONFIG = {
    "host": "localhost",
    "user": "task_api",
    "password": os.environ["DB_PASSWORD"],
    "database": "fastapi_test_db",
}


@pytest.fixture()
def db_connection(monkeypatch):
    # 1. Create fresh tables in the TEST database before the test runs.
    conn = mysql.connector.connect(**TEST_DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT NOT NULL,
            body TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

    # 2. Replace get_connection so it points at the TEST database
    def get_test_connection():
        return mysql.connector.connect(**TEST_DB_CONFIG)

    monkeypatch.setattr(db_module, "get_connection", get_test_connection)

    yield  # test runs here

    # 3. Clean up: wipe the tables after the test finishes.
    conn = mysql.connector.connect(**TEST_DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS comments;")
    cur.execute("DROP TABLE IF EXISTS tasks;")
    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture()
def client(db_connection):
    return TestClient(app)