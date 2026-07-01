"""
Comando: ModificarAtencionCommand (handler)

TODO: Implementar el endpoint PATCH /atenciones/{id}

Casos de uso típicos: corregir un diagnóstico, agregar/reemplazar
evidencia de receta después de creada la atención (ej. la enfermera
subió la foto más tarde porque no tenía la receta físicamente en el
momento de registrar la atención).

Debe:
1. Recibir atencion_id y los campos opcionales a modificar (similar a
   ActualizarDatosPacienteUseCase en MS1: PATCH parcial).
2. Buscar la atención con atencion_command_repository.buscar_por_id().
   Si no existe -> AtencionNoEncontradaException.
3. Si viene evidencia_receta_base64 nueva, subirla con
   evidencia_storage.subir_evidencia() y llamar a
   atencion.adjuntar_evidencia() (esto SÍ reemplaza la evidencia
   anterior, a diferencia del historial de MS1 que es append-only —
   ver docstring de Atencion.adjuntar_evidencia).
4. Si vienen cambios de diagnóstico, reconstruir el Value Object
   Diagnostico (es inmutable/frozen) y reasignar atencion.diagnostico.
5. Persistir con atencion_command_repository.actualizar(atencion).

Ejemplo de firma esperada:

    class ModificarAtencionUseCase:
        def __init__(
            self,
            atencion_repository: AtencionCommandRepository,
            evidencia_storage: EvidenciaStoragePort,
        ):
            ...

        async def ejecutar(self, atencion_id: UUID, datos: ModificarAtencionInputDTO) -> AtencionOutputDTO:
            ...
"""
