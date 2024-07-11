import os
from pprint import pprint

import scores.configuration.conf as conf
import scores.supplier_monthly_generation
import scores.supplier_time_matched_scores


def extract_regos(rego_path, supplier):
    return scores.supplier_monthly_generation.main(
        rego_path,
        supplier["rego_organisation_name"],
    )


def calculate_scores(grid, supplier):
    return scores.supplier_time_matched_scores.main(
        path_supplier_month_tech=os.path.join(
            os.environ["MATCHED_DATA"],
            "processed",
            f"month-tech-{supplier['file_id']}.csv",
        ),
        path_grid_month_tech=os.path.join(
            os.environ["MATCHED_DATA"], "processed", f"grid-month-tech.csv"
        ),
        path_grid_hh_generation=os.path.join(
            os.environ["MATCHED_DATA"], "processed", f"grid_hh.csv"
        ),
        path_supplier_hh_load=os.path.join(
            os.environ["MATCHED_DATA"],
            "final",
            f"{supplier['bsc_lead_party_id']}_load.csv",
        ),
    )


def process_supplier(rego_path, grid, supplier):
    results = extract_regos(rego_path, supplier)
    results.update(calculate_scores(grid, supplier))
    return results


def process_suppliers(rego_year="2022/23", suppliers="all"):
    ## Where does year belong? Needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness
    rego_path = conf.read("regos.yaml")[rego_year]
    grid = conf.read("grid.yaml")
    results = {}
    for supplier in conf.read("suppliers.yaml"):
        if suppliers == "all" or supplier["name"] in suppliers:
            results[supplier["name"]] = process_supplier(rego_path, grid, supplier)
    pprint(results)
    return results


if __name__ == "__main__":
    process_suppliers()
