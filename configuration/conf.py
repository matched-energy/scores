import os
import re

import scores.common.utils as utils

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def get_vars(text):
    return re.findall(r"\${(.*?)}", text)


def substitute_vars(text):
    for var in get_vars(text):
        try:
            text = text.replace(f"${{{var}}}", os.environ[var])
        except KeyError:
            raise KeyError(f"Enviroment variable {var} not set")
    return text


def read(path, conf_dir=False):
    with open(os.path.join(DIR, path) if conf_dir else path, "r") as file:
        return utils.from_yaml_text(substitute_vars(file.read()))
