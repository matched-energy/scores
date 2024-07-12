import datetime
import os
import re

import scores.common.utils as utils

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def get_vars(text):
    return re.findall(r"\${(.*?)}", text)


def substitute_vars(text):
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for var in get_vars(text):
        try:
            if var == "DATETIME":
                replacement = now
            else:
                replacement = os.environ[var]
            text = text.replace(f"${{{var}}}", replacement)
        except KeyError:
            raise KeyError(
                f"Don't recognise {var}: need environment variable or 'DATETIME'"
            )
    return text


def read(path, conf_dir=False):
    with open(os.path.join(DIR, path) if conf_dir else path, "r") as file:
        return utils.from_yaml_text(substitute_vars(file.read()))
