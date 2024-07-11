import argparse
import os
from pprint import pprint

import scores.s0142.concatenate_days
import scores.s0142.process_s0142_file
import scores.supplier_monthly_generation
import scores.supplier_time_matched_scores
from scores.configuration import conf

CONF_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "configuration"
)


def create_staged_directories(paths):
    os.mkdir(paths["LOCAL"]["staged"]["processed"])
    os.mkdir(os.path.join(paths["LOCAL"]["staged"]["processed"], "S0142"))
    os.mkdir(paths["LOCAL"]["staged"]["final"])


def setup(run_conf, paths=None):
    paths = conf.read(f"{CONF_DIR}/paths.yaml") if paths is None else conf.read(paths)

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


def extract_regos(paths, supplier):
    return scores.supplier_monthly_generation.main(
        paths["REGOS"],
        supplier["rego_organisation_name"],
        path_processed_agg_month_tech=os.path.join(
            paths["LOCAL"]["processed"], f"month-tech-{supplier['file_id']}.csv"
        ),
    )


def calculate_scores(paths, supplier):
    return scores.supplier_time_matched_scores.main(
        path_supplier_month_tech=os.path.join(
            paths["LOCAL"]["processed"], f"month-tech-{supplier['file_id']}.csv"
        ),
        path_grid_month_tech=paths["GRID"]["volumes_by_tech_by_month"],
        path_grid_hh_generation=paths["GRID"]["volumes_by_tech_by_half_hour"],
        path_supplier_hh_load=os.path.join(
            paths["LOCAL"]["final"],
            f"{supplier['bsc_lead_party_id']}_load.csv",
        ),
    )


def process_s0142_files(run_conf):
    input_dirs = run_conf["steps"]["process_s0142_files"]["input_abs"]
    output_dirs = run_conf["steps"]["process_s0142_files"]["output_abs"]
    filenames = run_conf["steps"]["process_s0142_files"].get("filenames")
    bsc_party_ids = run_conf["steps"]["process_s0142_files"].get("bsc_party_ids")

    scores.s0142.process_s0142_file.main(
        input_dir=os.path.join(input_dirs["raw"], "S0142"),
        output_dir=os.path.join(output_dirs["processed"], "S0142"),
        input_filenames=filenames,
        bsc_party_ids=bsc_party_ids,
    )

    return {}


def concatenate_days(paths, supplier):
    scores.s0142.concatenate_days.main(
        bsc_lead_party_id=supplier["bsc_lead_party_id"],
        input_dir=os.path.join(paths["LOCAL"]["processed"], "S0142"),
        output_path=os.path.join(
            paths["LOCAL"]["final"],
            f"{supplier['bsc_lead_party_id']}_load.csv",
        ),
    )
    return {}


def parse_args():
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

    return parser.parse_args()


def process_suppliers():
    ## Where does year belong? Needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness

    args = parse_args()

    run_conf = conf.read(args.run)

    run_conf = setup(run_conf, args.paths)
    print(run_conf)

    if "process_s0142_files" in run_conf["steps"]:
        process_s0142_files(run_conf)

    # results = {}
    # for supplier in conf.read("suppliers.yaml"):
    #     supplier_results = {}
    #     if arg_extract_regos:
    #         supplier_results.update(extract_regos(paths, supplier))
    #     if arg_aggregate_supplier_load:
    #         supplier_results.update(aggregate_supplier_load(paths, supplier))
    #     if arg_calculate_scores:
    #         supplier_results.update(calculate_scores(paths, supplier))
    #     results[supplier["name"]] = supplier_results
    # pprint(results)
    # return results


if __name__ == "__main__":
    process_suppliers()
