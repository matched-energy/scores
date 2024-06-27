import gzip
import os
import sys
from io import StringIO

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
            "Period Information Imbalance Volume"
        ]
        .sum()
        .reset_index()
    )


def extract_data(df, bsc_party_id="PURE"):
    low_lim = 0  # Initiate low limit variable

    # Loop through each row in the DataFrame
    for i, line in df.iterrows():
        if (
            line[0] == "BPH"
        ):  # Identify the BSC Party through the BSC Party Header (BPH) rows in the file
            if (
                line[8] == bsc_party_id
            ):  # Check if the row corresponds to the user inputted BSC Party Id
                low_lim = i  # Assign a low limit for the row No. for which the data file will be iterated

    def f(_df, header="APD", column_map=COLUMN_MAP_APD):
        df1 = pd.DataFrame()  # Create an empty DataFrame to store the data
        df1["Settlement Period"] = 0  # Add a Settlement Period column

        # Loop through all nested rows for the BSC Party Id using the low row limit
        for i, line in _df[low_lim + 1 :].iterrows():
            if line[0] == "SP7":  # Identify the Settlement Period
                SP = line[1]
            if line[0] == header:  # Identify the APD for the Settlement Period
                df1 = df1.append(line)
                df1.loc[i, "Settlement Period"] = SP
            if line[0] == "BPH":  # Exit loop once next BPH has been detected
                break

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
            ["Settlement Date", "Settlement Period", "Settlement Run Type"]
            + list(range(1, len(column_map) + 1)),
        ]  # Extract relevant columns of interest
        return df_final.rename(columns=column_map)

    df_final = f(df, "BP7", COLUMN_MAP_BP7)
    df_final.reset_index(drop=True, inplace=True)  # Reset Index of DataFrame

    df_final["BM Unit Metered Volume"] = df_final["BM Unit Metered Volume"].astype(
        float
    )
    df_final["Period Information Imbalance Volume"] = df_final[
        "Period Information Imbalance Volume"
    ].astype(float)
    df_final["Settlement Period"] = df_final["Settlement Period"].astype(int)

    return df_final  # Display the Dataframe inline for reference


def read_csv(content):
    col_count = [len(l.split("|")) for l in content.splitlines()]
    column_names = [i for i in range(0, max(col_count))]
    return pd.read_csv(
        StringIO(content), header=None, delimiter="|", names=column_names
    )


def process_file(filename, input_dir, output_dir, bsc_party_id):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename).replace(".gz", ".csv")
    with gzip.open(input_path, "rt") as f_in:
        if not os.path.isfile(output_path):
            print("Processing {}".format(input_path))
            df = read_csv(f_in.read())
            df_final = extract_data(df, bsc_party_id)
            load = calculate_half_hourly_load(df_final)
            load.to_csv(output_path, index=False)
        else:  # Skip if file already exists
            print("Skipping {}".format(input_path))


def main(input_dir, output_dir, bsc_party_id):
    filenames = sorted(
        [
            filename
            for filename in os.listdir(input_dir)
            if filename.startswith("S0142") and filename.endswith(".gz")
        ]
    )
    for filename in filenames:
        process_file(filename, input_dir, output_dir, bsc_party_id)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
