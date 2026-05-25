# Relación con el Observatorio Datos México

## Narrativa académica honesta

Este documento explica cómo el proyecto académico final de Bases
de Datos COM-12101-001 (ITAM, Primavera 2026) dio origen al
**Observatorio Datos México**, una iniciativa de investigación
con respaldo institucional del ITAM que hoy publica cuatro
datasets mexicanos vía SDK Python, API REST y sitio canónico.

---

## Cronología verificable

| Fecha | Hito |
|---|---|
| **2026-03-05** | Creación del repositorio de backend `DabtcAvila/datos-itam` en GitHub (vacío). |
| **2026-04-20** | Primer commit del backend (`b075421`): "feat: normalized DB schema + API + Railway deploy config". Estado raw pre-normalización capturado en dump físico local (`api/remuneraciones_cdmx.dump`, 16:16 CST); estado normalizado capturado 27 minutos después (`api/remuneraciones_cdmx_normalized.dump`, 16:43 CST). |
| **2026-04-21** | Auth JWT, CRUD endpoints, ingesta CSV vía API (`POST /ingest/csv`). |
| **2026-04-22** | Despliegue de la primera versión de la API a Railway (`api.datos-itam.org`). Sitio canónico inicial. Suite de tests E2E con Playwright contra producción. |
| **Abril 2026** | Cierre del entregable académico del proyecto final del curso de Bases de Datos. |
| **Mayo 2026** | Expansión del observatorio a tres datasets adicionales: ENIGH 2024 (Encuesta Nacional de Ingresos y Gastos de los Hogares), CONSAR AFORE recursos (Sistema de Ahorro para el Retiro), ENOE 15+ (Encuesta Nacional de Ocupación y Empleo). |
| **2026-05-23** | Audit interno completo del observatorio (Fase 1 inventario + Fase 2 contrato API). Reportes preservados en `docs/internal/audit-2026-05/` del repositorio privado del backend del observatorio — no están en este repo académico. |

---

## El proyecto académico como semilla

Lo que el equipo entregó como **proyecto final del curso**:

1. Selección del dataset Padrón CDMX
2. Carga preliminar y exploración SQL
3. Normalización a 4NF con `personas` + `nombramientos` + ocho catálogos
4. Análisis SQL avanzado (window functions, percentiles, brechas)
5. API REST FastAPI sobre el esquema normalizado

Este corpus inicial fue suficiente para cumplir la rúbrica del
curso y constituye el contenido de este repositorio académico.

---

## La expansión al observatorio

Después de cerrar el entregable académico, el equipo continuó
expandiendo el sistema con **objetivos académicos** (no
comerciales): tener una plataforma de investigación de datos
públicos mexicanos consumible por terceros académicos.

### Datasets adicionales incorporados

**ENIGH 2024 Nueva Serie** (`schema enigh`)

- Encuesta Nacional de Ingresos y Gastos de los Hogares 2024.
- 91,000 hogares muestra, expandible a 38.8M hogares nacional.
- 17 tablas + 111 catálogos + 5.78M filas de gastos + 864K personas + 366K negocios.
- Reproducción byte-exact de 13 bounds oficiales del Comunicado INEGI 112/25.

**CONSAR AFORE recursos** (`schema consar`)

- Serie mensual de recursos del Sistema de Ahorro para el Retiro.
- 326 meses (1998-05 a 2025-06), 11 AFOREs, 15 tipos de recurso.
- 35,617 filas de la serie principal + 9 tablas analíticas
  derivadas.

**ENOE 15+** (`schema enoe`)

- Encuesta Nacional de Ocupación y Empleo.
- 101.5M filas de microdatos + 76,557 indicadores agregados.
- 80 trimestres (2005T1-2025T1), 13 indicadores núcleo, 32
  entidades federativas, 3 etapas metodológicas.

### Componentes públicos consumibles

| Componente | Repositorio | Distribución |
|---|---|---|
| **API REST** | privada (deuda técnica documentada) | `api.datos-itam.org` |
| **SDK Python** `datos-mexico` | [`Datos-Mexico/datos-mexico-py`](https://github.com/Datos-Mexico/datos-mexico-py) público | PyPI: `pip install datos-mexico` |
| **Sitio canónico** | [`Datos-Mexico/datos-mexico-site`](https://github.com/Datos-Mexico/datos-mexico-site) público | `datosmexico.org` |
| **Repo académico** | `Datos-Mexico/proyecto-final-bd-itam-2026` (este repo) | público con licencia MIT |

### Deuda técnica honesta

El código del **backend completo** permanece en repositorio
privado por una deuda técnica conocida: una credencial de base
de datos histórica está presente en la historia de git del repo
privado. La mitigación (rotar la credencial Neon + reescribir
historia con `git filter-repo` o BFG + force-push) está en
roadmap. Mientras tanto:

- El backend privado opera la API pública sin interrupciones.
- El SDK y el sitio canónico son públicos y reproducibles.
- Este repo académico contiene un snapshot del backend recortado
  al scope CDMX, **sin secrets**, verificado archivo por
  archivo.

---

## Por qué este repo académico se limita al scope CDMX

El proyecto del curso pidió un solo dataset. El equipo cumplió
con CDMX, que satisface y sobrecumple los mínimos de la rúbrica
(≥5,000 registros, ≥15 atributos, ≥5 entidades) con holgura:

- 246,821 registros (49× el mínimo).
- 30+ atributos sumados a través del esquema normalizado.
- 10 entidades (2 datos + 8 catálogos).

Los otros tres datasets (ENIGH, CONSAR, ENOE) **no estaban en el
scope académico original** y se incorporaron al observatorio
después del entregable. Documentarlos aquí ampliaría el repo
hacia algo distinto a la entrega académica del curso —
intencionalmente se mantiene el scope CDMX para honrar la
naturaleza del entregable.

La narrativa académica de este repo es:

> "Aquí está, sin retoques, el proyecto del curso. El mismo
> trabajo continuó creciendo en el observatorio público; pero
> ese repo académico es lo que entregamos como evidencia del
> aprendizaje en la materia."

---

## Compromiso de portabilidad institucional

El observatorio se llama **Observatorio Datos México** (dominio
canónico `datosmexico.org`). El ITAM aparece como **respaldo
institucional actual**, no como dueño del observatorio. Esta
lectura es intencionalmente portable: si la relación con el ITAM
cambia en el futuro, el observatorio sobrevive con identidad
propia.

Aplicación a este repo: es la entrega académica del proyecto del
semestre, una atadura honesta a la clase específica y semestre
específico. Esa atadura es correcta para este repo (es la
naturaleza académica de la entrega), pero NO se extiende a
redefinir el observatorio entero. El repo académico es
artefacto académico complementario al observatorio, no su
definición.
