import os
import re

import scores.common.utils as utils

CONF_DIR = os.path.dirname(os.path.abspath(__file__))


def get_env_vars(text):
    return re.findall(r"\${(.*?)}", text)


def substitute_env_vars(text):
    for env_var in get_env_vars(text):
        try:
            text = text.replace(f"${{{env_var}}}", os.environ[env_var])
        except KeyError:
            raise KeyError(f"Environment variable {env_var} not set")
    return text


def read(filename):
    with open(f"{CONF_DIR}/{filename}", "r") as file:
        return utils.from_yaml_text(substitute_env_vars(file.read()))
