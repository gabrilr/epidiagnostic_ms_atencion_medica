"""
Tests unitarios de la entidad Atencion y sus value objects/entidades
internas. No requieren base de datos, MS1, ni Cloudinary — validan solo
el dominio puro.
"""
import uuid
from datetime import datetime, timedelta

import pytest

from app.domain.entities.atencion import Atencion
from app.domain.entities.evidencia_receta import EvidenciaReceta
from app.domain.entities.medicamento import Medicamento
from app.domain.value_objects.diagnostico import Diagnostico
from app.domain.value_objects.estado_atencion import EstadoAtencion


def _crear_atencion_valida() -> Atencion:
    return Atencion(
        paciente_id=uuid.uuid4(),
        personal_id=uuid.uuid4(),
        diagnostico=Diagnostico(motivo_consulta="Dolor abdominal"),
        fecha_atencion=datetime.utcnow() - timedelta(hours=1),
    )


def test_crear_atencion_valida_queda_en_estado_registrada():
    atencion = _crear_atencion_valida()
    assert atencion.estado == EstadoAtencion.REGISTRADA
    assert atencion.medicamentos == []
    assert atencion.evidencia_receta is None


def test_atencion_con_fecha_futura_lanza_excepcion():
    with pytest.raises(ValueError):
        Atencion(
            paciente_id=uuid.uuid4(),
            personal_id=uuid.uuid4(),
            diagnostico=Diagnostico(motivo_consulta="Dolor abdominal"),
            fecha_atencion=datetime.utcnow() + timedelta(days=1),
        )


def test_diagnostico_con_motivo_vacio_lanza_excepcion():
    with pytest.raises(ValueError):
        Diagnostico(motivo_consulta="")


def test_marcar_validada_cambia_estado():
    atencion = _crear_atencion_valida()
    atencion.marcar_validada()
    assert atencion.estado == EstadoAtencion.VALIDADA


def test_marcar_pendiente_validacion_no_rechaza_la_atencion():
    """
    Caso clave de la tolerancia a fallos: si MS1 no responde, la
    atención queda pendiente, NO rechazada.
    """
    atencion = _crear_atencion_valida()
    atencion.marcar_pendiente_validacion()
    assert atencion.estado == EstadoAtencion.PENDIENTE_VALIDACION
    assert atencion.estado != EstadoAtencion.RECHAZADA


def test_marcar_rechazada_cambia_estado():
    atencion = _crear_atencion_valida()
    atencion.marcar_rechazada()
    assert atencion.estado == EstadoAtencion.RECHAZADA


def test_agregar_medicamento():
    atencion = _crear_atencion_valida()
    medicamento = Medicamento(nombre="Paracetamol", dosis="500mg", frecuencia="cada 8 horas", duracion="3 días")
    atencion.agregar_medicamento(medicamento)
    assert len(atencion.medicamentos) == 1
    assert atencion.medicamentos[0].nombre == "Paracetamol"


def test_adjuntar_evidencia_reemplaza_no_anexa():
    """
    A diferencia del historial médico de MS1 (append-only), la
    evidencia de receta SÍ se reemplaza al adjuntar una nueva.
    """
    atencion = _crear_atencion_valida()
    evidencia_1 = EvidenciaReceta(url_imagen="https://cloudinary.com/img1.jpg", public_id_cloudinary="id1")
    evidencia_2 = EvidenciaReceta(url_imagen="https://cloudinary.com/img2.jpg", public_id_cloudinary="id2")

    atencion.adjuntar_evidencia(evidencia_1)
    assert atencion.evidencia_receta.url_imagen == "https://cloudinary.com/img1.jpg"

    atencion.adjuntar_evidencia(evidencia_2)
    assert atencion.evidencia_receta.url_imagen == "https://cloudinary.com/img2.jpg"
    # Solo existe UNA evidencia a la vez, no una lista acumulada.


def test_dos_atenciones_mismo_paciente_son_independientes():
    """
    Valida la regla de negocio confirmada en el diseño: dos atenciones
    al mismo paciente por personal distinto no generan ningún tipo de
    conflicto ni dependencia entre sí.
    """
    paciente_id = uuid.uuid4()
    atencion_1 = Atencion(
        paciente_id=paciente_id,
        personal_id=uuid.uuid4(),
        diagnostico=Diagnostico(motivo_consulta="Consulta comunidad A"),
        fecha_atencion=datetime.utcnow() - timedelta(days=2),
    )
    atencion_2 = Atencion(
        paciente_id=paciente_id,
        personal_id=uuid.uuid4(),
        diagnostico=Diagnostico(motivo_consulta="Consulta comunidad B"),
        fecha_atencion=datetime.utcnow() - timedelta(hours=1),
    )

    assert atencion_1.id != atencion_2.id
    assert atencion_1.paciente_id == atencion_2.paciente_id
    assert atencion_1.personal_id != atencion_2.personal_id
