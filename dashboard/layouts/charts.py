import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#e6edf3", "size": 12},
    "margin": {"t": 30, "r": 16, "b": 40, "l": 50},
    "colorway": ["#1abc9c", "#58a6ff", "#f0883e", "#f85149", "#bc8cff", "#3fb950", "#f1c40f", "#79c0ff", "#ffa657"],
    "xaxis": {"gridcolor": "#21262d", "linecolor": "#30363d", "tickfont": {"color": "#8b949e", "size": 11}},
    "yaxis": {"gridcolor": "#21262d", "linecolor": "#30363d", "tickfont": {"color": "#8b949e", "size": 11}},
    "legend": {"font": {"color": "#8b949e", "size": 11}, "bgcolor": "rgba(0,0,0,0)"},
}

CAT_COLORS = {
    "CAT_01": "#2d6a4f", "CAT_02": "#1b4f72", "CAT_03": "#5d6d7e",
    "CAT_04": "#2e86c1", "CAT_05": "#e67e22", "CAT_06": "#27ae60",
    "CAT_07": "#f1c40f", "CAT_08": "#8b6914", "CAT_09": "#7f8c8d",
}


def apply_theme(fig, height=360):
    fig.update_layout(
        **CHART_THEME,
        height=height,
        hoverlabel={"bgcolor": "#1c2128", "bordercolor": "#30363d", "font": {"color": "#e6edf3", "size": 12}},
    )
    return fig


def fig_evolucion_anual(df):
    by_year = df.groupby("año").size().reset_index(name="total")
    avg = by_year["total"].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=by_year["año"], y=by_year["total"],
        name="Denuncias por año",
        marker_color="#1abc9c", marker_line_color="#0d1117", marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>%{y} denuncias<extra></extra>",
    ))
    fig.add_hline(y=avg, line_dash="dot", line_color="#f0883e", line_width=1.5,
                  annotation_text=f"Promedio: {avg:.0f}", annotation_font_color="#f0883e")
    y_max = by_year["total"].max()
    apply_theme(fig)
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Denuncias",
        yaxis_range=[0, y_max * 1.15],
    )
    return fig


def fig_tendencia_mensual(df):
    monthly = df.groupby(df["timestamp"].dt.to_period("M")).size().reset_index(name="total")
    monthly["fecha"] = monthly["timestamp"].dt.to_timestamp()
    monthly["ma7"] = monthly["total"].rolling(3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["fecha"], y=monthly["total"],
        mode="lines", name="Mensual",
        line={"color": "#58a6ff", "width": 1.5},
        opacity=0.5,
    ))
    fig.add_trace(go.Scatter(
        x=monthly["fecha"], y=monthly["ma7"],
        mode="lines", name="Media móvil 3m",
        line={"color": "#1abc9c", "width": 2.5},
    ))
    y_max = max(monthly["total"].max(), monthly["ma7"].max())
    apply_theme(fig)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Denuncias / mes",
        yaxis_range=[0, y_max * 1.15],
    )
    return fig


def fig_heatmap_hora_dia(df):
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    pivot = df.groupby(["dia_semana", "hora"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(range(7), fill_value=0)
    pivot.index = dias

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"{h:02d}h" for h in range(24)], y=dias,
        colorscale=[[0, "#0d1117"], [0.3, "#1f3a35"], [0.7, "#1abc9c"], [1.0, "#3fb950"]],
        hovertemplate="<b>%{y} %{x}</b><br>%{z} denuncias<extra></extra>",
    ))
    apply_theme(fig, height=280)
    fig.update_layout(xaxis_title="Hora del día", yaxis_title="")
    return fig


def fig_treemap(df):
    agg = df.groupby(["categoria_label", "subcategoria"]).size().reset_index(name="total")
    fig = px.treemap(
        agg, path=["categoria_label", "subcategoria"], values="total",
        color="total",
        color_continuous_scale=[[0, "#1b4f72"], [0.5, "#1abc9c"], [1, "#3fb950"]],
    )
    fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value} denuncias<extra></extra>",
                      textfont_color="white")
    apply_theme(fig, height=400)
    fig.update_coloraxes(showscale=False)
    return fig


def fig_sunburst(df):
    agg = df.groupby(["categoria_label", "subcategoria"]).size().reset_index(name="total")
    cat_map = {v["label"]: k for k, v in __import__('data.generator', fromlist=['CATEGORIAS']).CATEGORIAS.items()}
    agg["cat_code"] = agg["categoria_label"].map(cat_map)
    fig = px.sunburst(
        agg, path=["categoria_label", "subcategoria"], values="total",
        color="categoria_label",
        color_discrete_map={v["label"]: v["color"] for v in __import__('data.generator', fromlist=['CATEGORIAS']).CATEGORIAS.values()},
    )
    fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value} denuncias<extra></extra>",
                      textfont_color="white", insidetextorientation="radial")
    apply_theme(fig, height=400)
    return fig


def fig_ranking_subcats(df, cat_filter=None):
    data = df if cat_filter is None else df[df["categoria_codigo"] == cat_filter]
    top = data.groupby("subcategoria").size().reset_index(name="total").nlargest(15, "total")
    fig = go.Figure(go.Bar(
        x=top["total"], y=top["subcategoria"],
        orientation="h",
        marker_color="#1abc9c",
        hovertemplate="<b>%{y}</b><br>%{x} denuncias<extra></extra>",
    ))
    apply_theme(fig, height=380)
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Denuncias")
    return fig


def fig_area_mensual_cat(df):
    df2 = df.copy()
    df2["periodo"] = df2["timestamp"].dt.to_period("M").dt.to_timestamp()
    agg = df2.groupby(["periodo", "categoria_label"]).size().reset_index(name="total")
    cats = df2["categoria_label"].value_counts().head(6).index.tolist()
    agg = agg[agg["categoria_label"].isin(cats)]

    from data.generator import CATEGORIAS
    label_to_color = {v["label"]: v["color"] for v in CATEGORIAS.values()}

    fig = go.Figure()
    for cat in cats:
        sub = agg[agg["categoria_label"] == cat]
        fig.add_trace(go.Scatter(
            x=sub["periodo"], y=sub["total"],
            mode="lines", name=cat,
            fill="tonexty",
            line={"color": label_to_color.get(cat, "#1abc9c"), "width": 1.5},
            stackgroup="one",
        ))
    apply_theme(fig, height=360)
    fig.update_layout(xaxis_title="", yaxis_title="Denuncias")
    return fig


def fig_mapa_coropletico(df):
    dept_counts = df.groupby("departamento").size().reset_index(name="total")

    DEPT_COORDS = {
        "Artigas": (-30.4, -56.5), "Canelones": (-34.5, -56.0), "Cerro Largo": (-32.4, -54.2),
        "Colonia": (-34.0, -57.8), "Durazno": (-33.4, -56.5), "Flores": (-33.6, -56.9),
        "Florida": (-34.1, -56.2), "Lavalleja": (-34.4, -55.2), "Maldonado": (-34.9, -54.9),
        "Montevideo": (-34.9, -56.2), "Paysandú": (-32.3, -58.1), "Río Negro": (-32.9, -57.9),
        "Rivera": (-31.0, -55.6), "Rocha": (-34.5, -54.3), "Salto": (-31.4, -57.9),
        "San José": (-34.3, -56.7), "Soriano": (-33.5, -57.8), "Tacuarembó": (-31.7, -56.0),
        "Treinta y Tres": (-33.2, -54.4),
    }
    dept_counts["lat"] = dept_counts["departamento"].map(lambda d: DEPT_COORDS.get(d, (-33, -56))[0])
    dept_counts["lon"] = dept_counts["departamento"].map(lambda d: DEPT_COORDS.get(d, (-33, -56))[1])

    fig = go.Figure(go.Scattermapbox(
        lat=dept_counts["lat"], lon=dept_counts["lon"],
        mode="markers+text",
        marker={
            "size": (dept_counts["total"] / dept_counts["total"].max() * 50 + 15).clip(15, 65),
            "color": dept_counts["total"],
            "colorscale": [[0, "#1b4f72"], [0.5, "#1abc9c"], [1, "#3fb950"]],
            "opacity": 0.8,
            "showscale": True,
            "colorbar": {"title": "Denuncias", "tickfont": {"color": "#8b949e"}},
        },
        text=dept_counts["departamento"],
        textposition="top center",
        textfont={"color": "#e6edf3", "size": 10},
        hovertemplate="<b>%{text}</b><br>%{marker.color:.0f} denuncias<extra></extra>",
    ))
    fig.update_layout(
        mapbox={"style": "carto-darkmatter", "center": {"lat": -32.7, "lon": -56.5}, "zoom": 5.5},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e6edf3"}, height=480,
        margin={"t": 10, "r": 0, "b": 10, "l": 0},
    )
    return fig


def fig_mapa_puntos(df, max_points=500):
    sample = df.dropna(subset=["latitud", "longitud"]).sample(min(max_points, len(df)), random_state=42)
    from data.generator import CATEGORIAS
    label_to_color = {v["label"]: v["color"] for v in CATEGORIAS.values()}
    fig = go.Figure(go.Scattermapbox(
        lat=sample["latitud"], lon=sample["longitud"],
        mode="markers",
        marker={"size": 7, "color": sample["categoria_label"].map(label_to_color).fillna("#1abc9c"), "opacity": 0.7},
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
        customdata=sample[["categoria_label", "departamento"]].values,
    ))
    fig.update_layout(
        mapbox={"style": "carto-darkmatter", "center": {"lat": -32.7, "lon": -56.5}, "zoom": 5.5},
        paper_bgcolor="rgba(0,0,0,0)", height=480,
        font={"color": "#e6edf3"},
        margin={"t": 10, "r": 0, "b": 10, "l": 0},
        legend={"font": {"color": "#8b949e"}},
    )
    return fig


def fig_top_depts_cat(df):
    top_depts = df.groupby("departamento").size().nlargest(8).index.tolist()
    agg = df[df["departamento"].isin(top_depts)].groupby(["departamento", "categoria_label"]).size().reset_index(name="total")
    from data.generator import CATEGORIAS
    label_to_color = {v["label"]: v["color"] for v in CATEGORIAS.values()}

    fig = go.Figure()
    for cat in agg["categoria_label"].unique():
        sub = agg[agg["categoria_label"] == cat]
        fig.add_trace(go.Bar(
            name=cat, x=sub["departamento"], y=sub["total"],
            marker_color=label_to_color.get(cat, "#1abc9c"),
        ))
    apply_theme(fig, height=380)
    fig.update_layout(barmode="stack", xaxis_title="", yaxis_title="Denuncias",
                      legend={"font": {"size": 9}, "orientation": "h", "y": -0.3})
    return fig


def fig_tipo_denunciante(df):
    counts = df["tipo_denunciante"].value_counts().reset_index()
    counts.columns = ["tipo", "total"]
    fig = go.Figure(go.Pie(
        labels=counts["tipo"], values=counts["total"],
        hole=0.55,
        marker_colors=["#1abc9c", "#58a6ff", "#8b949e"],
        textfont={"color": "#e6edf3"},
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
    ))
    apply_theme(fig, height=300)
    fig.update_layout(showlegend=True)
    return fig


def fig_recurrencia_cat(df):
    agg = df.groupby(["categoria_label", "recurrencia"]).size().reset_index(name="total")
    total_by_cat = agg.groupby("categoria_label")["total"].transform("sum")
    agg["pct"] = agg["total"] / total_by_cat * 100
    cats = df["categoria_label"].value_counts().head(6).index.tolist()
    agg = agg[agg["categoria_label"].isin(cats)]

    colors = {"Puntual": "#58a6ff", "Recurrente": "#f0883e", "Permanente": "#f85149"}
    fig = go.Figure()
    for rec in ["Puntual", "Recurrente", "Permanente"]:
        sub = agg[agg["recurrencia"] == rec]
        fig.add_trace(go.Bar(name=rec, x=sub["categoria_label"], y=sub["pct"],
                             marker_color=colors[rec],
                             hovertemplate="<b>%{x}</b><br>" + rec + ": %{y:.1f}%<extra></extra>"))
    apply_theme(fig, height=340)
    fig.update_layout(barmode="stack", yaxis_title="% del total", xaxis_tickangle=-25)
    return fig


def fig_urgencia_gauge(df):
    pct_urgente = df["urgencia"].mean() * 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_urgente,
        number={"suffix": "%", "font": {"color": "#e6edf3", "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#8b949e"}},
            "bar": {"color": "#f85149"},
            "bgcolor": "#21262d",
            "steps": [
                {"range": [0, 10], "color": "#1c2128"},
                {"range": [10, 25], "color": "#2d3748"},
                {"range": [25, 100], "color": "#3d1a1a"},
            ],
            "threshold": {"line": {"color": "#f85149", "width": 3}, "thickness": 0.75, "value": pct_urgente},
        },
        title={"text": "Denuncias urgentes", "font": {"color": "#8b949e", "size": 13}},
    ))
    apply_theme(fig, height=280)
    return fig


def fig_heatmap_correlacion(df):
    from data.generator import CATEGORIAS
    cats = list(CATEGORIAS.keys())
    depts = df["departamento"].value_counts().head(10).index.tolist()
    pivot = df[df["departamento"].isin(depts)].pivot_table(
        index="departamento", columns="categoria_codigo", values="id_denuncia",
        aggfunc="count", fill_value=0
    )
    pivot = pivot.reindex(columns=[c for c in cats if c in pivot.columns], fill_value=0)
    z = pivot.values.tolist()
    labels = [CATEGORIAS[c]["label"] for c in pivot.columns]

    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=pivot.index.tolist(),
        colorscale=[[0, "#0d1117"], [0.4, "#1b4f72"], [1, "#1abc9c"]],
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>%{z} denuncias<extra></extra>",
    ))
    apply_theme(fig, height=400)
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def fig_radar_dept(df, dept):
    from data.generator import CATEGORIAS
    cats = list(CATEGORIAS.keys())
    dept_data = df[df["departamento"] == dept]
    total_dept = len(dept_data)
    if total_dept == 0:
        return go.Figure()
    dept_pct = [(len(dept_data[dept_data["categoria_codigo"] == c]) / total_dept * 100) for c in cats]
    total_all = len(df)
    nat_pct = [(len(df[df["categoria_codigo"] == c]) / total_all * 100) for c in cats]
    labels = [CATEGORIAS[c]["label"] for c in cats]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=dept_pct + [dept_pct[0]], theta=labels + [labels[0]],
                                   fill="toself", name=dept, line_color="#1abc9c",
                                   fillcolor="rgba(26,188,156,0.15)"))
    fig.add_trace(go.Scatterpolar(r=nat_pct + [nat_pct[0]], theta=labels + [labels[0]],
                                   fill="toself", name="Media nacional", line_color="#58a6ff",
                                   fillcolor="rgba(88,166,255,0.1)", line_dash="dot"))
    apply_theme(fig, height=360)
    fig.update_layout(polar={"bgcolor": "rgba(0,0,0,0)",
                              "radialaxis": {"color": "#8b949e", "gridcolor": "#21262d"},
                              "angularaxis": {"color": "#8b949e", "gridcolor": "#21262d"}})
    return fig


def fig_anomalias_zscore(df):
    monthly = df.groupby(df["timestamp"].dt.to_period("M")).size().reset_index(name="total")
    monthly["fecha"] = monthly["timestamp"].dt.to_timestamp()
    monthly["zscore"] = (monthly["total"] - monthly["total"].mean()) / monthly["total"].std()
    monthly["anomalia"] = monthly["zscore"].abs() > 1.8
    normal = monthly[~monthly["anomalia"]]
    anom = monthly[monthly["anomalia"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=normal["fecha"], y=normal["total"], mode="lines+markers",
                             name="Normal", line_color="#58a6ff", marker_size=4))
    fig.add_trace(go.Scatter(x=anom["fecha"], y=anom["total"], mode="markers",
                             name="Anomalía", marker={"color": "#f85149", "size": 10, "symbol": "diamond"}))
    apply_theme(fig, height=340)
    fig.update_layout(xaxis_title="", yaxis_title="Denuncias / mes")
    return fig


def fig_matriz_triage(df):
    agg = df.groupby(["urgencia", "recurrencia"]).size().reset_index(name="total")
    agg["urgencia_label"] = agg["urgencia"].map({True: "Urgente", False: "No urgente"})
    pivot = agg.pivot(index="urgencia_label", columns="recurrencia", values="total").fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0, "#1c2128"], [0.5, "#1b4f72"], [1, "#f85149"]],
        text=pivot.values.astype(int).tolist(),
        texttemplate="%{text}",
        textfont={"color": "#e6edf3", "size": 14},
        hovertemplate="<b>%{y} × %{x}</b><br>%{z:.0f} denuncias<extra></extra>",
    ))
    apply_theme(fig, height=260)
    return fig


def fig_forecast_simple(df):
    monthly = df.groupby(df["timestamp"].dt.to_period("M")).size().reset_index(name="total")
    monthly["fecha"] = monthly["timestamp"].dt.to_timestamp()

    x = np.arange(len(monthly))
    y = monthly["total"].values
    if len(x) < 4:
        return go.Figure()

    coeffs = np.polyfit(x, y, 2)
    p = np.poly1d(coeffs)

    n_future = 12
    x_future = np.arange(len(monthly), len(monthly) + n_future)
    future_dates = pd.date_range(monthly["fecha"].iloc[-1] + pd.DateOffset(months=1), periods=n_future, freq="MS")
    y_future = p(x_future)
    noise = np.std(y) * 0.3
    ci_up = y_future + 1.96 * noise
    ci_dn = (y_future - 1.96 * noise).clip(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["fecha"], y=monthly["total"], mode="lines",
                             name="Histórico", line_color="#58a6ff"))
    fig.add_trace(go.Scatter(x=future_dates, y=y_future, mode="lines",
                             name="Pronóstico", line={"color": "#1abc9c", "dash": "dash"}))
    fig.add_trace(go.Scatter(x=list(future_dates) + list(future_dates[::-1]),
                             y=list(ci_up) + list(ci_dn[::-1]),
                             fill="toself", fillcolor="rgba(26,188,156,0.1)",
                             line={"color": "rgba(0,0,0,0)"}, name="IC 95%"))
    apply_theme(fig, height=360)
    fig.update_layout(xaxis_title="", yaxis_title="Denuncias / mes")
    return fig


def fig_top_palabras(df, cat=None):
    from collections import Counter
    import re
    STOPWORDS = {"de", "la", "el", "en", "y", "a", "que", "con", "del", "los", "las",
                 "por", "se", "es", "un", "una", "al", "lo", "su", "para", "no", "como"}
    data = df if cat is None else df[df["categoria_codigo"] == cat]
    labels = (data["subcategoria"].fillna("") + " " + data["categoria_label"].fillna("")).str.lower()
    words = []
    for text in labels:
        words.extend([w for w in re.findall(r"[a-záéíóúñü]+", text) if len(w) > 3 and w not in STOPWORDS])
    top = Counter(words).most_common(15)
    if not top:
        return go.Figure()
    words_top, counts = zip(*top)
    fig = go.Figure(go.Bar(x=list(counts), y=list(words_top), orientation="h",
                           marker_color="#bc8cff",
                           hovertemplate="<b>%{y}</b>: %{x}<extra></extra>"))
    apply_theme(fig, height=360)
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Frecuencia")
    return fig


def fig_clustering_depts(df):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from data.generator import CATEGORIAS

    cats = list(CATEGORIAS.keys())
    pivot = df.pivot_table(index="departamento", columns="categoria_codigo", values="id_denuncia",
                           aggfunc="count", fill_value=0)
    pivot = pivot.reindex(columns=[c for c in cats if c in pivot.columns], fill_value=0)

    if len(pivot) < 3:
        return go.Figure()

    scaler = StandardScaler()
    X = scaler.fit_transform(pivot)
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = km.fit_predict(X)

    pivot["cluster"] = clusters
    pivot["total"] = pivot[cats].sum(axis=1)
    pivot = pivot.reset_index()

    cluster_colors = {0: "#1abc9c", 1: "#58a6ff", 2: "#f0883e", 3: "#bc8cff"}
    cluster_names = {0: "Cluster A", 1: "Cluster B", 2: "Cluster C", 3: "Cluster D"}

    fig = go.Figure()
    for c in range(4):
        sub = pivot[pivot["cluster"] == c]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["total"], y=sub.index.tolist(),
            mode="markers+text",
            name=cluster_names[c],
            text=sub["departamento"],
            textposition="middle right",
            textfont={"size": 10},
            marker={"size": 14, "color": cluster_colors[c], "opacity": 0.85},
        ))

    apply_theme(fig, height=400)
    fig.update_layout(xaxis_title="Total denuncias", yaxis_title="",
                      showlegend=True, yaxis_showticklabels=False)
    return fig
