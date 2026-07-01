"""
Comando: CrearAtencionCommand (handler)

Implementa la regla de negocio central del MS2, definida en el diseño:

    1. Intenta validar paciente_id y personal_id contra MS1.
    2. Si responde y ambos existen -> atención se crea como VALIDADA.
    3. Si MS1 no responde (timeout) -> atención se crea igual, como
       PENDIENTE_VALIDACION. NO se bloquea el registro.
    4. Si MS1 responde pero alguno NO existe -> se RECHAZA la atención
       (error real, se le informa al cliente).

Como confirmaste en el diseño ("atenciones independientes, sin
conflicto"), este comando NO necesita ningún tipo de lock ni
coordinación con otras atenciones del mismo paciente — cada atención es
completamente independiente.

Si llega evidencia de receta (base64), se sube a Cloudinary a través del
puerto EvidenciaStoragePort ANTES de persistir la atención, para que la
URL quede guardada desde la creación.
"""
import uuid
from datetime import datetime

from app.application.dtos.atencion_command_dto import AtencionOutputDTO, CrearAtencionInputDTO
from app.application.ports.evidencia_storage_port import EvidenciaStoragePort
from app.application.ports.exceptions import ServicioExternoNoDisponibleException
from app.application.ports.paciente_client_port import PacienteClientPort
from app.application.ports.personal_client_port import PersonalClientPort
from app.domain.entities.atencion import Atencion
from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.entities.medicamento import Medicamento
from app.domain.repositories.atencion_command_repository import AtencionCommandRepository
from app.domain.value_objects.diagnostico import Diagnostico


class CrearAtencionUseCase:

    def __init__(
        self,
        atencion_repository: AtencionCommandRepository,
        paciente_client: PacienteClientPort,
        personal_client: PersonalClientPort,
        evidencia_storage: EvidenciaStoragePort,
    ):
        self._atencion_repository = atencion_repository
        self._paciente_client = paciente_client
        self._personal_client = personal_client
        self._evidencia_storage = evidencia_storage

    async def ejecutar(self, datos: CrearAtencionInputDTO) -> AtencionOutputDTO:
        # Idempotencia: si esta atención ya fue procesada antes (mismo
        # device_generated_id, típico de un reintento de batch desde el
        # celular), se devuelve la existente sin crear una nueva.
        if datos.device_generated_id:
            existente = await self._atencion_repository.buscar_por_device_generated_id(
                datos.device_generated_id
            )
            if existente is not None:
                return self._a_dto(existente)

        atencion = Atencion(
            paciente_id=uuid.UUID(datos.paciente_id),
            personal_id=uuid.UUID(datos.personal_id),
            diagnostico=Diagnostico(
                motivo_consulta=datos.motivo_consulta,
                descripcion=datos.diagnostico_descripcion,
            ),
            fecha_atencion=datos.fecha_atencion,
            device_generated_id=datos.device_generated_id,
        )

        for med in datos.medicamentos:
            atencion.agregar_medicamento(
                Medicamento(nombre=med.nombre, dosis=med.dosis, frecuencia=med.frecuencia, duracion=med.duracion)
            )

        await self._validar_contra_ms1(atencion)

        if datos.evidencia_receta_base64:
            subida = await self._evidencia_storage.subir_evidencia(
                datos.evidencia_receta_base64, str(atencion.id)
            )
            atencion.adjuntar_evidencia(
                EvidenciaReceta(url_imagen=subida.url_imagen, public_id_cloudinary=subida.public_id)
            )

        atencion_guardada = await self._atencion_repository.guardar(atencion)
        return self._a_dto(atencion_guardada)

    async def _validar_contra_ms1(self, atencion: Atencion) -> None:
        """
        Aplica la máquina de estados de tolerancia a fallos. Modifica
        `atencion` in-place (marca su estado) antes de persistir.
        """
        try:
            paciente = await self._paciente_client.obtener_paciente(atencion.paciente_id)
            personal = await self._personal_client.obtener_personal(atencion.personal_id)
        except ServicioExternoNoDisponibleException:
            # TODO: encolar esta atención en un mecanismo de reintento
            # (ej. un job periódico que vuelva a llamar a _validar_contra_ms1
            # para todas las atenciones en estado PENDIENTE_VALIDACION).
            atencion.marcar_pendiente_validacion()
            return

        if paciente is None or personal is None:
            atencion.marcar_rechazada()
            return

        atencion.marcar_validada()

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
