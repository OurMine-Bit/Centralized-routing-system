"""
controller/registry.py
Registro de routers conectados al controlador.
Sprint 3: integra logging de eventos de conexion y desconexion.
"""
from controller.dao.router_dao import RouterDAO
_router_dao = RouterDAO()



class RouterRegistry:

    def __init__(self, logger=None):
        self._routers = {}
        self._logger = logger

    def register(self, router_id, ip, port, conn_socket):
        self._routers[router_id] = {
            "ip": ip,
            "port": port,
            "socket": conn_socket,
            "status": "active"
        }
        print(f"[Registry] Router registrado: {router_id} ({ip}:{port})")
        _router_dao.save(router_id, ip, port)
        if self._logger:
            self._logger.log_router_registered(router_id, ip, port)

    def get(self, router_id):
        return self._routers.get(router_id)

    def get_socket(self, router_id):
        entry = self._routers.get(router_id)
        return entry["socket"] if entry and entry["status"] == "active" else None

    def all_ids(self):
        return [rid for rid, info in self._routers.items() if info["status"] == "active"]

    def remove(self, router_id):
        if router_id in self._routers:
            self._routers[router_id]["status"] = "inactive"
            self._routers[router_id]["socket"] = None
            print(f"[Registry] Router desconectado: {router_id}")
            _router_dao.set_inactive(router_id)
            if self._logger:
                self._logger.log_router_disconnected(router_id)

    def count(self):
        return len(self._routers)

    def display(self):
        print("\n--- Routers registrados ---")
        for rid, info in self._routers.items():
            print(f"  {rid}  IP={info['ip']}  Puerto={info['port']}  Estado={info['status']}")
        print("-" * 28)