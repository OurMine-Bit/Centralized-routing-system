"""
controller/dijkstra.py
Implementacion del algoritmo de Dijkstra para calcular rutas mas cortas.
Recibe el grafo de topologia y retorna las tablas de ruteo para cada router.

Sprint 2: FR-04, FR-05
"""

import heapq


def dijkstra(graph, source):
    """
    Calcula los caminos mas cortos desde 'source' hacia todos los nodos del grafo.

    Args:
        graph   : dict de adyacencia { "R1": {"R2": 4, "R3": 2}, ... }
        source  : nodo origen (str), ej. "R1"

    Returns:
        dist    : { nodo: costo_minimo } desde source
        prev    : { nodo: nodo_anterior } para reconstruir el camino
    """
    # Inicializar distancias a infinito para todos los nodos
    dist = {node: float("inf") for node in graph}
    dist[source] = 0
    prev = {node: None for node in graph}

    # Cola de prioridad: (costo_acumulado, nodo)
    heap = [(0, source)]

    visited = set()

    while heap:
        cost, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)

        for v, weight in graph.get(u, {}).items():
            new_cost = cost + weight
            if new_cost < dist.get(v, float("inf")):
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    return dist, prev


def get_next_hop(prev, source, destination):
    """
    Reconstruye el camino y retorna el primer salto (next hop) desde
    source hacia destination.

    Args:
        prev        : dict { nodo: nodo_anterior } generado por dijkstra()
        source      : nodo de origen
        destination : nodo de destino

    Returns:
        El ID del next hop (str) o None si no hay camino.
    """
    if destination == source:
        return source  # destino local

    # Reconstruir camino hacia atras desde destination hasta source
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = prev.get(current)

    path.reverse()

    # El camino debe empezar en source; si no, no hay ruta
    if not path or path[0] != source:
        return None

    # El next hop es el segundo nodo del camino (inmediatamente despues de source)
    if len(path) >= 2:
        return path[1]

    return None


def compute_routing_tables(graph):
    """
    Calcula las tablas de ruteo para TODOS los nodos del grafo.

    Para cada router origen, ejecuta Dijkstra y construye su tabla con entradas:
        { "destination": "Rx", "next_hop": "Ry", "cost": N }

    Args:
        graph : dict de adyacencia { "R1": {"R2": 4, ...}, ... }

    Returns:
        routing_tables : { router_id: [ {destination, next_hop, cost}, ... ] }
    """
    nodes = list(graph.keys())
    routing_tables = {}

    for source in nodes:
        dist, prev = dijkstra(graph, source)
        table = []

        for destination in nodes:
            cost = dist.get(destination, float("inf"))
            if cost == float("inf"):
                # No hay camino al destino; omitir
                continue

            next_hop = get_next_hop(prev, source, destination)
            if next_hop is None and destination != source:
                # No hay ruta valida
                continue

            table.append({
                "destination": destination,
                "next_hop": next_hop if next_hop else source,
                "cost": cost
            })

        # Ordenar por destino para presentacion consistente
        table.sort(key=lambda e: e["destination"])
        routing_tables[source] = table

    return routing_tables