"""
Query: ObtenerDetalleAtencionQuery (handler)

Implementa GET /atenciones/{atencion_id}. Devuelve la proyección
completa, incluyendo medicamentos y evidencia — a diferencia de
AtencionListadoDTO (usado en listados), que es deliberadamente ligero.
"""
from uuid import UUID

from app.application.dtos.atencion_query_dto import AtencionDetalleDTO, MedicamentoOutputDTO
from app.domain.exceptions.domain_exceptions import AtencionNoEncontradaException
from app.domain.repositories.atencion_query_repository import AtencionQueryRepository


class ObtenerDetalleAtencionUseCase:

    def __init__(self, query_repository: AtencionQueryRepository):
        self._query_repository = query_repository

    async def ejecutar(self, atencion_id: UUID) -> AtencionDetalleDTO:
        atencion = await self._query_repository.obtener_detalle(atencion_id)
        if atencion is None:
            raise AtencionNoEncontradaException(str(atencion_id))

        return AtencionDetalleDTO(
            id=str(atencion.id),
            paciente_id=str(atencion.paciente_id),
            personal_id=str(atencion.personal_id),
            motivo_consulta=atencion.diagnostico.motivo_consulta,
            diagnostico_descripcion=atencion.diagnostico.descripcion,
            fecha_atencion=atencion.fecha_atencion,
            estado=atencion.estado.value,
            medicamentos=[
                MedicamentoOutputDTO(nombre=m.nombre, dosis=m.dosis, frecuencia=m.frecuencia, duracion=m.duracion)
                for m in atencion.medicamentos
            ],
            evidencia_url=atencion.evidencia_receta.url_imagen if atencion.evidencia_receta else None,
            creado_en=atencion.creado_en,
            actualizado_en=atencion.actualizado_en,
        )
