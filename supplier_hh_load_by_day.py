import glob
import gzip
import os
import sys
from io import StringIO

import numpy as np
import pandas as pd

COLUMN_MAP_APD = {
    1: "Production/Consumption Flag",
    2: "BSSC Limited Cost Allocation",
    3: "Energy Imbalance Charge",
    4: "Information Imbalance Charge",
    5: "Residual Cashflow Reallocation Charge",
    6: "Account Bilateral Contract Volume",
    7: "Account Period Balancing Services Volume",
    8: "Account Energy Imbalance Volume",
    9: "Account Credited Energy Volume",
    10: "Residual Cashflow Reallocation Proportion",
}

COLUMN_MAP_BP7 = {
    1: "BM Unit Id",
    2: "Information Imbalance Cashflow",
    3: "BM Unit Period Non-Delivery Charge",
    4: "Period FPN",
    5: "Period BM Unit Balancing Services Volume",
    6: "Period Information Imbalance Volume",
    7: "Period Expected Metered Volume",
    8: "BM Unit Metered Volume",
    9: "Period BM Unit Non-Delivered Bid Volume",
    10: "Period BM Unit Non-Delivered Offer Volume",
    11: "Transmission Loss Factor",
    12: "Transmission Loss Multiplier",
    13: "Trading Unit Name",
    14: "Total Trading Unit Metered Volume",
    15: "BM Unit Applicable Balancing Services Volume",
    16: "Period Supplier BM Unit Delivered Volume",
    17: "Period Supplier BM Unit Non BM ABSVD Volume",
}


def calculate_half_hourly_load(df_final):
    return (
        df_final[df_final["BM Unit Id"].str.contains("^2__", regex=True)]
        .groupby(["Settlement Date", "Settlement Period"])[
            [
                "Period BM Unit Balancing Services Volume",
                "Period Information Imbalance Volume",
                "Period Expected Metered Volume",
                "Transmission Loss Factor",
                "Transmission Loss Multiplier",
                "BM Unit Applicable Balancing Services Volume",
                "Period Supplier BM Unit Delivered Volume",
                "Period Supplier BM Unit Non BM ABSVD Volume",
            ]
        ]
        .sum()
        .reset_index()
    )


def extract_data(df, bsc_party_ids):

    def f(_df, _idx, bsc_party_id, header="APD", column_map=COLUMN_MAP_APD):
        lines = []

        # Loop through all nested rows for the BSC Party Id using the low row limit
        for i, line in _df[_idx + 1 :].iterrows():
            if line[0] == "SP7":  # Identify the Settlement Period
                SP = int(line[1])
            if line[0] == header:  # Identify the APD for the Settlement Period
                lines.append(
                    np.append(
                        line,
                        [
                            SP,
                            bsc_party_id,
                        ],
                    )
                )

            if line[0] == "BPH":  # Exit loop once next BPH has been detected
                break

        df1 = pd.DataFrame(
            lines, columns=list(range(len(lines[0]) - 2)) + ["Settlement Period", "BSC"]
        )

        settlement_date = _df.loc[1, 1]  # Identify Settlement Period for csv file name
        run_type = _df.loc[1, 2]  # Identify Settlement Run Type
        df1["Settlement Date"] = (
            settlement_date[6:8]
            + "/"
            + settlement_date[4:6]
            + "/"
            + settlement_date[0:4]
        )  # Add Settlement Date to DataFrame
        df1["Settlement Run Type"] = run_type  # Add Settlement Run Type to DataFrame

        df_final = df1.loc[
            :,
            ["BSC", "Settlement Date", "Settlement Period", "Settlement Run Type"]
            + list(range(1, len(column_map) + 1)),
        ]  # Extract relevant columns of interest
        return df_final.rename(columns=column_map)

    # Loop through each row in the DataFrame
    for i, line in df.iterrows():
        if (
            line[0] == "BPH"
        ):  # Identify the BSC Party through the BSC Party Header (BPH) rows in the file
            if (
                line[8] in bsc_party_ids
            ):  # Check if the row corresponds to the user inputted BSC Party Id
                bsc_party_id = line[8]

                df_final = f(df, i, bsc_party_id, "BP7", COLUMN_MAP_BP7)
                df_final.reset_index(
                    drop=True, inplace=True
                )  # Reset Index of DataFrame

                df_final["BM Unit Metered Volume"] = df_final[
                    "BM Unit Metered Volume"
                ].astype(float)
                df_final["Period BM Unit Balancing Services Volume"] = df_final[
                    "Period BM Unit Balancing Services Volume"
                ].astype(float)
                df_final["Period Expected Metered Volume"] = df_final[
                    "Period Expected Metered Volume"
                ].astype(float)
                df_final["Period Information Imbalance Volume"] = df_final[
                    "Period Information Imbalance Volume"
                ].astype(float)
                df_final["Transmission Loss Factor"] = df_final[
                    "Transmission Loss Factor"
                ].astype(float)
                df_final["Transmission Loss Multiplier"] = df_final[
                    "Transmission Loss Multiplier"
                ].astype(float)
                df_final["BM Unit Applicable Balancing Services Volume"] = df_final[
                    "BM Unit Applicable Balancing Services Volume"
                ].astype(float)
                df_final["Period Supplier BM Unit Delivered Volume"] = df_final[
                    "Period Supplier BM Unit Delivered Volume"
                ].astype(float)
                df_final["Period Supplier BM Unit Non BM ABSVD Volume"] = df_final[
                    "Period Supplier BM Unit Non BM ABSVD Volume"
                ].astype(float)
                df_final["Settlement Period"] = df_final["Settlement Period"].astype(
                    int
                )

                yield bsc_party_id, df_final


def read_csv(content):
    col_count = [len(l.split("|")) for l in content.splitlines()]
    column_index = [i for i in range(0, max(col_count))]
    return pd.read_csv(
        StringIO(content), header=None, delimiter="|", names=column_index
    )


def process_file(filename, input_dir, output_dir, bsc_party_ids):
    input_path = os.path.join(input_dir, filename)
    output_path_prefix = os.path.join(output_dir, filename.strip(".gz"))
    with gzip.open(input_path, "rt") as f_in:
        if not glob.glob(output_path_prefix + "*"):
            print("Processing {}".format(input_path))
            df = read_csv(f_in.read())
            for bsc, df_final in extract_data(df, bsc_party_ids.split(" ")):
                load = calculate_half_hourly_load(df_final)
                load.to_csv(
                    output_path_prefix + "_{}.csv".format(bsc),
                    index=False,
                )
        else:  # Skip if file already exists
            print("Skipping {}".format(input_path))


def main(input_dir, output_dir, bsc_party_ids):
    filenames = sorted(
        [
            filename
            for filename in os.listdir(input_dir)
            if filename.startswith("S0142") and filename.endswith(".gz")
        ]
    )
    for filename in filenames:
        process_file(filename, input_dir, output_dir, bsc_party_ids)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
