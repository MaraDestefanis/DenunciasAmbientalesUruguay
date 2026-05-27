from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.layouts import charts
from data.generator import DEPARTAMENTOS


def render(df):
    return html.Div([
        html.Div([
            html.Span("Sección 2", className="section-badge"),
            html.H2("Análisis de Diagnóstico", className="section-title"),
            html.P("¿Por qué ocurre? · Patrones latentes · Correlaciones · Anomalías", className="section-desc"),
        ]),
        dbc.Tabs([
            dbc.Tab(label="🔗 Correlaciones", tab_id="tab-correlaciones"),
            dbc.Tab(label="⚠️ Anomalías", tab_id="tab-anomalias"),
            dbc.Tab(label="🎯 Triage", tab_id="tab-triage"),
        ], id="diag-tabs", active_tab="tab-correlaciones", className="custom-tabs mb-3"),
        html.Div(id="diag-tab-content"),
    ], className="content-area")


def render_correlaciones(df):
    dept_opts = [{"label": d, "value": d} for d in sorted(DEPARTAMENTOS)]
    default_dept = "Montevideo"
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Correlación motivo × departamento (heatmap)", className="chart-title"),
                dcc.Graph(figure=charts.fig_heatmap_correlacion(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=7),
            dbc.Col(html.Div([
                html.Div([
                    "Perfil ambiental — radar · ",
                    dcc.Dropdown(options=dept_opts, value=default_dept, id="radar-dept-filter",
                                 clearable=False,
                                 style={"display": "inline-block", "width": "160px",
                                        "verticalAlign": "middle", "fontSize": "12px"}),
                ], className="chart-title"),
                dcc.Graph(id="fig-radar-dept", config={"displayModeBar": False}),
            ], className="chart-card"), md=5),
        ], className="g-3"),
    ])


def render_anomalias(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Detección de anomalías temporales (Z-score)", className="chart-title"),
                dcc.Graph(figure=charts.fig_anomalias_zscore(df), config={"displayModeBar": False}),
                html.Div(
                    "Los puntos rojos (diamante) indican meses con desviación estándar > 1.8 respecto a la media histórica.",
                    style={"fontSize": "11px", "color": "#8b949e", "marginTop": "8px"}
                ),
            ], className="chart-card")),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(_render_alert_box(df), md=12),
        ], className="g-3"),
    ])


def _render_alert_box(df):
    import pandas as pd
    import numpy as np
    monthly = df.groupby(df["timestamp"].dt.to_period("M")).size()
    if len(monthly) < 3:
        return html.Div()
    zscore = (monthly - monthly.mean()) / monthly.std()
    anomalos = zscore[zscore.abs() > 1.8]

    items = []
    for period, z in anomalos.tail(5).items():
        tipo = "📈 Pico" if z > 0 else "📉 Caída"
        color = "#f85149" if z > 0 else "#58a6ff"
        items.append(html.Div([
            html.Span(f"{tipo} ", style={"color": color, "fontWeight": "700"}),
            html.Span(f"{str(period)}: Z-score = {z:.2f}", style={"color": "#e6edf3"}),
        ], style={"marginBottom": "6px", "fontSize": "13px"}))

    return html.Div([
        html.Div("Anomalías detectadas (últimos períodos)", className="chart-title"),
        html.Div(items if items else html.Div("No se detectaron anomalías significativas.",
                                               style={"color": "#8b949e", "fontSize": "13px"})),
    ], className="chart-card")


def render_triage(df):
    import pandas as pd
    agg = (df.groupby(["departamento", "categoria_label"])
           .agg(total=("id_denuncia", "count"),
                pct_urgente=("urgencia", "mean"),
                pct_permanente=("recurrencia", lambda x: (x == "Permanente").mean()))
           .reset_index())
    agg["score_riesgo"] = ((agg["total"] / agg["total"].max() * 40) +
                           (agg["pct_urgente"] * 35) +
                           (agg["pct_permanente"] * 25)).round(1)
    top = agg.nlargest(15, "score_riesgo")

    def semaforo(s):
        if s >= 60: return "🔴"
        if s >= 35: return "🟡"
        return "🟢"

    rows = []
    for _, row in top.iterrows():
        rows.append(html.Tr([
            html.Td(f"{semaforo(row['score_riesgo'])} {row['score_riesgo']:.0f}",
                    style={"fontWeight": "700", "color": "#e6edf3"}),
            html.Td(row["departamento"]),
            html.Td(row["categoria_label"]),
            html.Td(f"{row['total']:,}"),
            html.Td(f"{row['pct_urgente']*100:.0f}%"),
            html.Td(f"{row['pct_permanente']*100:.0f}%"),
        ]))

    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Matriz urgencia × recurrencia", className="chart-title"),
                dcc.Graph(figure=charts.fig_matriz_triage(df), config={"displayModeBar": False}),
                html.Div("Cuadrante urgente + permanente = prioridad máxima.",
                         style={"fontSize": "11px", "color": "#8b949e", "marginTop": "8px"}),
            ], className="chart-card"), md=5),
            dbc.Col(html.Div([
                html.Div("Score de riesgo ambiental — Top 15 combinaciones", className="chart-title"),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Score"), html.Th("Departamento"), html.Th("Categoría"),
                        html.Th("Denuncias"), html.Th("% Urgente"), html.Th("% Permanente"),
                    ])),
                    html.Tbody(rows),
                ], className="dep-table"),
            ], className="chart-card"), md=7),
        ], className="g-3"),
    ], className="content-area" if False else "")
