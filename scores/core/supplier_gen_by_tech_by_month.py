import datetime
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

COLUMNS: list[str] = [
    "Accreditation No.",
    "Generating Station / Agent Group",
    "Station TIC",
    "Scheme",
    "Country",
    "Technology Group",
    "Generation Type",
    "Output Period",
    "No. Of Certificates",
    "Start Certificate No.",
    "End Certificate No.",
    "MWh Per Certificate",
    "Issue Date",
    "Certificate Status",
    "Status Date",
    "Current Holder Organisation Name",
    "Company Registration Number",
]


class StatisticsRaw:
    # TODO: rectify StatisticsRaw and StatisticsProcessed classes.=]
    #  Is the intent that they inherit pd.Dataframe?

    def run(d):
        return {
            f.strip("stat_"): getattr(StatisticsRaw, f)(d)
            for f in dir(StatisticsRaw)
            if f.startswith("stat_")
        }

    def stat_cumulative_generation(d):
        return (d["No. Of Certificates"] * d["MWh Per Certificate"]).sum()

    def stat_cumulative_load_by_technology(d):
        s = pd.DataFrame(
            d.groupby("Technology Group")["No. Of Certificates"]
            .sum()
            .sort_values(ascending=False)
        )
        s["fraction"] = s["No. Of Certificates"] / s["No. Of Certificates"].sum()
        return s

    def stat_cumulative_load_by_generating_station(d):
        s = pd.DataFrame(
            d.groupby("Generating Station / Agent Group")["No. Of Certificates"]
            .sum()
            .sort_values(ascending=False)
        )
        s["fraction"] = s["No. Of Certificates"] / s["No. Of Certificates"].sum()
        return s


class StatisticsProcessed:
    def run(d):
        return {
            f.strip("stat_"): getattr(StatisticsProcessed, f)(d)
            for f in dir(StatisticsProcessed)
            if f.startswith("stat_")
        }

    def stat_cumulative_generation(d):
        return d["MWh"].sum()


def read(filepath: Path, current_holder_organisation_name: str) -> pd.DataFrame:
    d = pd.read_csv(filepath, names=COLUMNS, skiprows=4)
    return d[d["Current Holder Organisation Name"] == current_holder_organisation_name]


def parse_output_period(d: pd.DataFrame) -> pd.DataFrame:
    def parse_date_range(date_str: str) -> tuple[pd.Timestamp, pd.Timestamp]:
        if "/" in date_str:
            start, end = date_str.split(" - ")
            return (
                pd.to_datetime(start, dayfirst=True),
                pd.to_datetime(end, dayfirst=True),
            )
        elif " - " in date_str:
            year_start, year_end = date_str.split(" - ")
            start = pd.to_datetime("01/01/" + year_start, dayfirst=True)
            end = pd.to_datetime("31/12/" + year_end, dayfirst=True)
            return start, end
        elif "-" in date_str:
            month_year = pd.to_datetime(date_str, format="%b-%Y")
            start = month_year.replace(day=1)
            end = month_year + pd.offsets.MonthEnd(0)
            return start, end
        else:
            raise ValueError(r"Invalid date string {}".format(date_str))

    # df = pd.DataFrame(d, columns=["date_range"])

    # Apply function to create start and end columns
    d[["start", "end"]] = d["Output Period"].apply(
        lambda x: pd.Series(parse_date_range(x))
    )
    d["end"] += np.timedelta64(1, "D")
    d["months_difference"] = d.apply(
        lambda row: relativedelta(row["end"], row["start"]).years * 12
        + relativedelta(row["end"], row["start"]).months,
        axis=1,
    )

    # # Add columns for each month to represent if it's within the start/end range
    # for month in range(1, 13):
    #     month_name = f"month_{month}_in_range"
    #     df[month_name] = (df["start"].dt.month <= month) & (df["end"].dt.month >= month)

    # df.to_csv("test.csv")
    return d


def calculate_monthly_generation(d: pd.DataFrame) -> pd.DataFrame:
    monthly_generation = []
    for _, row in d.iterrows():
        if row["months_difference"] > 12:
            print(
                r"!!! WARNING!!! Cannot handle period from {} to {} for Accreditation Number {} - allowable range is 1 to 12 months".format(
                    row["start"], row["end"], row["Accreditation No."]
                )
            )
            continue
        for i in range(row["months_difference"]):
            output_year = row["start"].year
            output_month = row["start"].month + i
            if output_month > 12:
                output_month -= 12
                output_year += 1
            output_date = datetime.datetime(
                output_year,
                output_month,
                1,
            )
            monthly_generation.append(
                [
                    row["Generating Station / Agent Group"],
                    row["Technology Group"],
                    row["start"],
                    row["end"],
                    row["months_difference"],
                    output_date,
                    row["No. Of Certificates"]
                    * row["MWh Per Certificate"]
                    / row["months_difference"],
                ]
            )
    return pd.DataFrame(
        monthly_generation,
        columns=[
            "Generating Station / Agent Group",
            "Technology Group",
            "start",
            "end",
            "months_difference",
            "Output Month",
            "MWh",
        ],
    )


def group_by_technology_and_month(d_monthly: pd.DataFrame) -> pd.DataFrame:
    return (
        d_monthly.groupby(["Output Month", "Technology Group"])["MWh"]
        .sum()
        .reset_index()
        .sort_values(by=["Output Month", "Technology Group"])
    )


def simplify_technology_classification(d_agg_month_tech: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Biomass": "BIOMASS",
        "Biomass 50kW DNC or less": "BIOMASS",
        "Biogas": "BIOMASS",
        "Fuelled": "BIOMASS",
        "Hydro": "HYDRO",
        "Landfill Gas": "OTHER",
        "Off-shore Wind": "WIND",
        "On-shore Wind": "WIND",
        "Photovoltaic": "SOLAR",
        "Photovoltaic 50kW DNC or less": "SOLAR",
        "Wind": "WIND",
        "Hydro 20MW DNC or less": "HYDRO",
        "Hydro 50kW DNC or less": "HYDRO",
        "Micro Hydro": "HYDRO",
        "Tidal Flow": "HYDRO",
        "Hydro greater than 20MW DNC": "HYRDRO",
        "Sewage Gas": "OTHER",
        "Biodegradable": "BIOMASS",
    }
    d_agg_month_tech["Technology Group Simplified"] = d_agg_month_tech[
        "Technology Group"
    ].apply(lambda x: mapping[x])
    d_agg_month_simplified_tech = (
        d_agg_month_tech.groupby(["Output Month", "Technology Group Simplified"])["MWh"]
        .sum()
        .reset_index()
        .sort_values(by=["Output Month", "Technology Group Simplified"])
    )
    # return d_agg_month_simplified_tech pivoted on "Technology Group Simplified" with "Output Month" as index
    return d_agg_month_simplified_tech.pivot(
        index="Output Month", columns="Technology Group Simplified", values="MWh"
    ).reset_index()


def main(
    path_raw_rego: Path,
    current_holder_organisation_name: str,
    path_processed_regos: Optional[Path] = None,
    path_processed_agg_month_tech: Optional[Path] = None,
):
    d = read(path_raw_rego, current_holder_organisation_name)
    # TODO filter just redeemed
    d = parse_output_period(d)
    d_monthly = calculate_monthly_generation(d)
    if path_processed_regos:
        d_monthly.to_csv(path_processed_regos, index=False)
    d_agg_month_tech = group_by_technology_and_month(d_monthly)
    stats_processed = StatisticsProcessed.run(d_agg_month_tech)
    d_agg_month_tech = simplify_technology_classification(d_agg_month_tech)
    if path_processed_agg_month_tech:
        d_agg_month_tech.to_csv(path_processed_agg_month_tech, index=False)
    return stats_processed


if __name__ == "__main__":
    main(
        path_raw_rego=Path(sys.argv[1]),
        current_holder_organisation_name=sys.argv[2],
        path_processed_regos=Path(sys.argv[3]),
        path_processed_agg_month_tech=Path(sys.argv[4]),
    )
