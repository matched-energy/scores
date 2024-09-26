import numpy as np
import yaml


def float_representer(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:float", format(value, ".2f"))


yaml.add_representer(float, float_representer)
yaml.add_representer(np.float32, float_representer)
yaml.add_representer(np.float64, float_representer)


def from_yaml_text(text):
    return yaml.load(text, Loader=yaml.FullLoader)


def from_yaml_file(path):
    with open(path, "r") as file:
        return from_yaml_text(file.read())


def to_yaml_text(obj):
    return yaml.dump(obj, default_flow_style=False)


def to_yaml_file(obj, path):
    with open(path, "w") as file:
        file.write(to_yaml_text(obj))
