"""
controller/main.py
Punto de entrada del controlador.
Uso: python main.py [--host 0.0.0.0] [--port 5000]

Sprint 1: Acepta registro de routers y almacena topologia.
Sprint 2: Calcula rutas con Dijkstra y distribuye tablas a los routers.
"""

import sys
import os
import argparse

# Permite importar 'shared' desde la raiz del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.registry  import RouterRegistry
from controller.topology  import TopologyManager
from controller.server    import ControllerServer
from controller.dijkstra  import compute_routing_tables


# Referencia global al servidor para poder usarlo dentro del callback
_server = None


def compute_and_distribute(topology):
    """
    Ejecuta Dijkstra sobre la topologia actual y distribuye las tablas
    de ruteo a todos los routers registrados.

    Se llama automaticamente cada vez que la topologia cambia
    (registro de nuevo vecino o actualizacion de costo de enlace).
    """
    global _server

    graph = topology.get_graph()
    if not graph:
        print("[Main] Grafo vacio — no se calculan rutas.")
        return

    print("\n[Main] Calculando rutas con Dijkstra...")
    routing_tables = compute_routing_tables(graph)

    # Mostrar resumen en consola
    for router_id, table in routing_tables.items():
        print(f"\n  Tabla para {router_id}:")
        print(f"  {'Destino':<12} {'Next Hop':<12} {'Costo':<6}")
        print(f"  {'-'*30}")
        for entry in table:
            print(f"  {entry['destination']:<12} {entry['next_hop']:<12} {entry['cost']:<6}")

    # Distribuir a todos los routers activos
    if _server:
        _server.send_to_all_routers(routing_tables)
    else:
        print("[Main] Servidor no disponible — tablas no distribuidas.")


EXPECTED_ROUTERS = ["R1", "R2", "R3", "R4"]

def on_topology_ready(topology):
    """
    Callback que se ejecuta cada vez que se actualiza la topologia.
    Solo dispara Dijkstra cuando los 4 routers estan registrados
    Y han enviado su informacion de topologia.
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
    global _server

    parser = argparse.ArgumentParser(description="Controlador de ruteo centralizado")
    parser.add_argument("--host", default="0.0.0.0", help="IP de escucha (default: 0.0.0.0)")
    parser.add_argument("--port", default=5000, type=int, help="Puerto TCP (default: 5000)")
    args = parser.parse_args()

    print("=" * 45)
    print("  Centralized Routing System — Controlador")
    print("=" * 45)

    registry = RouterRegistry()
    topology = TopologyManager()

    _server = ControllerServer(
        host=args.host,
        port=args.port,
        registry=registry,
        topology=topology,
        on_topology_ready=on_topology_ready
    )

    _server.start()

    print("\nControlador en ejecucion. Comandos disponibles:")
    print("  routers   -> listar routers registrados")
    print("  topology  -> mostrar topologia actual")
    print("  tables    -> calcular y distribuir tablas de ruteo ahora")
    print("  exit      -> detener el controlador\n")

    try:
        while True:
            cmd = input("> ").strip().lower()

            if cmd == "routers":
                registry.display()

            elif cmd == "topology":
                topology.display()

            elif cmd == "tables":
                # Comando manual: forzar calculo y distribucion de tablas
                print("[Main] Calculo manual de tablas solicitado...")
                compute_and_distribute(topology)

            elif cmd == "exit":
                break

            elif cmd == "":
                pass

            else:
                print(f"Comando no reconocido: '{cmd}'")

    except KeyboardInterrupt:
        pass
    finally:
        _server.stop()
        print("Controlador detenido.")


if __name__ == "__main__":
    main()