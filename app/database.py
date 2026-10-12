import mysql.connector

from .settings import MYSQL_CONFIG


def connect():
    """Open a MySQL connection using settings from the local .env file."""
    return mysql.connector.connect(**MYSQL_CONFIG)
