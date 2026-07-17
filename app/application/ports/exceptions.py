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


class CredencialesInvalidasException(Exception):
    """
    Se lanza cuando MS1 responde 401 al reenviarle el Bearer del
    personal que originó la petición (token vencido/inválido). No es lo
    mismo que "MS1 no responde" (ServicioExternoNoDisponibleException),
    pero recibe el mismo tratamiento en CrearAtencionUseCase: la atención
    se marca PENDIENTE_VALIDACION, no se rechaza ni se corta con 401
    (decisión de diseño: puede que el token expire justo entre que el
    celular llamó a MS2 y MS2 llamó a MS1; no vale la pena perder el
    registro de la atención por eso, se revalida después).
    """
    def __init__(self, servicio: str, detalle: str = ""):
        self.servicio = servicio
        super().__init__(f"Credenciales rechazadas por '{servicio}'. {detalle}".strip())
