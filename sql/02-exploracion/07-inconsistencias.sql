-- ============================================================
-- 02-exploracion/07-inconsistencias.sql
--
-- Detección de inconsistencias semánticas en el dataset:
-- edades fuera del rango laboral plausible, sueldos negativos o
-- cero, sueldo neto mayor que sueldo bruto, longitudes anómalas en
-- nombres, etc.
-- ============================================================

-- Edades fuera del rango laboral plausible (15 a 90 años)
SELECT
    'Edad < 15'                                AS regla,
    COUNT(*)                                   AS filas,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4) AS pct
FROM servidores_publicos
WHERE edad IS NOT NULL AND edad < 15
UNION ALL
SELECT 'Edad > 90', COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4)
FROM servidores_publicos
WHERE edad IS NOT NULL AND edad > 90
UNION ALL

-- Sueldos en valores no plausibles
SELECT 'sueldo_bruto <= 0', COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4)
FROM servidores_publicos
WHERE sueldo_bruto IS NOT NULL AND sueldo_bruto <= 0
UNION ALL
SELECT 'sueldo_neto <= 0', COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4)
FROM servidores_publicos
WHERE sueldo_neto IS NOT NULL AND sueldo_neto <= 0
UNION ALL

-- Sueldo neto mayor que sueldo bruto (descuentos = positivo significaría neto<bruto)
SELECT 'sueldo_neto > sueldo_bruto', COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4)
FROM servidores_publicos
WHERE sueldo_bruto IS NOT NULL AND sueldo_neto IS NOT NULL
  AND sueldo_neto > sueldo_bruto
UNION ALL

-- Nombres extremadamente cortos
SELECT 'nombre LENGTH < 2', COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM servidores_publicos), 4)
FROM servidores_publicos
WHERE LENGTH(TRIM(nombre)) < 2

ORDER BY filas DESC, regla;
