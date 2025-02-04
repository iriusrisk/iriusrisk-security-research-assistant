import importlib.metadata

import typer
import typer.completion
from typer._completion_shared import Shells

from isra.src.component import component
from isra.src.config import config
from isra.src.ile import ile
from isra.src.screening import screening
from isra.src.standards import standards
from isra.src.tests import tests
from isra.src.tm import tm
from isra.src.srt import srt

app = typer.Typer(no_args_is_help=True, add_completion=False, add_help_option=False)
app_completion = typer.Typer(help="Generate and install completion scripts.", hidden=True)
app.add_typer(app_completion, name="completion")
app.add_typer(config.app, name="config")
app.add_typer(tests.app, name="tests")
app.add_typer(ile.app, name="ile", hidden=True)
app.add_typer(screening.app, name="screening")
app.add_typer(standards.app, name="standards")
app.add_typer(component.app, name="component")
app.add_typer(tm.app, name="tm", hidden=True)
app.add_typer(srt.app, name="srt", hidden=True)

config.initialize_configuration()


@app.callback()
def callback():
    """
    IriusRisk Security Research Assistant\n
    Amazing CLI tool from our beloved Security Research Team
    """


@app_completion.command(no_args_is_help=True, help="Show completion for the specified shell, to copy or customize it.")
def show(ctx: typer.Context, shell: Shells) -> None:
    typer.completion.show_callback(ctx, None, shell)


@app_completion.command(no_args_is_help=True, help="Install completion for the specified shell.")
def install(ctx: typer.Context, shell: Shells) -> None:
    typer.completion.install_callback(ctx, None, shell)


@app.command()
def about():
    """
    Information about this application
    """
    version = importlib.metadata.version('isra')
    typer.echo("Yet another tool made with love by Alvaro Reyes for IriusRisk")
    typer.echo(f"Version: {version}")


if __name__ == "__main__":
    config.initialize_configuration()
    app(["about"])
