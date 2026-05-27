from dash import html, dcc
import dash_bootstrap_components as dbc
from data.generator import CATEGORIAS, DEPARTAMENTOS, RECURRENCIA

EMOJI_MAP = {
    "CAT_01": "🦜", "CAT_02": "🌊", "CAT_03": "💨",
    "CAT_04": "💧", "CAT_05": "🗑️", "CAT_06": "🌿",
    "CAT_07": "🔊", "CAT_08": "⛏️", "CAT_09": "❓",
}

CAT_OPTIONS = [
    {"label": f"{EMOJI_MAP[k]}  {v['label']}", "value": k}
    for k, v in CATEGORIAS.items()
]

DEPT_OPTIONS = [{"label": d, "value": d} for d in sorted(DEPARTAMENTOS)]

RECURRENCIA_OPTIONS = [{"label": r, "value": r} for r in RECURRENCIA]

TIPO_OPTIONS = [
    {"label": "👤  Persona", "value": "Persona"},
    {"label": "🏢  Organización", "value": "Organización"},
    {"label": "🕵️  Anónimo", "value": "Anónimo"},
]

URGENCIA_OPTIONS = [
    {"label": "✅  No", "value": False},
    {"label": "🚨  Sí, es urgente", "value": True},
]

PREVIA_OPTIONS = [
    {"label": "No", "value": False},
    {"label": "Sí", "value": True},
]

ORGANISMO_OPTIONS = [
    {"label": o, "value": o} for o in ["DINAMA", "Intendencia", "Policía", "Otro"]
]

CIUDADES = {
    "Artigas":        ["Artigas", "Bella Unión", "Baltasar Brum", "Tomás Gomensoro", "Otra localidad"],
    "Canelones":      ["Atlántida", "Barros Blancos", "Canelones", "Ciudad de la Costa", "La Paz",
                       "Las Piedras", "Pando", "Progreso", "Salinas", "San Jacinto",
                       "San Ramón", "Santa Lucía", "Tala", "Otra localidad"],
    "Cerro Largo":    ["Aceguá", "Fraile Muerto", "Melo", "Río Branco", "Otra localidad"],
    "Colonia":        ["Carmelo", "Colonia del Sacramento", "Juan Lacaze",
                       "Nueva Helvecia", "Rosario", "Tarariras", "Otra localidad"],
    "Durazno":        ["Durazno", "La Paloma", "Sarandí del Yí", "Villa del Carmen", "Otra localidad"],
    "Flores":         ["Andresito", "Ismael Cortinas", "Trinidad", "Otra localidad"],
    "Florida":        ["Cardal", "Casupá", "Florida", "Fray Marcos", "Sarandí Grande", "Otra localidad"],
    "Lavalleja":      ["José Pedro Varela", "Minas", "Pirarajá", "Solís de Mataojo", "Otra localidad"],
    "Maldonado":      ["Aiguá", "Maldonado", "Pan de Azúcar", "Piriápolis",
                       "Punta del Este", "San Carlos", "Otra localidad"],
    "Montevideo":     ["Aguada", "Barrio Sur", "Buceo", "Capurro", "Carrasco", "Centro",
                       "Cerro", "Ciudad Vieja", "Cordón", "Goes", "Jacinto Vera",
                       "La Blanqueada", "La Teja", "Malvín", "Palermo", "Parque Rodó",
                       "Pocitos", "Prado", "Punta Carretas", "Sayago", "Tres Cruces",
                       "Unión", "Otra localidad"],
    "Paysandú":       ["Guichón", "Paysandú", "Porvenir", "Quebracho", "Otra localidad"],
    "Río Negro":      ["Fray Bentos", "Nuevo Berlín", "San Javier", "Young", "Otra localidad"],
    "Rivera":         ["Minas de Corrales", "Rivera", "Tranqueras", "Vichadero", "Otra localidad"],
    "Rocha":          ["Castillos", "Chuy", "La Paloma", "Lascano", "Rocha", "Otra localidad"],
    "Salto":          ["Belén", "Constitución", "Mataojo", "Salto", "Otra localidad"],
    "San José":       ["Ciudad del Plata", "Ecilda Paullier", "Libertad",
                       "Rodríguez", "San José de Mayo", "Otra localidad"],
    "Soriano":        ["Cardona", "Dolores", "José Enrique Rodó", "Mercedes", "Otra localidad"],
    "Tacuarembó":     ["Curtina", "Paso de los Toros", "San Gregorio de Polanco",
                       "Tacuarembó", "Otra localidad"],
    "Treinta y Tres": ["Lascano", "Treinta y Tres", "Vergara", "Otra localidad"],
}


def render():
    return html.Div([
        # ── Encabezado ─────────────────────────────────────────────────────
        html.Div([
            html.Span("Captura ciudadana", className="section-badge"),
            html.H2("📝 Nueva Denuncia Ambiental", className="section-title"),
            html.P(
                "Completá el formulario para registrar un problema ambiental en Uruguay. "
                "Tu denuncia queda registrada en tiempo real.",
                className="section-desc"
            ),
        ]),

        dbc.Row([
            # ── Columna principal del formulario ───────────────────────────
            dbc.Col([

                html.Div([
                    # S1 ── Identificación
                    _seccion("S1", "Identificación del denunciante"),
                    dbc.Row([
                        dbc.Col(_field(
                            "Tipo de denunciante *",
                            dcc.RadioItems(
                                id="form-tipo-denunciante",
                                options=TIPO_OPTIONS,
                                value="Persona",
                                inline=True,
                                inputStyle={"marginRight": "5px", "marginLeft": "14px"},
                                labelStyle={"color": "#e6edf3", "fontSize": "13px"},
                            )
                        ), md=12),
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col(_field("Nombre (opcional)",
                                       dcc.Input(id="form-nombre", type="text",
                                                 placeholder="Tu nombre o el de tu organización",
                                                 className="dep-input")), md=6),
                        dbc.Col(_field("Email (opcional)",
                                       dcc.Input(id="form-email", type="email",
                                                 placeholder="correo@ejemplo.com",
                                                 className="dep-input")), md=6),
                    ], className="mb-3"),

                    # S2 ── Ubicación
                    _seccion("S2", "Ubicación del problema"),
                    dbc.Row([
                        dbc.Col(_field("Departamento *",
                                       dcc.Dropdown(id="form-departamento",
                                                    options=DEPT_OPTIONS,
                                                    placeholder="Seleccioná el departamento…",
                                                    className="dep-dropdown")), md=6),
                        dbc.Col(_field("Ciudad / Localidad",
                                       dcc.Dropdown(
                                           id="form-ciudad",
                                           options=[],
                                           placeholder="Primero elegí el departamento…",
                                           className="dep-dropdown",
                                           disabled=True,
                                       )), md=6),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col(_field("Calle, número o punto de referencia",
                                       dcc.Input(id="form-referencia", type="text",
                                                 placeholder="Ej: Av. 18 de Julio 1234 o frente al Parque Rodó",
                                                 className="dep-input")), md=9),
                        dbc.Col([
                            html.Label(" ", className="dep-label"),
                            html.Button("📍 Verificar en mapa", id="btn-geocode",
                                        n_clicks=0, className="btn-geocode"),
                        ], md=3),
                    ], className="mb-2"),
                    html.Div(id="geocode-result", style={"marginBottom": "12px"}),
                    dcc.Store(id="geocode-data", data={}),

                    # S3A ── Categoría
                    _seccion("S3A", "Categoría del problema *"),
                    _field("",
                           dcc.Dropdown(
                               id="form-categoria",
                               options=CAT_OPTIONS,
                               placeholder="🔍  Seleccioná la categoría ambiental…",
                               className="dep-dropdown",
                               style={"backgroundColor": "#161b22", "color": "#e6edf3"},
                           )),
                    html.Div(style={"height": "12px"}),

                    # S3B ── Subcategoría
                    _seccion("S3B", "Subcategoría"),
                    _field("",
                           dcc.Dropdown(
                               id="form-subcategoria",
                               options=[],
                               placeholder="Primero seleccioná una categoría arriba…",
                               className="dep-dropdown",
                               disabled=True,
                               style={"backgroundColor": "#161b22", "color": "#e6edf3"},
                           )),
                    html.Div(style={"height": "12px"}),

                    # S3C ── Descripción
                    _seccion("S3C", "Descripción del problema"),
                    _field("Describí con tus palabras qué está pasando (máx. 500 caracteres)",
                           dcc.Textarea(
                               id="form-descripcion",
                               placeholder="Qué viste, qué oliste, dónde exactamente, desde cuándo…",
                               className="dep-textarea",
                               maxLength=500,
                               style={"height": "90px", "resize": "vertical"},
                           )),
                    html.Div(id="char-count",
                             style={"fontSize": "11px", "color": "#484f58",
                                    "textAlign": "right", "marginTop": "2px",
                                    "marginBottom": "12px"}),

                    # S4 ── Contexto
                    _seccion("S4", "Contexto y evidencia"),
                    dbc.Row([
                        dbc.Col(_field("Recurrencia *",
                                       dcc.Dropdown(id="form-recurrencia",
                                                    options=RECURRENCIA_OPTIONS,
                                                    placeholder="¿Con qué frecuencia?",
                                                    className="dep-dropdown")), md=6),
                        dbc.Col(_field("¿Es urgente?",
                                       dcc.RadioItems(
                                           id="form-urgencia",
                                           options=URGENCIA_OPTIONS,
                                           value=False,
                                           inline=True,
                                           inputStyle={"marginRight": "5px", "marginLeft": "12px"},
                                           labelStyle={"color": "#e6edf3", "fontSize": "13px"},
                                       )), md=6),
                    ], className="mb-3"),

                    # ── Mensaje y botón enviar ──────────────────────────
                    html.Div(id="form-msg", style={"marginBottom": "14px"}),

                    html.Button(
                        "📩  Ingresa tu denuncia",
                        id="btn-enviar",
                        n_clicks=0,
                        className="submit-btn",
                    ),

                ], className="form-card"),

            ], md=8),

            # ── Columna lateral informativa ────────────────────────────────
            dbc.Col([
                _panel_info(),
                _panel_categorias(),
            ], md=4),

        ], className="g-4"),
    ], className="content-area")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _seccion(codigo, titulo):
    return html.Div([
        html.Span(codigo, style={
            "fontSize": "10px", "fontWeight": "700", "color": "#1abc9c",
            "background": "rgba(26,188,156,0.12)", "border": "1px solid rgba(26,188,156,0.3)",
            "borderRadius": "20px", "padding": "2px 10px", "marginRight": "8px",
        }),
        html.Span(titulo, style={"fontSize": "12px", "fontWeight": "600",
                                  "color": "#e6edf3", "letterSpacing": "0.3px"}),
    ], style={
        "marginTop": "20px", "marginBottom": "12px", "paddingBottom": "8px",
        "borderBottom": "1px solid #30363d",
    })


def _field(label, component):
    children = []
    if label:
        children.append(html.Label(label, className="dep-label"))
    children.append(component)
    return html.Div(children, style={"marginBottom": "6px"})


def _panel_info():
    return html.Div([
        html.Div("🔒  Privacidad", style={"fontWeight": "700", "color": "#1abc9c",
                                           "fontSize": "13px", "marginBottom": "10px"}),
        html.P("Los campos nombre y email son opcionales. Las denuncias anónimas "
               "no muestran datos identificables en el tablero público.",
               style={"color": "#8b949e", "fontSize": "12px", "lineHeight": "1.6"}),
        html.Hr(style={"borderColor": "#30363d"}),
        html.Div("📋  Campos obligatorios", style={"fontWeight": "700", "color": "#e6edf3",
                                                     "fontSize": "12px", "marginBottom": "8px"}),
        html.Ul([
            html.Li("Departamento", style={"color": "#8b949e", "fontSize": "12px"}),
            html.Li("Categoría ambiental", style={"color": "#8b949e", "fontSize": "12px"}),
            html.Li("Recurrencia", style={"color": "#8b949e", "fontSize": "12px"}),
        ], style={"paddingLeft": "18px"}),
    ], className="chart-card", style={"marginBottom": "12px"})


def _panel_categorias():
    items = []
    for code, cat in CATEGORIAS.items():
        items.append(html.Div([
            html.Span(EMOJI_MAP.get(code, "📍"), style={"marginRight": "8px", "fontSize": "14px"}),
            html.Span(cat["label"], style={"fontSize": "12px", "color": "#8b949e"}),
        ], style={"marginBottom": "7px", "display": "flex", "alignItems": "center"}))
    return html.Div([
        html.Div("🗂️  Categorías del catálogo", style={
            "fontWeight": "700", "color": "#e6edf3",
            "fontSize": "13px", "marginBottom": "12px",
        }),
        *items,
    ], className="chart-card")
