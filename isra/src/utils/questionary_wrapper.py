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


def split_array(arr, segment_size):
    """Splits an array into segments of a fixed size."""
    return [arr[i:i + segment_size] for i in range(0, len(arr), segment_size)]


def join_arrays(arrays):
    """Joins a list of arrays into a single array."""
    return [item for sublist in arrays for item in sublist]


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
            print("Too many choices!")

            splitt = split_array(choices, 30)
            answer = None
            for i, arrd in enumerate(splitt):
                print(f"Page {i + 1}/{len(splitt)}")
                prev = questionary.select(message=question_text,
                                          use_shortcuts=True,
                                          use_arrow_keys=True,
                                          choices=["Next page"] + arrd).ask()
                if prev is None:
                    raise typer.Exit(-1)

                if prev != "Next page":
                    answer = prev
                    break

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
            print("Too many choices!")

            list_of_arrays = []
            splitt = split_array(choices, 30)
            for i, arrd in enumerate(splitt):
                print(f"Page {i + 1}/{len(splitt)}")
                prev = questionary.checkbox(message=question_text,
                                            choices=["Mark this to move to next page"] + arrd).ask()

                if prev is None:
                    raise typer.Exit(-1)

                if len(prev) == 1 and prev[0] == "Mark this to move to next page":
                    pass
                else:
                    list_of_arrays.append(prev)

            answer = join_arrays(list_of_arrays)
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


def qauto(question_text, default="", choices=None):
    if choices is None:
        choices = []
    try:
        answer = questionary.autocomplete(question_text, choices=choices, default=default).ask()
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
