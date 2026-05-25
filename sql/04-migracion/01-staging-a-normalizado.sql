-- ============================================================
-- sql/04-migracion/01-staging-a-normalizado.sql
--
-- Migración de los datos desde la tabla de staging
-- `servidores_publicos` hacia el esquema normalizado a 4NF
-- (`personas` + `nombramientos` + catálogos faltantes).
--
-- Precondiciones:
--   - La capa de staging está cargada (sql/01-staging/* aplicado).
--   - El DDL normalizado existe (sql/03-normalizado/01 aplicado).
--
-- Postcondición:
--   - personas y nombramientos están pobladas.
--   - cat_sexos y cat_niveles_salariales están pobladas.
--   - La tabla servidores_publicos puede ser dropeada al final.
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- Paso 1 — Poblar catálogos nuevos desde valores distintos
-- ------------------------------------------------------------

INSERT INTO cat_sexos (nombre)
SELECT DISTINCT sexo FROM servidores_publicos
WHERE sexo IS NOT NULL
ORDER BY sexo;

INSERT INTO cat_niveles_salariales (clave)
SELECT DISTINCT id_nivel_salarial FROM servidores_publicos
WHERE id_nivel_salarial IS NOT NULL
ORDER BY id_nivel_salarial;

-- ------------------------------------------------------------
-- Paso 2 — Poblar `personas`. Una fila por nombramiento del staging
--   produce una persona; el id se conserva alineado con servidores_publicos.id
--   para facilitar la migración 1-a-1 al primer nombramiento.
-- ------------------------------------------------------------

INSERT INTO personas (id, nombre, apellido_1, apellido_2, sexo_id, edad)
SELECT
    sp.id,
    sp.nombre,
    sp.apellido_1,
    sp.apellido_2,
    cs.id,
    sp.edad
FROM servidores_publicos sp
LEFT JOIN cat_sexos cs ON cs.nombre = sp.sexo;

-- Re-sincronizar la secuencia con el id máximo insertado
SELECT setval('personas_id_seq', (SELECT MAX(id) FROM personas));

-- ------------------------------------------------------------
-- Paso 3 — Poblar `nombramientos`. Una fila por nombramiento
--   del staging produce un nombramiento que apunta a la persona
--   correspondiente.
-- ------------------------------------------------------------

INSERT INTO nombramientos (
    persona_id, puesto_id, sector_id, tipo_nomina_id,
    tipo_contratacion_id, tipo_personal_id, universo_id,
    nivel_salarial_id, fecha_ingreso, sueldo_bruto, sueldo_neto
)
SELECT
    sp.id,
    sp.puesto_id,
    sp.sector_id,
    sp.tipo_nomina_id,
    sp.tipo_contratacion_id,
    sp.tipo_personal_id,
    sp.universo_id,
    cns.id,
    sp.fecha_ingreso,
    sp.sueldo_bruto,
    sp.sueldo_neto
FROM servidores_publicos sp
LEFT JOIN cat_niveles_salariales cns ON cns.clave = sp.id_nivel_salarial;

-- ------------------------------------------------------------
-- Paso 4 — Aplicar índices de la capa 03
-- ------------------------------------------------------------
-- (Ejecutar `sql/03-normalizado/02-create-indexes.sql` después de
--  esta migración para que los índices se construyan sobre los
--  datos ya poblados.)

-- ------------------------------------------------------------
-- Paso 5 — Vista de compatibilidad (denormalizada CSV-shape)
--   Se usa para verificar que la transformación preserva los datos.
-- ------------------------------------------------------------

CREATE VIEW v_servidores_publicos AS
SELECT
    p.id, p.nombre, p.apellido_1, p.apellido_2,
    cs.nombre AS sexo, p.edad,
    n.puesto_id, n.tipo_nomina_id, n.tipo_contratacion_id,
    n.tipo_personal_id, n.fecha_ingreso, n.universo_id, n.sector_id,
    cns.clave AS id_nivel_salarial, n.sueldo_bruto, n.sueldo_neto
FROM personas p
JOIN nombramientos n        ON n.persona_id = p.id
LEFT JOIN cat_sexos cs      ON cs.id = p.sexo_id
LEFT JOIN cat_niveles_salariales cns ON cns.id = n.nivel_salarial_id;

-- ------------------------------------------------------------
-- Paso 6 — Drop de la tabla staging (una vez verificada la migración)
--
-- Después de este DROP, las consultas de `sql/02-exploracion/*.sql`
-- (Etapa 2) ya no podrán ejecutarse contra esta base: dependen de
-- la tabla `servidores_publicos` desnormalizada. Los outputs de
-- esas exploraciones ya están preservados en
-- `evidencias/consultas-resultados/02-exploracion/`. Si necesitas
-- re-ejecutarlas, restaura el dump físico en una base separada.
-- ------------------------------------------------------------

DROP TABLE servidores_publicos CASCADE;

COMMIT;

-- ============================================================
-- Verificación post-migración (referencia)
--
--   SELECT COUNT(*) FROM personas;       -- esperado: ≈246,800
--   SELECT COUNT(*) FROM nombramientos;  -- esperado: ≈246,800 (1:1 inicial)
--   SELECT COUNT(*) FROM cat_sexos;      -- esperado: 2 ó 3
--   SELECT COUNT(*) FROM cat_niveles_salariales; -- esperado: ≈720
-- ============================================================
