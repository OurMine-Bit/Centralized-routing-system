"""
controller/dao/router_dao.py
Acceso a datos de la tabla routers en MySQL.
"""

from controller.dao.db_connection import get_connection


class RouterDAO:

    def save(self, router_id, ip, puerto):
        """Inserta o actualiza un router en la base de datos."""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            # Si ya existe, actualiza el estado a activo
            cursor.execute(
                "SELECT id FROM routers WHERE router_id = %s",
                (router_id,)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE routers SET ip=%s, puerto=%s, estado='activo' WHERE router_id=%s",
                    (ip, puerto, router_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO routers (router_id, ip, puerto, estado) VALUES (%s, %s, %s, 'activo')",
                    (router_id, ip, puerto)
                )
            conn.commit()
        except Exception as e:
            print(f"[RouterDAO] Error al guardar router: {e}")
        finally:
            cursor.close()
            conn.close()

    def set_inactive(self, router_id):
        """Marca un router como inactivo cuando se desconecta."""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE routers SET estado='inactivo' WHERE router_id=%s",
                (router_id,)
            )
            conn.commit()
        except Exception as e:
            print(f"[RouterDAO] Error al actualizar estado: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_all(self):
        """Retorna todos los routers registrados."""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM routers")
            return cursor.fetchall()
        except Exception as e:
            print(f"[RouterDAO] Error al obtener routers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()