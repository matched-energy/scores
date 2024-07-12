import os
import re
import sys
from pprint import pprint

import scores.grid_gen_by_tech_by_month
import scores.s0142.parse_s0142_files
import scores.s0142.supplier_load_by_half_hour
import scores.supplier_gen_by_tech_by_half_hour
import scores.supplier_gen_by_tech_by_month
import scores.supplier_scores
from scores.configuration import conf
from scores.workflow.helpers import make_path, read_conf_and_make_dirs, run_step


def grid_gen_by_tech_by_month(run_conf, step_conf):
    scores.grid_gen_by_tech_by_month.main(
        path_historic_generation_mix=make_path(
            step_conf, "input", "path_historic_generation_mix"
        ),
        path_grid_hh=make_path(step_conf, "output", "path_grid_hh"),
        path_grid_month_tech=make_path(step_conf, "output", "path_grid_month_tech"),
        start=run_conf["start_datetime"],
        end=run_conf["end_datetime"],
    )


def supplier_gen_by_tech_by_month(run_conf, step_conf, supplier, paths):
    return scores.supplier_gen_by_tech_by_month.main(
        path_raw_rego=make_path(step_conf, "input", "path_raw_rego"),
        current_holder_organisation_name=supplier["rego_organisation_name"],
        path_processed_agg_month_tech=make_path(
            step_conf,
            "output",
            "path_processed_agg_month_tech",
            dict(SUPPLIER=supplier["file_id"]),
        ),
    )


def supplier_gen_by_tech_by_half_hour(run_conf, step_conf, supplier):
    scores.supplier_gen_by_tech_by_half_hour.calculate_supplier_generation(
        path_supplier_month_tech=make_path(
            step_conf,
            "input",
            "path_supplier_month_tech",
            dict(SUPPLIER=supplier["file_id"]),
        ),
        path_grid_month_tech=make_path(step_conf, "input", "path_grid_month_tech"),
        path_grid_hh_generation=make_path(
            step_conf, "input", "path_grid_hh_generation"
        ),
        output_path=make_path(
            step_conf, "output", "output_path", subs=dict(SUPPLIER=supplier["file_id"])
        ),
    )
    return {}


def supplier_scores(run_conf, step_conf, supplier):
    return scores.supplier_scores.main(
        path_supplier_month_tech=make_path(
            step_conf,
            "input",
            "path_supplier_month_tech",
            dict(SUPPLIER=supplier["file_id"]),
        ),
        path_grid_month_tech=make_path(step_conf, "input", "path_grid_month_tech"),
        path_grid_hh_generation=make_path(
            step_conf, "input", "path_grid_hh_generation"
        ),
        path_supplier_gen_by_tech_by_half_hour=make_path(
            step_conf,
            "input",
            "path_supplier_gen_by_tech_by_half_hour",
            dict(SUPPLIER=supplier["file_id"]),
        ),
        path_supplier_hh_load=make_path(
            step_conf,
            "input",
            "path_supplier_hh_load",
            dict(BSC_PARTY_ID=supplier["bsc_party_id"]),
        ),
    )


def parse_s0142_files(run_conf, step_conf):
    bsc_party_ids = [
        supplier["bsc_party_id"]
        for supplier in conf.read("suppliers.yaml", conf_dir=True)
        if supplier["name"] in run_conf["suppliers"]
    ]
    scores.s0142.parse_s0142_files.main(
        input_dir=make_path(step_conf, "input", "input_dir"),
        output_dir=make_path(step_conf, "output", "output_dir"),
        prefixes=step_conf.get("prefixes"),
        bsc_party_ids=bsc_party_ids,
    )
    return {}


def supplier_load_by_half_hour(run_conf, step_conf, supplier):
    scores.s0142.supplier_load_by_half_hour.main(
        bsc_lead_party_id=supplier["bsc_party_id"],
        input_dir=make_path(step_conf, "input", "input_dir"),
        output_path=make_path(
            step_conf,
            "output",
            "output_path",
            dict(BSC_PARTY_ID=supplier["bsc_party_id"]),
        ),
        prefixes=step_conf.get("prefixes"),
    )
    return {}


def process_suppliers(*args):
    ## where does year belong? needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness

    run_conf, paths = read_conf_and_make_dirs(*args)

    run_step(grid_gen_by_tech_by_month, run_conf)
    run_step(parse_s0142_files, run_conf)

    results = {}
    for supplier in conf.read("suppliers.yaml", conf_dir=True):
        r = {}
        r.update(run_step(supplier_load_by_half_hour, run_conf, supplier))
        r.update(run_step(supplier_gen_by_tech_by_month, run_conf, supplier, paths))
        r.update(run_step(supplier_gen_by_tech_by_half_hour, run_conf, supplier))
        r.update(run_step(supplier_scores, run_conf, supplier))
        results[supplier["name"]] = r
    pprint(results)
    return results


if __name__ == "__main__":
    process_suppliers(*sys.argv[1:])
