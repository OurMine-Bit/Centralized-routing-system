"""
controller/logger.py
Logging de eventos del sistema de ruteo centralizado.
Registra en consola y en archivo de log con timestamp.
Cubre FR-09: registro de eventos importantes del sistema.
"""

import os
from datetime import datetime
from controller.dao.log_dao import LogDAO
_log_dao = LogDAO()

class SystemLogger:

    def __init__(self, log_file="routing_system.log"):
        self.log_file = log_file
        # Crear o limpiar el archivo al iniciar
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"=== Centralized Routing System Log ===\n")
            f.write(f"Inicio: {self._timestamp()}\n")
            f.write("=" * 40 + "\n\n")

    def _timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _write(self, level, category, message):
        line = f"[{self._timestamp()}] [{level}] [{category}] {message}"
        print(line)
        _log_dao.save_event(category, message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def info(self, category, message):
        self._write("INFO ", category, message)

    def warning(self, category, message):
        self._write("WARN ", category, message)

    def error(self, category, message):
        self._write("ERROR", category, message)

    # --- Metodos especificos por evento ---

    def log_router_registered(self, router_id, ip, port):
        self.info("REGISTRATION", f"Router {router_id} registrado — IP={ip} Puerto={port}")

    def log_topology_update(self, router_id, neighbors):
        neighbors_str = ", ".join(f"{n['neighbor_id']}(costo={n['cost']})" for n in neighbors)
        self.info("TOPOLOGY", f"Topologia actualizada desde {router_id} — Vecinos: {neighbors_str}")

    def log_route_computation(self, num_routers):
        self.info("DIJKSTRA", f"Calculo de rutas iniciado para {num_routers} routers")

    def log_table_delivered(self, router_id, num_entries):
        self.info("DELIVERY", f"Tabla de ruteo enviada a {router_id} ({num_entries} entradas)")

    def log_table_failed(self, router_id):
        self.warning("DELIVERY", f"No se pudo enviar tabla a {router_id} — sin socket activo")

    def log_link_update(self, source, destination, old_cost, new_cost):
        self.info("LINK_UPDATE", f"Enlace {source}<->{destination} actualizado: {old_cost} -> {new_cost}")

    def log_invalid_message(self, error):
        self.error("PROTOCOL", f"Mensaje invalido recibido: {error}")

    def log_router_disconnected(self, router_id):
        self.warning("CONNECTION", f"Router {router_id} desconectado")