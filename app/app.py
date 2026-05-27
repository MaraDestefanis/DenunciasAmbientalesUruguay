import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from data.db import init_db
from data.generator import get_data
from dashboard.layouts.header import render_header, render_kpis
from dashboard.callbacks.callbacks import register_callbacks

init_db()

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
    ],
    suppress_callback_exceptions=True,
    title="Denuncias Ambientales · D Empathy Project",
    assets_folder="dashboard/assets",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

@server.after_request
def add_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

df = get_data()

app.layout = html.Div([
    dcc.Store(id="data-store", data=0),
    dcc.Store(id="submit-store", data=0),
    dcc.Interval(id="kpi-interval", interval=4000, n_intervals=0),

    render_header(),
    render_kpis(df),

    dbc.Tabs(
        [
            dbc.Tab(label="📊 Descriptivo", tab_id="tab-descriptivo"),
            dbc.Tab(label="🔍 Diagnóstico", tab_id="tab-diagnostico"),
            dbc.Tab(label="🤖 Predictivo", tab_id="tab-predictivo"),
            dbc.Tab(label="📝 Nueva denuncia", tab_id="tab-encuesta"),
        ],
        id="main-tabs",
        active_tab="tab-descriptivo",
        className="custom-tabs",
        style={
            "padding": "0 24px",
            "backgroundColor": "#161b22",
            "borderBottom": "1px solid #30363d",
        },
    ),

    html.Div(id="main-content"),

], style={"minHeight": "100vh", "backgroundColor": "#0d1117"})

register_callbacks(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
