"""
controller/dao/topology_dao.py
Acceso a datos de la tabla enlaces en MySQL.
"""

from controller.dao.db_connection import get_connection


class TopologyDAO:

    def save_link(self, source, destination, cost):
        """Inserta o actualiza un enlace en la base de datos."""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM enlaces WHERE source_router=%s AND destination_router=%s",
                (source, destination)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE enlaces SET cost=%s WHERE source_router=%s AND destination_router=%s",
                    (cost, source, destination)
                )
            else:
                cursor.execute(
                    "INSERT INTO enlaces (source_router, destination_router, cost) VALUES (%s, %s, %s)",
                    (source, destination, cost)
                )
            conn.commit()
        except Exception as e:
            print(f"[TopologyDAO] Error al guardar enlace: {e}")
        finally:
            cursor.close()
            conn.close()

    def save_topology(self, graph):
        """
        Guarda toda la topologia en la base de datos.
        graph: { "R1": {"R2": 4, "R3": 2}, ... }
        """
        for source, neighbors in graph.items():
            for destination, cost in neighbors.items():
                self.save_link(source, destination, cost)

    def get_all(self):
        """Retorna todos los enlaces almacenados."""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM enlaces")
            return cursor.fetchall()
        except Exception as e:
            print(f"[TopologyDAO] Error al obtener enlaces: {e}")
            return []
        finally:
            cursor.close()
            conn.close()