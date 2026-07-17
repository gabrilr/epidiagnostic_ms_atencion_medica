"""
DTOs de la capa de aplicación, lado de COMANDOS (escritura).
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MedicamentoInputDTO:
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str


@dataclass
class CrearAtencionInputDTO:
    paciente_id: str
    personal_id: str
    motivo_consulta: str
    fecha_atencion: datetime
    comunidad: str
    municipio: str
    diagnostico_descripcion: str | None = None
    dias_evolucion_sintomas: int | None = None
    medicamentos: list[MedicamentoInputDTO] = field(default_factory=list)
    evidencia_receta_base64: str | None = None
    device_generated_id: str | None = None
    presion_sistolica: int | None = None
    presion_diastolica: int | None = None
    temperatura: float | None = None
    peso: float | None = None
    estatura: float | None = None
    glucosa: float | None = None
    frecuencia_cardiaca: int | None = None
    saturacion_oxigeno: int | None = None


@dataclass
class AtencionOutputDTO:
    id: str
    paciente_id: str
    personal_id: str
    motivo_consulta: str
    diagnostico_descripcion: str | None
    dias_evolucion_sintomas: int | None
    fecha_atencion: datetime
    comunidad: str
    municipio: str
    estado: str
    medicamentos: list[MedicamentoInputDTO]
    evidencia_url: str | None
    presion_sistolica: int | None
    presion_diastolica: int | None
    temperatura: float | None
    peso: float | None
    estatura: float | None
    glucosa: float | None
    frecuencia_cardiaca: int | None
    saturacion_oxigeno: int | None
    creado_en: datetime
    actualizado_en: datetime


@dataclass
class SincronizarAtencionesInputDTO:
    dispositivo_id: str
    atenciones: list[CrearAtencionInputDTO]


@dataclass
class ResultadoSincronizacionAtencionDTO:
    device_generated_id: str | None
    id_servidor: str
    estado: str  # "creada" | "ya_existente" | "error: ..."


@dataclass
class ModificarAtencionInputDTO:
    """
    Entrada del caso de uso ModificarAtencion. Todos los campos son
    opcionales (PATCH parcial): solo se modifica lo que venga distinto
    de None. `evidencia_receta_base64`, a diferencia del historial
    append-only de MS1, REEMPLAZA la evidencia anterior si ya existía.
    """
    motivo_consulta: str | None = None
    diagnostico_descripcion: str | None = None
    evidencia_receta_base64: str | None = None
