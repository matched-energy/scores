import datetime
import sys

import pandas as pd
import plotly.graph_objects as go

import scores.configuration.conf as conf


def plot_load(df):
    fig = go.Figure(
        data=go.Scatter(
            x=df["Settlement Datetime"], y=df["Period Information Imbalance Volume"]
        )
    )
    fig.show()


def plot_load_and_gen(hh_generation, l_hh, output_path):
    fig = go.Figure()

    for tech in conf.read("generation.yaml", conf_dir=True)["TECH"]:
        fig.add_trace(
            go.Scatter(
                x=hh_generation["DATETIME"],
                y=hh_generation[f"{tech}_supplier"] * 2,  # MW
                name=tech,
                stackgroup="one",
                mode="none",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=l_hh * 2,
            # x=l_hh["Settlement Datetime"],
            # y=l_hh["Period Information Imbalance Volume"] * 2,  # MW
            name="load",
            line=dict(color="black", width=2),
        )
    )
    range_min = pd.to_datetime(hh_generation["DATETIME"].min())
    range_max = range_min + datetime.timedelta(days=45)
    fig.update_layout(
        xaxis=dict(
            range=[range_min, range_max],
            rangeslider=dict(
                visible=True,
            ),
        ),
        yaxis=dict(
            title="MW",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
    )
    fig.write_html(output_path)
