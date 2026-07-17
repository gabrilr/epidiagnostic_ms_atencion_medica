"""
Adaptador de salida: AtencionQueryRepositoryImpl

Implementación concreta de AtencionQueryRepository. En esta versión
reutiliza la misma tabla y el mismo mapeo a entidad que el lado de
comandos (ver _a_entidad duplicado intencionalmente de
AtencionCommandRepositoryImpl, para mantener cada repositorio
autocontenido y no crear una dependencia cruzada entre el lado de
comandos y el de queries, que en CQRS deben poder evolucionar por
separado).

TODO (optimización futura, no necesaria a esta escala): si los listados
se vuelven lentos por volumen de datos, este repositorio puede
reemplazarse por consultas a una tabla de proyección desnormalizada
(ej. con nombre_paciente y nombre_personal ya resueltos) actualizada
por los propios comandos al escribir, evitando que el lado de lectura
tenga que reconstruir entidades de dominio completas para listados
simples.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.atencion import Atencion
from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.entities.medicamento import Medicamento
from app.domain.repositories.atencion_query_repository import AtencionQueryRepository
from app.domain.value_objects.diagnostico import Diagnostico
from app.domain.value_objects.estado_atencion import EstadoAtencion
from app.domain.value_objects.signos_vitales import SignosVitales
from app.domain.value_objects.ubicacion import Ubicacion
from app.infrastructure.adapters.output.persistence.models.atencion_model import AtencionModel


class AtencionQueryRepositoryImpl(AtencionQueryRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def listar_por_paciente(self, paciente_id: UUID) -> list[Atencion]:
        resultado = await self._session.execute(
            select(AtencionModel)
            .where(AtencionModel.paciente_id == paciente_id)
            .order_by(AtencionModel.fecha_atencion.desc())
        )
        modelos = resultado.scalars().all()
        return [self._a_entidad(m) for m in modelos]

    async def listar_por_personal(self, personal_id: UUID) -> list[Atencion]:
        resultado = await self._session.execute(
            select(AtencionModel)
            .where(AtencionModel.personal_id == personal_id)
            .order_by(AtencionModel.fecha_atencion.desc())
        )
        modelos = resultado.scalars().all()
        return [self._a_entidad(m) for m in modelos]

    async def obtener_detalle(self, atencion_id: UUID) -> Atencion | None:
        resultado = await self._session.execute(
            select(AtencionModel).where(AtencionModel.id == atencion_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    @staticmethod
    def _a_entidad(modelo: AtencionModel) -> Atencion:
        atencion = Atencion(
            id=modelo.id,
            paciente_id=modelo.paciente_id,
            personal_id=modelo.personal_id,
            diagnostico=Diagnostico(
                motivo_consulta=modelo.motivo_consulta,
                descripcion=modelo.diagnostico_descripcion,
                dias_evolucion_sintomas=modelo.dias_evolucion_sintomas,
            ),
            fecha_atencion=modelo.fecha_atencion,
            ubicacion=Ubicacion(comunidad=modelo.comunidad, municipio=modelo.municipio),
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
        if any(
            v is not None
            for v in (
                modelo.presion_sistolica,
                modelo.presion_diastolica,
                modelo.temperatura,
                modelo.peso,
                modelo.estatura,
                modelo.glucosa,
                modelo.frecuencia_cardiaca,
                modelo.saturacion_oxigeno,
            )
        ):
            atencion.signos_vitales = SignosVitales(
                presion_sistolica=modelo.presion_sistolica,
                presion_diastolica=modelo.presion_diastolica,
                temperatura=modelo.temperatura,
                peso=modelo.peso,
                estatura=modelo.estatura,
                glucosa=modelo.glucosa,
                frecuencia_cardiaca=modelo.frecuencia_cardiaca,
                saturacion_oxigeno=modelo.saturacion_oxigeno,
            )
        return atencion
