import collections
import pprint
import sys

import pandas as pd
import scores.configuration.conf as conf
import scores.plot.plot_supplier


def t_hh_rego_total(hh_rego):
    tech_categories = conf.read("generation.yaml", conf_dir=True)["TECH"]  # TODO
    return hh_rego[[f"{tech}_supplier" for tech in tech_categories]].sum(axis=1)


def calc_scores_new(hh_generation, hh_load):
    pass


def calc_scores(hh_generation, hh_load):
    ## TODO - assert timeseries are aligned
    hh_rego_total = t_hh_rego_total(hh_generation)
    load = -hh_load["BM Unit Metered Volume"]
    hh_load["deficit"] = (load - hh_rego_total).clip(lower=0)
    scores = collections.OrderedDict(
        generation_total=hh_rego_total.sum(),
        load_total=load.sum(),
        unmatched_volume_hh=hh_load["deficit"].sum(),
        matched_volume_percent_hh=(1 - hh_load["deficit"].sum() / (load.sum())) * 100,
        matched_volume_percent_annual=(hh_rego_total.sum() / (load.sum())) * 100,
    )
    pprint.pprint(scores)
    return scores


def get_supplier_load(path_supplier_hh_load):
    hh_load = pd.read_csv(path_supplier_hh_load)
    hh_load["Settlement Datetime"] = pd.to_datetime(hh_load["Settlement Datetime"])
    return hh_load


def main(
    path_supplier_gen_by_tech_by_half_hour,
    path_supplier_hh_load,
    plot=False,
):
    hh_generation = pd.read_csv(path_supplier_gen_by_tech_by_half_hour)
    hh_load = get_supplier_load(path_supplier_hh_load)

    if plot:
        scores.plot.plot_supplier.plot_and_gen(hh_generation, hh_load)

    calc_scores_new(hh_generation, hh_load)
    return calc_scores(hh_generation, hh_load)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
