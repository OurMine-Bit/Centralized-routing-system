"""
controller/dao/log_dao.py
Acceso a datos de la tabla eventos en MySQL.
"""

from controller.dao.db_connection import get_connection


class LogDAO:

    def save_event(self, tipo, descripcion):
        """Guarda un evento en la tabla eventos."""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eventos (tipo, descripcion) VALUES (%s, %s)",
                (tipo, descripcion)
            )
            conn.commit()
        except Exception as e:
            print(f"[LogDAO] Error al guardar evento: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all(self):
        """Retorna todos los eventos registrados."""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM eventos ORDER BY timestamp DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[LogDAO] Error al obtener eventos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()