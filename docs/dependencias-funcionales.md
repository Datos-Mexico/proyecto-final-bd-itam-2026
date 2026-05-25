# Dependencias funcionales y multivaluadas

Documento académico que registra las dependencias funcionales (DF) y
las dependencias multivaluadas (DMV) identificadas en el dataset
durante el proceso de normalización a 4NF.

---

## Dependencias funcionales triviales

Por la presencia de `id` (SERIAL PRIMARY KEY) en cada tabla:

- `personas.id → {nombre, apellido_1, apellido_2, sexo_id, edad}`
- `nombramientos.id → {persona_id, puesto_id, sector_id, tipo_nomina_id, tipo_contratacion_id, tipo_personal_id, universo_id, nivel_salarial_id, fecha_ingreso, sueldo_bruto, sueldo_neto}`
- Para cada catálogo `cat_X`: `cat_X.id → {todos los atributos descriptivos}`.

Estas son DFs estructurales esperadas (superclave determina al resto)
y no requieren tratamiento especial.

---

## Dependencias funcionales no triviales identificadas

### DF1. Identidad humana → atributos identitarios estables

```
{nombre, apellido_1, apellido_2, edad} → sexo
```

Una persona física con un nombre completo y edad dados tiene un
sexo determinado. Esta dependencia funcional fue la motivación
empírica para crear el catálogo `cat_sexos` y referenciarlo desde
`personas` (en lugar de mantener `sexo` como string repetido en
cada fila como estaba en staging).

**Caveat**: en presencia de **homónimos** (personas distintas con
el mismo nombre completo y misma edad) esta DF puede tener falsos
positivos. El padrón no provee identificadores únicos (CURP, RFC),
por lo que en la migración inicial 1:1 al esquema 4NF se asume
que cada fila del CSV es una persona distinta. La deduplicación
probabilística queda fuera del scope de este proyecto académico.

### DF2. FKs determinan atributos descriptivos del catálogo

Para cada catálogo `cat_X`, el id determina el resto:

- `cat_puestos.id → cat_puestos.nombre`
- `cat_sectores.id → {cat_sectores.clave, cat_sectores.nombre}`
- `cat_tipos_contratacion.id → cat_tipos_contratacion.nombre`
- `cat_tipos_nomina.id → cat_tipos_nomina.clave`
- `cat_tipos_personal.id → cat_tipos_personal.nombre`
- `cat_universos.id → {cat_universos.clave, cat_universos.nombre}`
- `cat_sexos.id → cat_sexos.nombre`
- `cat_niveles_salariales.id → cat_niveles_salariales.clave`

Estas DFs justifican la existencia de los catálogos como tablas
separadas (en lugar de columnas repetidas en `nombramientos`).

### DF3. Estructura puesto/nivel-salarial

```
puesto → nivel_salarial (sospecha empírica)
```

La observación de que los 15 puestos mejor pagados comparten
sueldos exactos por banda (`$111,178`, `$109,981`, `$104,740`,
`$99,967`, `$95,327` — ver `evidencias/consultas-resultados/05-analisis/03-ranking-puestos-window.txt`)
sugiere fuertemente que existe una DF `puesto → tabulador
salarial`. Sin embargo, esta DF se infiere del comportamiento
observado pero **no se modela formalmente** en el esquema 4NF
porque:

1. Hay puestos con sueldo único (e.g. "JEFE DE GOBIERNO") pero
   también puestos con rangos de sueldo (e.g. donde varios
   ocupantes del mismo puesto perciben sueldos distintos por
   tabulador específico).
2. El CSV publica `nivel_salarial` como atributo del nombramiento
   y `sueldo_bruto`/`sueldo_neto` como atributos del nombramiento.
   Modelar formalmente DF3 requeriría una tabla puente
   `(puesto_id, nivel_salarial_id) → sueldo_estándar` que el
   dataset oficial no provee.
3. El esquema 4NF preserva la flexibilidad: si una persona ocupa
   el mismo puesto pero en distinto sector / nivel, su sueldo
   puede variar.

---

## Dependencias multivaluadas (DMV)

### DMV1. Persona → nombramientos

```
persona_id →→ {puesto_id, sector_id, tipo_nomina_id, tipo_contratacion_id, tipo_personal_id, universo_id, nivel_salarial_id, fecha_ingreso, sueldo_bruto, sueldo_neto}
```

Una persona física puede tener **múltiples nombramientos
vigentes simultáneos** o **nombramientos consecutivos**
preservados en el padrón. Esta es la dependencia multivaluada
principal del dataset y motiva el split a dos tablas separadas
(la regla 4NF estándar):

- `personas` (datos identitarios)
- `nombramientos` (datos del nombramiento, con FK a persona)

**Verificación empírica**: la exploración SQL encontró que sólo
**51,710 nombres distintos** existen en **246,821 filas** del
padrón — proporción ~21% — confirmando que el cuarteto identitario
se repite intensivamente. Aunque algunos casos sean homónimos
legítimos, la inmensa mayoría sugiere fuertemente que el mismo
individuo ocupa varios nombramientos. (Ver
`evidencias/consultas-resultados/02-exploracion/04-duplicados-categoricos.txt`.)

### Caveat sobre DMV1

En la migración inicial del staging al esquema 4NF se hace un
mapeo **1:1** entre filas de `servidores_publicos` y filas de
`personas` + `nombramientos` (cada fila del CSV produce una
persona nueva más un nombramiento). Esto **no aprovecha
inmediatamente la DMV1**. La explotación práctica de DMV1
requiere un paso adicional de **deduplicación probabilística** de
personas físicas (record linkage sobre `(nombre, apellido_1,
apellido_2, edad)` con tolerancia a errores tipográficos y
ambigüedad de homónimos), que no es trivial y queda fuera del
scope del proyecto académico inicial.

El esquema queda **listo para deduplicación futura**: cualquier
proceso de record linkage produciría una tabla de mapeo
`persona_canonica_id → [persona_id_1, persona_id_2, ...]` que se
aplicaría como un UPDATE de `nombramientos.persona_id` apuntando
todos los nombramientos del mismo individuo a un único `id` en
`personas`, y luego un DELETE de los `personas` duplicados.

---

## Resumen para la rúbrica

| Categoría | Cantidad identificada | Tratamiento |
|---|---|---|
| DFs triviales (de superclave) | Por cada tabla | Estructural (PKs) |
| DFs no triviales (DF1, DF2, DF3) | 3 | DF1 y DF2 motivaron creación de catálogos; DF3 se documenta como observada pero no se modela |
| Dependencias multivaluadas (DMV1) | 1 | Modelada vía split `personas` / `nombramientos` con FK |

El esquema final 4NF preserva todas las DFs no triviales como
relaciones FK y elimina la DMV1 al separar las dos entidades
involucradas en tablas independientes.
