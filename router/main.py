"""
router/main.py
Punto de entrada de cada router.
Uso: python router/main.py --config router/config/r1.json

Lee su configuracion desde un JSON, se conecta al controlador,
se registra y envia su informacion de vecinos.
Queda en espera indefinida hasta recibir la tabla de ruteo del controlador.
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from router.client import RouterClient
from shared.messages import (
    build_register, build_topology_update,
    MSG_ACK, MSG_ERROR, MSG_ROUTING_TABLE
)


def load_config(path):
    """Lee el archivo JSON de configuracion del router."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def display_routing_table(router_id, routing_table):
    """Muestra la tabla de ruteo recibida en formato legible por CLI."""
    print(f"\n{'='*45}")
    print(f"  Tabla de ruteo — {router_id}")
    print(f"{'='*45}")
    print(f"  {'Destino':<12} {'Next Hop':<12} {'Costo':<8}")
    print(f"  {'-'*32}")
    for entry in routing_table:
        dest     = entry.get("destination", "?")
        next_hop = entry.get("next_hop", "?")
        cost     = entry.get("cost", "?")
        print(f"  {dest:<12} {next_hop:<12} {cost:<8}")
    print(f"{'='*45}\n")


def main():
    parser = argparse.ArgumentParser(description="Router del sistema de ruteo centralizado")
    parser.add_argument(
        "--config",
        required=True,
        help="Ruta al archivo JSON de configuracion del router (ej. router/config/r1.json)"
    )
    args = parser.parse_args()

    # --- Cargar configuracion ---
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"[Error] No se encontro el archivo de configuracion: {args.config}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[Error] JSON de configuracion invalido: {e}")
        sys.exit(1)

    router_id       = config["router_id"]
    router_ip       = config["ip"]
    router_port     = config["port"]
    controller_host = config["controller"]["host"]
    controller_port = config["controller"]["port"]
    neighbors       = config["neighbors"]

    print("=" * 45)
    print(f"  Router {router_id}  ({router_ip}:{router_port})")
    print("=" * 45)

    # timeout=10 para la fase de conexion y registro.
    # Luego set_blocking() lo cambia a espera infinita para no
    # desconectarse mientras espera la tabla de ruteo (Sprint 2).
    client = RouterClient(controller_host, controller_port, timeout=10)
    if not client.connect():
        sys.exit(1)

    # --- Registro (FR-01) ---
    print(f"\n[{router_id}] Enviando registro al controlador...")
    reg_msg  = build_register(router_id, router_ip, router_port)
    response = client.send_and_wait(reg_msg)

    if response is None:
        print(f"[{router_id}] Sin respuesta al registro. Abortando.")
        client.disconnect()
        sys.exit(1)

    if response.get("type") == MSG_ACK:
        print(f"[{router_id}] Registro confirmado por el controlador.")
    elif response.get("type") == MSG_ERROR:
        print(f"[{router_id}] Error en registro: {response.get('message')}")
        client.disconnect()
        sys.exit(1)

    # --- Envio de topologia (FR-02) ---
    print(f"[{router_id}] Enviando informacion de vecinos...")
    topo_msg = build_topology_update(router_id, neighbors)
    response = client.send_and_wait(topo_msg)

    if response and response.get("type") == MSG_ACK:
        print(f"[{router_id}] Topologia aceptada por el controlador.")
    else:
        print(f"[{router_id}] Respuesta inesperada a topologia: {response}")

    # --- Esperar tabla de ruteo (FR-06) ---
    # Sin timeout: el router queda vivo hasta que el controlador
    # le envie su tabla en Sprint 2.
    client.set_blocking()
    print(f"[{router_id}] Esperando tabla de ruteo del controlador...")
    print(f"[{router_id}] (Presiona Ctrl+C para salir)\n")

    routing_table = None

    try:
        while True:
            msg = client.receive()
            if msg is None:
                print(f"[{router_id}] Conexion cerrada por el controlador.")
                break

            msg_type = msg.get("type")

            if msg_type == MSG_ROUTING_TABLE:
                routing_table = msg.get("routing_table", [])
                display_routing_table(router_id, routing_table)
                print(f"[{router_id}] Comandos: show | exit\n")

            else:
                print(f"[{router_id}] Mensaje recibido: {msg}")

            # Mini CLI luego de recibir la tabla
            if routing_table is not None:
                try:
                    cmd = input(f"{router_id}> ").strip().lower()
                    if cmd == "show":
                        display_routing_table(router_id, routing_table)
                    elif cmd == "exit":
                        break
                except EOFError:
                    break

    except KeyboardInterrupt:
        print(f"\n[{router_id}] Detenido por el usuario.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()