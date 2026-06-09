"""
controller/dao/db_connection.py
Maneja la conexion a la base de datos MySQL.
Usa mysql-connector-python.
"""

import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host":     "127.0.0.1",
    "user":     "root",
    "password": "",
    "database": "centralized_routing_controller"
}


def get_connection():
    """Retorna una conexion activa a MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB] Error al conectar a MySQL: {e}")
        return None