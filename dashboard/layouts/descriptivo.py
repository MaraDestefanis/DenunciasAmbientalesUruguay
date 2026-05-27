from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard.layouts import charts


def render(df):
    return html.Div([
        html.Div([
            html.Span("Sección 1", className="section-badge"),
            html.H2("Análisis Descriptivo", className="section-title"),
            html.P("¿Qué está pasando? · ¿Cuánto? · ¿Dónde? · ¿Cuándo?", className="section-desc"),
        ]),

        dbc.Tabs([
            dbc.Tab(label="📈 Temporal", tab_id="tab-temporal"),
            dbc.Tab(label="🏷️ Categorías", tab_id="tab-categorias"),
            dbc.Tab(label="🗺️ Geográfico", tab_id="tab-geografico"),
            dbc.Tab(label="👤 Perfil denunciante", tab_id="tab-perfil"),
        ], id="desc-tabs", active_tab="tab-temporal",
           className="custom-tabs mb-3"),

        html.Div(id="desc-tab-content"),
    ], className="content-area")


def render_temporal(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Evolución anual de denuncias", className="chart-title"),
                dcc.Graph(figure=charts.fig_evolucion_anual(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Tendencia mensual con media móvil", className="chart-title"),
                dcc.Graph(figure=charts.fig_tendencia_mensual(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
    ])


def render_categorias(df):
    from data.generator import CATEGORIAS
    cat_opts = [{"label": v["label"], "value": k} for k, v in CATEGORIAS.items()]
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Distribución jerárquica: Treemap", className="chart-title"),
                dcc.Graph(figure=charts.fig_treemap(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Jerarquía categoría → subcategoría: Sunburst", className="chart-title"),
                dcc.Graph(figure=charts.fig_sunburst(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div([
                    "Top subcategorías ",
                    dcc.Dropdown(
                        options=[{"label": "Todas", "value": "all"}] + cat_opts,
                        value="all", id="subcat-filter",
                        clearable=False, style={"display": "inline-block", "width": "220px",
                                                "verticalAlign": "middle", "fontSize": "12px"}
                    ),
                ], className="chart-title"),
                dcc.Graph(id="fig-ranking-subcats", config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Evolución mensual por categoría (área apilada)", className="chart-title"),
                dcc.Graph(figure=charts.fig_area_mensual_cat(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
    ])


def render_geografico(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Mapa de burbujas por departamento", className="chart-title"),
                dcc.Graph(figure=charts.fig_mapa_coropletico(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
            dbc.Col(html.Div([
                html.Div("Puntos de denuncia geolocalizados", className="chart-title"),
                dcc.Graph(figure=charts.fig_mapa_puntos(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=6),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Composición por categoría en los 8 departamentos principales", className="chart-title"),
                dcc.Graph(figure=charts.fig_top_depts_cat(df), config={"displayModeBar": False}),
            ], className="chart-card")),
        ], className="g-3"),
    ])


def render_perfil(df):
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Tipo de denunciante", className="chart-title"),
                dcc.Graph(figure=charts.fig_tipo_denunciante(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=4),
            dbc.Col(html.Div([
                html.Div("Urgencia declarada", className="chart-title"),
                dcc.Graph(figure=charts.fig_urgencia_gauge(df), config={"displayModeBar": False}),
            ], className="chart-card"), md=4),
            dbc.Col(html.Div([
                _stat_mini("Denuncia previa ante organismo", f"{df['denuncia_previa'].mean()*100:.1f}%",
                           "de los casos ya fueron denunciados antes"),
                _stat_mini("Organismo más citado",
                           df[df["denuncia_previa"] == True]["organismo_previo"].value_counts().index[0]
                           if df["denuncia_previa"].any() else "—",
                           "en denuncias previas"),
            ], className="chart-card"), md=4),
        ], className="g-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div("Recurrencia del problema por categoría", className="chart-title"),
                dcc.Graph(figure=charts.fig_recurrencia_cat(df), config={"displayModeBar": False}),
            ], className="chart-card")),
        ], className="g-3"),
    ])


def _stat_mini(label, value, sub):
    return html.Div([
        html.Div(label, style={"fontSize": "11px", "color": "#8b949e", "marginBottom": "6px",
                               "textTransform": "uppercase", "letterSpacing": "0.5px"}),
        html.Div(value, style={"fontSize": "26px", "fontWeight": "700", "color": "#e6edf3", "marginBottom": "4px"}),
        html.Div(sub, style={"fontSize": "11px", "color": "#484f58"}),
    ], style={"marginBottom": "20px"})
