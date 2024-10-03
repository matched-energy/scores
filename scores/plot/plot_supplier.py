import datetime

from pathlib import Path

import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import scores.configuration.conf as conf



def plot_load(df: pd.DataFrame) -> None:
    fig = go.Figure(
        data=go.Scatter(
            x=df["Settlement Datetime"], y=df["Period Information Imbalance Volume"]
        )
    )
    fig.show()

    
def plot_load_and_gen(
    hh_generation: pd.DataFrame, l_hh: pd.Series, output_path: Path
) -> None:

    for tech in conf.read("generation.yaml", conf_dir=True)["TECH"]:
    hh_generation["total"] = hh_generation.drop(columns=["DATETIME"]).sum(axis=1)
    # row_heights = [0.7, 0.3]
    row_heights = [1]
    fig = make_subplots(
        rows=len(row_heights),
        cols=1,
        row_heights=row_heights,
        shared_xaxes=True,
        vertical_spacing=0.2,
    )
    # fig.add_trace(
    #     go.Scatter(
    #         x=hh_generation["DATETIME"],
    #         y=hh_generation["total"] * 2,  # MW
    #         name="renewable supply",
    #     )
    # )

    # Calculate the differences
    lower_dt = datetime.datetime(2022, 4, 1, tzinfo=datetime.timezone.utc)
    upper_dt = datetime.datetime(2023, 4, 1, tzinfo=datetime.timezone.utc)
    # lower_dt = datetime.datetime(2022, 8, 28, 6, tzinfo=datetime.timezone.utc)
    # upper_dt = datetime.datetime(2022, 8, 30, 17, tzinfo=datetime.timezone.utc)
    y_dtick = 1000
    y_range_min = 0
    y_range_max = 2000
    hh_generation["DATETIME"] = pd.to_datetime(hh_generation["DATETIME"])
    supply = hh_generation["total"] * 2
    supply = supply[
        (hh_generation["DATETIME"] >= lower_dt) & (hh_generation["DATETIME"] < upper_dt)
    ]
    load = l_hh * 2
    hh_generation = hh_generation.reindex(load.index)
    load = load[
        (hh_generation["DATETIME"] >= lower_dt) & (hh_generation["DATETIME"] < upper_dt)
    ]
    hh_generation = hh_generation[
        (hh_generation["DATETIME"] >= lower_dt) & (hh_generation["DATETIME"] < upper_dt)
    ]
    supply, load = supply.align(load)

    # load = load[
    #     (hh_generation["DATETIME"] >= datetime.datetime(2022, 6, 1))
    #     & (hh_generation["DATETIME"] >= datetime.datetime(2022, 6, 1))
    # ]

    # Create masks for the regions where load > supply and supply > load
    shortfall = load > supply
    surplus = supply > load

    cumulative_shortfall = np.cumsum(load - np.where(shortfall, supply, load))
    # cumulative_shortfall -= 1.643834e6
    cumulative_load = np.cumsum(load)
    # cumulative_load -= 7.088808e6
    hh_matching_score = 100 - 100 * cumulative_shortfall / load.sum()
    hh_matching_score_std = hh_matching_score.expanding().std()

    cumulative_annual_shortfall = cumulative_load - np.cumsum(supply)
    yr_matching_score = 100 - 100 * cumulative_annual_shortfall / load.sum()

    color_surplus = "rgba(195, 255, 165, 0.3)"  # light green
    color_supply = "#92bf7c"  # dark green
    color_shortfall = "rgba(225, 165, 255, 0.3)"  # light purple
    color_load = "#a97cbf"  # dark purple

    if len(row_heights) == 2:
        fig.add_trace(
            go.Scatter(
                x=hh_generation["DATETIME"],
                # y=cumulative_shortfall,
                y=hh_matching_score,
                mode="lines",
                line=dict(color="black", width=2),
                name="hh matching score",
                showlegend=False,
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=hh_generation["DATETIME"],
                # y=cumulative_annual_shortfall,
                y=yr_matching_score,
                mode="lines",
                line=dict(color="black", width=2, dash="dash"),
                name="yr matching score",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # Add the upper bound trace (for filling)
    # fig.add_trace(
    #     go.Scatter(
    #         x=hh_generation["DATETIME"],
    #         y=hh_matching_score + hh_matching_score_std,
    #         mode="lines",
    #         name="Upper Bound",
    #         line=dict(width=0),  # Hide the line
    #         showlegend=False,
    #     ),
    #     row=2,
    #     col=1,
    # )

    # # Add the lower bound trace (for filling)
    # fig.add_trace(
    #     go.Scatter(
    #         x=hh_generation["DATETIME"],
    #         y=hh_matching_score - hh_matching_score_std,
    #         mode="lines",
    #         name="Lower Bound",
    #         fill="tonexty",  # Fill the area between the lower and upper bounds
    #         fillcolor="rgba(173, 216, 230, 0.3)",  # Light blue fill with some transparency
    #         line=dict(width=0),  # Hide the line
    #         showlegend=False,
    #     ),
    #     row=2,
    #     col=1,
    # )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=load,
            mode="lines",
            line=dict(color=color_load, width=3),
            name="demand",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=np.where(
                surplus, supply, load
            ),  # take supply when there is surplus, otherwise load
            fill="tonexty",
            mode="none",
            fillcolor=color_surplus,
            name="surplus",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=supply,
            mode="lines",
            line=dict(color=color_supply, width=3),
            name="supply",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=np.where(
                shortfall, load, supply
            ),  # take load when there is shortfall, otherwise supply
            fill="tonexty",
            mode="none",
            fillcolor=color_shortfall,
            name="shortfall",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    fig.update_layout(
        xaxis=dict(
            # range=[x_range_min, x_range_max],
            rangeslider=dict(
                visible=False,
            ),
            dtick=24 * 60 * 60 * 1000,
            title_font=dict(size=14),
            tickfont=dict(size=14),
        ),
        xaxis2=dict(
            # range=[x_range_min, x_range_max],
            rangeslider=dict(
                visible=False,
            ),
            dtick=24 * 60 * 60 * 1000,
            title_font=dict(size=14),
            tickfont=dict(size=14),
        ),
        yaxis=dict(
            title="Power (MW)",
            dtick=y_dtick,
            range=(y_range_min, y_range_max),
            title_font=dict(size=14),
            tickfont=dict(size=14),
        ),
        yaxis2=dict(
            title="Matching Score (%)",
            range=(80, 120),
            dtick=20,
            title_font=dict(size=14),
            tickfont=dict(size=14),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        width=1200,
        height=800,
        margin=dict(l=10, r=10, b=40, t=40, pad=0),
    )
    fig.write_html(output_path)
    fig.write_image(f"{output_path}.png", scale=3)


def plot_load_and_gen_details(
  hh_generation: pd.DataFrame, 
  l_hh: pd.Series, 
  hh_load: pd.DataFrame, 
  output_path: Path
) -> None:
    fig = go.Figure()

    gen_plot_classes = dict(
        OTHER=dict(color="#9F6094"),  # Magenta (hue 300°)
        WIND=dict(color="#78F01D"),  # Green (hue 120°)
        SOLAR=dict(color="#E2F01D"),  # Light Green (hue 90°)
        BIOMASS=dict(color="#F0951D"),  # Orange (hue 30°)
        HYDRO=dict(color="#87d6d5"),  # Turquoise
        ## Flex
    )
    print(hh_generation.columns)

    for tech, conf in gen_plot_classes.items():
        fig.add_trace(
            go.Scatter(
                x=hh_generation["DATETIME"],
                y=hh_generation[f"{tech}_supplier"] * 2,  # MW
                name=tech,
                stackgroup="one",
                line=dict(width=0.5, color=conf["color"]),
                fillcolor=conf["color"],
                showlegend=True,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=l_hh * 2,
            # x=l_hh["Settlement Datetime"],
            # y=l_hh["Period Information Imbalance Volume"] * 2,  # MW
            name="Inferred Consumption",
            line=dict(color="black", width=2),
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=hh_load["BM Unit Metered Volume"] * 2,
            # x=l_hh["Settlement Datetime"],
            # y=l_hh["Period Information Imbalance Volume"] * 2,  # MW
            name="BMU Volume",
            line=dict(color="black", width=1, dash="dot"),
            showlegend=True,
        )
    )
    range_min = pd.to_datetime(hh_generation["DATETIME"].min())
    range_max = range_min + datetime.timedelta(days=7)
    fig.update_layout(
        xaxis=dict(
            range=[range_min, range_max],
            rangeslider=dict(
                visible=True,
            ),
        ),
        yaxis=dict(
            title="MW",
            # dtick=1000,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),  # Adjust the size to make the legend smaller
        ),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        width=790,
        height=633,
        margin=dict(l=10, r=10, b=10, t=10, pad=0),
    )
    fig.write_html(output_path)


def plot_load_and_gen_details_1(hh_generation, l_hh, output_path):
    fig = go.Figure()

    # from scores.plot.plot_grid_gen import GEN_CLASSES, GEN_PLOT_CLASSES, add_cols

    # print(GEN_PLOT_CLASSES)
    # GEN_PLOT_CLASSES["OTHER"] = GEN_PLOT_CLASSES["IMPORTS_AND_OTHER"]
    # GEN_PLOT_CLASSES.pop("IMPORTS_AND_OTHER", None)
    # GEN_PLOT_CLASSES.pop("COAL", None)
    # GEN_PLOT_CLASSES.pop("GAS", None)
    # GEN_PLOT_CLASSES.pop("NUCLEAR", None)
    # GEN_PLOT_CLASSES.pop("STORAGE_AND_HYDRO", None)

    supply_total = hh_generation.drop(columns=["DATETIME"]).sum(axis=1) * 2  # MW
    load = l_hh * 2  # MW
    supply_total, load = supply_total.align(load)

    color_load = mcolors.to_hex(mcolors.hsv_to_rgb([0 / 360, 0.45, 0.98]))
    color_match = mcolors.to_hex(mcolors.hsv_to_rgb([93 / 360, 0.35, 0.98]))
    color_surplus = mcolors.to_hex(mcolors.hsv_to_rgb([192 / 360, 0.075, 0.98]))
    color_deficit = mcolors.to_hex(mcolors.hsv_to_rgb([69 / 360, 0.05, 0.6]))

    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=np.where(supply_total < load, supply_total, load),
            name="supply",
            line=dict(width=0, color=color_match),
            fill="tozeroy",
            fillcolor=color_match,
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=load,
            name="load",
            line=dict(color=color_load, width=3, smoothing=1.3),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=np.where(
                supply_total < load,
                supply_total,
                load,
            ),
            name="load",
            fill="tonexty",
            fillcolor=color_deficit,
            line=dict(color=color_deficit, width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],  # TODO
            y=load,
            name="load",
            line=dict(color=color_load, width=3, smoothing=1.3),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hh_generation["DATETIME"],
            y=np.where(
                supply_total > load,
                supply_total,
                load,
            ),
            name="load",
            fill="tonexty",
            fillcolor=color_surplus,
            line=dict(color=color_surplus, width=0),
            showlegend=True,
        )
    )
    range_min = pd.to_datetime(hh_generation["DATETIME"].min())
    range_max = range_min + datetime.timedelta(days=45)
    fig.update_layout(
        xaxis=dict(
            range=[range_min, range_max],
            # rangeslider=dict(
            #     visible=True,
            # ),
        ),
        yaxis=dict(
            title="MW",
            dtick=1000,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        width=1200,
        height=800,
        margin=dict(l=10, r=10, b=10, t=10, pad=0),
    )
    fig.write_html(output_path)
