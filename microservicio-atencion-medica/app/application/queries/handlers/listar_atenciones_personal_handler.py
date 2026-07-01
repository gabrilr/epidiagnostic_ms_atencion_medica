"""
Query: ListarAtencionesPorPersonalQuery (handler)

TODO: Implementar el endpoint GET /atenciones/personal/{personal_id}

Sigue EXACTAMENTE el mismo patrón que
listar_atenciones_paciente_handler.py, solo cambiando el método del
repositorio:

class ListarAtencionesPorPersonalUseCase:
    def __init__(self, query_repository: AtencionQueryRepository):
        self._query_repository = query_repository

    async def ejecutar(self, personal_id: UUID) -> list[AtencionListadoDTO]:
        atenciones = await self._query_repository.listar_por_personal(personal_id)
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

Caso de uso típico: un médico/enfermera revisando cuántas atenciones ha
registrado, útil para reportes o auditoría de actividad por personal.
"""
