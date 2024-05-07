import json
import os
import shutil

from isra.src.config.config import get_app_dir


def set_component_from_file(input_file):
    directory_path = get_app_dir()
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Check if the directory path exists
    if not os.path.isdir(directory_path):
        print(f"Error: Directory path '{directory_path}' not found.")
        return

    # Get the base filename from the input file path
    file_name = os.path.basename(input_file)

    # Construct the destination file path in the directory
    destination_path = os.path.join(directory_path, "temp.irius")

    # Copy the file to the destination directory
    shutil.copy(str(input_file), str(destination_path))

    print(f"File '{file_name}' copied to '{directory_path}' successfully.")


def get_template():
    properties_dir = get_app_dir()
    template_path = os.path.join(properties_dir, "temp.irius")
    with open(template_path, "r") as f:
        template = json.loads(f.read())
    return template


def assert_process(result):
    if result.exit_code != 0:
        print(result.stdout)
    assert result.exit_code == 0
