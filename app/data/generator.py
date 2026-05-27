"""
Carga del dataset de denuncias ambientales — D Empathy Project · Uruguay.

Antes este módulo generaba datos sintéticos. Ahora carga el dataset REAL
producido por el notebook 01 (data/denuncias.parquet), que combina:
  - Denuncias 2010-2019 del Ministerio de Ambiente (3.007 filas)
  - Denuncias 2023 del Ministerio de Ambiente (1.239 filas)
Fuente original: catalogodatos.gub.uy (Ministerio de Ambiente, Uruguay).

Mantengo el mismo API (`get_data`, `add_new_record`, constantes `CATEGORIAS`,
`DEPARTAMENTOS`, etc.) que esperan los módulos del tablero, así no hay que
tocar nada más.
"""
import pandas as pd
from pathlib import Path

# Constantes que el resto del código del tablero importa de este modulo
DEPARTAMENTOS = [
    "Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno",
    "Flores", "Florida", "Lavalleja", "Maldonado", "Montevideo",
    "Paysandú", "Río Negro", "Rivera", "Rocha", "Salto",
    "San José", "Soriano", "Tacuarembó", "Treinta y Tres"
]

CATEGORIAS = {
    "CAT_01": {"label": "Fauna silvestre", "color": "#2d6a4f", "subcategorias": [
        "Caza, tenencia o venta ilegal de fauna",
        "Tala de monte nativo / especies autóctonas",
        "Afectación de humedales o áreas ecosistémicas",
        "Actividades no autorizadas en áreas protegidas",
        "Otro",
    ]},
    "CAT_02": {"label": "Costa y faja costera", "color": "#1b4f72", "subcategorias": [
        "Construcción irregular en faja costera",
        "Extracción de minerales en faja costera",
        "Vehículos en faja costera",
        "Afectación de humedales costeros",
        "Incumplimiento faja de amortiguación (Laguna del Sauce / Río Sta. Lucía)",
        "Otro",
    ]},
    "CAT_03": {"label": "Contaminación del aire", "color": "#5d6d7e", "subcategorias": [
        "Olores molestos — industrias / feedlots / vertederos",
        "Olores molestos — comercios o residencias",
        "Emisiones de chimenea / polvo / material particulado (industrias)",
        "Emisiones de chimenea — hoteles / residencias / comercios",
        "Otro",
    ]},
    "CAT_04": {"label": "Contaminación del agua", "color": "#2e86c1", "subcategorias": [
        "Vertido de efluentes industriales",
        "Vertido de efluentes — comercios o residencias",
        "Vertido de efluentes de saneamiento (cooperativas, MEVIR, etc.)",
        "Vertido de barométricas",
        "Contaminación por agroquímicos",
        "Mortandad de peces",
        "Presencia de cianobacterias",
        "Extracción de minerales en álveo de curso de agua",
        "Otro",
    ]},
    "CAT_05": {"label": "Residuos y basura", "color": "#e67e22", "subcategorias": [
        "Residuos asimilables a urbanos (basura doméstica)",
        "Residuos industriales, especiales u otros",
        "Envases de plaguicidas",
        "Bolsas plásticas",
        "Almacenamiento o derrame de sustancias químicas",
        "Otro",
    ]},
    "CAT_06": {"label": "Flora y vegetación", "color": "#27ae60", "subcategorias": [
        "Afectación de humedales o áreas de interés ecosistémico",
        "Tala o daño de monte nativo",
        "Otro",
    ]},
    "CAT_07": {"label": "Contaminación sonora", "color": "#f1c40f", "subcategorias": [
        "Ruidos de industrias",
        "Ruidos de comercios o residencias",
        "Otro tipo de ruido",
    ]},
    "CAT_08": {"label": "Extracción y act. productivas", "color": "#8b6914", "subcategorias": [
        "Extracción de minerales (canteras / área fiscal)",
        "Extracción de horizontes de suelo",
        "Otro tipo de extracción",
    ]},
    "CAT_09": {"label": "Otro problema ambiental", "color": "#7f8c8d", "subcategorias": [
        "Incumplimiento de autorizaciones ambientales",
        "Sustancias peligrosas",
        "Actividades no autorizadas en áreas protegidas",
        "Otro (especificar en descripción libre)",
    ]},
}

TIPO_DENUNCIANTE = ["Persona", "Organización", "Anónimo"]
RECURRENCIA      = ["Puntual", "Recurrente", "Permanente"]
ORGANISMOS       = ["DINAMA", "Intendencia", "Policía", "Otro"]

HERE = Path(__file__).resolve().parent
DATASET_PATH = HERE / "denuncias.parquet"


def _get_hist() -> pd.DataFrame:
    """Carga el dataset histórico real desde parquet. Cachea en memoria."""
    if not hasattr(_get_hist, "_cache"):
        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                f"No encontré {DATASET_PATH}. "
                f"Corré el notebook `notebooks/01_transformacion_datos.ipynb` "
                f"para generarlo a partir de los Excel oficiales."
            )
        _get_hist._cache = pd.read_parquet(DATASET_PATH)
    return _get_hist._cache.copy()


def get_data() -> pd.DataFrame:
    """Devuelve histórico real + denuncias persistidas en la base."""
    from data.db import load_denuncias
    hist = _get_hist()
    db_rows = load_denuncias()
    if db_rows.empty:
        return hist
    # Aliando columnas: las del formulario pueden no traer todas las del histórico
    for col in hist.columns:
        if col not in db_rows.columns:
            db_rows[col] = pd.NA
    db_rows = db_rows[hist.columns]
    combined = pd.concat([hist, db_rows], ignore_index=True)
    combined.sort_values("timestamp", inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


def add_new_record(record: dict) -> pd.DataFrame:
    """Persiste una denuncia nueva del formulario y devuelve el dataset completo."""
    from data.db import save_denuncia
    save_denuncia(record)
    return get_data()
