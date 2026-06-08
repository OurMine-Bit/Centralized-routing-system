"""
router/client.py
Cliente TCP del router.
Maneja la conexion con el controlador, envia mensajes y recibe respuestas.
"""

import socket
import json
import time

from shared.messages import encode, decode


class RouterClient:

    def __init__(self, controller_host, controller_port, timeout=10):
        self.controller_host = controller_host
        self.controller_port = controller_port
        self.timeout = timeout
        self._sock = None
        self._buffer = b""

    # ------------------------------------------------------------------
    # Conexion
    # ------------------------------------------------------------------

    def connect(self, retries=5, delay=2):
        """
        Intenta conectarse al controlador.
        Reintenta 'retries' veces con 'delay' segundos entre intentos.
        """
        for attempt in range(1, retries + 1):
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(self.timeout)
                self._sock.connect((self.controller_host, self.controller_port))
                print(f"[Client] Conectado al controlador {self.controller_host}:{self.controller_port}")
                return True
            except (ConnectionRefusedError, OSError) as e:
                print(f"[Client] Intento {attempt}/{retries} fallido: {e}")
                if attempt < retries:
                    time.sleep(delay)
        print("[Client] No se pudo conectar al controlador.")
        return False

    def set_blocking(self):
        """
        Elimina el timeout del socket.
        El router quedara bloqueado en receive() hasta que llegue
        un mensaje del controlador, sin desconectarse por timeout.
        Llamar despues de completar el registro y el envio de topologia.
        """
        if self._sock:
            self._sock.settimeout(None)

    def disconnect(self):
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        print("[Client] Desconectado del controlador.")

    # ------------------------------------------------------------------
    # Envio y recepcion
    # ------------------------------------------------------------------

    def send(self, msg_dict):
        """Envia un mensaje JSON al controlador."""
        if not self._sock:
            print("[Client] Sin conexion activa.")
            return False
        try:
            self._sock.sendall(encode(msg_dict))
            return True
        except OSError as e:
            print(f"[Client] Error al enviar mensaje: {e}")
            return False

    def receive(self):
        """
        Lee un mensaje completo del controlador (terminado en newline).
        Retorna el diccionario del mensaje o None si la conexion se cierra.
        Con set_blocking() activo, espera indefinidamente sin timeout.
        """
        if not self._sock:
            return None
        try:
            while b"\n" not in self._buffer:
                chunk = self._sock.recv(4096)
                if not chunk:
                    return None
                self._buffer += chunk

            line, self._buffer = self._buffer.split(b"\n", 1)
            return decode(line)

        except socket.timeout:
            print("[Client] Timeout esperando respuesta del controlador.")
            return None
        except (json.JSONDecodeError, OSError) as e:
            print(f"[Client] Error al recibir mensaje: {e}")
            return None

    def send_and_wait(self, msg_dict):
        """
        Envia un mensaje y espera la respuesta (ACK o ERROR).
        Retorna el diccionario de respuesta o None.
        """
        if self.send(msg_dict):
            return self.receive()
        return None