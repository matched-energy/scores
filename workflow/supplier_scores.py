import argparse
import os
from pprint import pprint
import sys

import scores.grid_monthly_generation
import scores.s0142.concatenate_days
import scores.s0142.process_s0142_file
import scores.supplier_gen_by_tech_by_half_hour
import scores.supplier_monthly_generation
import scores.supplier_time_matched_scores
from scores.configuration import conf


def create_staged_directories(paths):
    os.mkdir(paths["LOCAL"]["staged"]["processed"])
    os.mkdir(os.path.join(paths["LOCAL"]["staged"]["processed"], "S0142"))
    os.mkdir(paths["LOCAL"]["staged"]["final"])


def setup(run_conf, paths):
    created_staged_directories = False

    for step_name, step_conf in run_conf["steps"].items():
        for io in ["input", "output"]:
            path_abs = (
                step_conf.get(io)
                if step_conf.get(io) not in ["canonical", "staged"]
                else paths["LOCAL"][step_conf.get(io)]
            )
            run_conf["steps"][step_name][f"{io}_abs"] = path_abs
        if step_conf.get("output") == "staged" and not created_staged_directories:
            create_staged_directories(paths)
            created_staged_directories = True

    return run_conf


def grid_gen_by_tech_month(paths, run_conf, step_conf):
    scores.grid_monthly_generation.main(
        os.path.join(step_conf["input_abs"]["raw"], "historic-generation-mix.csv"),
        start=run_conf["start_datetime"],
        end=run_conf["end_datetime"],
        path_grid_hh=os.path.join(step_conf["output_abs"]["processed"], "grid_hh.csv"),
        path_grid_month_tech=os.path.join(
            step_conf["output_abs"]["processed"], "grid-month-tech.csv"
        ),
    )


def supplier_gen_by_tech_by_half_hour(step_conf, supplier):
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


def extract_regos(step_conf, supplier, paths):
    return scores.supplier_monthly_generation.main(
        paths["REGOS"],
        supplier["rego_organisation_name"],
        path_processed_agg_month_tech=os.path.join(
            step_conf["output_abs"]["processed"],
            f"month-tech-{supplier['file_id']}.csv",
        ),
    )


def calculate_scores(step_conf, supplier, paths):
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


def process_s0142_files(run_conf, step_conf):
    bsc_party_ids = [
        supplier["bsc_party_id"]
        for supplier in conf.read("suppliers.yaml", conf_dir=True)
        if supplier["name"] in run_conf["suppliers"]
    ]
    scores.s0142.process_s0142_file.main(
        input_dir=os.path.join(step_conf["input_abs"]["raw"], "S0142"),
        output_dir=os.path.join(step_conf["output_abs"]["processed"], "S0142"),
        input_filenames=step_conf.get("filenames"),
        bsc_party_ids=bsc_party_ids,
    )
    return {}


def concatenate_days(step_conf, supplier):
    scores.s0142.concatenate_days.main(
        bsc_lead_party_id=supplier["bsc_party_id"],
        input_dir=os.path.join(step_conf["input_abs"]["processed"], "S0142"),
        output_path=os.path.join(
            step_conf["output_abs"]["final"],
            f"{supplier['bsc_party_id']}_load.csv",
        ),
        prefixes=step_conf.get("prefix"),
    )
    return {}


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Process run configuration.")

    parser.add_argument(
        "run",
        type=str,
        help="Path to YAML file that defines run configuration",
    )
    parser.add_argument(
        "--paths",
        type=str,
        help="Path to YAML file that defines paths",
    )

    return parser.parse_args(args)


def process_suppliers(*args):
    ## Where does year belong? Needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness

    args = parse_args(args)

    run_conf = conf.read(args.run)
    paths = (
        conf.read("paths.yaml", conf_dir=True)
        if args.paths is None
        else conf.read(args.paths)
    )

    run_conf = setup(run_conf, paths)
    print(run_conf)

    if step_conf := run_conf["steps"].get("grid_gen_by_tech_by_month"):
        grid_gen_by_tech_month(paths, run_conf, step_conf)

    if step_conf := run_conf["steps"].get("process_s0142_files"):
        process_s0142_files(run_conf, step_conf)

    results = {}
for supplier in conf.read("suppliers.yaml", conf_dir=True):
        supplier_results = {}
        if step_conf := run_conf["steps"].get("concatenate_days"):
            supplier_results.update(concatenate_days(step_conf, supplier))
        if step_conf := run_conf["steps"].get("extract_regos"):
            supplier_results.update(extract_regos(step_conf, supplier, paths))
        if step_conf := run_conf["steps"].get("supplier_gen_by_tech_by_half_hour"):
            supplier_results.update(
                supplier_gen_by_tech_by_half_hour(step_conf, supplier)
            )
        if step_conf := run_conf["steps"].get("calculate_scores"):
            supplier_results.update(calculate_scores(step_conf, supplier, paths))
        results[supplier["name"]] = supplier_results
    pprint(results)
    return results


if __name__ == "__main__":
    process_suppliers(*sys.argv[1:])
