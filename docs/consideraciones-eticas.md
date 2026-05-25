# Consideraciones éticas

Documento académico que registra los dilemas éticos identificados
en el trabajo con el Padrón de Servidores Públicos de la CDMX,
las mitigaciones aplicadas, y los caveats que el equipo técnico
fundador asume como compromisos públicos.

---

## 1. Naturaleza del dataset y mandato legal de publicación

El Padrón de Servidores Públicos es **publicación obligada** por
ley:

- Ley General de Transparencia y Acceso a la Información Pública,
  artículos 70 fracción VIII (federal).
- Ley de Transparencia, Acceso a la Información Pública y
  Rendición de Cuentas de la Ciudad de México, artículo 121
  fracción VIII.

El acceso público a la información sobre quién trabaja en el
gobierno y cuánto gana es un principio constitutivo de la
rendición de cuentas democrática. Trabajar académicamente con
este dataset no plantea problemas éticos básicos de acceso: los
datos son legítimamente públicos.

## 2. Información incluida vs excluida del padrón

El CSV publicado **incluye**:

- Nombre completo (nombre + dos apellidos)
- Sexo
- Edad
- Sector / dependencia
- Puesto
- Tipo de contratación, tipo de personal, tipo de nómina
- Universo laboral
- Nivel salarial
- Fecha de ingreso
- Sueldo bruto y neto

El CSV publicado **NO incluye** (mitigación de exposición
implementada por el publicador):

- CURP, RFC, NSS u otros identificadores únicos
- Domicilio
- Teléfono o email
- Estado civil
- Datos bancarios
- Foto o datos biométricos

La exposición es **mínima compatible con la rendición de cuentas
pública**. El observatorio respeta esta línea: no enriquece el
padrón con datos personales adicionales obtenidos de otras
fuentes.

## 3. Riesgo de re-identificación

Aún con el subset publicado, la combinación
`(nombre completo, edad, sector)` permite re-identificar a una
persona física en muchos casos. Esto es una propiedad inherente
del dataset (no un defecto del proyecto académico) y el
publicador lo asume como costo aceptable del principio de
transparencia.

**Compromiso del observatorio**: los endpoints analíticos públicos
de `api.datos-itam.org` publican **agregados** sobre el padrón
(distribuciones, percentiles, rankings por sector), no la lectura
fila-a-fila del CSV. El padrón completo se accede únicamente vía
descarga directa del Portal de Datos Abiertos oficial de la
CDMX, no a través de la API del observatorio.

## 4. Sesgo de género en el dataset

El padrón registra `sexo` como variable de tres valores:
`MASCULINO`, `FEMENINO`, `NA`. Esto es una **limitación
ontológica** del dataset oficial:

- No registra identidad de género (distinta de sexo biológico).
- No registra personas no binarias como categoría reconocida.
- El valor `NA` aparece en una sola fila del padrón, lo cual
  sugiere que es un dato faltante puntual, no una categoría
  abierta.

**Compromiso académico**: cualquier análisis de brecha de género
sobre este dataset debe documentar esta limitación ontológica.
La brecha cuantificada (`+3.76%` a nivel padrón, hasta
`+28.90%` a nivel sector ver
[Etapa 4](04-analisis-resultados.md)) refleja diferencias entre
MASCULINO y FEMENINO binarios y no captura la realidad completa
del universo de género laboral.

## 5. Inconsistencias preservadas vs corregidas

El dataset contiene **11,426 filas (4.63%) con `sueldo_neto > sueldo_bruto`**.
Esta es una inconsistencia semántica clara desde el modelo
clásico de nómina, pero plausible en la práctica por bonos,
compensaciones retroactivas o pagos extraordinarios.

**Decisión académica**: **se preserva** la inconsistencia tal
cual aparece en el dataset oficial. Razones:

1. **Fidelidad al dataset**: limpiar inconsistencias introduciría
   un sesgo (¿qué filas se "corrigen"? ¿qué criterio se aplica?).
2. **Transparencia**: el caveat queda documentado y los
   consumidores del esquema 4NF pueden decidir si filtrar o no.
3. **Replicabilidad**: cualquier persona que reproduzca el
   proceso obtiene los mismos números, sin asumir corrigios
   ocultos.

Las consultas analíticas de la Etapa 4 documentan en su prosa
las inconsistencias relevantes cuando son materiales para el
hallazgo.

## 6. Deduplicación de personas físicas

El conteo `SELECT COUNT(*) FROM personas` arroja 246,821, igual al
conteo de nombramientos. La evidencia empírica disponible (246,490
cuartetos identitarios únicos sobre `(nombre, apellido_1,
apellido_2, edad)`) sugiere que el padrón tiene esencialmente una
persona única por nombramiento, con solamente 305 cuartetos
repetidos en 636 filas (0.26%). Sin acceso a un identificador único
como CURP o RFC, no es posible deduplicar personas físicas con
certeza académica: los cuartetos repetidos podrían corresponder a
homónimos genuinos (personas distintas con el mismo nombre,
apellidos y edad) o a la misma persona con múltiples nombramientos.
La normalización a 4NF aplicada en este proyecto NO pretende
deduplicar personas físicas; separa entidades léxicas (nombres,
apellidos) en catálogos reutilizables y normaliza los tabuladores
administrativos, dejando el padrón estructuralmente listo para una
futura deduplicación si se obtiene acceso a un identificador único.

**Caveat académico**: la deduplicación probabilística requiere:

1. Una clave natural confiable que el CSV no provee.
2. Tolerancia a errores tipográficos en nombres.
3. Manejo de homónimos legítimos (personas distintas con el
   mismo nombre completo y misma edad).

Implementar record linkage probabilístico está fuera del scope
del proyecto académico final. El esquema queda **listo para
deduplicación futura** sin requerir cambios estructurales (ver
[`dependencias-funcionales.md`](dependencias-funcionales.md) §DMV1).

## 7. Dilema de publicación del observatorio

El Observatorio Datos México publica como SDK Python (PyPI) y
sitio web canónico únicamente **agregados computados** del
padrón, nunca filas individuales identificables. Esto preserva
el balance entre:

- **Utilidad analítica pública** (cualquier investigador puede
  obtener estadísticas, distribuciones, brechas por sector,
  rankings).
- **Mitigación de exposición individual** (el observatorio no
  facilita búsquedas tipo "cuánto gana Juan Pérez de 45 años en
  la Secretaría X" más allá de lo que el CSV oficial ya permite).

Este compromiso es operacional, no es un secreto: aparece
publicado en `datosmexico.org` y en la sección
[Open source](../README.md#open-source-y-disponibilidad-pública-del-observatorio)
del README maestro.

## 8. Compromisos del equipo técnico fundador

El equipo asume públicamente los siguientes compromisos al trabajar
con este dataset:

1. **Cero re-publicación fila a fila**: el padrón completo no se
   re-publica desde la API del observatorio.
2. **Cero enriquecimiento con datos personales externos**: el
   padrón no se cruza con CURP, RFC, redes sociales, etc.
3. **Documentación honesta de limitaciones**: este documento es
   parte de la entrega académica oficial y se mantiene
   versionado.
4. **Reproducibilidad transparente**: cualquier persona con
   acceso al CSV oficial o al dump físico puede reproducir cada
   paso del proceso académico.
