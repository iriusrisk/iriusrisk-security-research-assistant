import os
import subprocess

import time
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn
from rich.progress import TextColumn, BarColumn, TimeRemainingColumn
from rich.style import Style

from isra.src.config.config import get_property
from isra.src.config.constants import ILE_JAR_FILE

app = typer.Typer(no_args_is_help=True, add_help_option=False)


@app.callback()
def callback():
    """
    IriusRisk Library Editor
    """


@app.command()
def run():
    """
    Run an ILE instance
    """
    rootdir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(rootdir, ILE_JAR_FILE)
    if filepath == "":
        print("No ILE jar has been defined. Please define the path to the ILE .jar file in the ile_jar_location "
              "config variable")
        raise typer.Exit(-1)
    if get_property("ile_root_folder") == "":
        print("No ILE root folder has been defined")
        raise typer.Exit(-1)
    if get_property("ile_port") == "":
        print("No ILE port has been defined")
        raise typer.Exit(-1)

    with Progress(SpinnerColumn(),
                  TextColumn("[#01ECB4]Ready to start in...", justify="right"),
                  BarColumn(complete_style=Style(color="#01ECB4"), finished_style=Style(color="white")),
                  TimeRemainingColumn(),
                  ) as progress:
        task1 = progress.add_task("Description", total=5)
        print("[red]Just making sure you read this:")
        print("1. This will launch an instance of ILE.")
        print("2. All elements will be stored where you have indicated in the ile_root_folder.")
        print("3. Make sure that you have Java 8+ installed. Otherwise this process won't be able to start the ILE.")
        print("4. The ILE will be running until you stop this process or you close the console.")
        print("5. The ILE is a [red]deprecated tool[/red] that doesn't handle UUIDs, be aware of that")
        print(f"You can access the ILE by accessing http://localhost:{get_property('ile_port')}")

        while not progress.finished:
            progress.update(task1, advance=1)
            time.sleep(1)
    try:
        subprocess.call(['java', f'-Dserver.port={get_property("ile_port")}',
                         f'-Dappdir={get_property("ile_root_folder")}', '-jar', filepath])
    except Exception as e:
        print("Error while launching ILE: ", e)
