# Microservicio 2 — Atención Médica

Parte de **EpiDiagnostic-Maya**. Responsable del registro de atenciones
médicas (diagnóstico, signos vitales, medicamentos y evidencia de
receta). Arquitectura hexagonal · CQRS · Patrón Database per service.

No tiene sistema de login propio ni gestiona pacientes/personal — para
cada atención valida `paciente_id` contra **ms-pacientes (MS1)** y
`personal_id` contra **ms-personal (MS3)**, reenviando el mismo Bearer
token con el que llegó la petición.

## Cómo levantar el proyecto

### Con Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://localhost:8001`, con documentación
interactiva en `http://localhost:8001/docs`.

### Migraciones de base de datos

Con los contenedores corriendo:

```bash
docker compose exec api alembic revision --autogenerate -m "crear tablas iniciales"
docker compose exec api alembic upgrade head
```

### Correr tests unitarios (no requiere base de datos)

```bash
pip install -r requirements.txt
pytest tests/unit/ -v
```

## Endpoints implementados

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/atenciones` | Registra una atención médica nueva, con signos vitales, ubicación, medicamentos y evidencia de receta opcionales. | 🔒 |
| POST | `/atenciones/sync` | Sincronización en batch desde la app móvil offline-first. Cada atención del lote se procesa de forma independiente. | 🔒 |
| PATCH | `/atenciones/{id}` | Corrige motivo de consulta, diagnóstico y/o evidencia de una atención existente (PATCH parcial). | 🔒 |
| GET | `/atenciones/paciente/{paciente_id}` | Historial de atenciones de un paciente. | — |
| GET | `/atenciones/personal/{personal_id}` | Atenciones registradas por un médico/enfermera específico. | — |
| GET | `/atenciones/{id}` | Detalle completo de una atención (medicamentos y evidencia incluidos). | — |
| GET | `/health` | Health check para orquestadores / API Gateway. | — |

🔒 = requiere `Authorization: Bearer <token>`, emitido por **ms-personal
(MS3)** y verificado aquí de forma stateless con la misma llave
compartida (`JWT_SECRET_KEY`/`JWT_ALGORITHM`).

> Los tres endpoints de lectura (`GET`) hoy no exigen token — pendiente
> de agregarles el mismo guard que ya tienen los de escritura.

## Regla de negocio clave: tolerancia a fallos al validar contra MS1/MS3

Al crear una atención, `paciente_id` y `personal_id` se validan contra
MS1 y MS3 reenviando el Bearer del usuario. Según lo que responda, la
atención queda en uno de estos estados (`EstadoAtencion`):

| Estado | Cuándo ocurre |
|---|---|
| `validada` | MS1 y MS3 confirmaron que paciente y personal existen. |
| `pendiente_validacion` | MS1/MS3 no respondieron (timeout/caído) o el token fue rechazado (401) — **no bloquea el registro**, se revalida después. |
| `rechazada` | MS1/MS3 respondieron pero el paciente o el personal no existen. |

Esta decisión de diseño evita que una caída momentánea de otro
microservicio le impida a una enfermera registrar una atención en
campo, a costa de aceptar temporalmente datos sin validar.

## Regla de negocio clave: idempotencia por `device_generated_id`

Igual que MS1 usa el CURP, aquí la idempotencia para la app móvil
offline-first se resuelve con `device_generated_id` (UUID generado en
el celular): si `POST /atenciones` o `POST /atenciones/sync` reciben
una atención con un `device_generated_id` ya procesado, se devuelve la
existente en vez de crear un duplicado — soporta reintentos de
sincronización sin conectividad estable.

## Signos vitales, ubicación y evidencia de receta

- Todos los signos vitales (presión sistólica/diastólica, temperatura,
  peso, estatura, glucosa, frecuencia cardíaca, saturación de oxígeno)
  son **opcionales** — se captura lo que se pueda medir en campo, cada
  uno con su propio rango fisiológico válido.
- `dias_evolucion_sintomas` registra cuánto tiempo lleva el paciente
  con síntomas antes de la consulta.
- `comunidad`/`municipio` registran dónde se realizó la atención
  (puede diferir de la comunidad/municipio de residencia del paciente).
- La evidencia de receta (imagen en base64) se sube a Cloudinary al
  crear la atención; en `PATCH /atenciones/{id}` se **reemplaza** si ya
  existía una (a diferencia del historial médico de MS1, que es
  append-only).

## Comunicación con otros microservicios

Este microservicio consume:

- `GET /pacientes/{id}` (MS1) y `GET /personal/{id}` (MS3) — para
  validar la atención al crearla, reenviando el Bearer del usuario.

Y es consumido por la app móvil directamente para registrar/consultar
atenciones y sincronizar el batch offline-first.
