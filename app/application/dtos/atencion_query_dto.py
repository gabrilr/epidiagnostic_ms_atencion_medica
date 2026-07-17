"""
DTOs de la capa de aplicación, lado de QUERIES (lectura).

Separados de atencion_command_dto.py siguiendo CQRS: el lado de lectura
puede evolucionar de forma independiente (ej. agregar campos
desnormalizados como nombre_paciente) sin afectar los DTOs de escritura.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MedicamentoOutputDTO:
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str


@dataclass
class AtencionListadoDTO:
    """Proyección ligera para listados (GET /atenciones/paciente/{id}, /personal/{id})."""
    id: str
    paciente_id: str
    personal_id: str
    motivo_consulta: str
    fecha_atencion: datetime
    estado: str
    tiene_evidencia: bool


@dataclass
class AtencionDetalleDTO:
    """Proyección completa para el detalle de una atención específica."""
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
    medicamentos: list[MedicamentoOutputDTO]
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
