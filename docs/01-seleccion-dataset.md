# Etapa 1 — Selección del conjunto de datos

Este documento responde las preguntas que la rúbrica del curso pide
para la Etapa 1 sobre el **Padrón de Servidores Públicos de la
Ciudad de México**.

---

## 1. Resumen

Dataset abierto publicado por el Gobierno de la Ciudad de México que
contiene una fila por nombramiento vigente de servidores públicos
de la administración pública de la CDMX al corte de la publicación.
Cada fila documenta el nombre completo, sexo, edad, fecha de
ingreso, puesto, sector dependencia, tipo de contratación, tipo de
nómina, tipo de personal, universo laboral, nivel salarial, y los
sueldos bruto y neto del nombramiento. Al corte preservado en el
dump físico del 2026-04-20, el dataset registra **246,821
nombramientos** distribuidos en **73 sectores de gobierno** con
**246,490 cuartetos identitarios únicos** sobre
`(nombre, apellido_1, apellido_2, edad)`. Sin acceso a un
identificador único como CURP o RFC, no es posible determinar con
certeza cuántas personas físicas distintas componen el padrón; los
305 cuartetos que se repiten (en 636 filas, 0.26% del total) pueden
corresponder a homónimos genuinos o a la misma persona con
múltiples nombramientos.

## 2. Origen y autoría

- **Productor**: Dirección General de Administración de Personal y
  Desarrollo Administrativo de la Secretaría de Administración y
  Finanzas del Gobierno de la Ciudad de México.
- **Publicador**: Portal de Datos Abiertos del Gobierno de la Ciudad
  de México (`datos.cdmx.gob.mx`).
- **Marco legal**: artículo 121 fracción VIII de la Ley de
  Transparencia, Acceso a la Información Pública y Rendición de
  Cuentas de la Ciudad de México.

## 3. Justificación de elección

Cuatro criterios convergen en este dataset:

1. **Relevancia pública** — los sueldos de servidores públicos son
   tema de interés ciudadano permanente, vinculado a fiscalización
   y rendición de cuentas.
2. **Tamaño suficiente** — 246,821 filas, muy por encima del mínimo
   de 5,000 que pide la rúbrica.
3. **Estructura rica** — 16 columnas con tipos mixtos (numéricas,
   categóricas con baja y alta cardinalidad, fechas, texto) permiten
   ilustrar todas las técnicas de la rúbrica.
4. **Disponibilidad confiable** — dataset oficial, actualización
   periódica documentada, formato CSV estandarizado.

## 4. Disponibilidad y acceso

- **Acceso**: público y gratuito a través del Portal de Datos
  Abiertos del Gobierno de la Ciudad de México.
- **Formato de descarga**: CSV (UTF-8) y XLSX.
- **Licencia**: datos abiertos del Gobierno de la CDMX bajo los
  términos del Portal de Datos Abiertos.
- **Requiere autenticación**: no.
- **Endpoints alternativos**: la API REST `api.datos-itam.org` del
  Observatorio Datos México expone subconjuntos analíticos
  computados sobre el padrón sin autenticación
  (`/api/v1/dashboard/stats`, `/api/v1/sectores/`,
  `/api/v1/analytics/*`).

## 5. Periodicidad

El padrón se publica con periodicidad regular por el Gobierno de la
Ciudad de México. Cada publicación es un snapshot del estado
vigente de los nombramientos en el momento del corte. Este
proyecto académico trabaja sobre el snapshot preservado en el dump
físico del 2026-04-20.

## 6. Dimensiones del dataset

| Dimensión | Valor |
|---|---|
| Filas (nombramientos) | 246,821 |
| Columnas (atributos por fila) | 16 |
| Sectores de gobierno | 73 |
| Puestos distintos | 1,772 |
| Tipos de contratación | 7 |
| Tipos de personal | 11 |
| Tipos de nómina | 7 |
| Universos laborales | 27 |
| Niveles salariales | 721 |
| Rango etario | 16-60 años |
| Rango salario bruto | $461 - $111,178 MXN |

## 7. Diccionario sintético

| Columna del CSV | Tipo lógico | Cardinalidad | Notas |
|---|---|---|---|
| `nombre` | texto identitario | 51,710 strings distintos (universo léxico) | Primer nombre del servidor. |
| `apellido_1` | texto identitario | 7,864 distintos | Apellido paterno. |
| `apellido_2` | texto identitario | 7,872 distintos | Apellido materno; algunos servidores no tienen. |
| `sexo` | categórico | 3 valores | MASCULINO, FEMENINO, NA. |
| `edad` | numérico discreto | 45 valores | 16-60 años. |
| `puesto` | categórico alta cardinalidad | 1,772 valores | Catalogable. |
| `sector` (clave + nombre) | categórico | 73 sectores | Catalogable. |
| `tipo_contratacion` | categórico | 7 valores | Catalogable. |
| `tipo_personal` | categórico | 11 valores | Catalogable. |
| `tipo_nomina` | numérico categórico | 7 valores | Catalogable. |
| `universo` | categórico | 27 valores | Catalogable. |
| `nivel_salarial` | numérico categórico | 721 valores | Catalogable. |
| `fecha_ingreso` | fecha | 14,133 distintas | Serie temporal. |
| `sueldo_bruto` | numérico continuo | 858 valores | NUMERIC(12,2). |
| `sueldo_neto` | numérico continuo | 859 valores | NUMERIC(12,2). |

El diccionario completo del esquema 4NF (con tipos PostgreSQL,
constraints y FKs) está en
[`diccionario-datos.md`](diccionario-datos.md).

## 8. Variables cuantitativas

Tres variables cuantitativas centrales:

- `edad` (entero discreto, 16-60). Distribución sesgada hacia el
  rango 36-55 años (ver `evidencias/consultas-resultados/02-exploracion/03-estadisticas-numericas.txt`).
- `sueldo_bruto` (numeric 12,2). Distribución de cola larga: media
  $13,225 pero P75 sólo $16,451 y máximo $111,178.
- `sueldo_neto` (numeric 12,2). Análogo. Media $11,796.

## 9. Variables cualitativas

Trece variables cualitativas, todas catalogables (extraídas como
catálogos en la capa de staging y referenciadas por FK desde la
tabla principal `servidores_publicos` y, post-normalización, desde
`personas` y `nombramientos`).

## 10. Texto no estructurado

El padrón no contiene texto no estructurado en sentido NLP. Los
campos textuales (`nombre`, `apellido_1`, `apellido_2`, descripciones
de puesto y sector) son etiquetas identitarias o categóricas
discretas con bajo ruido.

## 11. Series temporales

`fecha_ingreso` define la única dimensión temporal del dataset: la
fecha de inicio del nombramiento. Permite reconstruir series de
antigüedad y distribución temporal de los nombramientos vigentes.
Rango empírico del dump: el padrón vigente al 2026-04-20 contiene
nombramientos con fecha de ingreso a lo largo de 14,133 fechas
distintas (~38.6 años).

## 12. Visión estratégica

El padrón es la base empírica para múltiples análisis de política
pública:

- **Equidad salarial**: detección y cuantificación de brechas de
  género por sector, puesto, antigüedad, edad.
- **Estructura presupuestal**: composición del gasto público en
  remuneraciones de la administración de la CDMX por sector.
- **Movilidad laboral**: una vez identificadas personas físicas
  (post-normalización a 4NF), análisis de carreras dentro del
  gobierno (un mismo individuo en distintos nombramientos).
- **Comparativos cross-dataset**: vinculado a ENIGH y ENOE (otros
  datasets del observatorio), permite comparar el sueldo del
  servidor público contra la distribución de ingresos del hogar
  nacional.

## 13. Consideraciones éticas

Resumen aquí; el análisis completo está en
[`consideraciones-eticas.md`](consideraciones-eticas.md).

- **Datos personales**: el padrón es publicación oficial obligada
  por la Ley de Transparencia local. La publicación no expone
  domicilio, CURP, RFC, ni teléfono — sólo nombre completo,
  sexo, edad y datos del nombramiento. La exposición es la mínima
  posible compatible con el principio de rendición de cuentas
  pública.
- **Riesgo de re-identificación**: nombre completo + edad +
  sector + sueldo permite re-identificar a personas físicas. El
  observatorio respeta este compromiso al publicar agregados
  (sin re-publicar el padrón fila a fila) en los endpoints
  analíticos.
- **Sesgo de género**: el dataset registra el sexo binario/
  ternario. Cualquier análisis de brecha debe documentar esta
  limitación.
- **Cobertura**: el padrón cubre nombramientos vigentes únicamente,
  no incluye servidores que ya salieron de la administración ni a
  contratistas externos. Cualquier inferencia sobre "el universo
  laboral del gobierno de la CDMX" debe limitarse a esta cobertura.
