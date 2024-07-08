import time
from io import BytesIO
import requests
from urllib.parse import urlencode
import datetime
from typing import Optional

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

from matched.definitions.renewableandchpregister import (
    CertificatesFilter, 
    OutputPeriodYearFrom,
    OutputPeriodYearTo,
    OutputPeriodMonthFrom, 
    OutputPeriodMonthTo,
    OutputPeriodMonth,
)


def get_report_viewer_soup(session):
    url = 'https://renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx'
    params = {
        'ReportPath': '/DatawarehouseReports/CertificatesExternalPublicDataWarehouse',
        'ReportVisibility': 1,
        'ReportCategory': 2
    }

    r = session.get(url, params=params)
    r.raise_for_status()

    return bs(r.text, 'html.parser')

def get_excel_file(response_1: requests.Response, session: requests.Session) -> requests.Response:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': 'https://renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    params = {
        'ReportSession': response_1.text.split('?ReportSession=')[1].split('\\')[0],
        'Culture': '2057',
        'CultureOverrides': 'True',
        'UICulture': '2057',
        'UICultureOverrides': 'True',
        'ReportStack': '1',
        'ControlID': response_1.text.split('u0026ControlID=')[1].split('\\')[0],
        'OpType': 'Export',
        'FileName': 'CertificatesExternalPublicDataWarehouse',
        'ContentDisposition': 'OnlyHtmlInline',
        'Format': 'EXCELOPENXML',
    }

    return session.get(
        'https://renewablesandchp.ofgem.gov.uk/Reserved.ReportViewerWebControl.axd',
        params=params,
        headers=headers,
    )

def certificates_filter_to_df(certificates_filter: CertificatesFilter) -> pd.DataFrame:
    url = 'https://renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx'

    params = {
        'ReportPath': '/DatawarehouseReports/CertificatesExternalPublicDataWarehouse',
        'ReportVisibility': 1,
        'ReportCategory': 2
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://renewablesandchp.ofgem.gov.uk',
        'priority': 'u=1, i',
        'referer': 'https://renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'x-microsoftajax': 'Delta=true',
        'x-requested-with': 'XMLHttpRequest',
    }

    with requests.Session() as session:
        soup_in_1 = get_report_viewer_soup(session)

        payload_items_1 = certificates_filter.to_payload_items(soup_in_1=soup_in_1, stage=1)
        payload_items_str = urlencode(payload_items_1)
        response_1 = session.post(url, params=params, headers=headers, data=payload_items_str)

        soup_in_2 = bs(response_1.text, 'html.parser')
        payload_items_2 = certificates_filter.to_payload_items(soup_in_1=soup_in_1, soup_in_2=soup_in_2, stage=2)
        payload_items_str = urlencode(payload_items_2)
        response_2 = session.post(url, params=params, headers=headers, data=payload_items_str)

    r = get_excel_file(response_1, session)

    response_2.raise_for_status()


    if r.status_code == 200:
        excel_data = BytesIO(r.content)
    else:
        raise ValueError(f'Failed to download Excel file: {r.status_code}')

    return (
        pd
        .read_excel(excel_data, skiprows=7)
        .dropna(how='all', axis=1)
        .rename(columns=lambda x: x.lower().replace(' ', '_').replace('_/', '').replace('.', '').rstrip('_'))
    )


def get_certificates_by_date_range(
    start_date: datetime.datetime, 
    end_date: datetime.datetime, 
    certificates_filter: Optional[CertificatesFilter] = None
):
    if certificates_filter is None:
        certificates_filter = CertificatesFilter()

    current_date = start_date.replace(day=1)  # ensures the 32 day offset doesn't push us 2 months ahead
    year_month_pairs = []

    while current_date <= end_date:
        year = current_date.year
        month_name = getattr(OutputPeriodMonth, current_date.strftime('%b').lower()).value

        year_month_pairs.append((year, month_name))

        current_date += datetime.timedelta(days=32)  # move to next month
        current_date = current_date.replace(day=1)  # set day to 1st of the month

    dfs = []

    for year, month_name in tqdm(year_month_pairs):
        try:
            certificates_filter.output_year_from = OutputPeriodYearFrom(item=year)
            certificates_filter.output_year_to = OutputPeriodYearTo(item=year)
            certificates_filter.output_month_from = OutputPeriodMonthFrom(item=month_name)
            certificates_filter.output_month_to = OutputPeriodMonthTo(item=month_name)

            df = certificates_filter_to_df(certificates_filter)
            dfs.append(pd.DataFrame(df))
            time.sleep(0.5)
        except Exception as e:
            print(f'Failed to get data for {year} {month_name}: {e}')
    return pd.concat(dfs, ignore_index=True)

def map_dt_to_end_of_month(dt: datetime.datetime) -> datetime.datetime:
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()

    next_month_year = dt.year
    next_month = dt.month + 1

    if next_month == 13:
        next_month = 1
        next_month_year += 1

    return dt.replace(month=next_month, year=next_month_year) - datetime.timedelta(days=1)

def check_certificates(df: pd.DataFrame) -> None:
    assert (df['start_certificate_no'].str[:10] == df['accreditation_no']).mean() == 1
    assert (df['start_certificate_no'].str[:10] == df['end_certificate_no'].str[:10]).mean() == 1
    assert (df['start_certificate_idx'].astype(int) == df['start_certificate_idx']).mean() == 1
    assert (df['end_certificate_idx'].astype(int) == df['end_certificate_idx']).mean() == 1

def extract_rego_roc_dfs(df: pd.DataFrame) -> pd.DataFrame:
    df['certificate_type'] = df['start_certificate_no'].str[-3:]

    assert len(set(df['scheme'].unique()) - {'REGO', 'RO'}) == 0
    df_rego = df.query('scheme=="REGO"').drop(columns='scheme')
    df_ro = df.query('scheme=="RO"').drop(columns='scheme')

    # REGO
    df_rego = df_rego.assign(
        start_certificate_idx=(
            df_rego
            ['start_certificate_no']
            .str[10:]
            .str[:-13]
            .str.lstrip('0')
            .astype(int)
            .subtract(1)
            .divide(100)
            .add(1)
        )
    )

    df_rego = df_rego.assign(
        end_certificate_idx=(
            df_rego
            ['end_certificate_no']
            .str[10:]
            .str[:-13]
            .str.lstrip('0')
            .astype(int)
            .subtract(1)
            .divide(100)
            .add(1)
        )
    )

    df_rego = df_rego.assign(delivery_start=pd.to_datetime(df_rego['start_certificate_no'].str[20:].str[:-9], format='%d%m%y'))
    df_rego = df_rego.assign(delivery_end=pd.to_datetime(df_rego['start_certificate_no'].str[26:].str[:-3], format='%d%m%y'))

    # RO
    df_ro = df_ro.assign(delivery_start=pd.to_datetime(df_ro['start_certificate_no'].str[-7:].str[:-3], format='%m%y'))
    df_ro = df_ro.assign(delivery_end=df_ro['delivery_start'].apply(map_dt_to_end_of_month))
    df_ro = df_ro.assign(start_certificate_idx=df_ro.apply(lambda row: row['start_certificate_no'][len(row['accreditation_no']):-7], axis=1).astype(float).add(1))
    df_ro = df_ro.assign(end_certificate_idx=df_ro.apply(lambda row: row['end_certificate_no'][len(row['accreditation_no']):-7], axis=1).astype(float).add(1))

    # checks
    check_certificates(df_rego)
    check_certificates(df_ro)

    df_rego = df_rego.astype({'start_certificate_idx': int, 'end_certificate_idx': int})
    df_ro = df_ro.astype({'start_certificate_idx': int, 'end_certificate_idx': int})

    return df_rego, df_ro
