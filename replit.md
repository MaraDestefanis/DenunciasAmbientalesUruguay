# Sistema de Denuncias Ambientales · D Empathy Project · Uruguay

## Resumen del proyecto

Tablero analítico interactivo para el seguimiento y análisis de denuncias ambientales en Uruguay. Incluye un formulario de captura ciudadana integrado en el mismo tablero, junto con análisis descriptivo, diagnóstico y predictivo.

## Stack técnico

- **Framework**: Plotly Dash + Dash Bootstrap Components
- **Lenguaje**: Python 3.11
- **Datos**: Dataset sintético (4.281 registros, 2014-2025) + denuncias reales persistidas en PostgreSQL
- **Base de datos**: PostgreSQL integrada (Replit) — tabla `denuncias`, conexión via `DATABASE_URL`
- **Puerto**: 5000

## Estructura del proyecto

```
app.py                     # Punto de entrada principal (Dash app)
main.py                    # Runner alternativo
data/
  generator.py             # Generador de datos sintéticos + get_data() + add_new_record()
  db.py                    # Módulo PostgreSQL: init_db(), save_denuncia(), load_denuncias()
  __init__.py
dashboard/
  assets/
    custom.css             # Tema oscuro estilo D Empathy Project
  layouts/
    header.py              # Header + barra de KPIs
    charts.py              # Todas las funciones de gráficos Plotly
    descriptivo.py         # Sección 1: análisis descriptivo (4 sub-tabs)
    diagnostico.py         # Sección 2: correlaciones, anomalías, triage
    predictivo.py          # Sección 3: pronósticos, NLP, alertas, clustering
    encuesta.py            # Formulario de captura ciudadana
    __init__.py
  callbacks/
    callbacks.py           # Todos los callbacks de Dash registrados
    __init__.py
```

## Secciones del tablero

### KPIs siempre visibles (header fijo)
- Total de denuncias acumuladas
- Denuncias del mes actual
- Categoría más frecuente (últimos 30 días)
- Departamento líder (año en curso)

### Sección 1 — Análisis Descriptivo
- **Temporal**: evolución anual, tendencia mensual con media móvil, heatmap hora × día
- **Categorías**: treemap, sunburst, ranking subcategorías, área apilada por categoría
- **Geográfico**: mapa de burbujas por departamento, mapa de puntos geolocalizados, composición por categoría en top depts
- **Perfil denunciante**: tipo (donut), urgencia (gauge), recurrencia por categoría

### Sección 2 — Análisis de Diagnóstico
- **Correlaciones**: heatmap motivo × departamento, radar chart vs media nacional
- **Anomalías**: detección Z-score, lista de períodos anómalos
- **Triage**: matriz urgencia × recurrencia, score de riesgo ambiental (tabla top 15)

### Sección 3 — Análisis Predictivo
- **Pronósticos**: tendencia + IC 95% a 12 meses, mini-KPIs por categoría
- **Texto & NLP**: top términos frecuentes por categoría, fuente de datos
- **Alertas**: semáforos en tiempo real, tabla de umbrales configurables
- **Clustering territorial**: K-Means k=4 sobre perfil de categorías por departamento

### Formulario de denuncia (Nueva denuncia)
- S1: Tipo de denunciante (Persona / Organización / Anónimo)
- S2: Ubicación (departamento, ciudad, referencia, URL Google Maps)
- S3A: Categoría con botones visuales (9 categorías)
- S3B: Subcategoría condicional (desplegable según cat. elegida)
- S3C: Descripción libre (máx. 500 caracteres con contador)
- S4: Fecha, recurrencia, urgencia, denuncia previa y organismo
- Los envíos se agregan en tiempo real al dataset y actualizan los KPIs

## Esquema de datos (DENUNCIAS)

Campos: id_denuncia, timestamp, tipo_denunciante, departamento, ciudad_localidad, referencia_lugar, url_mapa, latitud, longitud, categoria_codigo (CAT_01–CAT_09), categoria_label, subcategoria, descripcion_libre, fecha_hecho, recurrencia, urgencia, denuncia_previa, organismo_previo, adjunto_url, fuente, año, mes, trimestre, semana_año, dia_semana, hora, mes_nombre

## Categorías ambientales

| Código | Categoría | Subcategorías |
|--------|-----------|--------------|
| CAT_01 | Fauna silvestre | 5 |
| CAT_02 | Costa y faja costera | 6 |
| CAT_03 | Contaminación del aire | 5 |
| CAT_04 | Contaminación del agua | 9 |
| CAT_05 | Residuos y basura | 6 |
| CAT_06 | Flora y vegetación | 3 |
| CAT_07 | Contaminación sonora | 3 |
| CAT_08 | Extracción y actividades productivas | 3 |
| CAT_09 | Otro problema ambiental | 4 |

## Extensiones pendientes (fases futuras)

- Integración con Google Sheets via gspread (pipeline ETL en tiempo real)
- Geocodificación automática desde URL Maps (regex + Google Maps API)
- Pronósticos con Prophet (requiere ≥ 2 años datos continuos)
- Clasificador NLP TF-IDF + Regresión Logística
- Autenticación básica para secciones diagnóstico / predictivo
- Exportar datos a Parquet/CSV
