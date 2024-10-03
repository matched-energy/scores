import collections
import copy
import sys

import pandas as pd
import plotly.graph_objects as go

GEN_CLASSES = collections.OrderedDict(
    NUCLEAR=dict(color="purple"),
    COAL=dict(color="black"),
    GAS=dict(color="teal"),
    WIND=dict(color="green"),
    HYDRO=dict(color="blue"),
    IMPORTS=dict(color="pink"),
    BIOMASS=dict(color="brown"),
    OTHER=dict(color="red"),
    SOLAR=dict(color="yellow"),
    STORAGE=dict(color="violet"),
)


GEN_PLOT_CLASSES = collections.OrderedDict(
    NUCLEAR=dict(color="#9F6075"),  # Purple (hue 240°)
    WIND=dict(color="#78F01D"),  # Green (hue 120°)
    SOLAR=dict(color="#E2F01D"),  # Light Green (hue 90°)
    BIOMASS=dict(color="#F0951D"),  # Orange (hue 30°)
    STORAGE_AND_HYDRO=dict(color="#8A609F"),  # Violet (hue 270°)
    IMPORTS_AND_OTHER=dict(color="#9F6094"),  # Magenta (hue 300°)
    COAL=dict(color="#50565B"),  # Red (hue 0°)
    GAS=dict(color="#687076"),  # Cyan (hue 180°)
    ## Flex
)


def add_cols(d):
    new_d = copy.deepcopy(d)
    new_d["TOTAL"] = sum(new_d[gen_class] for gen_class in GEN_CLASSES.keys())
    new_d["IMPORTS_AND_OTHER"] = new_d["IMPORTS"] + new_d["OTHER"]
    new_d["STORAGE_AND_HYDRO"] = new_d["STORAGE"] + new_d["HYDRO"]
    return new_d


def plot(d):

    fig = go.Figure()
    d = add_cols(d)
    for gen_class, conf in GEN_PLOT_CLASSES.items():
        fig.add_trace(
            go.Scatter(
                x=d["DATETIME"],
                y=100 * d[gen_class] / d["TOTAL"],
                name=gen_class,
                stackgroup="one",
                line=dict(width=0.5, color=conf["color"]),
                fillcolor=conf["color"],
                showlegend=False,
            )
        )

    fig.update_layout(
        yaxis_title="%",
        xaxis=dict(
            range=[
                pd.to_datetime("2022-09-17 03:00"),
                pd.to_datetime("2022-09-23 20:00"),
            ]
        ),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
        width=950,
        height=800,
        margin=dict(l=10, r=10, b=10, t=10, pad=0),
    )
    fig.write_html("/tmp/historic_generation_mix.html")


def plot_aggregate_mix(d):
    fig = go.Figure()
    d = add_cols(d)
    total_sum = d["TOTAL"].sum()
    fractional_totals = {
        gen_class: d[gen_class].sum() / total_sum for gen_class in GEN_CLASSES.keys()
    }

    # Sort the fractional totals in ascending order
    sorted_totals = dict(sorted(fractional_totals.items(), key=lambda item: item[1]))

    # Create a bar chart
    fig = go.Figure(
        go.Bar(
            x=list(sorted_totals.keys()),
            y=list(sorted_totals.values()),
            marker=dict(
                color=[
                    "red" if gen_class == "STORAGE" else "teal"
                    for gen_class in sorted_totals.keys()
                ]
            ),
        )
    )

    # Update layout for better visualization
    fig.update_layout(
        xaxis=dict(
            categoryorder="total ascending",
            tickfont=dict(size=22),
        ),
        yaxis=dict(
            tickfont=dict(size=18),
            tickformat=".0%",
            dtick=0.1,
            title=dict(text="Annual British grid-mix", font=dict(size=22)),
        ),
        template="plotly_white",  # Optional: clean background
        width=1200,
        height=800,
        margin=dict(l=10, r=10, b=10, t=10, pad=0),
    )

    fig.show()


if __name__ == "__main__":
    plot_aggregate_mix(pd.read_csv(sys.argv[1]))
