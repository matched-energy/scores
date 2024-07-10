import yaml


def from_yaml_file(path):
    with open(path, "r") as file:
        return from_yaml_text(file.read())


def from_yaml_text(text):
    return yaml.load(text, Loader=yaml.FullLoader)
