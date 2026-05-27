from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.layouts import charts
from data.generator import CATEGORIAS


def render(df):
    return html.Div([
        html.Div([
            html.Span("Sección 3", className="section-badge"),
            html.H2("Análisis Predictivo", className="section-title"),
            html.P("¿Qué va a pasar? · Pronósticos · Clasificación automática · Alertas", className="section-desc"),
        ]),
        dbc.Tabs([
            dbc.Tab(label="📊 Pronósticos", tab_id="tab-forecast"),
            dbc.Tab(label="🔤 Texto & NLP", tab_id="tab-nlp"),
            dbc.Tab(label="🚨 Alertas", tab_id="tab-alertas"),
            dbc.Tab(label="🗂️ Clustering territorial", tab_id="tab-clustering"),
        ], id="pred-tabs", active_tab="tab-forecast", className="custom-tabs mb-3"),
        html.Div(id="pred-tab-content"),
    ], className="content-area")


def render_forecast(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Pronóstico de volumen total — próximos 12 meses", className="chart-title"),
                dcc.Graph(figure=charts.fig_forecast_simple(df), config={"displayModeBar": False}),
                html.Div("Modelo de tendencia polinómica con banda de confianza al 95%. "
                         "Para predicciones robustas se requieren ≥ 2 años de datos continuos.",
                         style={"fontSize": "11px", "color": "#8b949e", "marginTop": "8px"}),
            ], className="chart-card")),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(_forecast_by_cat(df), md=12),
        ], className="g-3"),
    ])


def _forecast_by_cat(df):
    import pandas as pd
    import numpy as np
    cats = df["categoria_codigo"].value_counts().head(4).index.tolist()
    cols = []
    for cat in cats:
        sub = df[df["categoria_codigo"] == cat]
        monthly = sub.groupby(sub["timestamp"].dt.to_period("M")).size().reset_index(name="total")
        monthly["fecha"] = monthly["timestamp"].dt.to_timestamp()
        label = CATEGORIAS[cat]["label"]
        color = CATEGORIAS[cat]["color"]

        if len(monthly) < 4:
            continue
        x = np.arange(len(monthly))
        y = monthly["total"].values
        coeffs = np.polyfit(x, y, 1)
        trend = "↑" if coeffs[0] > 0.1 else ("↓" if coeffs[0] < -0.1 else "→")
        trend_color = "#f85149" if trend == "↑" else ("#3fb950" if trend == "↓" else "#8b949e")

        cols.append(dbc.Col(html.Div([
            html.Div(label, style={"fontSize": "11px", "color": "#8b949e", "marginBottom": "4px",
                                   "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            html.Div([
                html.Span(f"{monthly['total'].iloc[-1]}", style={"fontSize": "22px", "fontWeight": "700",
                                                                  "color": "#e6edf3"}),
                html.Span(f" {trend}", style={"fontSize": "18px", "color": trend_color, "marginLeft": "6px"}),
            ]),
            html.Div("último mes registrado", style={"fontSize": "10px", "color": "#484f58"}),
        ], className="chart-card"), md=3))

    return dbc.Row(cols, className="g-3")


def render_nlp(df):
    cat_opts = [{"label": v["label"], "value": k} for k, v in CATEGORIAS.items()]
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    "Top 15 términos más frecuentes · filtro: ",
                    dcc.Dropdown(
                        options=[{"label": "Todas las categorías", "value": "all"}] + cat_opts,
                        value="all", id="nlp-cat-filter", clearable=False,
                        style={"display": "inline-block", "width": "220px",
                               "verticalAlign": "middle", "fontSize": "12px"}
                    ),
                ], className="chart-title"),
                dcc.Graph(id="fig-top-palabras", config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Distribución de denuncias nuevas vs históricas", className="chart-title"),
                dcc.Graph(figure=_fig_fuente(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("🤖 Clasificación automática de texto (próximamente)", className="chart-title"),
                html.Div([
                    html.P("El módulo NLP con TF-IDF + Regresión Logística clasificará automáticamente "
                           "las descripciones libres del formulario en categorías del catálogo.",
                           style={"color": "#8b949e", "fontSize": "13px"}),
                    html.P("Requerimientos: mínimo 200 registros con descripción libre. "
                           "Estado: pendiente de datos suficientes.",
                           style={"color": "#484f58", "fontSize": "12px"}),
                ]),
            ], className="chart-card")),
        ], className="g-3"),
    ])


def _fig_fuente(df):
    import plotly.graph_objects as go
    counts = df["fuente"].value_counts() if "fuente" in df.columns else {"historico": len(df)}
    labels = {"historico": "Histórico 2010-2023", "formulario": "Vía formulario (nuevas)"}
    fig = go.Figure(go.Pie(
        labels=[labels.get(k, k) for k in counts.index],
        values=counts.values,
        hole=0.55,
        marker_colors=["#58a6ff", "#1abc9c"],
        textfont={"color": "#e6edf3"},
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font={"color": "#e6edf3"}, height=300,
                      legend={"font": {"color": "#8b949e"}})
    return fig


def render_alertas(df):
    import pandas as pd
    import numpy as np

    monthly = df.groupby(df["timestamp"].dt.to_period("M")).size()
    if len(monthly) >= 3:
        zscore_last = (monthly.iloc[-1] - monthly.mean()) / monthly.std()
        pico = zscore_last > 2.0
    else:
        zscore_last, pico = 0, False

    urg_72h = df[df["timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]["urgencia"].sum()
    new_combos = len(df[df["fuente"] == "formulario"]) if "fuente" in df.columns else 0

    alerts = [
        {
            "icon": "🔴" if pico else "🟢",
            "title": "Pico anómalo de denuncias",
            "desc": f"Z-score último mes: {zscore_last:.2f}. {'⚠️ Por encima del umbral (>2.0)' if pico else 'Dentro del rango normal.'}",
            "color": "#f85149" if pico else "#3fb950",
        },
        {
            "icon": "🟡" if urg_72h >= 5 else "🟢",
            "title": "Denuncias urgentes recientes",
            "desc": f"{int(urg_72h)} denuncias urgentes en los últimos 30 días. {'⚠️ Revisar.' if urg_72h >= 5 else 'Nivel normal.'}",
            "color": "#f1c40f" if urg_72h >= 5 else "#3fb950",
        },
        {
            "icon": "🔵",
            "title": "Nuevas denuncias vía formulario",
            "desc": f"{new_combos} registros ingresados por el formulario web integrado.",
            "color": "#58a6ff",
        },
    ]

    cards = []
    for a in alerts:
        cards.append(dbc.Col(html.Div([
            html.Div([
                html.Span(a["icon"], style={"fontSize": "22px", "marginRight": "10px"}),
                html.Span(a["title"], style={"fontSize": "14px", "fontWeight": "600",
                                              "color": a["color"]}),
            ], style={"marginBottom": "8px"}),
            html.P(a["desc"], style={"color": "#8b949e", "fontSize": "13px", "margin": 0}),
        ], className="chart-card"), md=4))

    return html.Div([
        dbc.Row(cards, className="g-3 mb-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Configuración de umbrales de alerta", className="chart-title"),
                html.Div([
                    html.P("Los umbrales son configurables según las necesidades del equipo:",
                           style={"color": "#8b949e", "fontSize": "13px", "marginBottom": "12px"}),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Alerta"), html.Th("Método"), html.Th("Umbral"),
                        ])),
                        html.Tbody([
                            html.Tr([html.Td("Pico anómalo"), html.Td("Z-score 7 días"), html.Td("> 2.5")]),
                            html.Tr([html.Td("Crecimiento estructural"), html.Td("Ruptures / PELT"), html.Td("p < 0.05")]),
                            html.Tr([html.Td("Nueva combinación dpto+subcat"), html.Td("Detección novedad"), html.Td("1er registro")]),
                            html.Tr([html.Td("Urgentes acumuladas"), html.Td("Conteo 72h"), html.Td("≥ 5 registros")]),
                        ]),
                    ], className="dep-table"),
                ]),
            ], className="chart-card")),
        ], className="g-3"),
    ])


def render_clustering(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Clustering K-Means de departamentos por perfil ambiental", className="chart-title"),
                dcc.Graph(figure=charts.fig_clustering_depts(df), config={"displayModeBar": False}),
                html.Div("Departamentos con perfil ambiental similar se agrupan en el mismo cluster "
                         "(K-Means, k=4, normalizado por total de denuncias).",
                         style={"fontSize": "11px", "color": "#8b949e", "marginTop": "8px"}),
            ], className="chart-card")),
        ], className="g-3"),
    ])
