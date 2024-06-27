import datetime
import os
import sys

import pandas as pd
import requests


def download_file(filename, download_dir):
    url = r"https://downloads.elexonportal.co.uk/p114/download?key=x1zwyzsk0w53xts&filename={}".format(
        filename
    )
    local_filename = os.path.join(download_dir, filename)
    if not os.path.isfile(local_filename):
        print(r"Downloading {}".format(filename))
        response = requests.get(url)
        with open(local_filename, "wb") as f:
            f.write(response.content)
    else:
        print(r"Skipping {}".format(filename))


def filter_files(files, pattern="_SF_"):
    if len(files) == 0:
        return []
    else:
        return [f for f in files.keys() if pattern in f]


def get_list_of_files(date):
    url = r"https://downloads.elexonportal.co.uk/p114/list?key=x1zwyzsk0w53xts&date={}&filter=s0142".format(
        date.strftime("%Y-%m-%d")
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main(start_date, end_date, download_dir):
    date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    while date < end_date:
        files = get_list_of_files(date)
        for f in filter_files(files):
            download_file(f, download_dir)
        date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
