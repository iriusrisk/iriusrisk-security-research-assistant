import json
import os

import typer

from isra.src.config.constants import get_app_dir
from isra.src.config.constants import TEMPLATE_FILE


def check_current_component(raise_if_not_exists=True):
    properties_dir = get_app_dir()
    template_path = os.path.join(properties_dir, TEMPLATE_FILE)

    if os.path.exists(template_path):
        return template_path
    else:
        print("No component initialized")
        if raise_if_not_exists:
            raise typer.Exit(-1)
        else:
            return ""


def read_current_component():
    template_path = check_current_component()
    with open(template_path, "r") as f:
        template = json.load(f)
    return template


def write_current_component(template):
    template_path = check_current_component()
    with open(template_path, "w") as f:
        f.write(json.dumps(template, indent=4))
