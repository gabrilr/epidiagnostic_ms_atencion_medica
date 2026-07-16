"""
Adaptador de entrada: atencion_command_router

Lado de COMANDOS (escritura) de CQRS. Separado deliberadamente del
router de queries (atencion_query_router.py) para que la frontera CQRS
sea visible también en la capa de entrada, no solo en application/.
"""
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.atencion_command_dto import (
    CrearAtencionInputDTO,
    MedicamentoInputDTO,
    ModificarAtencionInputDTO,
    SincronizarAtencionesInputDTO,
)
from app.application.commands.handlers.crear_atencion_handler import CrearAtencionUseCase
from app.application.commands.handlers.modificar_atencion_handler import ModificarAtencionUseCase
from app.application.commands.handlers.sincronizar_atenciones_handler import (
    SincronizarAtencionesBatchUseCase,
)
from app.domain.exceptions.domain_exceptions import AtencionNoEncontradaException, EvidenciaInvalidaException
from app.infrastructure.adapters.input.api.atencion_schemas import (
    AtencionResponse,
    CrearAtencionRequest,
    MedicamentoResponse,
    ModificarAtencionRequest,
    ResultadoSincronizacionAtencionResponse,
    SincronizarAtencionesRequest,
    SincronizarAtencionesResponse,
)
from app.infrastructure.dependency_injection import (
    get_crear_atencion_use_case,
    get_modificar_atencion_use_case,
    get_sincronizar_atenciones_batch_use_case,
)

router = APIRouter(prefix="/atenciones", tags=["Atención Médica · Comandos"])


def _request_a_input_dto(request: CrearAtencionRequest) -> CrearAtencionInputDTO:
    return CrearAtencionInputDTO(
        paciente_id=request.paciente_id,
        personal_id=request.personal_id,
        motivo_consulta=request.motivo_consulta,
        fecha_atencion=request.fecha_atencion,
        diagnostico_descripcion=request.diagnostico_descripcion,
        medicamentos=[
            MedicamentoInputDTO(nombre=m.nombre, dosis=m.dosis, frecuencia=m.frecuencia, duracion=m.duracion)
            for m in request.medicamentos
        ],
        evidencia_receta_base64=request.evidencia_receta_base64,
        device_generated_id=request.device_generated_id,
    )


@router.post(
    "",
    response_model=AtencionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra una atención médica nueva.",
)
async def crear_atencion(
    request: CrearAtencionRequest,
    use_case: Annotated[CrearAtencionUseCase, Depends(get_crear_atencion_use_case)],
) -> AtencionResponse:
    """
    Valida paciente_id y personal_id contra el Microservicio 1 de forma
    tolerante a fallos: si MS1 no responde, la atención se crea igual
    con estado `pendiente_validacion` (no se bloquea el registro). Ver
    EstadoAtencion para el detalle de la máquina de estados.
    """
    try:
        input_dto = _request_a_input_dto(request)
        resultado = await use_case.ejecutar(input_dto)
        return AtencionResponse(
            **{**resultado.__dict__, "medicamentos": [MedicamentoResponse(**m.__dict__) for m in resultado.medicamentos]}
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    except EvidenciaInvalidaException as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.post(
    "/sync",
    response_model=SincronizarAtencionesResponse,
    summary="Sincronización batch de atenciones desde la app móvil offline-first.",
)
async def sincronizar_atenciones(
    request: SincronizarAtencionesRequest,
    use_case: Annotated[
        SincronizarAtencionesBatchUseCase, Depends(get_sincronizar_atenciones_batch_use_case)
    ],
) -> SincronizarAtencionesResponse:
    """
    Procesa un lote de atenciones acumuladas en el celular durante
    periodos sin conectividad. Cada atención se procesa de forma
    independiente: un error en una no aborta el resto del batch.
    """
    input_dto = SincronizarAtencionesInputDTO(
        dispositivo_id=request.dispositivo_id,
        atenciones=[_request_a_input_dto(a) for a in request.atenciones],
    )
    resultados = await use_case.ejecutar(input_dto)
    return SincronizarAtencionesResponse(
        resultados=[ResultadoSincronizacionAtencionResponse(**r.__dict__) for r in resultados]
    )


@router.patch(
    "/{atencion_id}",
    response_model=AtencionResponse,
    summary="Corrige diagnóstico y/o evidencia de una atención existente.",
)
async def modificar_atencion(
    atencion_id: UUID,
    request: ModificarAtencionRequest,
    use_case: Annotated[ModificarAtencionUseCase, Depends(get_modificar_atencion_use_case)],
) -> AtencionResponse:
    """
    PATCH parcial: solo se modifica lo que venga en el body distinto de
    null. A diferencia del historial médico de MS1 (append-only), la
    evidencia de receta aquí se REEMPLAZA si ya existía una.
    """
    try:
        input_dto = ModificarAtencionInputDTO(
            motivo_consulta=request.motivo_consulta,
            diagnostico_descripcion=request.diagnostico_descripcion,
            evidencia_receta_base64=request.evidencia_receta_base64,
        )
        resultado = await use_case.ejecutar(atencion_id, input_dto)
        return AtencionResponse(
            **{**resultado.__dict__, "medicamentos": [MedicamentoResponse(**m.__dict__) for m in resultado.medicamentos]}
        )
    except AtencionNoEncontradaException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    except EvidenciaInvalidaException as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
