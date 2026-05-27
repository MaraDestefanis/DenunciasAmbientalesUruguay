# Sistema de Denuncias Ambientales — Uruguay

**D Empathy Project** · Tablero analítico + sistema de captura ciudadana

[![Python](https://img.shields.io/badge/python-3.10+-blue)]() [![Dash](https://img.shields.io/badge/dash-2.14+-teal)]() [![Datos abiertos UY](https://img.shields.io/badge/datos-catalogodatos.gub.uy-success)]()

---

## ¿De qué se trata?

Este proyecto centraliza, normaliza y visualiza las **denuncias ambientales de Uruguay** combinando dos fuentes:

1. **Datos abiertos oficiales** del Ministerio de Ambiente — 4.282 denuncias del período 2010–2019 y 2023, publicadas en [catalogodatos.gub.uy](https://catalogodatos.gub.uy/dataset/ministerio-de-ambiente-denuncias-ambientales).
2. **Captura ciudadana en tiempo real** vía un formulario web integrado al tablero (Dash + PostgreSQL).

Todo se unifica bajo un esquema normalizado de 9 categorías ambientales (`CAT_01`…`CAT_09`) y se publica en un **tablero analítico** con tres niveles de análisis: descriptivo, diagnóstico y predictivo.

> 🌐 **Tablero en producción:** [denuncias-uy.dempathyproject.com](https://denuncias-uy.dempathyproject.com/)

---

## Estructura del repositorio

```
.
├── README.md                          ← este archivo
├── notebooks/                         ← análisis paso a paso (pedagógico)
│   ├── 01_transformacion_datos.ipynb  ← genera data/denuncias.parquet desde los Excel oficiales
│   ├── 02_descriptivo.ipynb           ← evolución, categorías, geografía, perfil
│   ├── 03_diagnostico.ipynb           ← correlaciones, anomalías, triage
│   ├── 04_predictivo.ipynb            ← forecast, NLP, alertas, clustering
│   └── 05_nueva_denuncia.ipynb        ← documentación del formulario de captura
├── data/
│   ├── denuncias_ambientales2010_19.xlsx    ← fuente cruda (no modificar)
│   ├── denuncias-ambientales.xlsx           ← fuente cruda (no modificar)
│   ├── TABLAMOTIVOS.XLSX                    ← crosswalk motivo→categoría
│   ├── denuncias_ambientales_UY_DEP.xlsx    ← esquema target + catálogos
│   ├── denuncias.parquet                    ← producto unificado (regenerable)
│   └── denuncias.csv                        ← idem en CSV
└── app/                                     ← tablero Dash
    ├── app.py                               ← entrada
    ├── main.py                              ← shim para Gunicorn
    ├── data/
    │   ├── generator.py                     ← carga data/denuncias.parquet
    │   └── db.py                            ← persistencia Postgres
    └── dashboard/
        ├── layouts/                         ← un archivo por tab
        └── callbacks/
```

---

## Setup rápido

```bash
# 1. Clonar
git clone https://github.com/MaraDestefanis/DenunciasAmbientalesUruguay.git
cd DenunciasAmbientalesUruguay

# 2. Crear entorno
python -m venv .venv && source .venv/bin/activate    # o conda
pip install -r requirements.txt

# 3. (Opcional pero recomendado) regenerar el parquet desde los Excel oficiales
jupyter notebook notebooks/01_transformacion_datos.ipynb

# 4. Levantar el tablero
cd app
export DATABASE_URL="postgresql://user:pass@host:5432/denuncias"  # opcional
python app.py
# → http://127.0.0.1:5000
```

Si no configurás `DATABASE_URL`, el tablero funciona igual — solo no se pueden registrar denuncias nuevas vía formulario (todo lo demás muestra el histórico).

---

## Dependencias

```
pandas >= 2.0
numpy >= 1.24
pyarrow >= 14.0          # para leer/escribir parquet
openpyxl >= 3.1          # para leer los Excel oficiales
plotly >= 5.18
dash >= 2.14
dash-bootstrap-components >= 1.5
psycopg2-binary >= 2.9   # solo si vas a usar Postgres
scikit-learn >= 1.3      # para el clustering K-Means del notebook 04
jupyter >= 1.0           # para correr los notebooks
```

---

## Cómo se procesan los datos

Los Excel originales tienen esquemas distintos (el de 2010-2019 trae 19 columnas, el de 2023 trae 8). El notebook **01_transformacion_datos.ipynb**:

1. Carga ambas fuentes.
2. Normaliza nombres de departamento (`'Rio Negro'` → `'Río Negro'`, `'Treinta y tres'` → `'Treinta y Tres'`, etc.).
3. Descarta filas con departamento inválido (`'No aplica'`, multi-departamento) — pierde el 0.86%.
4. Mapea los 46 motivos del catálogo oficial a las 9 categorías ambientales del tablero usando `TABLAMOTIVOS.XLSX`.
5. Asigna coordenadas: centroide de la capital del departamento + jitter normal (std=0.15°) — sin sugerir precisión que no tenemos.
6. Agrega columnas temporales calculadas (año, mes, trimestre, día de semana, hora).
7. Deja los campos del formulario nuevo (`urgencia`, `recurrencia`, `tipo_denunciante`, `descripcion_libre`) como `NaN` en el histórico — es lo honesto.
8. Exporta `data/denuncias.parquet` y `data/denuncias.csv`.

Resultado: **4.246 denuncias × 29 columnas** listas para análisis.

---

## El tablero

Tres secciones siguiendo el orden DIKW (datos → información → conocimiento):

### 📊 Descriptivo
- Evolución temporal anual y mensual
- Treemap y sunburst de categorías → subcategorías
- Mapa de burbujas por departamento + mapa de puntos con jitter
- Perfil del denunciante (se llena con datos del formulario)

### 🔍 Diagnóstico
- Heatmap motivo × departamento (absoluto y % por fila)
- Radar chart: perfil ambiental de cada departamento vs. media nacional
- Detección de anomalías mensuales por Z-score
- Score de triage compuesto (volumen + urgencia + permanencia)

### 🔮 Predictivo
- Pronóstico de volumen mensual a 12 meses
- Top 15 términos frecuentes globales y por categoría (NLP baseline)
- Sistema de alertas (Z-score sobre serie reciente)
- Clustering K-Means (k=4) de departamentos por perfil ambiental

---

## Captura ciudadana

El tablero incluye un **formulario** (tab "Nueva denuncia") para que cualquier persona pueda registrar una denuncia. Se persiste en PostgreSQL y se incorpora al tablero en tiempo real.

Estructura (4 secciones, ver `app/dashboard/layouts/encuesta.py`):

1. **Identificación** — Persona / Organización / Anónimo
2. **Ubicación** — Departamento + ciudad + referencia + link de Google Maps
3. **Categoría** — CAT_01..CAT_09 + subcategoría condicional + descripción libre
4. **Contexto** — Fecha del hecho, recurrencia, urgencia, denuncia previa

El notebook **05_nueva_denuncia.ipynb** documenta el flujo completo: validación, geocodificación desde URL de Maps, persistencia y combinación con el histórico.

---

## Limitaciones conocidas

| Tema | Estado |
|------|--------|
| Gap 2020–2022 | Los datos abiertos públicos no incluyen este período. El forecast lo refleja con banda ancha. |
| Coordenadas históricas | Aproximadas a nivel departamento. Las nuevas (formulario) pueden ser precisas. |
| Campos del formulario en histórico | `urgencia`, `recurrencia`, `tipo_denunciante`, `descripcion_libre` (2023) son `NaN`. |
| Pronóstico | Usa polinomio grado 2 sobre el log; en producción conviene migrar a **Prophet** (recomendado en doc técnico v1.0). |
| NLP | Baseline (frecuencia + stopwords). Para producción: BERT multilingüe fine-tuneado. |

---

## Créditos y origen de datos

- **Datos fuente:** Ministerio de Ambiente de Uruguay — [catalogodatos.gub.uy](https://catalogodatos.gub.uy/dataset/ministerio-de-ambiente-denuncias-ambientales) (datos abiertos)
- **Proyecto:** D Empathy Project
- **Autora:** Mara Destéfanis ([github.com/MaraDestefanis](https://github.com/MaraDestefanis))
- **Análisis previo:** [dempathyproject.com/novedades/posts/2025/12/Uruguay_2025.html](https://dempathyproject.com/novedades/posts/2025/12/Uruguay_2025.html)
- **Documento técnico:** `doc_tecnico_tablero_ambiental_UY.docx` v1.0 (Marzo 2026)

---

## Licencia

Los datos originales son **abiertos** (Ministerio de Ambiente de Uruguay).
El código de este repositorio se publica bajo licencia [a definir — sugerencia: MIT].
