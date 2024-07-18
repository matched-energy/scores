import collections
import pprint
import sys

import numpy as np
import pandas as pd
import scipy.optimize
import scores.configuration.conf as conf


def t_hh_rego_total(hh_rego):
    tech_categories = conf.read("generation.yaml", conf_dir=True)["TECH"]  # TODO
    return hh_rego[[f"{tech}_supplier" for tech in tech_categories]].sum(axis=1)


def assemble_stats(bsc_hh, r_hh, g_hh, l_hh):
    l_hh_sum = l_hh.sum()
    g_hh_sum = g_hh.sum()

    # r_yr_sum = (l_hh.sum() - g_hh.sum()).clip(min=0)
    # r_yr_sum = (-bsc_vol).sum().clip(min=0)
    r_yr_sum = (r_hh.sum()).clip(min=0)
    # r_hh_sum = (l_hh - g_hh).clip(lower=0).sum()
    # r_hh_sum = (-bsc_vol).clip(lower=0).sum()
    r_hh_sum = (r_hh).clip(lower=0).sum()

    s_yr = 1 - r_yr_sum / l_hh_sum
    s_hh = 1 - r_hh_sum / l_hh_sum

    return collections.OrderedDict(
        bsc_hh_sum=bsc_hh["BM Unit Metered Volume"].sum(),
        g_hh_sum=g_hh_sum,
        l_hh_sum=l_hh_sum,
        r_yr_sum=r_yr_sum,
        r_hh_sum=r_hh_sum,
        s_yr=s_yr,
        s_hh=s_hh,
        g_l_ratio=g_hh_sum / l_hh_sum,
    )


def independent(g_rego_hh, bsc_hh):
    g_hh = g_rego_hh
    l_hh = -bsc_hh["BM Unit Metered Volume"]
    r_hh = l_hh - g_hh
    return assemble_stats(bsc_hh, r_hh, g_hh, l_hh)


def embedded(g_rego_hh, bsc_hh):
    g_hh = g_rego_hh
    l_hh = g_rego_hh - bsc_hh["BM Unit Metered Volume"]
    r_hh = -bsc_hh["BM Unit Metered Volume"]

    return assemble_stats(bsc_hh, r_hh, g_hh, l_hh)


def approach_4(g_rego_hh, bsc_hh):

    def f(r):
        g_embedded_hh = r * g_rego_hh
        l_hh = g_embedded_hh - bsc_hh["BM Unit Metered Volume"]
        return abs(l_hh.sum() - g_rego_hh.sum())

    result = scipy.optimize.minimize_scalar(f, bounds=(0, 1), method="bounded")
    r = result.x

    g_hh = g_rego_hh
    g_embedded_hh = r * g_rego_hh
    l_hh = g_embedded_hh - bsc_hh["BM Unit Metered Volume"]
    g_independent_hh = (1 - r) * g_rego_hh
    r_hh = -bsc_hh["BM Unit Metered Volume"] - g_independent_hh

    results = assemble_stats(bsc_hh, r_hh, g_hh, l_hh)
    results.update({"r": r}, inplace=True)
    return results


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_gen_by_tech_by_half_hour,
    path_supplier_hh_load,
    plot=False,
):
    ## TODO - hh_load --> bsc_hh
    ## TODO - assert timeseries are aligned
    hh_generation = pd.read_csv(path_supplier_gen_by_tech_by_half_hour)
    hh_load = get_supplier_load(path_supplier_hh_load)

    if plot:
        scores.plot.plot_supplier.plot_and_gen(hh_generation, hh_load)

    g_rego_hh = t_hh_rego_total(hh_generation)

    scores = {}
    scores["independent"] = independent(g_rego_hh, hh_load)
    scores["embedded"] = embedded(g_rego_hh, hh_load)
    scores["approach_4"] = approach_4(g_rego_hh, hh_load)
    return scores


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
