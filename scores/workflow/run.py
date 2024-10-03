import sys
from pprint import pprint

import scores.common.utils as utils
import scores.core.grid_gen_by_tech_by_month
import scores.core.supplier_gen_by_tech_by_half_hour
import scores.core.supplier_gen_by_tech_by_month
import scores.core.supplier_load_by_half_hour
import scores.core.supplier_scores
import scores.publish
import scores.publish.supplier
import scores.s0142.parse_s0142_files
from scores.configuration import conf
from scores.workflow.helpers import (
    get_suppliers,
    make_path,
    read_conf_and_make_dirs,
    run_step,
)


def grid_gen_by_tech_by_month(run_conf, step_conf):
    scores.core.grid_gen_by_tech_by_month.main(
        path_historic_generation_mix=make_path(
            step_conf, "input", "path_historic_generation_mix"
        ),
        path_grid_hh=make_path(step_conf, "output", "path_grid_hh"),
        path_grid_month_tech=make_path(step_conf, "output", "path_grid_month_tech"),
        start=run_conf["start_datetime"],
        end=run_conf["end_datetime"],
    )


def supplier_gen_by_tech_by_month(run_conf, step_conf, supplier):
    return scores.core.supplier_gen_by_tech_by_month.main(
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
    scores.core.supplier_gen_by_tech_by_half_hour.calculate_supplier_generation(
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
    return scores.core.supplier_scores.main(
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
        scoring_methodology=supplier["scoring_methodology"],
        output_path_scores=make_path(
            step_conf,
            "output",
            "path_scores",
            dict(SUPPLIER=supplier["file_id"]),
        ),
        output_path_plot=make_path(
            step_conf,
            "output",
            "path_plot",
            dict(SUPPLIER=supplier["file_id"]),
        ),
    )


def parse_s0142_files(run_conf, step_conf):
    bsc_party_ids = [
        supplier["bsc_party_id"]
        for supplier in conf.read("suppliers.yaml", conf_dir=True)
    ]
    scores.s0142.parse_s0142_files.main(
        input_dir=make_path(step_conf, "input", "input_dir"),
        output_dir=make_path(step_conf, "output", "output_dir"),
        prefixes=step_conf.get("prefixes"),
        bsc_party_ids=bsc_party_ids,
    )
    return {}


def supplier_load_by_half_hour(run_conf, step_conf, supplier):
    scores.core.supplier_load_by_half_hour.main(
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


def publish(run_conf, step_conf, supplier):
    subs = dict(SUPPLIER=supplier["file_id"])
    scores.publish.supplier.main(
        scores_input_path=make_path(step_conf, "input", "scores_input_path", subs),
        scores_output_path=make_path(step_conf, "output", "scores_output_path", subs),
        plot_src_path=make_path(step_conf, "input", "plot_src_path", subs),
        plot_target_path=make_path(step_conf, "output", "plot_target_path", subs),
        supplier=supplier,
    )
    return {}


def process_suppliers(*args):
    ## where does year belong? needs apply to regos and grid.
    ## ^   should handle in pre-processing
    ## ... and be explicit about timeranges in filename
    ## ... and have functions that validate data range & completeness

    run_conf = read_conf_and_make_dirs(*args)

    run_step(grid_gen_by_tech_by_month, run_conf)
    run_step(parse_s0142_files, run_conf)

    results = {}
    for supplier in get_suppliers(run_conf):
        r = {}
        r.update(run_step(supplier_load_by_half_hour, run_conf, supplier))
        r.update(run_step(supplier_gen_by_tech_by_month, run_conf, supplier))
        r.update(run_step(supplier_gen_by_tech_by_half_hour, run_conf, supplier))
        r.update(run_step(supplier_scores, run_conf, supplier))
        r.update(run_step(publish, run_conf, supplier))
        results[supplier["name"]] = r

    pprint(results)
    return results


if __name__ == "__main__":
    process_suppliers(*sys.argv[1:])
