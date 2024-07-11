import datetime
import os
import re

import scores.common.utils as utils


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


def read(path):
    with open(path, "r") as file:
        return utils.from_yaml_text(substitute_vars(file.read()))
