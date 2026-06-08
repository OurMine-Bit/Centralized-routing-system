"""
shared/messages.py
Definicion de todos los tipos de mensajes JSON del sistema.
Todos los mensajes tienen el campo 'type' como identificador.
"""

import json


# Tipos de mensajes del protocolo
MSG_REGISTER_ROUTER  = "REGISTER_ROUTER"
MSG_TOPOLOGY_UPDATE  = "TOPOLOGY_UPDATE"
MSG_ROUTING_TABLE    = "ROUTING_TABLE"
MSG_LINK_COST_UPDATE = "LINK_COST_UPDATE"
MSG_ACK              = "ACK"
MSG_ERROR            = "ERROR"


def build_register(router_id, ip, port):
    """
    Router -> Controlador
    Registra un router en el controlador.
    """
    return {
        "type": MSG_REGISTER_ROUTER,
        "router_id": router_id,
        "ip": ip,
        "port": port
    }


def build_topology_update(router_id, neighbors):
    """
    Router -> Controlador
    Envia la lista de vecinos y costos de enlace.
    neighbors: lista de {"neighbor_id": "R2", "cost": 5}
    """
    return {
        "type": MSG_TOPOLOGY_UPDATE,
        "router_id": router_id,
        "neighbors": neighbors
    }


def build_routing_table(router_id, routing_table):
    """
    Controlador -> Router
    Envia la tabla de ruteo calculada.
    routing_table: lista de {"destination": "R3", "next_hop": "R2", "cost": 7}
    """
    return {
        "type": MSG_ROUTING_TABLE,
        "router_id": router_id,
        "routing_table": routing_table
    }


def build_link_cost_update(source, destination, new_cost):
    """
    Admin/Router -> Controlador
    Solicita actualizar el costo de un enlace.
    """
    return {
        "type": MSG_LINK_COST_UPDATE,
        "source": source,
        "destination": destination,
        "new_cost": new_cost
    }


def build_ack(router_id, reference_type):
    """
    Confirmacion de operacion exitosa.
    reference_type: tipo del mensaje que se esta confirmando.
    """
    return {
        "type": MSG_ACK,
        "router_id": router_id,
        "reference": reference_type
    }


def build_error(router_id, message):
    """
    Mensaje de error.
    """
    return {
        "type": MSG_ERROR,
        "router_id": router_id,
        "message": message
    }


def encode(msg_dict):
    """Serializa un mensaje a bytes UTF-8 terminado en newline."""
    return (json.dumps(msg_dict) + "\n").encode("utf-8")


def decode(raw_bytes):
    """
    Deserializa bytes a diccionario.
    Lanza ValueError si el JSON es invalido.
    """
    text = raw_bytes.decode("utf-8").strip()
    return json.loads(text)