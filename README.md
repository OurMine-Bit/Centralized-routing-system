# Centralized Routing System — Sprint 1

## Topologia de red (diamante)

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

Rutas optimas esperadas (para validar en Sprint 2):
- R1 -> R2: directo, costo 4
- R1 -> R3: directo, costo 2
- R1 -> R4: via R2, costo 7  (R1->R2->R4 = 4+3)  [mejor que R1->R3->R4 = 2+5=7, empate]
- R2 -> R3: via R1, costo 6  (R2->R1->R3 = 4+2)
- R2 -> R4: directo, costo 3
- R3 -> R4: via R2, costo 7  (R3->R1->R2->R4 = 2+4+3)  o directo 5... directo R3->R4=5 gana

## Como ejecutar (Sprint 1)

### 1. Iniciar el controlador
```bash
cd centralized-routing
python -m controller.main
```

### 2. Iniciar cada router (en terminales separadas)
```bash
python -m router.main --config router/config/r1.json
python -m router.main --config router/config/r2.json
python -m router.main --config router/config/r3.json
python -m router.main --config router/config/r4.json
```

## Estructura del proyecto
```
centralized-routing/
├── controller/
│   ├── main.py       # Punto de entrada del controlador
│   ├── server.py     # Servidor TCP con threading
│   ├── topology.py   # Grafo de topologia de red
│   └── registry.py   # Registro de routers conectados
├── router/
│   ├── main.py       # Punto de entrada de cada router
│   ├── client.py     # Cliente TCP
│   └── config/
│       ├── r1.json   # Configuracion de R1
│       ├── r2.json   # Configuracion de R2
│       ├── r3.json   # Configuracion de R3
│       └── r4.json   # Configuracion de R4
└── shared/
    └── messages.py   # Definicion de todos los mensajes JSON
```

## Requisitos
- Python 3.8+
- No requiere librerias externas (solo stdlib)
