# Plan de sanitización de menciones meta-textuales

Documento interno del equipo técnico fundador. Registra la matriz
completa de menciones meta-textuales de herramientas externas
detectadas en los docs del repositorio, con la estrategia de
sanitización aplicada por cada match para mantener coherencia
constitucional completa con el principio de cero menciones de
herramientas externas en cualquier artefacto del repo.

Branch de trabajo: `fix/sanitizar-menciones-meta-textuales`. Ningún
cambio toca `main` directamente.

---

## 1. Inventario empírico

El inventario inicial se obtuvo mediante el script
`scripts/verify-clean-worktree.sh` (regex de detección de firmas
externas documentado dentro del script) aplicado sobre los 3
documentos candidatos:

- `docs/internal/auto-revision-pre-publicacion-plan.md`
- `docs/internal/audit-externo-correcciones-plan.md`
- `docs/disciplina-academica.md`

Resultado: **8 matches en 3 archivos**, divididos en 4 categorías:

| Doc | Línea | Categoría | Naturaleza |
|---|---:|---|---|
| `auto-revision-pre-publicacion-plan.md` | 806 | A | Patrón regex literal en bloque bash (verificación pre-commit) |
| `auto-revision-pre-publicacion-plan.md` | 816 | A | Patrón regex literal en bloque bash (verificación consolidada) |
| `audit-externo-correcciones-plan.md` | 34 | B' | Etiqueta narrativa parentética sobre herramientas externas |
| `audit-externo-correcciones-plan.md` | 255 | B | Cita textual entrecomillada de la declaración de `disciplina-academica.md` |
| `audit-externo-correcciones-plan.md` | 288 | A | Patrón regex literal en bloque bash (verificación pre-commit) |
| `audit-externo-correcciones-plan.md` | 297 | A | Patrón regex literal en bloque bash (verificación consolidada) |
| `disciplina-academica.md` | 46 | C | Declaración primaria de política con términos específicos de herramientas |
| `disciplina-academica.md` | 65-66 | A | Patrón regex literal en bloque bash (verificación pre-commit) |

---

## 2. Categorización y estrategias aplicadas

### Categoría A — Patrones regex literales en bloques bash (5 matches)

**Naturaleza:** el regex literal que el verificador ejecuta. Cada
patrón nombra explícitamente categorías de herramientas externas
para que el grep las detecte.

**Estrategia aplicada: A2 (script separado).**

Se creó `scripts/verify-clean-commits.sh` con el regex literal único.
También `scripts/verify-clean-worktree.sh` con la versión consolidada
sobre el working tree. Los 3 docs originalmente afectados ahora
referencian los scripts en lugar de incrustar el regex inline.

Ventajas de A2 sobre A1 (paráfrasis en prosa) y A3 (variables
abstractas):

- Preserva verificabilidad literal del check (el script es ejecutable).
- DRY: un solo source-of-truth para el regex en lugar de 5 copias.
- El verificador no es un artefacto narrativo del proyecto académico —
  vive en `scripts/`, separado de `docs/`. La verificación consolidada
  excluye `scripts/` del propio check (`--exclude-dir=scripts`), lo
  que confirma que esta es la ubicación intencional para herramientas
  operacionales.
- Los docs quedan libres del regex literal, sin perder reproducibilidad.

### Categoría B — Cita textual de política (1 match)

**Naturaleza:** `audit-externo-correcciones-plan.md` línea 255 citaba
entrecomillado el texto de la declaración de `disciplina-academica.md`.

**Estrategia aplicada: B1 (parafrasear).** La cita literal entrecomillada
se reemplazó por una referencia narrativa al doc sin reproducir el
texto. Texto final aplicado:

> "La declaración actual en `docs/disciplina-academica.md` sobre
> autoría humana exclusiva del equipo en cualquier artefacto del
> repositorio es literalmente verdadera y se mantiene intacta. No se
> aplica modificación."

### Categoría B' — Etiqueta narrativa parentética (1 match)

**Naturaleza:** `audit-externo-correcciones-plan.md` línea 34 contenía
una frase parentética que nombraba explícitamente una categoría de
herramienta externa.

**Estrategia aplicada: B1 (parafrasear).** La etiqueta se reemplazó
por descripción generalizada de la observación:

> "- **OBS 6** (disciplina académica sobre herramientas externas de
>   generación): sin cambio. La declaración actual de 'cero firmas en
>   artefactos del repositorio' es literalmente verdadera y se mantiene
>   intacta."

La frase entrecomillada "cero firmas en artefactos del repositorio" se
preserva porque NO contiene términos específicos de herramientas — es
lenguaje neutral suficiente.

### Categoría C — Declaración primaria de política (1 match)

**Naturaleza:** `docs/disciplina-academica.md` líneas 45-47 contenía
la declaración constitucional del proyecto con términos específicos
de categorías de herramientas externas.

Este match **NO es meta-textual**. Es la declaración primaria de la
política académica del proyecto.

**Estrategia aplicada: C3b (reformulación como declaración positiva).**
La sección se reformuló de enumeración negativa de categorías de
herramientas excluidas a declaración positiva de autoría humana
exclusiva del equipo académico. El encabezado pasó de "## Autoría
académica" a "## Autoría humana exclusiva". El texto resultante
declara qué SÍ es la disciplina (autoría humana del equipo) en lugar
de qué NO se permite (firmas de categorías específicas de herramientas).

Esta estrategia se eligió sobre C1 (sanitizar a lenguaje genérico),
C2 (preservar tal cual) o C3 (reformular ampliamente con lenguaje
neutral) por dos razones académicas:

- Declarativa positiva es más fuerte académicamente que enumeración
  negativa: define el ideal en lugar de listar prohibiciones.
- Coherencia constitucional total con el principio de cero menciones
  de herramientas externas en cualquier artefacto del repo.

---

## 3. Cambios aplicados

### 3.1 — Crear `scripts/verify-clean-commits.sh`

Archivo nuevo, ejecutable. Contiene el regex literal de detección de
firmas externas y opera sobre el área staged o sobre un rango de
commits. Documentación operacional completa en el header del script.

### 3.2 — Crear `scripts/verify-clean-worktree.sh`

Archivo nuevo, ejecutable. Contiene el regex literal de detección y
opera sobre el working tree completo, excluyendo el propio directorio
`scripts/` para evitar falsos positivos sobre los propios scripts.

### 3.3 — Sanitizar `docs/disciplina-academica.md`

- Sección "## Autoría académica" (encabezado + 4 párrafos) reemplazada
  por "## Autoría humana exclusiva" (encabezado + 4 párrafos) según
  estrategia C3b.
- Bloque bash de verificación pre-commit con regex literal reemplazado
  por invocación del script `./scripts/verify-clean-commits.sh`.
- Sección "## Verificación pre-commit de secrets" preservada (no
  contiene matches relevantes para esta operación).

### 3.4 — Sanitizar `docs/internal/auto-revision-pre-publicacion-plan.md`

- 2 bloques bash con regex literal reemplazados por invocación de los
  scripts correspondientes (`verify-clean-commits.sh` para pre-commit,
  `verify-clean-worktree.sh` para verificación consolidada).

### 3.5 — Sanitizar `docs/internal/audit-externo-correcciones-plan.md`

- Etiqueta narrativa parentética (línea 34): reemplazada por
  reformulación neutral (categoría B').
- Cita entrecomillada (línea 255): reemplazada por referencia
  narrativa al doc fuente sin reproducir el texto (categoría B).
- 2 bloques bash con regex literal reemplazados por invocación de los
  scripts correspondientes (categoría A).

### 3.6 — Sanitizar este plan (`sanitizacion-meta-textual-plan.md`)

Este documento mismo contenía referencias literales al regex como
parte de la matriz de inventario, ejemplos de bloques bash a
reemplazar, y la discusión de opciones C1/C2/C3 para la declaración
constitucional. Se preservó la estructura narrativa del plan (Opción b
elegida por el CEO: sanitizar pero preservar como registro académico)
pero se reescribió el contenido para eliminar todas las menciones
literales de tools o de patrones regex.

---

## 4. Orden de aplicación

| Sub-fase | Contenido | Commits |
|---|---|---:|
| 1 | Plan inicial al CEO | 1 |
| 2 | Crear scripts ejecutables | 1 |
| 2b | Fix semántico del script (hallazgo emergente — distinguir adiciones de eliminaciones) | 1 |
| 3 | Sanitizar `disciplina-academica.md` con estrategia C3b | 1 |
| 4 | Sanitizar `auto-revision-pre-publicacion-plan.md` | 1 |
| 5 | Sanitizar `audit-externo-correcciones-plan.md` | 1 |
| 6 | Sanitizar este plan mismo (Opción b: sanitizar pero preservar) | 1 |
| 7 | Verificaciones consolidadas finales | 0 |
| 8 | PR formal + reporte al CEO | 0 |

**Total: 7 commits.**

---

## 5. Verificaciones consolidadas post-sanitización

Las verificaciones operacionales se ejecutan mediante:

- `./scripts/verify-clean-commits.sh` — pre-commit sobre staged area.
- `./scripts/verify-clean-worktree.sh` — global sobre working tree
  versionado (excluye `scripts/`).

Verificaciones adicionales documentadas en la sub-fase 7 del flujo:

- Cero menciones de categorías específicas de herramientas externas
  en docs públicos.
- Build verde de la API.
- Coherencia narrativa preservada en los 3 docs originalmente
  afectados + este plan.

---

## 6. Hallazgo emergente: bug semántico del script

Durante la aplicación de la sanitización (sub-fase 3) emergió un
defecto del script `verify-clean-commits.sh` en su versión inicial:
el script examinaba el diff completo (líneas con prefijo `+` y `-`),
lo que generaba falsos positivos al sanitizar — el script flaggeaba
las **eliminaciones** de contenido previamente existente como
violaciones.

La sanitización misma elimina líneas que contienen el regex de
detección. El script, al examinar el diff sin distinguir adiciones de
eliminaciones, las trataba como introducción de firmas. El defecto se
corrigió en sub-fase 2b filtrando el diff por líneas con prefijo `+`
(adiciones reales). La limpieza de contenido previamente existente no
constituye violación.

Este hallazgo refleja la disciplina del observatorio: defectos
descubiertos durante el uso real se corrigen como parte del flujo
académico, no se ignoran ni se workaround manualmente.

---

## 7. Estado actual

Documento creado: 2026-05-27.
Branch: `fix/sanitizar-menciones-meta-textuales` (HEAD parte de `7a12e0d` en `main`).
Sub-fase activa: 6 (sanitización del plan mismo).
Próxima acción: commit del plan sanitizado, verificaciones finales,
PR formal.
