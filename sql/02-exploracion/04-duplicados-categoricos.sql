-- ============================================================
-- 02-exploracion/04-duplicados-categoricos.sql
--
-- Detección de duplicados a nivel de persona. El CSV publica una
-- fila por nombramiento; una misma persona física puede ocupar
-- varios nombramientos simultáneos o consecutivos, lo cual aparece
-- como duplicado del cuarteto (nombre, apellido_1, apellido_2, edad).
--
-- Este hallazgo motiva el split en `personas` (identidad estable)
-- y `nombramientos` (relación laboral) en la capa 03 (normalización
-- a 4NF), eliminando la dependencia funcional implícita
-- {nombre, apellido_1, apellido_2, edad} → atributos identitarios.
-- ============================================================

-- Cuántos cuartetos identitarios aparecen más de una vez
WITH duplicados AS (
    SELECT
        nombre, apellido_1, apellido_2, edad,
        COUNT(*) AS apariciones
    FROM servidores_publicos
    GROUP BY 1, 2, 3, 4
    HAVING COUNT(*) > 1
)
SELECT
    'Cuartetos identitarios con > 1 aparición'    AS metrica,
    COUNT(*)                                       AS valor
FROM duplicados
UNION ALL
SELECT
    'Filas totales explicadas por cuartetos repetidos',
    SUM(apariciones)
FROM duplicados
UNION ALL
SELECT
    'Personas físicas estimadas (cuartetos únicos)',
    COUNT(*)
FROM (
    SELECT DISTINCT nombre, apellido_1, apellido_2, edad
    FROM servidores_publicos
) t
ORDER BY 1;

-- Top 10 personas con más nombramientos en el padrón
SELECT
    nombre, apellido_1, apellido_2, edad,
    COUNT(*) AS nombramientos
FROM servidores_publicos
GROUP BY 1, 2, 3, 4
ORDER BY nombramientos DESC
LIMIT 10;
