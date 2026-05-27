import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

DEPARTAMENTOS = [
    "Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno",
    "Flores", "Florida", "Lavalleja", "Maldonado", "Montevideo",
    "Paysandú", "Río Negro", "Rivera", "Rocha", "Salto",
    "San José", "Soriano", "Tacuarembó", "Treinta y Tres"
]

CATEGORIAS = {
    "CAT_01": {"label": "Fauna silvestre", "color": "#2d6a4f", "subcategorias": [
        "Caza furtiva", "Tráfico de especies", "Destrucción de hábitat", "Abandono de animales", "Envenenamiento"
    ]},
    "CAT_02": {"label": "Costa y faja costera", "color": "#1b4f72", "subcategorias": [
        "Construcción ilegal", "Erosión costera", "Contaminación de playas", "Pesca ilegal", "Vertido al mar", "Daño a médanos"
    ]},
    "CAT_03": {"label": "Contaminación del aire", "color": "#5d6d7e", "subcategorias": [
        "Quema a cielo abierto", "Emisiones industriales", "Olores nauseabundos", "Humo de vehículos", "Polvo industrial"
    ]},
    "CAT_04": {"label": "Contaminación del agua", "color": "#2e86c1", "subcategorias": [
        "Vertidos industriales", "Cianobacterias", "Contaminación de arroyos", "Aguas residuales", 
        "Contaminación de pozos", "Basura en agua", "Derrames de combustible", "Agrotóxicos", "Eutrofización"
    ]},
    "CAT_05": {"label": "Residuos y basura", "color": "#e67e22", "subcategorias": [
        "Basural clandestino", "Residuos peligrosos", "Escombros", "Residuos electrónicos", "Microbasurales", "Quema de residuos"
    ]},
    "CAT_06": {"label": "Flora y vegetación", "color": "#27ae60", "subcategorias": [
        "Tala ilegal", "Quema de pastizales", "Invasión de especies exóticas"
    ]},
    "CAT_07": {"label": "Contaminación sonora", "color": "#f1c40f", "subcategorias": [
        "Ruido industrial", "Ruido nocturno", "Ruido vehicular"
    ]},
    "CAT_08": {"label": "Extracción y actividades productivas", "color": "#8b6914", "subcategorias": [
        "Minería ilegal", "Extracción de áridos", "Actividad agropecuaria irregular"
    ]},
    "CAT_09": {"label": "Otro problema ambiental", "color": "#7f8c8d", "subcategorias": [
        "Problema no categorizado", "Daño a espacio público", "Contaminación lumínica", "Otro"
    ]},
}

TIPO_DENUNCIANTE = ["Persona", "Organización", "Anónimo"]
RECURRENCIA = ["Puntual", "Recurrente", "Permanente"]
ORGANISMOS = ["DINAMA", "Intendencia", "Policía", "Otro"]


def _seasonal_weight(date):
    month = date.month
    base = 1.0
    if month in [1, 2]: base = 1.4
    elif month in [6, 7]: base = 0.7
    elif month in [11, 12]: base = 1.2
    return base


def _cat_monthly_bias(cat_code, month):
    biases = {
        "CAT_04": {1: 1.8, 2: 2.0, 12: 1.5},
        "CAT_07": {12: 2.0, 1: 1.8, 2: 1.6},
        "CAT_02": {1: 1.6, 2: 1.7, 12: 1.4},
        "CAT_05": {6: 1.3, 7: 1.4, 8: 1.2},
    }
    return biases.get(cat_code, {}).get(month, 1.0)


def _dept_cat_bias(dept, cat_code):
    biases = {
        "Montevideo": {"CAT_07": 2.5, "CAT_03": 2.0, "CAT_05": 1.8},
        "Canelones": {"CAT_05": 1.6, "CAT_04": 1.4},
        "Maldonado": {"CAT_02": 2.2, "CAT_04": 1.5},
        "Rocha": {"CAT_02": 1.8, "CAT_01": 1.5},
        "Salto": {"CAT_04": 1.6, "CAT_08": 1.4},
        "Colonia": {"CAT_04": 1.5, "CAT_08": 1.3},
    }
    return biases.get(dept, {}).get(cat_code, 1.0)


def generate_historical_data(n=4281, seed=42):
    rng = np.random.default_rng(seed)
    random.seed(seed)

    # Períodos reales: 2010-2019 (histórico), pausa 2020-2022, retoma 2023
    def _random_dates(start, end, count):
        span = (end - start).days
        return [start + timedelta(days=int(rng.integers(0, span))) for _ in range(count)]

    dates_historico = _random_dates(datetime(2010, 1, 1), datetime(2019, 12, 31), 3800)
    dates_2023      = _random_dates(datetime(2023, 1, 1), datetime(2023, 12, 31),  481)

    all_dates = dates_historico + dates_2023
    rng.shuffle(all_dates)
    all_dates = all_dates[:n]

    records = []
    cat_codes = list(CATEGORIAS.keys())
    cat_weights_base = [0.08, 0.10, 0.10, 0.18, 0.20, 0.08, 0.10, 0.08, 0.08]

    for i, ts in enumerate(all_dates):
        dept = rng.choice(DEPARTAMENTOS, p=_dept_weights())
        cat_weights = []
        for j, code in enumerate(cat_codes):
            w = cat_weights_base[j] * _seasonal_weight(ts) * _cat_monthly_bias(code, ts.month) * _dept_cat_bias(dept, code)
            cat_weights.append(w)
        total_w = sum(cat_weights)
        cat_weights = [w / total_w for w in cat_weights]
        cat_code = rng.choice(cat_codes, p=cat_weights)
        cat = CATEGORIAS[cat_code]
        subcat = rng.choice(cat["subcategorias"])
        urgency = bool(rng.random() < 0.15)
        prev = bool(rng.random() < 0.25)

        records.append({
            "id_denuncia": f"URY-{ts.year}-{i+1:04d}",
            "timestamp": ts + timedelta(hours=int(rng.integers(6, 22)), minutes=int(rng.integers(0, 60))),
            "tipo_denunciante": rng.choice(TIPO_DENUNCIANTE, p=[0.60, 0.15, 0.25]),
            "departamento": dept,
            "ciudad_localidad": _random_city(dept, rng),
            "categoria_codigo": cat_code,
            "categoria_label": cat["label"],
            "subcategoria": subcat,
            "fecha_hecho": ts - timedelta(days=int(rng.integers(0, 30))),
            "recurrencia": rng.choice(RECURRENCIA, p=[0.45, 0.35, 0.20]),
            "urgencia": urgency,
            "denuncia_previa": prev,
            "organismo_previo": rng.choice(ORGANISMOS) if prev else None,
            "latitud": _lat_for_dept(dept, rng),
            "longitud": _lon_for_dept(dept, rng),
            "fuente": "historico",
        })

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["fecha_hecho"] = pd.to_datetime(df["fecha_hecho"])
    df["año"] = df["timestamp"].dt.year
    df["mes"] = df["timestamp"].dt.month
    df["trimestre"] = df["timestamp"].dt.quarter
    df["semana_año"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["dia_semana"] = df["timestamp"].dt.dayofweek
    df["hora"] = df["timestamp"].dt.hour
    df["mes_nombre"] = df["timestamp"].dt.strftime("%b")
    return df.sort_values("timestamp").reset_index(drop=True)


def _dept_weights():
    weights = {
        "Artigas": 0.03, "Canelones": 0.12, "Cerro Largo": 0.03,
        "Colonia": 0.06, "Durazno": 0.03, "Flores": 0.02,
        "Florida": 0.03, "Lavalleja": 0.03, "Maldonado": 0.08,
        "Montevideo": 0.25, "Paysandú": 0.05, "Río Negro": 0.03,
        "Rivera": 0.04, "Rocha": 0.04, "Salto": 0.06,
        "San José": 0.05, "Soriano": 0.03, "Tacuarembó": 0.04,
        "Treinta y Tres": 0.03,
    }
    vals = [weights[d] for d in DEPARTAMENTOS]
    total = sum(vals)
    return [v / total for v in vals]


def _random_city(dept, rng):
    cities = {
        "Montevideo": ["Montevideo", "Pocitos", "Punta Carretas", "La Blanqueada", "Peñarol"],
        "Canelones": ["Las Piedras", "La Paz", "Pando", "Atlántida", "Canelones"],
        "Maldonado": ["Maldonado", "Punta del Este", "San Carlos", "Pan de Azúcar"],
        "Salto": ["Salto", "Constitución", "Belén"],
        "Colonia": ["Colonia del Sacramento", "Carmelo", "Nueva Helvecia"],
    }
    default = [dept]
    return str(rng.choice(cities.get(dept, default)))


DEPT_COORDS = {
    "Artigas": (-30.4, -56.5), "Canelones": (-34.5, -56.0), "Cerro Largo": (-32.4, -54.2),
    "Colonia": (-34.0, -57.8), "Durazno": (-33.4, -56.5), "Flores": (-33.6, -56.9),
    "Florida": (-34.1, -56.2), "Lavalleja": (-34.4, -55.2), "Maldonado": (-34.9, -54.9),
    "Montevideo": (-34.9, -56.2), "Paysandú": (-32.3, -58.1), "Río Negro": (-32.9, -57.9),
    "Rivera": (-31.0, -55.6), "Rocha": (-34.5, -54.3), "Salto": (-31.4, -57.9),
    "San José": (-34.3, -56.7), "Soriano": (-33.5, -57.8), "Tacuarembó": (-31.7, -56.0),
    "Treinta y Tres": (-33.2, -54.4),
}


def _lat_for_dept(dept, rng):
    base_lat, _ = DEPT_COORDS.get(dept, (-33.0, -56.0))
    return round(float(base_lat + rng.normal(0, 0.3)), 4)


def _lon_for_dept(dept, rng):
    _, base_lon = DEPT_COORDS.get(dept, (-33.0, -56.0))
    return round(float(base_lon + rng.normal(0, 0.3)), 4)


_hist_df = None   # Historical synthetic data — generated once, never changes


def _get_hist():
    global _hist_df
    if _hist_df is None:
        _hist_df = generate_historical_data()
    return _hist_df


def get_data() -> pd.DataFrame:
    """Return historical + all persisted form submissions from the DB."""
    from data.db import load_denuncias
    hist = _get_hist()
    db_rows = load_denuncias()
    if db_rows.empty:
        return hist.copy()
    combined = pd.concat([hist, db_rows], ignore_index=True)
    combined.sort_values("timestamp", inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


def add_new_record(record: dict) -> pd.DataFrame:
    """Persist a new citizen complaint to the database."""
    from data.db import save_denuncia
    save_denuncia(record)
    return get_data()
