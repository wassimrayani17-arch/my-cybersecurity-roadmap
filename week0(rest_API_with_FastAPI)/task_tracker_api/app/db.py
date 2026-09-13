import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="task_api",
        password=os.environ["DB_PASSWORD"],
        database="task_tracker",
    )