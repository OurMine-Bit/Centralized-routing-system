"""
controller/topology.py
Almacena y actualiza la topologia de red como un grafo no dirigido.
Estructura interna: { "R1": {"R2": 5, "R3": 10}, "R2": {"R1": 5, ...}, ... }
"""


class TopologyManager:

    def __init__(self):
        # grafo de adyacencia: { nodo: { vecino: costo } }
        self._graph = {}

    def update(self, router_id, neighbors):
        """
        Actualiza los enlaces del router_id con su lista de vecinos.
        neighbors: lista de {"neighbor_id": "R2", "cost": 5}
        El grafo es no dirigido: se actualiza en ambas direcciones.
        """
        # Asegurar que el nodo existe
        if router_id not in self._graph:
            self._graph[router_id] = {}

        for entry in neighbors:
            neighbor_id = entry["neighbor_id"]
            cost = entry["cost"]

            # Enlace directo
            self._graph[router_id][neighbor_id] = cost

            # Enlace inverso (grafo no dirigido)
            if neighbor_id not in self._graph:
                self._graph[neighbor_id] = {}
            self._graph[neighbor_id][router_id] = cost

        print(f"[Topology] Topologia actualizada desde {router_id}: {neighbors}")

    def update_link_cost(self, source, destination, new_cost):
        """Actualiza el costo de un enlace existente en ambas direcciones."""
        if source in self._graph and destination in self._graph[source]:
            self._graph[source][destination] = new_cost
            self._graph[destination][source] = new_cost
            print(f"[Topology] Enlace {source}<->{destination} actualizado a costo {new_cost}")
            return True
        print(f"[Topology] Enlace {source}<->{destination} no existe")
        return False

    def get_graph(self):
        """Retorna una copia del grafo actual."""
        return {node: dict(neighbors) for node, neighbors in self._graph.items()}

    def get_nodes(self):
        return list(self._graph.keys())

    def is_complete(self, expected_routers):
        """
        Retorna True si todos los routers esperados ya enviaron su topologia.
        expected_routers: lista de IDs, ej. ["R1","R2","R3","R4"]
        """
        return all(r in self._graph for r in expected_routers)

    def display(self):
        print("\n--- Topologia actual ---")
        for node, neighbors in self._graph.items():
            links = ", ".join(f"{n}(costo={c})" for n, c in neighbors.items())
            print(f"  {node} -> {links}")
        print("-" * 24)