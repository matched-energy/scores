import argparse
import datetime
import os
import re
from pathlib import Path

from scores.configuration import conf


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Process run configuration.")

    parser.add_argument(
        "run",
        type=str,
        help="Path to YAML file that defines run configuration",
    )

    return parser.parse_args(args)


def create_staged_dirs_and_set_abs_paths(run_conf):
    staged_path = run_conf["local_dirs"]["staged"].replace(
        "DATETIME", datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    )
    dirs = [
        # TODO: move to configuration or infer from run.yaml
        (staged_path,),
        (staged_path, "processed"),
        (staged_path, "processed", "S0142"),
        (staged_path, "final"),
        (staged_path, "final", "published"),
        (staged_path, "final", "published", "scores_data"),
    ]
    for supplier in get_suppliers(run_conf):
        dirs.append(
            (staged_path, "final", "published", "scores_data", supplier["file_id"])
        )
    for dir in dirs:
        path = os.path.join(*dir)
        if not os.path.exists(path):
            os.mkdir(path)

    for step_name, step_conf in run_conf["steps"].items():
        for io in ["input", "output"]:
            for key, path_conf in step_conf.get(io, {}).items():
                if path_conf["root_dir"] == "staged":
                    root_dir_abs = staged_path
                elif path_conf["root_dir"] == "canonical":
                    root_dir_abs = run_conf["local_dirs"]["canonical"]
                else:
                    root_dir_abs = path_conf["root_dir"]
                run_conf["steps"][step_name][f"{io}"][key][
                    "root_dir_abs"
                ] = root_dir_abs

    return run_conf


def read_conf_and_make_dirs(*args):
    args = parse_args(args)
    run_conf = conf.read(args.run)
    run_conf = create_staged_dirs_and_set_abs_paths(run_conf)
    return run_conf


def get_suppliers(run_conf):
    return [
        supplier
        for supplier in conf.read("suppliers.yaml", conf_dir=True)
        if ((subset := run_conf.get("suppliers")) is None or supplier["name"] in subset)
    ]


def run_step(f, run_conf, *args):
    if step_conf := run_conf["steps"].get(f.__name__):
        return f(run_conf, step_conf, *args)
    else:
        return {}


def make_path(path_conf, io, key, subs=None) -> Path:
    conf = path_conf[io][key]

    filename = conf.get("filename", "")
    for var in re.findall(r"\/(.*?)\/", filename):
        try:
            filename = filename.replace(f"/{var}/", subs[var])
        except (KeyError, TypeError):
            raise KeyError(f"Variable {var} not found in subs")

    return Path(conf["root_dir_abs"]) / conf["sub_dir"] / filename