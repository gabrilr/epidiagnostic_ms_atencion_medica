-- Schema DDL para el Microservicio de Atención Médica (EpiDiagnostic-Maya)
-- Motor de Base de Datos: MySQL / MariaDB

CREATE DATABASE IF NOT EXISTS atencion_medica_db;
USE atencion_medica_db;

-- -------------------------------------------------------------
-- Tabla: atenciones
-- -------------------------------------------------------------
-- Almacena el registro principal de las consultas médicas.
CREATE TABLE IF NOT EXISTS atenciones (
    id CHAR(36) NOT NULL,
    paciente_id CHAR(36) NOT NULL,
    personal_id CHAR(36) NOT NULL,
    motivo_consulta VARCHAR(500) NOT NULL,
    diagnostico_descripcion VARCHAR(1000) DEFAULT NULL,
    dias_evolucion_sintomas INT DEFAULT NULL,
    fecha_atencion DATETIME NOT NULL,
    -- Dónde se realizó la atención (no necesariamente donde vive el
    -- paciente ni donde está asignado el personal, ver Ubicacion en el dominio).
    comunidad VARCHAR(255) NOT NULL,
    municipio VARCHAR(255) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'registrada',
    device_generated_id VARCHAR(36) DEFAULT NULL,
    -- Signos vitales: todos opcionales, se captura lo que se pueda medir.
    presion_sistolica INT DEFAULT NULL,
    presion_diastolica INT DEFAULT NULL,
    temperatura FLOAT DEFAULT NULL,
    peso FLOAT DEFAULT NULL,
    estatura FLOAT DEFAULT NULL,
    glucosa FLOAT DEFAULT NULL,
    frecuencia_cardiaca INT DEFAULT NULL,
    saturacion_oxigeno INT DEFAULT NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices de la tabla atenciones
CREATE INDEX ix_atenciones_paciente_id ON atenciones (paciente_id);
CREATE INDEX ix_atenciones_personal_id ON atenciones (personal_id);
CREATE UNIQUE INDEX ix_atenciones_device_generated_id ON atenciones (device_generated_id);


-- -------------------------------------------------------------
-- Tabla: evidencias_recetas
-- -------------------------------------------------------------
-- Almacena la referencia a las recetas escaneadas (guardadas en Cloudinary).
-- Relación 1-a-1 con la tabla atenciones.
CREATE TABLE IF NOT EXISTS evidencias_recetas (
    id CHAR(36) NOT NULL,
    atencion_id CHAR(36) NOT NULL,
    url_imagen VARCHAR(1000) NOT NULL,
    public_id_cloudinary VARCHAR(500) NOT NULL,
    fecha_captura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_evidencias_recetas_atencion FOREIGN KEY (atencion_id) REFERENCES atenciones (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índice de relación 1-a-1
CREATE UNIQUE INDEX ix_evidencias_recetas_atencion_id ON evidencias_recetas (atencion_id);


-- -------------------------------------------------------------
-- Tabla: medicamentos
-- -------------------------------------------------------------
-- Almacena los medicamentos recetados en cada atención médica.
-- Relación 1-a-Muchos con la tabla atenciones.
CREATE TABLE IF NOT EXISTS medicamentos (
    id CHAR(36) NOT NULL,
    atencion_id CHAR(36) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    dosis VARCHAR(100) NOT NULL,
    frecuencia VARCHAR(100) NOT NULL,
    duracion VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_medicamentos_atencion FOREIGN KEY (atencion_id) REFERENCES atenciones (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índice de la tabla medicamentos
CREATE INDEX ix_medicamentos_atencion_id ON medicamentos (atencion_id);
