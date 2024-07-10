import os
from pprint import pprint

import scores.configuration.conf as conf
import scores.supplier_monthly_generation


def extract_regos(rego_path, supplier):
    return scores.supplier_monthly_generation.main(
        rego_path,
        supplier["rego_organisation_name"],
    )


def main(rego_year="2022/23", suppliers="all"):
    rego_path = conf.read("regos.yaml")[rego_year]
    results = {}
    for supplier in conf.read("suppliers.yaml"):
        if suppliers == "all" or supplier["name"] in suppliers:
            results[supplier["name"]] = {}
            results[supplier["name"]].update(extract_regos(rego_path, supplier))
    pprint(results)
    return results


if __name__ == "__main__":
    main()
