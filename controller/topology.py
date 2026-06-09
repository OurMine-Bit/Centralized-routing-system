"""
controller/topology.py
Almacena y actualiza la topologia de red como un grafo no dirigido.
Sprint 3: integra logging de actualizaciones de topologia y enlaces.
"""
from controller.dao.topology_dao import TopologyDAO
_topology_dao = TopologyDAO()

class TopologyManager:

    def __init__(self, logger=None):
        self._graph = {}
        self._logger = logger

    def update(self, router_id, neighbors):
        if router_id not in self._graph:
            self._graph[router_id] = {}

        for entry in neighbors:
            neighbor_id = entry["neighbor_id"]
            cost = entry["cost"]
            self._graph[router_id][neighbor_id] = cost
            if neighbor_id not in self._graph:
                self._graph[neighbor_id] = {}
            self._graph[neighbor_id][router_id] = cost

        print(f"[Topology] Topologia actualizada desde {router_id}: {neighbors}")
        _topology_dao.save_topology(self._graph)
        if self._logger:
            self._logger.log_topology_update(router_id, neighbors)

    def update_link_cost(self, source, destination, new_cost):
        if source in self._graph and destination in self._graph.get(source, {}):
            self._graph[source][destination] = new_cost
            self._graph[destination][source] = new_cost
            print(f"[Topology] Enlace {source}<->{destination} actualizado a costo {new_cost}")
            return True
        print(f"[Topology] Enlace {source}<->{destination} no existe")
        return False

    def get_graph(self):
        return {node: dict(neighbors) for node, neighbors in self._graph.items()}

    def get_nodes(self):
        return list(self._graph.keys())

    def is_complete(self, expected_routers):
        return all(r in self._graph for r in expected_routers)

    def display(self):
        print("\n--- Topologia actual ---")
        for node, neighbors in self._graph.items():
            links = ", ".join(f"{n}(costo={c})" for n, c in neighbors.items())
            print(f"  {node} -> {links}")
        print("-" * 24)