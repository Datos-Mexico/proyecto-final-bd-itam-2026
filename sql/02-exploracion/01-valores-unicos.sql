-- ============================================================
-- 02-exploracion/01-valores-unicos.sql
--
-- Cuenta de valores distintos por columna. Sirve para detectar
-- candidatos a normalización (columnas con baja cardinalidad que
-- merecen un catálogo) y para verificar la cobertura de los
-- catálogos ya extraídos del CSV.
-- ============================================================

SELECT 'Total de filas (servidores_publicos)' AS metrica, COUNT(*) AS valor
FROM servidores_publicos
UNION ALL
SELECT 'Nombres distintos',          COUNT(DISTINCT nombre)               FROM servidores_publicos
UNION ALL
SELECT 'Apellido_1 distintos',       COUNT(DISTINCT apellido_1)           FROM servidores_publicos
UNION ALL
SELECT 'Apellido_2 distintos',       COUNT(DISTINCT apellido_2)           FROM servidores_publicos
UNION ALL
SELECT 'Sexo distintos',             COUNT(DISTINCT sexo)                 FROM servidores_publicos
UNION ALL
SELECT 'Edades distintas',           COUNT(DISTINCT edad)                 FROM servidores_publicos
UNION ALL
SELECT 'Puesto_id distintos',        COUNT(DISTINCT puesto_id)            FROM servidores_publicos
UNION ALL
SELECT 'Tipo_nomina_id distintos',   COUNT(DISTINCT tipo_nomina_id)       FROM servidores_publicos
UNION ALL
SELECT 'Tipo_contratacion_id distintos', COUNT(DISTINCT tipo_contratacion_id) FROM servidores_publicos
UNION ALL
SELECT 'Tipo_personal_id distintos', COUNT(DISTINCT tipo_personal_id)     FROM servidores_publicos
UNION ALL
SELECT 'Fechas_ingreso distintas',   COUNT(DISTINCT fecha_ingreso)        FROM servidores_publicos
UNION ALL
SELECT 'Universo_id distintos',      COUNT(DISTINCT universo_id)          FROM servidores_publicos
UNION ALL
SELECT 'Sector_id distintos',        COUNT(DISTINCT sector_id)            FROM servidores_publicos
UNION ALL
SELECT 'Nivel_salarial distintos',   COUNT(DISTINCT id_nivel_salarial)    FROM servidores_publicos
UNION ALL
SELECT 'Sueldo_bruto distintos',     COUNT(DISTINCT sueldo_bruto)         FROM servidores_publicos
UNION ALL
SELECT 'Sueldo_neto distintos',      COUNT(DISTINCT sueldo_neto)          FROM servidores_publicos
ORDER BY 1;
