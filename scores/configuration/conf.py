import os
import re
from pathlib import Path
from typing import Any

import scores.common.utils as utils

DIR = Path.cwd()


def get_vars(text: str) -> list[str]:
    return re.findall(r"\${(.*?)}", text)


def substitute_vars(text: str) -> str:
    for var in get_vars(text):
        try:
            text = text.replace(f"${{{var}}}", os.environ[var])
        except KeyError:
            raise KeyError(f"Environment variable {var} not set")
    return text


def read(path: Path, conf_dir: bool = False) -> Any:
    with open(DIR / path if conf_dir else path, "r") as file:
        return utils.from_yaml_text(substitute_vars(file.read()))
