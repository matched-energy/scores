import os
from pprint import pprint

import scores.s0142.concatenate_days
import scores.s0142.process_s0142_file
import scores.supplier_monthly_generation
import scores.supplier_time_matched_scores
from scores.configuration import conf


def setup(paths, overwrite=False):
    if not overwrite:
        os.mkdir(paths["OUTPUT"]["processed_to_review"])
        os.mkdir(os.path.join(paths["OUTPUT"]["processed_to_review"], "S0142"))
        os.mkdir(paths["OUTPUT"]["final_to_review"])


def extract_regos(paths, supplier):
    return scores.supplier_monthly_generation.main(
        paths["REGOS"],
        supplier["rego_organisation_name"],
    )


def calculate_scores(paths, supplier):
    return scores.supplier_time_matched_scores.main(
        path_supplier_month_tech=os.path.join(
            os.environ["MATCHED_DATA"],
            "processed",
            f"month-tech-{supplier['file_id']}.csv",
        ),
        path_grid_month_tech=paths["GRID"]["volumes_by_tech_by_month"],
        path_grid_hh_generation=paths["GRID"]["volumes_by_tech_by_half_hour"],
        path_supplier_hh_load=os.path.join(
            paths["OUTPUT"]["final_to_review"],
            f"{supplier['bsc_lead_party_id']}_load.csv",
        ),
    )


def process_s0142_files(paths):
    scores.s0142.process_s0142_file.main(
        input_dir=os.path.join(os.environ["MATCHED_DATA"], "raw", "S0142"),
        input_filenames=[
            "S0142_20220401_SF_20220427115520.gz",
            "S0142_20220402_SF_20220427114051.gz",
        ],
        output_dir=os.path.join(paths["OUTPUT"]["processed_to_review"], "S0142"),
        bsc_party_ids=["PURE", "MERCURY"],
    )


def aggregate_supplier_load(paths, supplier):
    scores.s0142.concatenate_days.main(
        bsc_lead_party_id=supplier["bsc_lead_party_id"],
        input_dir=os.path.join(paths["OUTPUT"]["processed_to_review"], "S0142"),
        output_path=os.path.join(
            paths["OUTPUT"]["final_to_review"],
            f"{supplier['bsc_lead_party_id']}_load.csv",
        ),
    )


def process_supplier(paths, supplier):
    results = extract_regos(paths, supplier)
    aggregate_supplier_load(paths, supplier)
    results.update(calculate_scores(paths, supplier))
    return results


def process_suppliers(suppliers="all"):
    ## Where does year belong? Needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness
    paths = conf.read("paths.yaml")
    setup(paths)
    process_s0142_files(paths)

    results = {}
    for supplier in conf.read("suppliers.yaml"):
        if suppliers == "all" or supplier["name"] in suppliers:
            results[supplier["name"]] = process_supplier(paths, supplier)
    pprint(results)
    return results


if __name__ == "__main__":
    process_suppliers()
