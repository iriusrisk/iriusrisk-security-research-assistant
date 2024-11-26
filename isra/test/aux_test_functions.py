import json
import os
import shutil

from isra.src.config.constants import get_app_dir, TEMPLATE_FILE, CONFIG_FOLDER


def set_component_from_file(input_file):
    directory_path = CONFIG_FOLDER
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Check if the directory path exists
    if not os.path.isdir(CONFIG_FOLDER):
        print(f"Error: Directory path '{CONFIG_FOLDER}' not found.")
        return

    # Get the base filename from the input file path
    file_name = os.path.basename(input_file)

    # Copy the file to the destination directory
    shutil.copy(str(input_file), str(TEMPLATE_FILE))

    print(f"File '{file_name}' copied to '{directory_path}' successfully.")


def get_template():
    with open(TEMPLATE_FILE, "r") as f:
        template = json.loads(f.read())
    return template


def assert_process(result):
    if result.exit_code != 0:
        print(result.stdout)
    assert result.exit_code == 0
