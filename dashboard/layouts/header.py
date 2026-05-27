from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime


def render_header():
    return html.Div([
        html.Div([
            html.Div([
                html.Div("🌿", className="dep-logo-badge"),
                html.Div([
                    html.Div("D Empathy Project", className="dep-title"),
                    html.Div("Sistema de Denuncias Ambientales · Uruguay", className="dep-subtitle"),
                ]),
                html.Div([
                    html.Div(className="dep-live-dot"),
                    html.Span("En vivo"),
                ], className="dep-live-badge"),
                html.Button(
                    "📩 Ingresa tu denuncia",
                    id="btn-nueva-denuncia-header",
                    n_clicks=0,
                    className="btn-nueva-header",
                ),
            ], className="dep-logo-row"),
        ]),
    ], className="dep-header")


def render_kpis(df: pd.DataFrame):
    now = datetime.now()
    total = len(df)
    mes_actual = len(df[
        (df["timestamp"].dt.year == now.year) &
        (df["timestamp"].dt.month == now.month)
    ])

    last_30 = df[df["timestamp"] >= pd.Timestamp.now() - pd.DateOffset(days=30)]
    cat_freq = (last_30["categoria_label"].value_counts().index[0]
                if len(last_30) > 0
                else df["categoria_label"].value_counts().index[0])

    dept_year = df[df["timestamp"].dt.year == now.year]["departamento"].value_counts()
    dept_top = dept_year.index[0] if len(dept_year) > 0 else df["departamento"].value_counts().index[0]

    return html.Div([
        _kpi_card("Total denuncias", f"{total:,}", "Histórico + nuevas", "🗂️", "kpi-green"),
        _kpi_card("Este mes", str(mes_actual), now.strftime("%B %Y"), "📅", "kpi-blue"),
        _kpi_card("Cat. más frecuente", cat_freq, "Últimos 30 días", "🏷️", "kpi-orange"),
        _kpi_card("Depto. líder", dept_top, f"Año {now.year}", "📍", "kpi-purple"),
    ], className="kpi-bar", id="kpi-bar")


def _kpi_card(label, value, sub, icon, color_class):
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div(value, className="kpi-value"),
        html.Div(sub, className="kpi-sub"),
        html.Div(icon, className="kpi-icon"),
    ], className=f"kpi-card {color_class}")
