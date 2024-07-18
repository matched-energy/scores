import collections
import pprint
import sys

import numpy as np
import pandas as pd
import scipy.optimize
import scores.common.utils as utils
import scores.configuration.conf as conf
import scores.plot.plot_supplier


def t_hh_rego_total(hh_rego):
    tech_categories = conf.read("generation.yaml", conf_dir=True)["TECH"]  # TODO
    return hh_rego[[f"{tech}_supplier" for tech in tech_categories]].sum(axis=1)


def assemble_stats(bsc_hh, r_hh, g_hh, l_hh, embedded_ratio):
    l_hh_sum = l_hh.sum()
    g_hh_sum = g_hh.sum()

    r_yr = (r_hh.sum()).clip(min=0)
    r_hh_sum = (r_hh).clip(lower=0).sum()

    l_metered_discernable_yr = -bsc_hh["BM Unit Metered Volume: -ve"].sum()
    g_embedded_metered_discernable_yr = bsc_hh["BM Unit Metered Volume: +ve"].sum()

    s_yr = 1 - r_yr / l_hh_sum
    s_hh = 1 - r_hh_sum / l_hh_sum

    return dict(
        bsc_hh_sum=float(bsc_hh["BM Unit Metered Volume"].sum()),
        g_hh_sum=float(g_hh_sum),
        g_embedded_metered_discernable_yr=float(g_embedded_metered_discernable_yr),
        g_embedded_metered_discernable_ratio=float(
            g_embedded_metered_discernable_yr / g_hh_sum
        ),
        l_hh_sum=float(l_hh_sum),
        l_metered_discernable_hh=float(l_metered_discernable_yr),
        l_metered_discernable_ratio=float(l_metered_discernable_yr / l_hh_sum),
        r_yr=float(r_yr),
        r_hh_sum=float(r_hh_sum),
        s_yr=float(s_yr),
        s_hh=float(s_hh),
        g_l_ratio=float(g_hh_sum / l_hh_sum),
        embedded=float(embedded_ratio),
    )


def independent(g_rego_hh, bsc_hh):
    g_hh = g_rego_hh
    l_hh = -bsc_hh["BM Unit Metered Volume"]
    r_hh = l_hh - g_hh
    return assemble_stats(bsc_hh, r_hh, g_hh, l_hh, embedded_ratio=0)


def embedded(g_rego_hh, bsc_hh):
    g_hh = g_rego_hh
    l_hh = g_rego_hh - bsc_hh["BM Unit Metered Volume"]
    r_hh = -bsc_hh["BM Unit Metered Volume"]

    return assemble_stats(bsc_hh, r_hh, g_hh, l_hh, embedded_ratio=1)


def opt(g_rego_hh, bsc_hh):

    def f(x):
        g_embedded_hh = x * g_rego_hh
        l_hh = g_embedded_hh - bsc_hh["BM Unit Metered Volume"]
        return abs(l_hh.sum() - g_rego_hh.sum())

    opt = scipy.optimize.minimize_scalar(f, bounds=(0, 1), method="bounded")

    g_hh = g_rego_hh
    g_embedded_hh = opt.x * g_rego_hh
    l_hh = g_embedded_hh - bsc_hh["BM Unit Metered Volume"]
    g_independent_hh = (1 - opt.x) * g_rego_hh
    r_hh = -bsc_hh["BM Unit Metered Volume"] - g_independent_hh

    return assemble_stats(bsc_hh, r_hh, g_hh, l_hh, embedded_ratio=opt.x)


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_gen_by_tech_by_half_hour,
    path_supplier_hh_load,
    output_path_scores=None,
    output_path_plot=None,
):
    ## TODO - hh_load --> bsc_hh
    ## TODO - assert timeseries are aligned
    hh_generation = pd.read_csv(path_supplier_gen_by_tech_by_half_hour)
    hh_load = get_supplier_load(path_supplier_hh_load)

    g_rego_hh = t_hh_rego_total(hh_generation)

    results = {}
    results["independent"] = independent(g_rego_hh, hh_load)
    results["embedded"] = embedded(g_rego_hh, hh_load)
    results["opt"] = opt(g_rego_hh, hh_load)
    if output_path_scores:
        utils.to_yaml_file(results, output_path_scores)
    if output_path_plot:
        scores.plot.plot_supplier.plot_load_and_gen(
            hh_generation, hh_load, output_path_plot
        )
    return results


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
