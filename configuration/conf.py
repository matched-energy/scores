import datetime
import os
import re

import scores.common.utils as utils

CONF_DIR = os.path.dirname(os.path.abspath(__file__))


def get_vars(text):
    return re.findall(r"\${(.*?)}", text)


def substitute_vars(text):
    for var in get_vars(text):
        try:
            if var == "DATETIME":
                replacement = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            else:
                replacement = os.environ[var]
            text = text.replace(f"${{{var}}}", replacement)
        except KeyError:
            raise KeyError(
                f"Don't recognise {var}: need environment variable or 'DATETIME'"
            )
    return text


def read(filename):
    with open(f"{CONF_DIR}/{filename}", "r") as file:
        return utils.from_yaml_text(substitute_vars(file.read()))
