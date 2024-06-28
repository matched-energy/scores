import pprint
import sys

import pandas as pd
import plotly.express as px


def read(filename, start, end):
    d = pd.read_csv(filename)
    d["DATETIME"] = pd.to_datetime(d["DATETIME"])
    return d[(d["DATETIME"] > start) & (d["DATETIME"] < end)]


def plot(d):
    import plotly.graph_objects as go

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


def group_by_month_and_tech(d):
    d["month"] = d["DATETIME"].dt.to_period("M")
    return (
        d[["month", "BIOMASS", "HYDRO", "OTHER", "WIND", "SOLAR"]]
        .groupby(["month"])
        .sum()
        / 2  # convert from MW to MWh
    ).reset_index()


def main(path_historic_generation_mix, start, end, path_grid_hh, path_grid_month_tech):
    d = read(path_historic_generation_mix, start, end)
    d.to_csv(path_grid_hh, index=False)
    plot(d)
    d_agg_month_tech = group_by_month_and_tech(d)
    d_agg_month_tech.to_csv(path_grid_month_tech, index=False)


if __name__ == "__main__":
    main(
        path_historic_generation_mix=sys.argv[1],
        start=sys.argv[2],
        end=sys.argv[3],
        path_grid_hh=sys.argv[4],
        path_grid_month_tech=sys.argv[5],
    )
