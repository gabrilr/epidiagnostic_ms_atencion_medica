"""
Comando: ModificarAtencionCommand (handler)

Implementa el endpoint PATCH /atenciones/{id}. Casos de uso típicos:
corregir un diagnóstico, o agregar/reemplazar evidencia de receta
después de creada la atención (ej. la enfermera subió la foto más tarde
porque no tenía la receta físicamente en el momento de registrar la
atención).
"""
from uuid import UUID

from app.application.dtos.atencion_command_dto import AtencionOutputDTO, ModificarAtencionInputDTO
from app.application.ports.evidencia_storage_port import EvidenciaStoragePort
from app.domain.entities.atencion import Atencion
from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.exceptions.domain_exceptions import AtencionNoEncontradaException
from app.domain.repositories.atencion_command_repository import AtencionCommandRepository
from app.domain.value_objects.diagnostico import Diagnostico


class ModificarAtencionUseCase:

    def __init__(
        self,
        atencion_repository: AtencionCommandRepository,
        evidencia_storage: EvidenciaStoragePort,
    ):
        self._atencion_repository = atencion_repository
        self._evidencia_storage = evidencia_storage

    async def ejecutar(self, atencion_id: UUID, datos: ModificarAtencionInputDTO) -> AtencionOutputDTO:
        atencion = await self._atencion_repository.buscar_por_id(atencion_id)
        if atencion is None:
            raise AtencionNoEncontradaException(str(atencion_id))

        if datos.motivo_consulta is not None or datos.diagnostico_descripcion is not None:
            # Diagnostico es un Value Object inmutable: se reconstruye
            # completo, conservando el valor actual del campo que no
            # vino en el PATCH.
            atencion.diagnostico = Diagnostico(
                motivo_consulta=(
                    datos.motivo_consulta
                    if datos.motivo_consulta is not None
                    else atencion.diagnostico.motivo_consulta
                ),
                descripcion=(
                    datos.diagnostico_descripcion
                    if datos.diagnostico_descripcion is not None
                    else atencion.diagnostico.descripcion
                ),
            )

        if datos.evidencia_receta_base64:
            subida = await self._evidencia_storage.subir_evidencia(
                datos.evidencia_receta_base64, str(atencion.id)
            )
            atencion.adjuntar_evidencia(
                EvidenciaReceta(url_imagen=subida.url_imagen, public_id_cloudinary=subida.public_id)
            )

        atencion_actualizada = await self._atencion_repository.actualizar(atencion)
        return self._a_dto(atencion_actualizada)

    @staticmethod
    def _a_dto(atencion: Atencion) -> AtencionOutputDTO:
        from app.application.dtos.atencion_command_dto import MedicamentoInputDTO

        return AtencionOutputDTO(
            id=str(atencion.id),
            paciente_id=str(atencion.paciente_id),
            personal_id=str(atencion.personal_id),
            motivo_consulta=atencion.diagnostico.motivo_consulta,
            diagnostico_descripcion=atencion.diagnostico.descripcion,
            fecha_atencion=atencion.fecha_atencion,
            estado=atencion.estado.value,
            medicamentos=[
                MedicamentoInputDTO(nombre=m.nombre, dosis=m.dosis, frecuencia=m.frecuencia, duracion=m.duracion)
                for m in atencion.medicamentos
            ],
            evidencia_url=atencion.evidencia_receta.url_imagen if atencion.evidencia_receta else None,
            creado_en=atencion.creado_en,
            actualizado_en=atencion.actualizado_en,
        )
