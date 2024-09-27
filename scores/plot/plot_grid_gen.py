import plotly.graph_objects as go


def plot(d):

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=d["DATETIME"], y=d["GAS"], name="GAS", stackgroup="one"))
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["COAL"], name="COAL", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["NUCLEAR"], name="NUCLEAR", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["WIND"], name="WIND", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["HYDRO"], name="HYDRO", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["IMPORTS"], name="IMPORTS", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["BIOMASS"], name="BIOMASS", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["OTHER"], name="OTHER", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["SOLAR"], name="SOLAR", stackgroup="one")
    )
    fig.add_trace(
        go.Scatter(x=d["DATETIME"], y=d["STORAGE"], name="STORAGE", stackgroup="one")
    )

    fig.update_layout(
        title="Historic Generation Mix", yaxis_title="Generation Mix", barmode="stack"
    )
    fig.write_html("/tmp/historic_generation_mix.html")
