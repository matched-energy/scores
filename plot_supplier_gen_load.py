import datetime
import sys

import pandas as pd
import plotly.graph_objects as go

TECH = ["BIOMASS", "HYDRO", "OTHER", "WIND", "SOLAR"]


def plot_old(hh_generation, hh_load):
    fig = go.Figure()

    for tech in TECH:
        fig.add_trace(
            go.Scatter(
                x=hh_generation["DATETIME"],
                y=hh_generation[f"{tech}_supplier"] * 2,  # MW
                name=tech,
                stackgroup="one",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=hh_load["Settlement Datetime"],
            y=hh_load["Period Information Imbalance Volume"] * 2,  # MW
            name="load",
            line=dict(color="black", width=2),
        )
    )
    fig.update_layout(
        yaxis=dict(
            title="MW",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
    )
    fig.write_html("/tmp/supplier_generation_and_load.html")


def plot(hh_generation, hh_load):

    def slice(start, end):
        print(start, end)
        data = []
        for tech in TECH:
            data.append(
                go.Scatter(
                    x=hh_generation["DATETIME"][start:end],
                    y=hh_generation[f"{tech}_supplier"][start:end] * 2,  # MW
                    name=tech,
                    stackgroup="one",
                    # mode="none",
                )
            )
        data.append(
            go.Scatter(
                x=hh_load["Settlement Datetime"][start:end],
                y=hh_load["Period Information Imbalance Volume"][start:end] * 2,  # MW
                name="load",
                line=dict(color="black", width=2),
            )
        )
        return data

    layout = go.Layout(
        yaxis=dict(
            title="MW",
        ),
        xaxis=dict(
            range=[datetime.datetime(2022, 4, 1), datetime.datetime(2022, 4, 30)],
            rangeslider=dict(
                visible=True,
            ),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        width=1200,
        height=700,
    )

    d = slice(0, 100000)
    fig = go.Figure(
        data=d,
        # frames=[go.Frame(data=d) for i in range(7)],
        layout=layout,
    )
    for i, f in enumerate(fig.frames):
        f.layout.update(
            xaxis=dict(
                range=[
                    datetime.datetime(2022, 4, 1),
                    datetime.datetime(2022, 4, 7) + datetime.timedelta(days=i),
                ],
                rangeslider=dict(
                    visible=True,
                ),
            ),
        )
    fig.write_html("/tmp/supplier_generation_and_load.html")
    return fig


def plot_slider(hh_generation, hh_load):

    def slice(start, end):
        print(start, end)
        data = []
        for tech in TECH:
            data.append(
                go.Scatter(
                    x=hh_generation["DATETIME"][start:end],
                    y=hh_generation[f"{tech}_supplier"][start:end] * 2,  # MW
                    name=tech,
                    stackgroup="one",
                )
            )
        data.append(
            go.Scatter(
                x=hh_load["Settlement Datetime"][start:end],
                y=hh_load["Period Information Imbalance Volume"][start:end] * 2,  # MW
                name="load",
                line=dict(color="black", width=2),
            )
        )
        return data

    layout = go.Layout(
        yaxis=dict(
            title="MW",
        ),
        # xaxis=dict(
        #     range=[datetime.datetime(2022, 4, 1), datetime.datetime(2022, 4, 7)],
        #     rangeslider=dict(
        #         visible=True,
        #     ),
        # ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
    )

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 3, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }
    ranges = []
    frames = []
    for i in range(30):
        i_date = datetime.datetime(2022, 4, 1) + datetime.timedelta(days=i)
        start_idx = i * 48
        end_idx = start_idx + 48 * 7
        ranges.append((i_date, i_date + datetime.timedelta(days=7)))
        print(i, i_date, start_idx, end_idx)
        frames.append(go.Frame(data=slice(start_idx, end_idx), name=str(i)))
        step = {
            "args": [[i]],
            "label": str(i),
            "method": "animate",
        }
        sliders_dict["steps"].append(step)

    layout.update(sliders=[sliders_dict])

    fig = go.Figure(
        data=slice(0, 10000),
        frames=frames,
        layout=layout,
    )

    for i, f in enumerate(fig.frames):
        i_date = datetime.datetime(2022, 4, 1) + datetime.timedelta(days=i)
        f.layout.update(
            xaxis=dict(
                range=[ranges[i][0], ranges[i][1]],
                #     i_date,
                #     i_date + datetime.timedelta(days=7),
                # ],
                # rangeslider=dict(
                #     visible=True,
                # ),
            ),
        )
    fig.write_html("/tmp/supplier_generation_and_load.html")
    return fig
