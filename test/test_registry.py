"""
tests/test_registry.py
Tests automatizados para el modulo de registro de routers.
Ejecutar con: pytest tests/test_registry.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller.registry import RouterRegistry


def test_register_stores_router():
    """Verifica que register() almacena el router correctamente."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    info = reg.get("R1")
    assert info is not None
    assert info["ip"] == "127.0.0.1"
    assert info["port"] == 5001
    assert info["status"] == "active"


def test_register_multiple_routers():
    """Verifica que se pueden registrar multiples routers."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.register("R2", "127.0.0.1", 5002, None)
    reg.register("R3", "127.0.0.1", 5003, None)
    reg.register("R4", "127.0.0.1", 5004, None)
    assert reg.count() == 4


def test_all_ids_returns_active_only():
    """Verifica que all_ids() retorna solo routers activos."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.register("R2", "127.0.0.1", 5002, None)
    reg.remove("R1")
    ids = reg.all_ids()
    assert "R1" not in ids
    assert "R2" in ids


def test_remove_sets_inactive():
    """Verifica que remove() marca el router como inactivo."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.remove("R1")
    info = reg.get("R1")
    assert info["status"] == "inactive"


def test_get_socket_returns_none_when_inactive():
    """Verifica que get_socket() retorna None para routers inactivos."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.remove("R1")
    assert reg.get_socket("R1") is None


def test_get_nonexistent_router():
    """Verifica que get() retorna None para routers no registrados."""
    reg = RouterRegistry()
    assert reg.get("R99") is None


def test_register_updates_existing():
    """Verifica que registrar un router existente actualiza su info."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.remove("R1")
    reg.register("R1", "127.0.0.1", 5001, None)
    info = reg.get("R1")
    assert info["status"] == "active"


def test_count_includes_all():
    """Verifica que count() incluye activos e inactivos."""
    reg = RouterRegistry()
    reg.register("R1", "127.0.0.1", 5001, None)
    reg.register("R2", "127.0.0.1", 5002, None)
    reg.remove("R1")
    assert reg.count() == 2