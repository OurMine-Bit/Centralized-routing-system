"""
controller/server.py
Servidor TCP del controlador.
Sprint 3: integra logging de mensajes invalidos y entregas de tablas.
"""

import socket
import threading
import json

from shared.messages import (
    MSG_REGISTER_ROUTER, MSG_TOPOLOGY_UPDATE,
    MSG_LINK_COST_UPDATE, MSG_ACK, MSG_ERROR,
    build_ack, build_error, build_routing_table, encode, decode
)


class ControllerServer:

    def __init__(self, host, port, registry, topology, on_topology_ready=None, logger=None):
        self.host = host
        self.port = port
        self.registry = registry
        self.topology = topology
        self.on_topology_ready = on_topology_ready
        self._logger = logger
        self._server_socket = None
        self._running = False
        self._lock = threading.Lock()

    def start(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)
        self._running = True
        print(f"[Server] Controlador escuchando en {self.host}:{self.port}")
        t = threading.Thread(target=self._accept_loop, daemon=True)
        t.start()

    def stop(self):
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        print("[Server] Servidor detenido.")

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                print(f"[Server] Nueva conexion desde {addr}")
                t = threading.Thread(target=self._handle_router, args=(conn, addr), daemon=True)
                t.start()
            except OSError:
                break

    def _handle_router(self, conn, addr):
        router_id = None
        buffer = b""
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    router_id = self._process_message(line, conn, router_id)
        except ConnectionResetError:
            print(f"[Server] Conexion reiniciada por {addr}")
        except Exception as e:
            print(f"[Server] Error inesperado con {addr}: {e}")
        finally:
            if router_id:
                with self._lock:
                    self.registry.remove(router_id)
            conn.close()

    def _process_message(self, raw, conn, current_router_id):
        try:
            msg = decode(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            error_msg = f"JSON invalido: {e}"
            print(f"[Server] Mensaje invalido recibido: {e}")
            if self._logger:
                self._logger.log_invalid_message(error_msg)
            self._send(conn, build_error("unknown", error_msg))
            return current_router_id

        msg_type = msg.get("type")

        if msg_type == MSG_REGISTER_ROUTER:
            return self._handle_register(msg, conn)
        elif msg_type == MSG_TOPOLOGY_UPDATE:
            self._handle_topology(msg, conn)
            return current_router_id
        elif msg_type == MSG_LINK_COST_UPDATE:
            self._handle_link_update(msg, conn)
            return current_router_id
        else:
            print(f"[Server] Tipo de mensaje desconocido: {msg_type}")
            if self._logger:
                self._logger.log_invalid_message(f"Tipo desconocido: {msg_type}")
            self._send(conn, build_error(msg.get("router_id", "unknown"),
                                         f"Tipo desconocido: {msg_type}"))
            return current_router_id

    def _handle_register(self, msg, conn):
        router_id = msg.get("router_id")
        ip        = msg.get("ip")
        port      = msg.get("port")
        if not all([router_id, ip, port]):
            self._send(conn, build_error("unknown", "Campos faltantes en REGISTER_ROUTER"))
            return None
        with self._lock:
            self.registry.register(router_id, ip, port, conn)
        self._send(conn, build_ack(router_id, MSG_REGISTER_ROUTER))
        self.registry.display()
        return router_id

    def _handle_topology(self, msg, conn):
        router_id = msg.get("router_id")
        neighbors = msg.get("neighbors", [])
        if not router_id:
            self._send(conn, build_error("unknown", "Falta router_id en TOPOLOGY_UPDATE"))
            return
        with self._lock:
            self.topology.update(router_id, neighbors)
        self._send(conn, build_ack(router_id, MSG_TOPOLOGY_UPDATE))
        self.topology.display()
        if self.on_topology_ready:
            self.on_topology_ready(self.topology)

    def _handle_link_update(self, msg, conn):
        source      = msg.get("source")
        destination = msg.get("destination")
        new_cost    = msg.get("new_cost")
        if not all([source, destination, new_cost is not None]):
            self._send(conn, build_error(msg.get("router_id", "unknown"),
                                          "Campos faltantes en LINK_COST_UPDATE"))
            return
        with self._lock:
            updated = self.topology.update_link_cost(source, destination, new_cost)
        router_id = msg.get("router_id", source)
        if updated:
            self._send(conn, build_ack(router_id, MSG_LINK_COST_UPDATE))
            if self.on_topology_ready:
                self.on_topology_ready(self.topology)
        else:
            self._send(conn, build_error(router_id,
                                          f"Enlace {source}-{destination} no encontrado"))

    def _send(self, conn, msg_dict):
        try:
            conn.sendall(encode(msg_dict))
        except OSError as e:
            print(f"[Server] Error al enviar: {e}")

    def send_to_router(self, router_id, msg_dict):
        conn = self.registry.get_socket(router_id)
        if conn:
            self._send(conn, msg_dict)
            return True
        return False

    def send_to_all_routers(self, routing_tables):
        """
        Recibe { router_id: [lista de entradas] } y envia
        el mensaje ROUTING_TABLE a cada router activo.
        """
        total = len(routing_tables)
        sent  = 0
        for router_id, table in routing_tables.items():
            msg  = build_routing_table(router_id, table)
            conn = self.registry.get_socket(router_id)
            if conn:
                self._send(conn, msg)
                sent += 1
                print(f"[Server] Tabla de ruteo enviada a {router_id} ({len(table)} entradas).")
                if self._logger:
                    self._logger.log_table_delivered(router_id, len(table))
            else:
                print(f"[Server] Router {router_id} no tiene socket activo — tabla no enviada.")
                if self._logger:
                    self._logger.log_table_failed(router_id)
        print(f"[Server] Tablas distribuidas: {sent}/{total} routers.")