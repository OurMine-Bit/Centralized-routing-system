"""
tests/test_dijkstra.py
Tests automatizados para el algoritmo de Dijkstra.
Ejecutar con: pytest tests/test_dijkstra.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.dijkstra import dijkstra, get_next_hop, compute_routing_tables

# Topologia del proyecto:
# R1-R2(4), R1-R3(2), R2-R4(3), R3-R4(5)
GRAPH = {
    "R1": {"R2": 4, "R3": 2},
    "R2": {"R1": 4, "R4": 3},
    "R3": {"R1": 2, "R4": 5},
    "R4": {"R2": 3, "R3": 5},
}


def test_dijkstra_from_r1_costs():
    """Verifica que los costos desde R1 sean correctos."""
    distances, _ = dijkstra(GRAPH, "R1")
    assert distances["R1"] == 0
    assert distances["R2"] == 4
    assert distances["R3"] == 2
    assert distances["R4"] == 7


def test_dijkstra_from_r2_costs():
    """Verifica que los costos desde R2 sean correctos."""
    distances, _ = dijkstra(GRAPH, "R2")
    assert distances["R2"] == 0
    assert distances["R1"] == 4
    assert distances["R4"] == 3
    assert distances["R3"] == 6


def test_dijkstra_from_r3_costs():
    """Verifica que los costos desde R3 sean correctos."""
    distances, _ = dijkstra(GRAPH, "R3")
    assert distances["R3"] == 0
    assert distances["R1"] == 2
    assert distances["R4"] == 5
    assert distances["R2"] == 6


def test_dijkstra_from_r4_costs():
    """Verifica que los costos desde R4 sean correctos."""
    distances, _ = dijkstra(GRAPH, "R4")
    assert distances["R4"] == 0
    assert distances["R2"] == 3
    assert distances["R3"] == 5
    assert distances["R1"] == 7


def test_next_hop_direct_link():
    """Verifica next hop para enlaces directos."""
    _, previous = dijkstra(GRAPH, "R1")
    assert get_next_hop(previous, "R1", "R2") == "R2"
    assert get_next_hop(previous, "R1", "R3") == "R3"


def test_next_hop_indirect_link():
    """Verifica next hop para destinos no directos."""
    _, previous = dijkstra(GRAPH, "R2")
    assert get_next_hop(previous, "R2", "R3") == "R1"


def test_next_hop_same_node():
    """Verifica next hop cuando source == destination."""
    _, previous = dijkstra(GRAPH, "R1")
    assert get_next_hop(previous, "R1", "R1") == "R1"


def test_compute_routing_tables_all_routers():
    """Verifica que se generan tablas para todos los routers."""
    tables = compute_routing_tables(GRAPH)
    assert "R1" in tables
    assert "R2" in tables
    assert "R3" in tables
    assert "R4" in tables


def test_routing_table_has_all_destinations():
    """Verifica que cada tabla tiene todos los destinos."""
    tables = compute_routing_tables(GRAPH)
    for router_id, table in tables.items():
        destinations = [e["destination"] for e in table]
        for other in GRAPH.keys():
            if other != router_id:
                assert other in destinations, f"{router_id} no tiene ruta a {other}"


def test_routing_table_entry_fields():
    """Verifica que cada entrada tiene los campos correctos."""
    tables = compute_routing_tables(GRAPH)
    for router_id, table in tables.items():
        for entry in table:
            assert "destination" in entry
            assert "next_hop" in entry
            assert "cost" in entry
            assert entry["cost"] >= 0  # >= 0 porque incluye ruta a si mismo con costo 0


def test_link_cost_change_updates_routes():
    """Verifica que al cambiar un costo, las rutas se recalculan."""
    import copy
    modified_graph = copy.deepcopy(GRAPH)
    # Cambiar R1-R3 de 2 a 10
    modified_graph["R1"]["R3"] = 10
    modified_graph["R3"]["R1"] = 10

    tables = compute_routing_tables(modified_graph)

    # R1 a R3 ahora cuesta 10 (directo sigue siendo la ruta, pero mas cara)
    r1_to_r3 = next(e for e in tables["R1"] if e["destination"] == "R3")
    assert r1_to_r3["cost"] == 10

    # R1 a R4 ahora deberia ir via R2 (4+3=7) en vez de via R3 (10+5=15)
    r1_to_r4 = next(e for e in tables["R1"] if e["destination"] == "R4")
    assert r1_to_r4["next_hop"] == "R2"
    assert r1_to_r4["cost"] == 7