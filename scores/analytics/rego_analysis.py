import math
from datetime import timedelta
from pathlib import Path

import click
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots

import scores.common
import scores.common.utils
import scores.core.supplier_gen_by_tech_by_month


# Function to calculate the number of full months between two dates
def list_months(start, end):
    months = []
    current = start
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)
    return months


def format_number(num):
    num = int(num)
    if num < 1000:
        return str(num)
    elif 1000 <= num < 1e6:
        return f"{num / 1000:.0f}k"
    elif 1e6 <= num < 1e9:
        return f"{num / 1e6:.0f}M"
    elif 1e9 <= num < 1e12:
        return f"{num / 1e9:.0f}B"
    else:
        return f"{num / 1e12:.0f}T"


tech_simple_colors = dict(
    OTHER="#9F6094",  # Magenta (hue 300°)
    WIND="#78F01D",  # Green (hue 120°)
    SOLAR="#E2F01D",  # Light Green (hue 90°)
    BIOMASS="#F0951D",  # Orange (hue 30°)
    HYDRO="#87d6d5",  # Turquoise
)

tech_simple = {
    "Photovoltaic": "SOLAR",
    "Hydro": "HYDRO",
    "Wind": "WIND",
    "Biomass": "BIOMASS",
    "Biogas": "BIOMASS",
    "Landfill Gas": "BIOMASS",
    "On-shore Wind": "WIND",
    "Hydro 20MW DNC or less": "HYDRO",
    "Fuelled": "BIOMASS",
    "Off-shore Wind": "WIND",
    "Micro Hydro": "HYDRO",
    "Biomass 50kW DNC or less": "BIOMASS",
}


@click.command()
@click.option(
    "--regos",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="Path to REGO csv",
)
@click.option(
    "--suppliers",
    type=str,
    help="Path to suppliers.yaml",
)
def main(regos: Path, suppliers: str) -> None:
    for supplier in scores.common.utils.from_yaml_file(suppliers):
        plot_supplier(regos, supplier["rego_organisation_name"])


def plot_supplier(regos: Path, current_holder: str, output_path: Path) -> None:
    regos_supplier = scores.core.supplier_gen_by_tech_by_month.read(
        regos, current_holder_organisation_name=current_holder
    )
    regos_supplier = scores.core.supplier_gen_by_tech_by_month.parse_output_period(
        regos_supplier
    )
    regos_supplier["MWh"] = (
        regos_supplier["MWh Per Certificate"] * regos_supplier["No. Of Certificates"]
    )
    regos_supplier["tech_simple"] = regos_supplier["Technology Group"].map(tech_simple)

    regos_supplier_by_station = (
        regos_supplier.groupby("Generating Station / Agent Group")
        .agg(
            MWh=("MWh", "sum"),
            Technology_group=("Technology Group", "first"),
            tech_simple=("tech_simple", "first"),
        )
        .sort_values(by="MWh", ascending=False)
    )
    regos_supplier_by_station_MWh_cumsum = regos_supplier_by_station["MWh"].cumsum()
    regos_supplier_by_station_hist = (
        pd.cut(
            regos_supplier_by_station["MWh"],
            bins=[0, 1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6],
        )
        .value_counts()
        .sort_index()
    )
    regos_supplier_by_station_tech_simple_color_map = regos_supplier_by_station[
        "tech_simple"
    ].map(tech_simple_colors)
    regos_supplier_by_tech_simple = (
        regos_supplier.groupby("tech_simple")["MWh"].sum().sort_values(ascending=False)
    )
    rego_supplier_by_station_term = {}
    for index, row in regos_supplier.iterrows():
        row = row.to_dict()
        if row["Generating Station / Agent Group"] not in rego_supplier_by_station_term:
            rego_supplier_by_station_term[row["Generating Station / Agent Group"]] = (
                set()
            )
        rego_supplier_by_station_term[row["Generating Station / Agent Group"]].update(
            list_months(row["start"], row["end"])
        )
    rego_supplier_by_station_term_df = (
        pd.DataFrame(
            [
                [station, len(months) - 1]
                for station, months in rego_supplier_by_station_term.items()
            ],
            columns=["Generating Station / Agent Group", "term_months"],
        )
        .set_index("Generating Station / Agent Group")
        .reindex(regos_supplier_by_station.index)
    )
    print(rego_supplier_by_station_term_df)

    regos_all = scores.core.supplier_gen_by_tech_by_month.read(regos)
    regos_all["MWh"] = (
        regos_all["MWh Per Certificate"] * regos_all["No. Of Certificates"]
    )
    regos_all_by_station = (
        regos_all.groupby("Generating Station / Agent Group")["MWh"]
        .sum()
        .reindex(regos_supplier_by_station.index)
    )

    row_heights = [0.2] * 5  # [0.33, 0.33, 0.33]
    column_widths = [0.8, 0.2]
    subplot_titles = {
        "<b>MWh per generator</b>": (0, 1),
        "<b>Offtake by contract size</b>": (0.75, 1),
        "<b>Offtake by asset class</b>": (0.75, 0.8 - 0.01),
        "<b>Offtake as fraction of whole</b>": (0, 0.4 - 0.02),
        "<b>Shared/exclusive offtake</b>": (0.75, 0.6 - 0.025),
        "<b>Offtake term</b>": (0, 0.2 - 0.03),
        "<b>Offtake term (months)</b>": (0.75, 0.4 - 0.02),
        "<b>Offtake volume versus term</b>": (0.75, 0.2 - 0.04),
    }
    fig = make_subplots(
        rows=len(row_heights),
        cols=len(column_widths),
        row_heights=row_heights,
        column_widths=column_widths,
        vertical_spacing=0.05,
        horizontal_spacing=0.1,
        specs=[
            [{"secondary_y": True, "rowspan": 3}, {"secondary_y": True}],
            [None, {"secondary_y": True}],
            [None, {"secondary_y": True, "rowspan": 1}],
            [{"secondary_y": True}, {"secondary_y": True}],
            [{"secondary_y": True}, {"secondary_y": True}],
        ],
        subplot_titles=list(subplot_titles.keys()),
    )
    if len(regos_supplier) == 0:
        fig.write_html(output_path)
        return

    ## 1 PARETO
    fig.add_trace(
        go.Bar(
            x=regos_supplier_by_station.index,
            y=regos_supplier_by_station["MWh"],
            marker=dict(color=regos_supplier_by_station_tech_simple_color_map),
            showlegend=False,
        ),
        col=1,
        row=1,
        secondary_y=False,
    )
    # Manually add a legend by creating dummy traces for each technology group
    for tech_group, color in tech_simple_colors.items():
        fig.add_trace(
            go.Bar(
                x=[None],  # No data, only for legend
                y=[None],
                marker=dict(color=color),
                name=tech_group,
                showlegend=True,
            ),
            col=1,
            row=1,
            secondary_y=False,
        )
    fig.add_trace(
        go.Scatter(
            x=regos_supplier_by_station_MWh_cumsum.index,
            y=regos_supplier_by_station_MWh_cumsum.values,
            showlegend=False,
        ),
        col=1,
        row=1,
        secondary_y=True,
    )

    fig.add_annotation(
        text=f"Cumulative generation = {format_number(regos_supplier_by_station_MWh_cumsum.iloc[-1])} MWh",
        xref="x",
        yref="y",
        x=regos_supplier_by_station_MWh_cumsum.index[
            int(len(regos_supplier_by_station_MWh_cumsum) * 0.93)
        ],
        y=regos_supplier_by_station_MWh_cumsum.iloc[-1] * 0.98,
        col=1,
        row=1,
        showarrow=False,
        font=dict(size=8),
        secondary_y=True,
    )
    fig.update_xaxes(tickangle=-45, matches="x", showticklabels=False, col=1, row=1)
    fig.update_yaxes(
        title=dict(text="<b>MWh</b>", font=dict(size=8)),
        type="log",
        dtick=1,
        col=1,
        row=1,
        secondary_y=False,
    )
    fig.update_yaxes(
        showticklabels=False,
        overlaying="y",
        side="right",
        col=1,
        row=1,
        secondary_y=True,
    )

    ## 2 FRACTIONAL OFFTAKE
    col = 1
    row = 4
    fractional_offtake = (
        100 * regos_supplier_by_station["MWh"] / regos_all_by_station.values
    )
    fig.add_trace(
        go.Scatter(
            x=regos_supplier_by_station.index,
            y=fractional_offtake,
            showlegend=False,
        ),
        col=col,
        row=row,
    )
    fig.update_xaxes(
        showticklabels=False,
        matches="x",
        col=col,
        row=row,
    )
    fig.update_yaxes(
        title=dict(text="<b>%</b>", font=dict(size=8)),
        dtick=25,
        col=col,
        row=row,
    )
    ## TERM LENGTH
    col = 1
    row = 5
    fig.add_trace(
        go.Scatter(
            x=rego_supplier_by_station_term_df.index,
            y=rego_supplier_by_station_term_df["term_months"],
            showlegend=False,
        ),
        col=col,
        row=row,
        secondary_y=False,
    )
    fig.update_xaxes(
        title=dict(font=dict(size=8)),
        tickangle=-45,
        matches="x",
        col=col,
        row=row,
    )
    fig.update_yaxes(
        title=dict(text="<b>months</b>", font=dict(size=8)),
        dtick=6,
        col=col,
        row=row,
        secondary_y=False,
    )

    ## OFFTAKE VOLUMES
    col = 2
    row = 1
    x2 = [
        f"{format_number(interval.left)} MWh"
        for interval in regos_supplier_by_station_hist.index
    ]
    fig.add_trace(
        go.Bar(
            x=x2,
            y=regos_supplier_by_station_hist.values,
            showlegend=False,
        ),
        col=col,
        row=row,
        secondary_y=False,
    )
    fig.update_xaxes(tickangle=-45, col=2, row=1, tickfont=dict(size=7))
    fig.update_yaxes(
        title=dict(text="<b>Generator count</b>", font=dict(size=8)),
        col=col,
        row=row,
    )

    ## BY TECH
    col = 2
    row = 2
    fig.add_trace(
        go.Bar(
            x=regos_supplier_by_tech_simple.index,
            y=regos_supplier_by_tech_simple.values,
            showlegend=False,
        ),
        col=col,
        row=row,
    )
    fig.update_xaxes(tickfont=dict(size=8))
    fig.update_yaxes(
        title=dict(text="<b>MWh</b>", font=dict(size=8)),
        col=col,
        row=row,
    )

    ## BY OWNERSHIP
    shared = regos_supplier_by_station[fractional_offtake - 100 < 0]
    exclusive = regos_supplier_by_station[fractional_offtake - 100 == 0]
    fig.add_trace(
        go.Bar(
            x=["shared", "exclusive"],
            y=[shared["MWh"].sum(), exclusive["MWh"].sum()],
            showlegend=False,
        ),
        col=2,
        row=3,
    )
    # fig.add_annotation(
    #     text="MWh",
    #     xref="x",
    #     yref="y",
    #     x="exclusive",
    #     y=exclusive["MWh"].sum() * 0.85,
    #     col=2,
    #     row=3,
    #     showarrow=False,
    #     font=dict(size=8),
    #     secondary_y=False,
    # )
    # shared_generator_count = [len(shared["MWh"]), len(exclusive["MWh"])]
    # fig.add_trace(
    #     go.Scatter(
    #         x=["shared", "exclusive"],
    #         y=shared_generator_count,
    #         mode="markers",
    #         showlegend=False,
    #     ),
    #     col=2,
    #     row=3,
    #     secondary_y=True,
    # )
    # fig.add_annotation(
    #     text="# Generators",
    #     xref="x",
    #     yref="y",
    #     x="exclusive",
    #     y=shared_generator_count[1] * 0.95,
    #     col=2,
    #     row=3,
    #     showarrow=False,
    #     font=dict(size=8),
    #     secondary_y=True,
    # )
    fig.update_yaxes(
        title=dict(text="<b>MWh</b>", font=dict(size=8)),
        col=2,
        row=3,
    )
    # fig.update_yaxes(
    #     range=[0, math.ceil(shared_generator_count[0] / 50) * 50],
    #     title=dict(text="<b>Count</b>", font=dict(size=8)),
    #     col=2,
    #     row=3,
    #     secondary_y=True,
    # )

    ## TERM HIST
    col = 2
    row = 4
    # term_hist = (
    #     pd.cut(
    #         rego_supplier_by_station_term_df["term_months"],
    #         bins=[0, 1, 2, 3, 6, 9, 12, 24],
    #     )
    #     .value_counts()
    #     .sort_index()
    # )
    # x = [f"< {interval.right} m" for interval in term_hist.index]
    # fig.add_trace(
    #     go.Bar(
    #         x=x,
    #         y=term_hist.values,
    #         showlegend=False,
    #     ),
    #     col=col,
    #     row=row,
    #     secondary_y=False,
    # )
    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24]
    regos_supplier_by_station["term_months"] = pd.cut(
        rego_supplier_by_station_term_df["term_months"],
        bins=bins,
    )
    vol_hist = regos_supplier_by_station.groupby("term_months")["MWh"].sum()
    fig.add_trace(
        go.Bar(
            # x=[str(i) for i in vol_hist.index],
            x=[f"> {b}" for b in bins],
            y=vol_hist.values,
            showlegend=False,
        ),
        col=col,
        row=row,
        secondary_y=False,
    )
    fig.update_xaxes(
        tickfont=dict(size=7),
        tickangle=-45,
        col=col,
        row=row,
    )
    fig.update_yaxes(
        title=dict(text="<b>MWh</b>", font=dict(size=8)),
        col=col,
        row=row,
    )

    ## TERM-VOL SCATTER
    col = 2
    row = 5
    fig.add_trace(
        go.Scatter(
            x=rego_supplier_by_station_term_df["term_months"],
            y=regos_supplier_by_station["MWh"],
            mode="markers",
            showlegend=False,
        ),
        col=col,
        row=row,
        secondary_y=False,
    )
    fig.update_yaxes(
        title=dict(text="<b>MWh</b>", font=dict(size=8)),
        col=col,
        row=row,
        secondary_y=False,
    )
    fig.update_xaxes(
        title=dict(text="<b>months</b>", font=dict(size=8)),
        dtick=6,
        col=col,
        row=row,
    )

    ## FINAL UPDATES
    fig.update_layout(
        annotations=[
            (
                dict(
                    x=subplot_titles.get(text)[0],
                    y=subplot_titles.get(text)[1],
                    text=text,
                    showarrow=False,
                    xanchor="left",
                    font=dict(
                        size=10,
                        color="black",
                    ),
                )
                if (text := annotation["text"]) in subplot_titles
                else annotation
            )
            for annotation in fig["layout"]["annotations"]
        ],
        legend=dict(
            orientation="h",
            x=0.67,
            y=0.418,
            xanchor="right",
            yanchor="top",
            font=dict(size=8),
            tracegroupgap=2,
        ),
        plot_bgcolor="rgba(255,255,255,1)",
        paper_bgcolor="rgba(255,255,255,1)",
    )
    fig.write_html(output_path)


if __name__ == "__main__":
    main()
