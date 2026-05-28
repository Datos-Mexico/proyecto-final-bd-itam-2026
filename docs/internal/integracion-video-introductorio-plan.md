# Plan de integración del video introductorio

Documento interno del equipo técnico fundador. Registra la matriz
completa de cambios para integrar el video introductorio del
observatorio al README del repositorio académico como thumbnail
clickeable, ubicado al inicio del documento.

Branch de trabajo: `feat/integrar-video-introductorio`. Ningún cambio
toca `main` directamente.

---

## 1. Recurso a integrar

| Campo | Valor |
|---|---|
| URL | `https://www.youtube.com/watch?v=eEzjg_IHslI` |
| ID del video | `eEzjg_IHslI` |
| Duración | 37 segundos |
| Canal | Canal oficial del observatorio en YouTube |
| Uso original | Apertura visual de la presentación oral del proyecto académico |

Thumbnail URL primario: `https://img.youtube.com/vi/eEzjg_IHslI/maxresdefault.jpg`
Fallbacks en orden si maxresdefault no existe: `hqdefault.jpg` (480×360),
`mqdefault.jpg` (320×180). La validación HTTP 200 se ejecuta en sub-fase 2.

---

## 2. Estructura actual del README

Inventario empírico de las primeras 30 líneas del `README.md` en
`main` (HEAD `73d5e32`):

| Línea | Contenido |
|---:|---|
| 1 | `# Proyecto final — Bases de Datos COM-12101-001` (título maestro) |
| 2 | (línea en blanco) |
| 3 | `## ITAM, Primavera 2026` (subtítulo) |
| 4 | (línea en blanco) |
| 5 | `> Snapshot académico del Observatorio Datos México.` (tagline) |
| 6 | (línea en blanco) |
| 7 | `---` (separador) |
| 8 | (línea en blanco) |
| 9 | `## Resumen del proyecto` (primera sección de contenido) |
| ... | (resumen del proyecto, líneas 10-25) |
| 27 | `---` (separador) |
| 29 | `## Equipo académico` (segunda sección de contenido) |

El README **no contiene badges** (shield.io u otros). La estructura es
título maestro + subtítulo + tagline + separador + secciones.

---

## 3. Ubicación de inserción aplicada

El bloque del video se inserta **entre el tagline (línea 5) y el
separador (línea 7)**. Esto coloca el video como el primer elemento
visual del repo tras el título maestro, antes del separador inicial y
de la sección `## Resumen del proyecto`.

Justificación de la ubicación:
- Respeta el contrato del prompt: "al inicio del README justo después
  de los badges (si existen) o el título maestro".
- El tagline es la última línea del bloque del título maestro; el
  separador `---` marca el final del bloque introductorio.
- Insertar antes del separador integra el video como parte del bloque
  introductorio del documento, no como una sección posterior.
- Quien navega al repo ve la apertura visual del observatorio antes
  del primer texto descriptivo, coherente con la apertura visual de
  la presentación oral del proyecto académico.

Diff aplicado (formulación final aprobada por el CEO):

```diff
 > Snapshot académico del Observatorio Datos México.

+<p align="center">
+  <a href="https://www.youtube.com/watch?v=eEzjg_IHslI">
+    <img src="https://img.youtube.com/vi/eEzjg_IHslI/maxresdefault.jpg" alt="Observatorio Datos México — video introductorio" width="640">
+  </a>
+</p>
+
+<p align="center"><em>Video introductorio del observatorio · 37 segundos</em></p>
+
 ---

 ## Resumen del proyecto
```

---

## 4. Texto literal del bloque insertado (formulación final aprobada)

```html
<p align="center">
  <a href="https://www.youtube.com/watch?v=eEzjg_IHslI">
    <img src="https://img.youtube.com/vi/eEzjg_IHslI/maxresdefault.jpg" alt="Observatorio Datos México — video introductorio" width="640">
  </a>
</p>

<p align="center"><em>Video introductorio del observatorio · 37 segundos</em></p>
```

Cambios respecto a la propuesta original de sub-fase 1:
- Sin heading `## Video introductorio` (eliminado para no competir
  jerárquicamente con el subtítulo institucional ITAM Primavera 2026).
- Sin párrafo descriptivo de dos líneas (reemplazado por caption breve
  en cursiva).
- HTML `<p align="center">` para centrar el thumbnail en la página
  del README renderizado por GitHub.
- Ancho del thumbnail fijado en `640px` para presencia visual sin
  desbordar el ancho de lectura.

Notas técnicas:
- HTML estándar compatible con el renderer de GitHub. Al clickear la
  imagen, se abre el video en YouTube en una pestaña nueva.
- El `alt` text es académicamente honesto y no contiene términos de
  herramientas externas.
- El caption en cursiva (`<em>`) contextualiza brevemente al lector
  sobre el contenido y duración del video.

---

## 5. Justificación académica

El video fue producido como pieza institucional del observatorio y
utilizado como apertura de la presentación oral del proyecto académico
ante el profesor del curso. Integrarlo como primer visual del repo
refuerza la coherencia narrativa: quien navega al repo después de la
presentación ve lo mismo que vio el profesor al inicio de la
presentación, consolidando la experiencia académica.

La integración respeta los principios constitucionales del observatorio:

- **Transparencia 100%**: el video es público en el canal de YouTube
  del observatorio y se referencia con URL completa, no embebido.
- **Replicabilidad**: el thumbnail es URL pública de YouTube
  (`img.youtube.com`), no requiere assets binarios commiteados al
  repo.
- **Coherencia constitucional**: el bloque no contiene firmas
  externas ni menciones de herramientas no autorizadas.

---

## 6. Plan de verificaciones post-inserción

1. Verificación del thumbnail URL:
   ```bash
   curl -sI "https://img.youtube.com/vi/eEzjg_IHslI/maxresdefault.jpg" | head -1
   ```
   Esperado: `HTTP/2 200` o `HTTP/1.1 200 OK`. Si falla, fallback a
   `hqdefault.jpg` o `mqdefault.jpg`.

2. Verificación pre-commit con el script:
   ```bash
   ./scripts/verify-clean-commits.sh
   ```
   Esperado: exit code 0.

3. Verificación consolidada del working tree:
   ```bash
   ./scripts/verify-clean-worktree.sh
   ```
   Esperado: cero firmas externas detectadas.

4. Verificación visual del README renderizado (opcional manual del CEO):
   `gh pr view <numero> --web` para ver el preview del PR en GitHub
   antes del merge.

---

## 7. Estado actual

Documento creado: 2026-05-27.
Branch: `feat/integrar-video-introductorio` (HEAD parte de `73d5e32` en `main`).
Sub-fase activa: 1.
Próxima acción: commit este plan, push, reportar al CEO, pausar.
