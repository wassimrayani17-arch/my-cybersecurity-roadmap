import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "task_api"),
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "task_tracker"),
    )
