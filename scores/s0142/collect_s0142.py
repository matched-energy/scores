import datetime
import sys
from pathlib import Path

import pandas as pd
import requests


def download_file(filename: str, download_dir: Path) -> None:
    url = rf"https://downloads.elexonportal.co.uk/p114/download?key=x1zwyzsk0w53xts&filename={filename}"
    local_filepath = download_dir / filename
    if not local_filepath.is_file():
        print(rf"Downloading {filename}")
        response = requests.get(url)
        with open(local_filepath, "wb") as f:
            f.write(response.content)
    else:
        print(rf"Skipping {filename}")


def filter_files(files: dict, pattern: str = "_SF_") -> list[str]:
    if len(files) == 0:
        return []

    return [f for f in files.keys() if pattern in f]


def get_dict_of_files(date: pd.Timestamp) -> dict:
    """Returns a dict with filenames as the keys"""
    url = rf"https://downloads.elexonportal.co.uk/p114/list?key=x1zwyzsk0w53xts&date={date:%Y-%m-%d}&filter=s0142"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main(start_date: pd.Timestamp, end_date: pd.Timestamp, download_dir: Path) -> None:
    date = start_date
    end_date = end_date
    while date < end_date:
        files = get_dict_of_files(date)
        for f in filter_files(files):
            download_file(f, download_dir)
        date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(pd.Timestamp(sys.argv[1]), pd.Timestamp(sys.argv[2]), Path(sys.argv[3]))