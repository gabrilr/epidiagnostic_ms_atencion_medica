"""
Schemas Pydantic: contrato HTTP del API de atención médica.

Igual que en MS1, separados de los DTOs de aplicación a propósito: el
contrato HTTP puede evolucionar (versionado de API) sin tocar lógica de
negocio.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class MedicamentoRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    dosis: str = Field(..., min_length=1, max_length=100)
    frecuencia: str = Field(..., min_length=1, max_length=100)
    duracion: str = Field(..., min_length=1, max_length=100)


class MedicamentoResponse(BaseModel):
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str


class CrearAtencionRequest(BaseModel):
    paciente_id: str = Field(..., description="ID del paciente, obtenido del catálogo de MS1.")
    personal_id: str = Field(..., description="ID del personal médico, obtenido del catálogo de MS1.")
    motivo_consulta: str = Field(..., min_length=1, max_length=500)
    fecha_atencion: datetime
    diagnostico_descripcion: str | None = Field(default=None, max_length=1000)
    medicamentos: list[MedicamentoRequest] = Field(default_factory=list)
    evidencia_receta_base64: str | None = Field(
        default=None,
        description="Imagen de la receta en base64 (data URI o string puro), subida a Cloudinary al crear la atención.",
    )
    device_generated_id: str | None = Field(
        default=None,
        description="UUID generado por el celular en modo offline-first, usado para idempotencia del batch.",
    )


class AtencionResponse(BaseModel):
    id: str
    paciente_id: str
    personal_id: str
    motivo_consulta: str
    diagnostico_descripcion: str | None
    fecha_atencion: datetime
    estado: str = Field(
        description="registrada | validada | pendiente_validacion | rechazada. "
        "Ver EstadoAtencion en el dominio."
    )
    medicamentos: list[MedicamentoResponse]
    evidencia_url: str | None
    creado_en: datetime
    actualizado_en: datetime


class AtencionListadoResponse(BaseModel):
    """Proyección ligera para listados, sin medicamentos ni URL completa de evidencia."""
    id: str
    paciente_id: str
    personal_id: str
    motivo_consulta: str
    fecha_atencion: datetime
    estado: str
    tiene_evidencia: bool


class SincronizarAtencionesRequest(BaseModel):
    dispositivo_id: str
    atenciones: list[CrearAtencionRequest]


class ResultadoSincronizacionAtencionResponse(BaseModel):
    device_generated_id: str | None
    id_servidor: str
    estado: str


class SincronizarAtencionesResponse(BaseModel):
    resultados: list[ResultadoSincronizacionAtencionResponse]


class ModificarAtencionRequest(BaseModel):
    """Todos los campos son opcionales: PATCH parcial, solo se modifica lo que venga."""
    motivo_consulta: str | None = Field(default=None, min_length=1, max_length=500)
    diagnostico_descripcion: str | None = Field(default=None, max_length=1000)
    evidencia_receta_base64: str | None = Field(
        default=None,
        description="Reemplaza la evidencia existente (si ya había una) o la agrega si no había.",
    )
