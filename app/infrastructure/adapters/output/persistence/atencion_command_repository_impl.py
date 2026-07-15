"""
Adaptador de salida: AtencionCommandRepositoryImpl

Implementación concreta de AtencionCommandRepository usando SQLAlchemy
async + MySQL. Traduce entre Atencion (entidad de dominio) y
AtencionModel (modelo ORM), igual patrón que PacienteRepositoryImpl en
MS1.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.atencion import Atencion
from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.entities.medicamento import Medicamento
from app.domain.repositories.atencion_command_repository import AtencionCommandRepository
from app.domain.value_objects.diagnostico import Diagnostico
from app.domain.value_objects.estado_atencion import EstadoAtencion
from app.infrastructure.adapters.output.persistence.models.atencion_model import AtencionModel
from app.infrastructure.adapters.output.persistence.models.evidencia_receta_model import (
    EvidenciaRecetaModel,
)
from app.infrastructure.adapters.output.persistence.models.medicamento_model import MedicamentoModel


class AtencionCommandRepositoryImpl(AtencionCommandRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, atencion: Atencion) -> Atencion:
        modelo = AtencionModel(
            id=atencion.id,
            paciente_id=atencion.paciente_id,
            personal_id=atencion.personal_id,
            motivo_consulta=atencion.diagnostico.motivo_consulta,
            diagnostico_descripcion=atencion.diagnostico.descripcion,
            fecha_atencion=atencion.fecha_atencion,
            estado=atencion.estado.value,
            device_generated_id=atencion.device_generated_id,
            creado_en=atencion.creado_en,
            actualizado_en=atencion.actualizado_en,
            medicamentos=[
                MedicamentoModel(
                    id=m.id, nombre=m.nombre, dosis=m.dosis, frecuencia=m.frecuencia, duracion=m.duracion
                )
                for m in atencion.medicamentos
            ],
        )
        if atencion.evidencia_receta:
            modelo.evidencia = EvidenciaRecetaModel(
                id=atencion.evidencia_receta.id,
                url_imagen=atencion.evidencia_receta.url_imagen,
                public_id_cloudinary=atencion.evidencia_receta.public_id_cloudinary,
                fecha_captura=atencion.evidencia_receta.fecha_captura,
            )

        self._session.add(modelo)
        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    async def buscar_por_id(self, atencion_id: UUID) -> Atencion | None:
        resultado = await self._session.execute(
            select(AtencionModel).where(AtencionModel.id == atencion_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def buscar_por_device_generated_id(self, device_generated_id: str) -> Atencion | None:
        resultado = await self._session.execute(
            select(AtencionModel).where(AtencionModel.device_generated_id == device_generated_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def actualizar(self, atencion: Atencion) -> Atencion:
        resultado = await self._session.execute(
            select(AtencionModel).where(AtencionModel.id == atencion.id)
        )
        modelo = resultado.scalar_one_or_none()
        if modelo is None:
            raise ValueError(f"No se puede actualizar: atención {atencion.id} no existe en persistencia.")

        modelo.motivo_consulta = atencion.diagnostico.motivo_consulta
        modelo.diagnostico_descripcion = atencion.diagnostico.descripcion
        modelo.estado = atencion.estado.value

        if atencion.evidencia_receta:
            if modelo.evidencia is None:
                modelo.evidencia = EvidenciaRecetaModel(
                    id=atencion.evidencia_receta.id,
                    url_imagen=atencion.evidencia_receta.url_imagen,
                    public_id_cloudinary=atencion.evidencia_receta.public_id_cloudinary,
                    fecha_captura=atencion.evidencia_receta.fecha_captura,
                )
            else:
                # Reemplazo de evidencia (no append-only, a diferencia del
                # historial médico de MS1, ver Atencion.adjuntar_evidencia).
                modelo.evidencia.url_imagen = atencion.evidencia_receta.url_imagen
                modelo.evidencia.public_id_cloudinary = atencion.evidencia_receta.public_id_cloudinary

        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    @staticmethod
    def _a_entidad(modelo: AtencionModel) -> Atencion:
        atencion = Atencion(
            id=modelo.id,
            paciente_id=modelo.paciente_id,
            personal_id=modelo.personal_id,
            diagnostico=Diagnostico(
                motivo_consulta=modelo.motivo_consulta,
                descripcion=modelo.diagnostico_descripcion,
            ),
            fecha_atencion=modelo.fecha_atencion,
            device_generated_id=modelo.device_generated_id,
            estado=EstadoAtencion(modelo.estado),
            medicamentos=[
                Medicamento(id=m.id, nombre=m.nombre, dosis=m.dosis, frecuencia=m.frecuencia, duracion=m.duracion)
                for m in modelo.medicamentos
            ],
            creado_en=modelo.creado_en,
            actualizado_en=modelo.actualizado_en,
        )
        if modelo.evidencia:
            atencion.evidencia_receta = EvidenciaReceta(
                id=modelo.evidencia.id,
                url_imagen=modelo.evidencia.url_imagen,
                public_id_cloudinary=modelo.evidencia.public_id_cloudinary,
                fecha_captura=modelo.evidencia.fecha_captura,
            )
        return atencion
