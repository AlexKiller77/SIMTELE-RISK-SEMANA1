-- SIMTELE-RISK | Esquema SQL obligatorio (Semana 2)
-- Basado en la Sección 8 de la consigna: 6 entidades mínimas con trazabilidad completa.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS caso_estudio (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    modelo_version TEXT NOT NULL DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS escenario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caso_id TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('NORMAL', 'ESTRES', 'MAL_CONDICIONADO')),
    parametros_json TEXT NOT NULL,
    fuente_datos TEXT NOT NULL,
    FOREIGN KEY (caso_id) REFERENCES caso_estudio(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS simulacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    escenario_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    usuario_equipo TEXT DEFAULT 'local',
    estado TEXT NOT NULL DEFAULT 'COMPLETADA',
    FOREIGN KEY (escenario_id) REFERENCES escenario(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ejecucion_metodo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacion_id INTEGER NOT NULL,
    metodo TEXT NOT NULL,
    tolerancia REAL DEFAULT 1e-10,
    paso REAL,
    max_iter INTEGER DEFAULT 500,
    convergio INTEGER NOT NULL DEFAULT 1,
    tiempo_ms REAL DEFAULT 0.0,
    FOREIGN KEY (simulacion_id) REFERENCES simulacion(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS iteracion_resultado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ejecucion_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    aproximacion_json TEXT NOT NULL,
    residual REAL,
    error_abs REAL,
    error_rel REAL,
    FOREIGN KEY (ejecucion_id) REFERENCES ejecucion_metodo(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS resultado_resumen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ejecucion_id INTEGER NOT NULL,
    referencia TEXT NOT NULL,
    valor_json TEXT NOT NULL,
    metrica_error_json TEXT NOT NULL,
    interpretacion TEXT,
    FOREIGN KEY (ejecucion_id) REFERENCES ejecucion_metodo(id) ON DELETE CASCADE
);

-- Semillas iniciales de los 4 módulos obligatorios
INSERT OR IGNORE INTO caso_estudio (id, nombre, modelo_version) VALUES
    ('detencion', 'Detención de emergencia', '2.0'),
    ('deterioro', 'Deterioro y mantenimiento', '2.0'),
    ('oscilaciones', 'Oscilaciones por viento', '2.0'),
    ('sensores', 'Reconstrucción de sensores', '2.0');
