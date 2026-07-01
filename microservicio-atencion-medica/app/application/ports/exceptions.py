"""
Excepción de aplicación: ServicioExternoNoDisponibleException

Representa específicamente el caso de "no se pudo contactar al
servicio externo" (timeout, conexión rechazada, 5xx), DISTINTO del caso
"se contactó y respondió que no existe" (404, que se modela devolviendo
None en los puertos PacienteClientPort/PersonalClientPort).

Esta distinción es la base de la tolerancia a fallos: cuando se lanza
esta excepción, la atención se marca PENDIENTE_VALIDACION (se acepta
igual), no RECHAZADA.
"""


class ServicioExternoNoDisponibleException(Exception):
    def __init__(self, servicio: str, detalle: str = ""):
        self.servicio = servicio
        super().__init__(f"El servicio externo '{servicio}' no está disponible. {detalle}".strip())
