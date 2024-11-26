import json
import os.path

import typer
from rich import print

from isra.src.config.constants import THREAT_MODEL_FILE, get_app_dir
from isra.src.utils.questionary_wrapper import qselect, qmulti

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def edit_threats_countermeasures():
    data = read_current_threat_model()
    security_threats = data["security_threats"]

    while True:
        control_ids = set()
        for threat in security_threats:
            for cm in threat['countermeasures']:
                control_ids.add(cm['countermeasure_id'])

        threat_ids = [x["threat_id"] for x in security_threats]
        control_ids = list(control_ids)

        print(f"Threats: {len(threat_ids)}")
        print(f"Countermeasures: {len(control_ids)}")
        print()
        print("Options:")
        choices = [
            "Delete specific threats",
            "Delete specific countermeasures",
            # "Move a countermeasure to another threat",
            "Save changes and exit",
            "Exit without saving"
        ]

        choice = qselect("Choose an option: ", choices=choices)

        if choice == 'Delete specific threats':
            selected_threat_ids = qmulti("Enter the ID of the threats", choices=threat_ids)

            initial_count = len(security_threats)  # Count before removal
            security_threats = [threat for threat in security_threats if threat['threat_id'] not in selected_threat_ids]

            # Check how many threats were removed
            removed_count = initial_count - len(security_threats)
            if removed_count > 0:
                print(f"Removed {removed_count} threat(s).")
            else:
                print("No threats were found with the specified IDs.")

            data["security_threats"] = security_threats
        elif choice == "Delete specific countermeasures":
            selected_control_ids = qmulti("Enter the ID of the countermeasures", choices=control_ids)

            for threat in security_threats:
                initial_count = len(threat['countermeasures'])  # Count before removal
                threat['countermeasures'] = [
                    cm for cm in threat['countermeasures'] if cm['countermeasure_id'] not in selected_control_ids
                ]
                removed_count = initial_count - len(threat['countermeasures'])  # Count of removed countermeasures

                if removed_count > 0:
                    print(f"Removed {removed_count} countermeasure(s) from threat ID {threat['threat_id']}.")

            data["security_threats"] = security_threats

        elif choice == 'Move a countermeasure to another threat':
            print("Work in progress!")
        elif choice == 'Save changes and exit':
            write_current_threat_model(data)
            print("Changes saved. Exiting.")
            break
        elif choice == 'Exit without saving':
            print("Exiting without saving.")
            break

        else:
            print("Invalid option. Please try again.")


def create_new_threat_model():
    threat_model = {
        "security_threats": []
    }
    write_current_threat_model(threat_model)
    print("New threat model initialized")


def check_current_threat_model(raise_if_not_exists=True):
    properties_dir = get_app_dir()
    threat_model_path = os.path.join(properties_dir, THREAT_MODEL_FILE)

    if os.path.exists(threat_model_path):
        return threat_model_path
    else:
        print("No threat model initialized")
        if raise_if_not_exists:
            raise typer.Exit(-1)
        else:
            return ""


def read_current_threat_model():
    threat_model_path = check_current_threat_model()
    with open(threat_model_path, "r") as f:
        template = json.load(f)
    return template


def write_current_threat_model(threat_model):
    threat_model_path = check_current_threat_model()
    with open(threat_model_path, "w") as f:
        f.write(json.dumps(threat_model, indent=4))


# Commands

@app.callback()
def callback():
    """
    Threat model creation
    """


@app.command()
def new():
    """
    Starts the creation of a new component
    """
    create_new_threat_model()


@app.command()
def edit():
    """
    Starts the creation of a new component
    """
    edit_threats_countermeasures()


@app.command()
def info():
    """
    Shows current threat model status
    """
    threat_model = read_current_threat_model()

    threats_count = 0
    controls_count = 0
    for threat in threat_model["security_threats"]:
        threats_count += 1
        print(threat["threat_id"])
        for control in threat["countermeasures"]:
            controls_count += 1
            print("\t" + control["countermeasure_id"])

    print()
    print(f"Total threats: {threats_count}")
    print(f"Total controls: {controls_count}")
