from pathlib import Path
from typing import Any, Optional

import numpy as np
import yaml
from yaml import ScalarNode


def float_representer(dumper, value) -> ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:float", format(value, ".2f"))


yaml.add_representer(float, float_representer)
yaml.add_representer(np.float32, float_representer)
yaml.add_representer(np.float64, float_representer)


def from_yaml_text(text: str) -> Any:
    return yaml.load(text, Loader=yaml.FullLoader)


def from_yaml_file(path: Path) -> Any:
    with open(path, "r") as file:
        return from_yaml_text(file.read())


def to_yaml_text(obj: Any) -> Optional[str]:
    return yaml.dump(obj, default_flow_style=False)


def to_yaml_file(obj: Any, path: Path) -> None:
    with open(path, "w") as file:
        file.write(to_yaml_text(obj))
