"""
Adaptador de entrada: atencion_query_router

Lado de QUERIES (lectura) de CQRS. Endpoints más simples, sin
validación de negocio compleja — solo proyecciones de lectura.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.queries.handlers.listar_atenciones_paciente_handler import (
    ListarAtencionesPorPacienteUseCase,
)
from app.application.queries.handlers.listar_atenciones_personal_handler import (
    ListarAtencionesPorPersonalUseCase,
)
from app.application.queries.handlers.obtener_detalle_atencion_handler import (
    ObtenerDetalleAtencionUseCase,
)
from app.domain.exceptions.domain_exceptions import AtencionNoEncontradaException
from app.infrastructure.adapters.input.api.atencion_schemas import (
    AtencionListadoResponse,
    AtencionResponse,
    MedicamentoResponse,
)
from app.infrastructure.dependency_injection import (
    get_listar_atenciones_paciente_use_case,
    get_listar_atenciones_personal_use_case,
    get_obtener_detalle_atencion_use_case,
)

router = APIRouter(prefix="/atenciones", tags=["Atención Médica · Consultas"])


@router.get(
    "/paciente/{paciente_id}",
    response_model=list[AtencionListadoResponse],
    summary="Historial de atenciones de un paciente (todas, sin importar quién lo atendió).",
)
async def listar_atenciones_por_paciente(
    paciente_id: UUID,
    use_case: Annotated[
        ListarAtencionesPorPacienteUseCase, Depends(get_listar_atenciones_paciente_use_case)
    ],
) -> list[AtencionListadoResponse]:
    resultados = await use_case.ejecutar(paciente_id)
    return [AtencionListadoResponse(**r.__dict__) for r in resultados]


@router.get(
    "/{atencion_id}",
    response_model=AtencionResponse,
    summary="Detalle completo de una atención (medicamentos y evidencia incluidos).",
)
async def obtener_detalle_atencion(
    atencion_id: UUID,
    use_case: Annotated[ObtenerDetalleAtencionUseCase, Depends(get_obtener_detalle_atencion_use_case)],
) -> AtencionResponse:
    try:
        resultado = await use_case.ejecutar(atencion_id)
        return AtencionResponse(
            **{**resultado.__dict__, "medicamentos": [MedicamentoResponse(**m.__dict__) for m in resultado.medicamentos]}
        )
    except AtencionNoEncontradaException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.get(
    "/personal/{personal_id}",
    response_model=list[AtencionListadoResponse],
    summary="Atenciones registradas por un médico/enfermera específico.",
)
async def listar_atenciones_por_personal(
    personal_id: UUID,
    use_case: Annotated[
        ListarAtencionesPorPersonalUseCase, Depends(get_listar_atenciones_personal_use_case)
    ],
) -> list[AtencionListadoResponse]:
    resultados = await use_case.ejecutar(personal_id)
    return [AtencionListadoResponse(**r.__dict__) for r in resultados]
