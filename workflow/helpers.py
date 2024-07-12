import argparse
import datetime
import os
import re

from scores.configuration import conf


def create_staged_dirs_and_set_abs_paths(run_conf, paths):
    staged_dir = os.path.join(
        paths["LOCAL"]["staged"],
        f"scores-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
    )
    os.mkdir(staged_dir)
    os.mkdir(os.path.join(staged_dir, "processed"))
    os.mkdir(os.path.join(staged_dir, "processed", "S0142"))
    os.mkdir(os.path.join(staged_dir, "final"))

    for step_name, step_conf in run_conf["steps"].items():
        for io in ["input", "output"]:
            for key, path_conf in step_conf.get(io, {}).items():
                if path_conf["root_dir"] == "staged":
                    root_dir_abs = staged_dir
                elif path_conf["root_dir"] == "canonical":
                    root_dir_abs = paths["LOCAL"]["canonical"]
                else:
                    raise KeyError(
                        f"root_dir for {step_name} must be 'staged' or 'canonical' rather than {root_dir}"
                    )
                run_conf["steps"][step_name][f"{io}"][key][
                    "root_dir_abs"
                ] = root_dir_abs

    return run_conf


def read_conf_and_make_dirs(*args):
    args = parse_args(args)
    paths = conf.read(args.paths)
    run_conf = conf.read(args.run)
    run_conf = create_staged_dirs_and_set_abs_paths(run_conf, paths)
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


def make_path(path_conf, io, key, subs=None):
    conf = path_conf[io][key]

    filename = conf.get("filename", "")
    for var in re.findall(r"\/(.*?)\/", filename):
        try:
            filename = filename.replace(f"/{var}/", subs[var])
        except (KeyError, TypeError):
            raise KeyError(f"Variable {var} not found in subs")

    return os.path.join(
        conf["root_dir_abs"],
        conf["sub_dir"],
        filename,
    )
