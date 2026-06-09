"""
controller/main.py
Punto de entrada del controlador.
Uso: python controller/main.py [--host 0.0.0.0] [--port 5000]

Sprint 1: Acepta registro de routers y almacena topologia.
Sprint 2: Calcula rutas con Dijkstra y distribuye tablas a los routers.
Sprint 3: Comando 'link' para simular cambios de costo, logging de eventos.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.registry import RouterRegistry
from controller.topology import TopologyManager
from controller.server   import ControllerServer
from controller.dijkstra import compute_routing_tables
from controller.logger   import SystemLogger

_server = None
_logger = None

EXPECTED_ROUTERS = ["R1", "R2", "R3", "R4"]


def compute_and_distribute(topology):
    """
    Ejecuta Dijkstra y distribuye las tablas a todos los routers activos.
    """
    global _server, _logger

    graph = topology.get_graph()
    if not graph:
        print("[Main] Grafo vacio — no se calculan rutas.")
        return

    print("\n[Main] Calculando rutas con Dijkstra...")
    _logger.log_route_computation(len(graph))
    routing_tables = compute_routing_tables(graph)

    # Mostrar resumen en consola
    for router_id, table in routing_tables.items():
        print(f"\n  Tabla para {router_id}:")
        print(f"  {'Destino':<12} {'Next Hop':<12} {'Costo':<6}")
        print(f"  {'-'*30}")
        for entry in table:
            print(f"  {entry['destination']:<12} {entry['next_hop']:<12} {entry['cost']:<6}")

    # Distribuir
    if _server:
        _server.send_to_all_routers(routing_tables)
    else:
        print("[Main] Servidor no disponible.")


def on_topology_ready(topology):
    """
    Callback ejecutado cada vez que se actualiza la topologia.
    Dispara Dijkstra solo cuando los 4 routers estan registrados y conectados.
    """
    global _server

    registered = _server.registry.all_ids() if _server else []
    missing_reg = [r for r in EXPECTED_ROUTERS if r not in registered]
    if missing_reg:
        print(f"[Main] Esperando registro de: {missing_reg}")
        return

    if not topology.is_complete(EXPECTED_ROUTERS):
        missing_topo = [r for r in EXPECTED_ROUTERS if r not in topology.get_nodes()]
        print(f"[Main] Esperando topologia de: {missing_topo}")
        return

    print(f"\n[Main] Topologia completa con {EXPECTED_ROUTERS}. Calculando rutas...")
    compute_and_distribute(topology)


def main():
    global _server, _logger

    parser = argparse.ArgumentParser(description="Controlador de ruteo centralizado")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    _logger = SystemLogger("routing_system.log")

    print("=" * 45)
    print("  Centralized Routing System — Controlador")
    print("=" * 45)

    registry = RouterRegistry(logger=_logger)
    topology = TopologyManager(logger=_logger)

    _server = ControllerServer(
        host=args.host,
        port=args.port,
        registry=registry,
        topology=topology,
        on_topology_ready=on_topology_ready,
        logger=_logger
    )
    _server.start()

    print("\nControlador en ejecucion. Comandos disponibles:")
    print("  routers        -> listar routers registrados")
    print("  topology       -> mostrar topologia actual")
    print("  tables         -> recalcular y redistribuir tablas ahora")
    print("  link R1 R3 10  -> cambiar costo del enlace R1-R3 a 10")
    print("  exit           -> detener el controlador\n")

    try:
        while True:
            cmd = input("> ").strip()

            if cmd == "":
                pass

            elif cmd == "routers":
                registry.display()

            elif cmd == "topology":
                topology.display()

            elif cmd == "tables":
                print("[Main] Calculo manual de tablas solicitado...")
                compute_and_distribute(topology)

            elif cmd.lower().startswith("link "):
                # Formato: link R1 R3 10
                parts = cmd.split()
                if len(parts) != 4:
                    print("Uso correcto: link <origen> <destino> <nuevo_costo>")
                    print("Ejemplo:      link R1 R3 10")
                else:
                    try:
                        source   = parts[1].upper()
                        dest     = parts[2].upper()
                        new_cost = int(parts[3])

                        # Obtener costo actual para el log
                        graph = topology.get_graph()
                        old_cost = graph.get(source, {}).get(dest, "?")

                        updated = topology.update_link_cost(source, dest, new_cost)
                        if updated:
                            _logger.log_link_update(source, dest, old_cost, new_cost)
                            print(f"\n[Main] Enlace {source}<->{dest} actualizado: {old_cost} -> {new_cost}")
                            print("[Main] Recalculando rutas...")
                            compute_and_distribute(topology)
                        else:
                            print(f"[Main] Enlace {source}-{dest} no existe en la topologia.")
                            print(f"       Enlaces disponibles: usa 'topology' para verlos.")
                    except ValueError:
                        print("El costo debe ser un numero entero. Ejemplo: link R1 R3 10")

            elif cmd == "exit":
                break

            else:
                print(f"Comando no reconocido: '{cmd}'. Escribe 'exit' para salir.")

    except KeyboardInterrupt:
        pass
    finally:
        _server.stop()
        print("Controlador detenido.")


if __name__ == "__main__":
    main()