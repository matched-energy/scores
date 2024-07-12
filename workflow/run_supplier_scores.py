import os
import sys
from pprint import pprint

import scores.grid_monthly_generation
import scores.s0142.concatenate_days
import scores.s0142.process_s0142_file
import scores.supplier_gen_by_tech_by_half_hour
import scores.supplier_monthly_generation
import scores.supplier_time_matched_scores
from scores.configuration import conf
from scores.workflow.helpers import read_conf_and_make_dirs, run_step


def grid_gen_by_tech_by_month(run_conf, step_conf):
    scores.grid_monthly_generation.main(
        os.path.join(step_conf["input_abs"]["raw"], "historic-generation-mix.csv"),
        start=run_conf["start_datetime"],
        end=run_conf["end_datetime"],
        path_grid_hh=os.path.join(step_conf["output_abs"]["processed"], "grid_hh.csv"),
        path_grid_month_tech=os.path.join(
            step_conf["output_abs"]["processed"], "grid-month-tech.csv"
        ),
    )


def supplier_gen_by_tech_by_half_hour(run_conf, step_conf, supplier):
    scores.supplier_gen_by_tech_by_half_hour.calculate_supplier_generation(
        path_supplier_month_tech=os.path.join(
            step_conf["input_abs"]["processed"], f"month-tech-{supplier['file_id']}.csv"
        ),
        path_grid_month_tech=os.path.join(
            step_conf["input_abs"]["processed"], "grid-month-tech.csv"
        ),
        path_grid_hh_generation=os.path.join(
            step_conf["input_abs"]["processed"], "grid_hh.csv"
        ),
        output_path=os.path.join(
            step_conf["output_abs"]["final"],
            f"{supplier['file_id']}_gen_by_tech_by_half_hour.csv",
        ),
    )
    return {}


def supplier_gen_by_tech_by_month(run_conf, step_conf, supplier, paths):
    return scores.supplier_monthly_generation.main(
        paths["REGOS"],
        supplier["rego_organisation_name"],
        path_processed_agg_month_tech=os.path.join(
            step_conf["output_abs"]["processed"],
            f"month-tech-{supplier['file_id']}.csv",
        ),
    )


def supplier_scores(run_conf, step_conf, supplier):
    return scores.supplier_time_matched_scores.main(
        path_supplier_month_tech=os.path.join(
            step_conf["input_abs"]["processed"], f"month-tech-{supplier['file_id']}.csv"
        ),
        path_grid_month_tech=os.path.join(
            step_conf["input_abs"]["processed"], "grid-month-tech.csv"
        ),
        path_grid_hh_generation=os.path.join(
            step_conf["input_abs"]["processed"], "grid_hh.csv"
        ),
        path_supplier_gen_by_tech_by_half_hour=os.path.join(
            step_conf["input_abs"]["final"],
            f"{supplier['file_id']}_gen_by_tech_by_half_hour.csv",
        ),
        path_supplier_hh_load=os.path.join(
            step_conf["input_abs"]["final"],
            f"{supplier['bsc_party_id']}_load.csv",
        ),
    )


def parse_s0142_files(run_conf, step_conf):
    bsc_party_ids = [
        supplier["bsc_party_id"]
        for supplier in conf.read("suppliers.yaml", conf_dir=True)
        if supplier["name"] in run_conf["suppliers"]
    ]
    scores.s0142.process_s0142_file.main(
        input_dir=os.path.join(step_conf["input_abs"]["raw"], "s0142"),
        output_dir=os.path.join(step_conf["output_abs"]["processed"], "s0142"),
        prefixes=step_conf.get("prefixes"),
        bsc_party_ids=bsc_party_ids,
    )
    return {}


def supplier_load_by_half_hour(run_conf, step_conf, supplier):
    scores.s0142.concatenate_days.main(
        bsc_lead_party_id=supplier["bsc_party_id"],
        input_dir=os.path.join(step_conf["input_abs"]["processed"], "s0142"),
        output_path=os.path.join(
            step_conf["output_abs"]["final"],
            f"{supplier['bsc_party_id']}_load.csv",
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
