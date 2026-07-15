"""
Comando: SincronizarAtencionesBatchCommand (handler)

Implementa POST /atenciones/sync, usado por la app móvil offline-first
al recuperar conectividad. Reutiliza CrearAtencionUseCase para cada
atención del batch, igual que se hizo en MS1 con
SincronizarPacientesBatchUseCase.

Igual que en MS1: procesamiento secuencial y tolerante a fallos
individuales — un error en una atención no aborta el resto del batch.

Diferencia clave respecto a MS1: aquí la idempotencia NO es por una
business key como el CURP, sino por device_generated_id, porque ya
asumimos (ver diseño) que paciente_id y personal_id llegan correctos
(el celular ya los descargó del catálogo de MS1), así que no hay
ambigüedad de identidad que resolver, solo evitar reprocesar la misma
atención si el batch se reintenta.
"""
from app.application.commands.handlers.crear_atencion_handler import CrearAtencionUseCase
from app.application.dtos.atencion_command_dto import (
    ResultadoSincronizacionAtencionDTO,
    SincronizarAtencionesInputDTO,
)


class SincronizarAtencionesBatchUseCase:

    def __init__(self, crear_atencion_use_case: CrearAtencionUseCase):
        self._crear_atencion_use_case = crear_atencion_use_case

    async def ejecutar(
        self, datos: SincronizarAtencionesInputDTO
    ) -> list[ResultadoSincronizacionAtencionDTO]:
        resultados: list[ResultadoSincronizacionAtencionDTO] = []

        for atencion_input in datos.atenciones:
            try:
                resultado = await self._crear_atencion_use_case.ejecutar(atencion_input)
                resultados.append(
                    ResultadoSincronizacionAtencionDTO(
                        device_generated_id=atencion_input.device_generated_id,
                        id_servidor=resultado.id,
                        estado=resultado.estado,
                    )
                )
            except ValueError as error:
                # TODO: registrar en log estructurado / tabla de errores
                # de sincronización, igual que en MS1.
                resultados.append(
                    ResultadoSincronizacionAtencionDTO(
                        device_generated_id=atencion_input.device_generated_id,
                        id_servidor="",
                        estado=f"error: {str(error)}",
                    )
                )

        return resultados
