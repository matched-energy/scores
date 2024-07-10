import yaml


def from_yaml(path):
    with open(path, "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)
