import os
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create the denuncias table if it doesn't exist. Called at app startup."""
    sql = """
        CREATE TABLE IF NOT EXISTS denuncias (
            id SERIAL PRIMARY KEY,
            id_denuncia VARCHAR(30) UNIQUE NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            tipo_denunciante VARCHAR(50),
            departamento VARCHAR(50),
            ciudad_localidad VARCHAR(100),
            referencia_lugar TEXT,
            url_mapa TEXT,
            latitud DOUBLE PRECISION,
            longitud DOUBLE PRECISION,
            categoria_codigo VARCHAR(10),
            categoria_label VARCHAR(100),
            subcategoria VARCHAR(100),
            descripcion_libre TEXT,
            fecha_hecho DATE,
            recurrencia VARCHAR(20),
            urgencia BOOLEAN DEFAULT FALSE,
            denuncia_previa BOOLEAN DEFAULT FALSE,
            organismo_previo VARCHAR(100),
            adjunto_url TEXT,
            fuente VARCHAR(20) DEFAULT 'formulario',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print("[db] Table 'denuncias' ready.")
    except Exception as e:
        print(f"[db] init_db error: {e}")


def save_denuncia(record: dict):
    sql = """
        INSERT INTO denuncias (
            id_denuncia, timestamp, tipo_denunciante, departamento,
            ciudad_localidad, referencia_lugar, url_mapa, latitud, longitud,
            categoria_codigo, categoria_label, subcategoria, descripcion_libre,
            fecha_hecho, recurrencia, urgencia, denuncia_previa, organismo_previo,
            adjunto_url, fuente
        ) VALUES (
            %(id_denuncia)s, %(timestamp)s, %(tipo_denunciante)s, %(departamento)s,
            %(ciudad_localidad)s, %(referencia_lugar)s, %(url_mapa)s, %(latitud)s, %(longitud)s,
            %(categoria_codigo)s, %(categoria_label)s, %(subcategoria)s, %(descripcion_libre)s,
            %(fecha_hecho)s, %(recurrencia)s, %(urgencia)s, %(denuncia_previa)s, %(organismo_previo)s,
            %(adjunto_url)s, %(fuente)s
        )
        ON CONFLICT (id_denuncia) DO NOTHING
    """
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, record)
    except Exception as e:
        print(f"[db] Error saving denuncia: {e}")


_COLS = [
    "id_denuncia", "timestamp", "tipo_denunciante", "departamento",
    "ciudad_localidad", "referencia_lugar", "url_mapa", "latitud", "longitud",
    "categoria_codigo", "categoria_label", "subcategoria", "descripcion_libre",
    "fecha_hecho", "recurrencia", "urgencia", "denuncia_previa", "organismo_previo",
    "adjunto_url", "fuente",
]


def load_denuncias() -> pd.DataFrame:
    sql = f"""
        SELECT {', '.join(_COLS)}
        FROM denuncias
        ORDER BY timestamp ASC
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        if not rows:
            return pd.DataFrame(columns=_COLS)
        df = pd.DataFrame([dict(r) for r in rows], columns=_COLS)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_localize(None)
        df["fecha_hecho"] = pd.to_datetime(df["fecha_hecho"])
        df["año"] = df["timestamp"].dt.year
        df["mes"] = df["timestamp"].dt.month
        df["trimestre"] = df["timestamp"].dt.quarter
        df["semana_año"] = df["timestamp"].dt.isocalendar().week.astype(int)
        df["dia_semana"] = df["timestamp"].dt.dayofweek
        df["hora"] = df["timestamp"].dt.hour
        df["mes_nombre"] = df["timestamp"].dt.strftime("%b")
        return df
    except Exception as e:
        print(f"[db] Error loading denuncias: {e}")
        return pd.DataFrame(columns=_COLS)


def count_denuncias() -> int:
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM denuncias")
                return cur.fetchone()[0]
    except Exception as e:
        print(f"[db] Error counting: {e}")
        return 0
