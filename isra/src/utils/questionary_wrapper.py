import questionary
import sys
import typer

if sys.platform == "win32":
    from prompt_toolkit.output.win32 import NoConsoleScreenBufferError

"""
The reason this wrapper exists is because it seems that I can't ask questions using PyCharm on Windows.
Every time I run a script it throws this NoConsoleScreenBufferError that I cannot be constantly handling over the code.
Instead, I just create this wrapper script that handles this exception and uses the default input function
"""


def qconfirm(question_text):
    try:
        answer = questionary.confirm(question_text).ask()
    except NoConsoleScreenBufferError:
        answer = input(question_text + " (y/n)") == "y"

    if answer is None:
        raise typer.Exit(-1)

    return answer


def qselect(question_text, choices):
    try:
        if len(choices) > 36:
            print("Too many choices! Please input the answer manually.")
            answer = input(question_text + " " + str(choices))
        else:
            answer = questionary.select(message=question_text,
                                        use_shortcuts=True,
                                        use_arrow_keys=True,
                                        choices=choices).ask()
    except NoConsoleScreenBufferError:
        answer = input(question_text + " " + str(choices))

    if answer is None:
        raise typer.Exit(-1)

    return answer


def qmulti(question_text, choices):
    try:
        if len(choices) > 36:
            print("Too many choices! Please input the answer manually.")
            answer = input(question_text + " " + str(choices))
        else:
            answer = questionary.checkbox(message=question_text,
                                          choices=choices).ask()
    except NoConsoleScreenBufferError:
        answer = input(question_text + " " + str(choices))
        answer = [answer]

    if answer is None:
        raise typer.Exit(-1)

    return answer


def qtext(question_text, default=""):
    try:
        answer = questionary.text(question_text, default=default).ask()
    except NoConsoleScreenBufferError:
        answer = input(question_text)

    if answer is None:
        raise typer.Exit(-1)

    return answer


def qpath(question_text, default=""):
    try:
        answer = questionary.path(question_text, default=default).ask()
    except NoConsoleScreenBufferError:
        answer = input(question_text)

    if answer is None:
        raise typer.Exit(-1)

    return answer
