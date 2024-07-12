import argparse
import os

from scores.configuration import conf


def create_staged_directories(paths):
    os.mkdir(paths["LOCAL"]["staged"]["processed"])
    os.mkdir(os.path.join(paths["LOCAL"]["staged"]["processed"], "S0142"))
    os.mkdir(paths["LOCAL"]["staged"]["final"])


def add_abs_paths(run_conf, paths):
    need_staged_dirs = False
    for step_name, step_conf in run_conf["steps"].items():
        for io in ["input", "output"]:
            path_abs = (
                step_conf.get(io)
                if step_conf.get(io) not in ["canonical", "staged"]
                else paths["LOCAL"][step_conf.get(io)]
            )
            run_conf["steps"][step_name][f"{io}_abs"] = path_abs
        if step_conf.get("output") == "staged":
            need_staged_dirs = True
    return run_conf, need_staged_dirs


def read_conf_and_make_dirs(*args):
    args = parse_args(args)
    paths = conf.read(args.paths)
    run_conf = conf.read(args.run)
    run_conf, need_staged_dirs = add_abs_paths(run_conf, paths)
    if need_staged_dirs:
        create_staged_directories(paths)
    return run_conf, paths


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
        default=os.path.join(conf.DIR, "paths.yaml"),
    )

    return parser.parse_args(args)


def run_step(f, run_conf, *args):
    if step_conf := run_conf["steps"].get(f.__name__):
        return f(run_conf, step_conf, *args)
    else:
        return {}
