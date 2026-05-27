from dash import Input, Output, State, html, no_update
from datetime import datetime
from urllib.parse import quote
from data.generator import CATEGORIAS, add_new_record, get_data
from dashboard.layouts import charts, descriptivo, diagnostico, predictivo, encuesta
from dashboard.layouts.encuesta import CIUDADES


def register_callbacks(app):

    # ── Main section tabs ───────────────────────────────────────────────────
    @app.callback(
        Output("main-content", "children"),
        Input("main-tabs", "active_tab"),
        Input("data-store", "data"),
    )
    def render_main_content(tab, _):
        df = get_data()
        if tab == "tab-diagnostico":
            return diagnostico.render(df)
        elif tab == "tab-predictivo":
            return predictivo.render(df)
        elif tab == "tab-encuesta":
            return encuesta.render()
        return descriptivo.render(df)

    # ── KPI bar update ──────────────────────────────────────────────────────
    @app.callback(
        Output("kpi-bar", "children"),
        Input("data-store", "data"),
        Input("submit-store", "data"),
        Input("kpi-interval", "n_intervals"),
    )
    def update_kpis(_, _s, _i):
        from dashboard.layouts.header import render_kpis
        df = get_data()
        return render_kpis(df).children

    # ── Botón "Nueva denuncia" del header ───────────────────────────────────
    @app.callback(
        Output("main-tabs", "active_tab"),
        Input("btn-nueva-denuncia-header", "n_clicks"),
        prevent_initial_call=True,
    )
    def ir_a_formulario(n):
        return "tab-encuesta"

    # ── Descriptivo sub-tabs ────────────────────────────────────────────────
    @app.callback(
        Output("desc-tab-content", "children"),
        Input("desc-tabs", "active_tab"),
        Input("data-store", "data"),
        Input("submit-store", "data"),
    )
    def render_desc_content(tab, _, _s):
        df = get_data()
        if tab == "tab-categorias":
            return descriptivo.render_categorias(df)
        elif tab == "tab-geografico":
            return descriptivo.render_geografico(df)
        elif tab == "tab-perfil":
            return descriptivo.render_perfil(df)
        return descriptivo.render_temporal(df)

    @app.callback(
        Output("fig-ranking-subcats", "figure"),
        Input("subcat-filter", "value"),
        prevent_initial_call=True,
    )
    def update_ranking_subcats(cat_filter):
        df = get_data()
        return charts.fig_ranking_subcats(df, None if cat_filter == "all" else cat_filter)

    # ── Diagnóstico sub-tabs ────────────────────────────────────────────────
    @app.callback(
        Output("diag-tab-content", "children"),
        Input("diag-tabs", "active_tab"),
        Input("data-store", "data"),
        Input("submit-store", "data"),
    )
    def render_diag_content(tab, _, _s):
        df = get_data()
        if tab == "tab-anomalias":
            return diagnostico.render_anomalias(df)
        elif tab == "tab-triage":
            return diagnostico.render_triage(df)
        return diagnostico.render_correlaciones(df)

    @app.callback(
        Output("fig-radar-dept", "figure"),
        Input("radar-dept-filter", "value"),
        prevent_initial_call=True,
    )
    def update_radar(dept):
        return charts.fig_radar_dept(get_data(), dept)

    # ── Predictivo sub-tabs ─────────────────────────────────────────────────
    @app.callback(
        Output("pred-tab-content", "children"),
        Input("pred-tabs", "active_tab"),
        Input("data-store", "data"),
        Input("submit-store", "data"),
    )
    def render_pred_content(tab, _, _s):
        df = get_data()
        if tab == "tab-nlp":
            return predictivo.render_nlp(df)
        elif tab == "tab-alertas":
            return predictivo.render_alertas(df)
        elif tab == "tab-clustering":
            return predictivo.render_clustering(df)
        return predictivo.render_forecast(df)

    @app.callback(
        Output("fig-top-palabras", "figure"),
        Input("nlp-cat-filter", "value"),
        prevent_initial_call=True,
    )
    def update_top_palabras(cat_filter):
        return charts.fig_top_palabras(get_data(), None if cat_filter == "all" else cat_filter)

    # ── Formulario: ciudades según departamento ─────────────────────────────
    @app.callback(
        Output("form-ciudad", "options"),
        Output("form-ciudad", "disabled"),
        Output("form-ciudad", "placeholder"),
        Output("form-ciudad", "value"),
        Input("form-departamento", "value"),
        prevent_initial_call=True,
    )
    def update_ciudades(dept):
        if not dept:
            return [], True, "Primero elegí el departamento…", None
        opts = [{"label": c, "value": c} for c in CIUDADES.get(dept, ["Otra localidad"])]
        return opts, False, "Seleccioná la localidad…", None

    # ── Formulario: geocodificación de dirección ────────────────────────────
    @app.callback(
        Output("geocode-result", "children"),
        Output("geocode-data", "data"),
        Input("btn-geocode", "n_clicks"),
        State("form-referencia", "value"),
        State("form-ciudad", "value"),
        State("form-departamento", "value"),
        prevent_initial_call=True,
    )
    def geocodificar(n_clicks, referencia, ciudad, dept):
        import requests as req
        partes = [p for p in [referencia, ciudad, dept, "Uruguay"] if p]
        if len(partes) < 2:
            return html.Div("⚠️  Completá al menos el departamento y la referencia.",
                            style={"color": "#f85149", "fontSize": "12px"}), {}
        query = ", ".join(partes)
        try:
            resp = req.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1, "countrycodes": "uy"},
                headers={"User-Agent": "DenunciasAmbientalesUY/1.0"},
                timeout=5,
            )
            results = resp.json()
        except Exception:
            results = []

        if not results:
            query_enc = quote(query)
            url = f"https://www.google.com/maps/search/?api=1&query={query_enc}"
            return html.Div([
                html.Span("⚠️  No se encontró la dirección exacta. ",
                          style={"color": "#e3b341", "fontSize": "12px"}),
                html.A("Abrí el mapa manualmente ↗", href=url, target="_blank",
                       style={"color": "#1abc9c", "fontSize": "12px"}),
            ]), {}

        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        display = results[0].get("display_name", query)
        maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=17&marker={lat},{lon}"
        osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=17"

        resultado = html.Div([
            html.Div("✅  Dirección verificada:", style={
                "fontSize": "11px", "color": "#3fb950", "fontWeight": "700", "marginBottom": "4px"
            }),
            html.Div(display[:120] + ("…" if len(display) > 120 else ""), style={
                "fontSize": "11px", "color": "#8b949e", "marginBottom": "6px"
            }),
            html.Div([
                html.Span(f"📌 Lat: {lat:.5f}  |  Lon: {lon:.5f}",
                          style={"fontSize": "11px", "color": "#1abc9c",
                                 "fontWeight": "600", "marginRight": "14px"}),
                html.A("Google Maps ↗", href=maps_url, target="_blank",
                       style={"fontSize": "11px", "color": "#1abc9c",
                              "marginRight": "10px", "textDecoration": "none"}),
                html.A("OpenStreetMap ↗", href=osm_url, target="_blank",
                       style={"fontSize": "11px", "color": "#8b949e", "textDecoration": "none"}),
            ]),
        ], style={
            "background": "rgba(26,188,156,0.08)", "border": "1px solid rgba(26,188,156,0.25)",
            "borderRadius": "6px", "padding": "10px 14px",
        })

        return resultado, {"lat": lat, "lon": lon, "direccion": display}

    # ── Formulario: subcategorías según categoría ───────────────────────────
    @app.callback(
        Output("form-subcategoria", "options"),
        Output("form-subcategoria", "disabled"),
        Output("form-subcategoria", "placeholder"),
        Input("form-categoria", "value"),
        prevent_initial_call=True,
    )
    def update_subcategorias(cat_code):
        if not cat_code:
            return [], True, "Primero seleccioná una categoría arriba…"
        subcats = CATEGORIAS.get(cat_code, {}).get("subcategorias", [])
        opts = [{"label": s, "value": s} for s in subcats]
        return opts, False, "Seleccioná la subcategoría…"

    # ── Formulario: contador de caracteres ──────────────────────────────────
    @app.callback(
        Output("char-count", "children"),
        Input("form-descripcion", "value"),
        prevent_initial_call=True,
    )
    def update_char_count(text):
        n = len(text) if text else 0
        color = "#f85149" if n > 450 else "#484f58"
        return f"{n}/500 caracteres"

    # ── Formulario: envío ───────────────────────────────────────────────────
    @app.callback(
        Output("form-msg", "children"),
        Output("submit-store", "data"),
        Input("btn-enviar", "n_clicks"),
        State("form-tipo-denunciante", "value"),
        State("form-nombre", "value"),
        State("form-email", "value"),
        State("form-departamento", "value"),
        State("form-ciudad", "value"),
        State("form-referencia", "value"),
        State("form-categoria", "value"),
        State("form-subcategoria", "value"),
        State("form-descripcion", "value"),
        State("form-recurrencia", "value"),
        State("form-urgencia", "value"),
        State("geocode-data", "data"),
        prevent_initial_call=True,
    )
    def submit_form(n_clicks, tipo, nombre, email, dept, ciudad, referencia,
                    cat_code, subcat, desc, recurrencia, urgencia, geocode):

        # Validación
        faltantes = []
        if not dept:
            faltantes.append("Departamento")
        if not cat_code:
            faltantes.append("Categoría")
        if not recurrencia:
            faltantes.append("Recurrencia")

        if faltantes:
            return html.Div(
                f"⚠️  Completá los campos obligatorios: {', '.join(faltantes)}.",
                className="alert-error"
            ), no_update

        now = datetime.now()
        cat = CATEGORIAS.get(cat_code, {})
        from data.db import count_denuncias
        idx = count_denuncias() + 1

        geo = geocode or {}
        lat = geo.get("lat")
        lon = geo.get("lon")
        maps_url = (f"https://www.google.com/maps?q={lat},{lon}&z=17"
                    if lat and lon else "")

        record = {
            "id_denuncia": f"URY-{now.year}-F{idx:04d}",
            "timestamp": now,
            "tipo_denunciante": tipo or "Anónimo",
            "departamento": dept,
            "ciudad_localidad": ciudad or "",
            "referencia_lugar": geo.get("direccion") or referencia or "",
            "url_mapa": maps_url,
            "latitud": lat,
            "longitud": lon,
            "categoria_codigo": cat_code,
            "categoria_label": cat.get("label", ""),
            "subcategoria": subcat or "",
            "descripcion_libre": desc or "",
            "fecha_hecho": now.strftime("%Y-%m-%d"),
            "recurrencia": recurrencia,
            "urgencia": bool(urgencia),
            "denuncia_previa": False,
            "organismo_previo": None,
            "adjunto_url": None,
            "fuente": "formulario",
        }

        add_new_record(record)
        total = 4281 + count_denuncias()

        msg = html.Div([
            html.Strong("✅  ¡Denuncia registrada correctamente!"),
            html.Br(),
            html.Span(
                f"ID: URY-{now.year}-F{idx:04d}  ·  {cat.get('label','')}  ·  {dept}",
                style={"fontSize": "13px"},
            ),
            html.Br(),
            html.Span(
                f"Total acumulado en el sistema: {total:,} denuncias.",
                style={"fontSize": "12px", "color": "#3fb950"},
            ),
        ], className="alert-success")

        return msg, n_clicks
