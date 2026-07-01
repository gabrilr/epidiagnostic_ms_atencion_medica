"""
Excepciones de dominio del Microservicio de Atención Médica.
"""


class DomainException(Exception):
    pass


class AtencionNoEncontradaException(DomainException):
    def __init__(self, identificador: str):
        self.identificador = identificador
        super().__init__(f"No se encontró ninguna atención con identificador {identificador}.")


class PacienteInvalidoException(DomainException):
    """
    Se lanza cuando el Microservicio 1 confirma explícitamente que el
    paciente_id referenciado NO existe (no es lo mismo que un timeout:
    eso se maneja con EstadoAtencion.PENDIENTE_VALIDACION, no con esta
    excepción).
    """
    def __init__(self, paciente_id: str):
        self.paciente_id = paciente_id
        super().__init__(f"El paciente {paciente_id} no existe en el sistema.")


class PersonalInvalidoException(DomainException):
    """
    Se lanza cuando el Microservicio 1 confirma explícitamente que el
    personal_id referenciado no existe o está inactivo.
    """
    def __init__(self, personal_id: str):
        self.personal_id = personal_id
        super().__init__(f"El personal médico {personal_id} no existe o está inactivo.")


class EvidenciaInvalidaException(DomainException):
    """Se lanza cuando la imagen de evidencia no cumple validaciones básicas (tamaño, formato)."""
    def __init__(self, detalle: str):
        super().__init__(f"Evidencia de receta inválida: {detalle}")
