# Centralized Routing System

A software-based centralized routing system built in Python where router applications communicate with a controller via TCP. The controller collects network topology, computes optimal routes using Dijkstra's algorithm, generates routing tables, and distributes them to all routers.

## Team
- Cristian Alexander Cuastumal
- Pablo Andres Collazos

**Course:** Informatics for Telecommunications
**Program:** Telecommunication Engineering
**Date:** June 2026

---

## Network Topology

```
        R1
       /  \
   (4)/    \(2)
     /      \
    R2       R3
     \      /
   (3)\    /(5)
       \  /
        R4
```

---

## Project Structure

```
Centralized_Routing/
├── controller/
│   ├── main.py           # Entry point, CLI, callback
│   ├── server.py         # TCP server with threading
│   ├── registry.py       # Router registry
│   ├── topology.py       # Network graph
│   ├── dijkstra.py       # Shortest path algorithm
│   ├── logger.py         # Event logging
│   └── dao/
│       ├── db_connection.py  # MySQL connection
│       ├── router_dao.py     # Router persistence
│       ├── topology_dao.py   # Topology persistence
│       └── log_dao.py        # Event persistence
├── router/
│   ├── main.py           # Entry point, CLI
│   ├── client.py         # TCP client
│   └── config/
│       ├── r1.json
│       ├── r2.json
│       ├── r3.json
│       └── r4.json
├── shared/
│   └── messages.py       # JSON message definitions
├── test/
│   ├── test_dijkstra.py
│   ├── test_topology.py
│   └── test_registry.py
└── README.md
```

---

## Requirements

- Python 3.11+
- MySQL (via XAMPP or standalone)
- mysql-connector-python

```
pip install mysql-connector-python pytest
```

### MySQL setup

```
CREATE DATABASE centralized_routing_controller;
USE centralized_routing_controller;

CREATE TABLE routers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    router_id VARCHAR(10),
    ip VARCHAR(20),
    puerto INT,
    estado VARCHAR(10) DEFAULT 'activo'
);

CREATE TABLE enlaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_router VARCHAR(10),
    destination_router VARCHAR(10),
    cost INT
);

CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50),
    descripcion VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## How to Run

Step 1 - Start MySQL (via XAMPP Control Panel)

Step 2 - Start the controller:
```
python controller/main.py
```

Step 3 - Start each router in separate terminals:
```
python router/main.py --config router/config/r1.json
python router/main.py --config router/config/r2.json
python router/main.py --config router/config/r3.json
python router/main.py --config router/config/r4.json
```

---

## Controller CLI Commands

| Command         | Description                                  |
|-----------------|----------------------------------------------|
| routers         | List registered routers                      |
| topology        | Show current network topology                |
| tables          | Recalculate and redistribute routing tables  |
| link R1 R3 10   | Change link cost between R1 and R3 to 10     |
| exit            | Stop the controller                          |

---

## Router CLI Commands

| Command | Description                    |
|---------|--------------------------------|
| show    | Display current routing table  |
| exit    | Disconnect from controller     |

---

## Running Tests

```
pytest tests/ -v
```

Expected output: 29 passed

---

## Message Protocol

All messages use JSON format over TCP, delimited by newline.

| Message           | Direction             | Description                        |
|-------------------|-----------------------|------------------------------------|
| REGISTER_ROUTER   | Router -> Controller  | Register with ID, IP, port         |
| TOPOLOGY_UPDATE   | Router -> Controller  | Send neighbor list and costs       |
| ROUTING_TABLE     | Controller -> Router  | Send computed routing table        |
| LINK_COST_UPDATE  | Controller            | Update link cost                   |
| ACK               | Controller -> Router  | Confirm message received           |
| ERROR             | Controller -> Router  | Report invalid message             |

---

## Database

All events are stored in MySQL database centralized_routing_controller:

- routers  - registered routers with IP, port and status
- enlaces  - network links with costs
- eventos  - full event history with timestamps

---

## GitHub

https://github.com/OurMine-Bit/Centralized-routing-system
