-- ============================================================
-- 02-exploracion/08-columnas-redundantes.sql
--
-- Análisis: Columnas Redundantes
--
-- Objetivo: Evaluar dependencias funcionales entre columnas del staging
-- para detectar redundancias residuales que justifiquen catálogos
-- adicionales o validar las dependencias ya documentadas.
--
-- Alcance del análisis (transparencia académica):
-- Este script opera sobre la tabla `servidores_publicos` del staging
-- preservado en el dump físico custodiado por el equipo técnico fundador
-- (`api/remuneraciones_cdmx.dump`, 2026-04-20 16:16 CST), NO sobre el
-- CSV crudo del Portal de Datos Abiertos del Gobierno de la CDMX.
--
-- Razón del alcance: el dump físico ya tiene los catálogos puesto,
-- sector, tipo de nómina, tipo de contratación, tipo de personal y
-- universo extraídos como FK ids (`puesto_id`, `sector_id`,
-- `tipo_nomina_id`, `tipo_contratacion_id`, `tipo_personal_id`,
-- `universo_id`). Las redundancias clave-descriptor del CSV crudo
-- (e.g. `id_universo` vs `n_universo`) ya quedaron resueltas en la
-- extracción inicial de catálogos. Este análisis evalúa las
-- dependencias funcionales que permanecen entre las columnas FK y
-- entre FK y valores numéricos del staging.
--
-- Conexión con docs/dependencias-funcionales.md: la dependencia
-- funcional DF3 (`puesto → nivel_salarial`) está declarada como
-- "sospecha empírica" en ese documento. Las queries 2 y 4 de este
-- script validan empíricamente esa sospecha contra los datos reales.
-- ============================================================

-- 1. ¿tipo_nomina_id → tipo_contratacion_id?
--    Pregunta académica: ¿el tipo de nómina determina funcionalmente
--    el tipo de contratación? Si sí, una de las dos columnas es
--    redundante en `nombramientos`.
SELECT
    'tipo_nomina_id → tipo_contratacion_id' AS dependencia_evaluada,
    COUNT(DISTINCT tipo_nomina_id) AS cardinalidad_clave,
    COUNT(DISTINCT tipo_contratacion_id) AS cardinalidad_valor,
    COUNT(DISTINCT (tipo_nomina_id, tipo_contratacion_id)) AS combinaciones_unicas,
    CASE
        WHEN COUNT(DISTINCT (tipo_nomina_id, tipo_contratacion_id)) =
             COUNT(DISTINCT tipo_nomina_id)
        THEN 'REDUNDANTE: tipo_contratacion_id derivable de tipo_nomina_id'
        ELSE 'NO redundante: hay variación dentro del mismo id'
    END AS conclusion
FROM servidores_publicos;

-- 2. ¿puesto_id → id_nivel_salarial?
--    Validación empírica de DF3 declarada en
--    docs/dependencias-funcionales.md como sospecha. Si la cardinalidad
--    de combinaciones únicas iguala la cardinalidad de puestos, cada
--    puesto tiene exactamente un nivel salarial y DF3 se confirma.
SELECT
    'puesto_id → id_nivel_salarial' AS dependencia_evaluada,
    COUNT(DISTINCT puesto_id) AS cardinalidad_clave,
    COUNT(DISTINCT id_nivel_salarial) AS cardinalidad_valor,
    COUNT(DISTINCT (puesto_id, id_nivel_salarial)) AS combinaciones_unicas,
    CASE
        WHEN COUNT(DISTINCT (puesto_id, id_nivel_salarial)) =
             COUNT(DISTINCT puesto_id)
        THEN 'REDUNDANTE: id_nivel_salarial derivable de puesto_id (DF3 confirmada)'
        ELSE 'NO redundante: el mismo puesto admite varios niveles salariales (DF3 no se confirma)'
    END AS conclusion
FROM servidores_publicos;

-- 3. ¿id_nivel_salarial → (sueldo_bruto, sueldo_neto)?
--    Pregunta académica: ¿el nivel salarial determina los sueldos
--    exactos? Si sí, los sueldos son derivables del nivel y la tabla
--    `cat_niveles_salariales` podría enriquecerse con un par
--    (sueldo_bruto, sueldo_neto) por nivel, eliminando duplicación.
SELECT
    'id_nivel_salarial → (sueldo_bruto, sueldo_neto)' AS dependencia_evaluada,
    COUNT(DISTINCT id_nivel_salarial) AS cardinalidad_clave,
    COUNT(DISTINCT (sueldo_bruto, sueldo_neto)) AS cardinalidad_par_sueldos,
    COUNT(DISTINCT (id_nivel_salarial, sueldo_bruto, sueldo_neto)) AS combinaciones_unicas,
    CASE
        WHEN COUNT(DISTINCT (id_nivel_salarial, sueldo_bruto, sueldo_neto)) =
             COUNT(DISTINCT id_nivel_salarial)
        THEN 'REDUNDANTE: sueldos derivables de id_nivel_salarial'
        ELSE 'NO redundante: hay variación de sueldos dentro del mismo nivel'
    END AS conclusion
FROM servidores_publicos;

-- 4. ¿puesto_id → (sueldo_bruto, sueldo_neto)?
--    Pregunta académica: ¿el puesto determina los sueldos exactos
--    directamente, sin pasar por nivel_salarial? La evidencia
--    descriptiva (15 puestos top con sueldos exactos repetidos por
--    banda) sugiere que algunos puestos sí, pero la pregunta es si
--    se cumple universalmente para los 1,772 puestos del padrón.
SELECT
    'puesto_id → (sueldo_bruto, sueldo_neto)' AS dependencia_evaluada,
    COUNT(DISTINCT puesto_id) AS cardinalidad_clave,
    COUNT(DISTINCT (sueldo_bruto, sueldo_neto)) AS cardinalidad_par_sueldos,
    COUNT(DISTINCT (puesto_id, sueldo_bruto, sueldo_neto)) AS combinaciones_unicas,
    CASE
        WHEN COUNT(DISTINCT (puesto_id, sueldo_bruto, sueldo_neto)) =
             COUNT(DISTINCT puesto_id)
        THEN 'REDUNDANTE: sueldos derivables de puesto_id'
        ELSE 'NO redundante: el mismo puesto admite varios pares de sueldos'
    END AS conclusion
FROM servidores_publicos;
