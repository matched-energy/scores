import collections
import pprint
import sys

import pandas as pd

import scores.configuration.conf as conf
import scores.plot.plot_supplier


def t_hh_rego_total(hh_rego):
    tech_categories = conf.read("generation.yaml", conf_dir=True)["TECH"]  # TODO
    return hh_rego[[f"{tech}_supplier" for tech in tech_categories]].sum(axis=1)


def all_independent(hh_generation, hh_load):
    g_rego_hh = t_hh_rego_total(hh_generation)
    bm_hh = hh_load["BM Unit Metered Volume"]

    g_hh = g_rego_hh
    g_hh_sum = g_hh.sum()
    l_hh = -bm_hh
    l_hh_sum = l_hh.sum()

    r_yr_sum = (l_hh.sum() - g_hh.sum()).clip(min=0)
    r_hh_sum = (l_hh - g_hh).clip(lower=0).sum()

    s_yr = 1 - r_yr_sum / l_hh_sum
    s_hh = 1 - r_hh_sum / l_hh_sum

    return collections.OrderedDict(
        g_hh_sum=g_hh_sum,
        l_hh_sum=l_hh_sum,
        r_yr_sum=r_yr_sum,
        r_hh_sum=r_hh_sum,
        s_yr=s_yr,
        s_hh=s_hh,
    )


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_gen_by_tech_by_half_hour,
    path_supplier_hh_load,
    plot=False,
):
    ## TODO - assert timeseries are aligned
    hh_generation = pd.read_csv(path_supplier_gen_by_tech_by_half_hour)
    hh_load = get_supplier_load(path_supplier_hh_load)

    if plot:
        scores.plot.plot_supplier.plot_and_gen(hh_generation, hh_load)

    return all_independent(hh_generation, hh_load)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
