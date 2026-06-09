"""
tests/test_topology.py
Tests automatizados para el modulo de topologia.
Ejecutar con: pytest tests/test_topology.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.topology import TopologyManager


def test_topology_update_stores_nodes():
    """Verifica que update() almacena los nodos correctamente."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}])
    graph = topo.get_graph()
    assert "R1" in graph
    assert "R2" in graph


def test_topology_update_stores_costs():
    """Verifica que los costos de enlace se almacenan correctamente."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}, {"neighbor_id": "R3", "cost": 2}])
    graph = topo.get_graph()
    assert graph["R1"]["R2"] == 4
    assert graph["R1"]["R3"] == 2


def test_topology_is_bidirectional():
    """Verifica que el grafo es no dirigido (enlaces en ambas direcciones)."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}])
    graph = topo.get_graph()
    assert graph["R1"]["R2"] == 4
    assert graph["R2"]["R1"] == 4


def test_topology_is_complete_false():
    """Verifica que is_complete() retorna False si faltan routers."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}])
    assert not topo.is_complete(["R1", "R2", "R3", "R4"])


def test_topology_is_complete_true():
    """Verifica que is_complete() retorna True cuando estan todos."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}, {"neighbor_id": "R3", "cost": 2}])
    topo.update("R2", [{"neighbor_id": "R1", "cost": 4}, {"neighbor_id": "R4", "cost": 3}])
    topo.update("R3", [{"neighbor_id": "R1", "cost": 2}, {"neighbor_id": "R4", "cost": 5}])
    topo.update("R4", [{"neighbor_id": "R2", "cost": 3}, {"neighbor_id": "R3", "cost": 5}])
    assert topo.is_complete(["R1", "R2", "R3", "R4"])


def test_topology_update_link_cost():
    """Verifica que update_link_cost() actualiza el costo correctamente."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R3", "cost": 2}])
    topo.update_link_cost("R1", "R3", 10)
    graph = topo.get_graph()
    assert graph["R1"]["R3"] == 10
    assert graph["R3"]["R1"] == 10


def test_topology_update_link_cost_bidirectional():
    """Verifica que update_link_cost() actualiza ambas direcciones."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}])
    topo.update_link_cost("R1", "R2", 9)
    graph = topo.get_graph()
    assert graph["R1"]["R2"] == 9
    assert graph["R2"]["R1"] == 9


def test_topology_update_nonexistent_link():
    """Verifica que update_link_cost() retorna False para enlaces inexistentes."""
    topo = TopologyManager()
    result = topo.update_link_cost("R1", "R4", 5)
    assert result == False


def test_topology_get_nodes():
    """Verifica que get_nodes() retorna los nodos correctos."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}])
    nodes = topo.get_nodes()
    assert "R1" in nodes
    assert "R2" in nodes


def test_topology_full_graph():
    """Verifica el grafo completo con los 4 routers del proyecto."""
    topo = TopologyManager()
    topo.update("R1", [{"neighbor_id": "R2", "cost": 4}, {"neighbor_id": "R3", "cost": 2}])
    topo.update("R2", [{"neighbor_id": "R1", "cost": 4}, {"neighbor_id": "R4", "cost": 3}])
    topo.update("R3", [{"neighbor_id": "R1", "cost": 2}, {"neighbor_id": "R4", "cost": 5}])
    topo.update("R4", [{"neighbor_id": "R2", "cost": 3}, {"neighbor_id": "R3", "cost": 5}])
    graph = topo.get_graph()
    assert graph["R1"]["R2"] == 4
    assert graph["R1"]["R3"] == 2
    assert graph["R2"]["R4"] == 3
    assert graph["R3"]["R4"] == 5