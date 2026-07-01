"""
Query: ListarAtencionesPorPacienteQuery (handler)

Implementa GET /atenciones/paciente/{paciente_id}. Es el historial
clínico completo de un paciente, sin importar qué personal médico lo
atendió en cada ocasión — coherente con la decisión de diseño de
"atenciones independientes, sin conflicto".
"""
from uuid import UUID

from app.application.dtos.atencion_query_dto import AtencionListadoDTO
from app.domain.repositories.atencion_query_repository import AtencionQueryRepository


class ListarAtencionesPorPacienteUseCase:

    def __init__(self, query_repository: AtencionQueryRepository):
        self._query_repository = query_repository

    async def ejecutar(self, paciente_id: UUID) -> list[AtencionListadoDTO]:
        atenciones = await self._query_repository.listar_por_paciente(paciente_id)
        return [
            AtencionListadoDTO(
                id=str(a.id),
                paciente_id=str(a.paciente_id),
                personal_id=str(a.personal_id),
                motivo_consulta=a.diagnostico.motivo_consulta,
                fecha_atencion=a.fecha_atencion,
                estado=a.estado.value,
                tiene_evidencia=a.evidencia_receta is not None,
            )
            for a in atenciones
        ]
