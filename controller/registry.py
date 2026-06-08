"""
controller/registry.py
Registro de routers conectados al controlador.
Almacena informacion de cada router: ID, IP, puerto y socket de conexion.
"""


class RouterRegistry:

    def __init__(self):
        # { router_id: { "ip": ..., "port": ..., "socket": ..., "status": ... } }
        self._routers = {}

    def register(self, router_id, ip, port, conn_socket):
        """Registra un router. Si ya existe, actualiza su informacion."""
        self._routers[router_id] = {
            "ip": ip,
            "port": port,
            "socket": conn_socket,
            "status": "active"
        }
        print(f"[Registry] Router registrado: {router_id} ({ip}:{port})")

    def get(self, router_id):
        """Retorna la info de un router o None si no existe."""
        return self._routers.get(router_id)

    def get_socket(self, router_id):
        """Retorna el socket de un router registrado."""
        entry = self._routers.get(router_id)
        return entry["socket"] if entry else None

    def all_ids(self):
        """Retorna lista de todos los IDs registrados."""
        return list(self._routers.keys())

    def remove(self, router_id):
        """Marca un router como inactivo cuando se desconecta."""
        if router_id in self._routers:
            self._routers[router_id]["status"] = "inactive"
            self._routers[router_id]["socket"] = None
            print(f"[Registry] Router desconectado: {router_id}")

    def count(self):
        return len(self._routers)

    def display(self):
        print("\n--- Routers registrados ---")
        for rid, info in self._routers.items():
            print(f"  {rid}  IP={info['ip']}  Puerto={info['port']}  Estado={info['status']}")
        print("-" * 28)