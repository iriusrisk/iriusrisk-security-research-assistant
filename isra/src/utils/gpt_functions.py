import base64
import inspect
import os
import random

import httpx
import typer
from openai import OpenAI
from rich import print
from rich.progress import Progress, TextColumn, SpinnerColumn

from isra.src.config.config import get_property, get_resource
from isra.src.config.constants import TEST_ANSWERS_FILE, HINTS, PROMPTS_DIR
from isra.src.utils.text_functions import replace_non_ascii


def get_hint():
    return HINTS[random.randint(0, len(HINTS) - 1)]


def calculate_message_cost(gpt_model, prompt_tokens, answer_tokens):
    model_cost = {
        "gpt-3.5-turbo-0613": {"prompt_tokens": 0.000010, "answer_tokens": 0.000020},
        "gpt-3.5-turbo-1106": {"prompt_tokens": 0.000010, "answer_tokens": 0.000020},
        "gpt-3.5-turbo-16k": {"prompt_tokens": 0.000010, "answer_tokens": 0.000020},
        "gpt-4": {"prompt_tokens": 0.00003, "answer_tokens": 0.00006},
        "gpt-4-32k": {"prompt_tokens": 0.00006, "answer_tokens": 0.00012}
    }

    cost = model_cost[gpt_model]["prompt_tokens"] * prompt_tokens + model_cost[gpt_model][
        "answer_tokens"] * answer_tokens
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Answer tokens: {answer_tokens}")
    print(f"💸💸💸[green]That'll be [bold green]${round(cost, 6)}[/bold green][green], please💸💸💸")


def query_chatgpt(messages):
    result = ""
    test_mode = os.getenv("ISRA_TEST_MODE") == "1"
    if test_mode:
        print("[red]Test mode!")
        caller_name = inspect.stack()[1][3]
        print(f"Generating mock ChatGPT answer for function {caller_name}")
        test_answers_yaml = get_resource(TEST_ANSWERS_FILE)

        if caller_name in test_answers_yaml:
            result = test_answers_yaml[caller_name]
        elif caller_name + "_base64" in test_answers_yaml:
            result = base64.b64decode(test_answers_yaml[caller_name + "_base64"]).decode("utf-8")
        else:
            print(f"No mock answer found for function {caller_name}. "
                  f"Simply type what you would expect ChatGPT to respond")
            result = input()

    else:
        if get_property("openai_assistant_id") != "":
            with Progress(
                    SpinnerColumn(),
                    TextColumn(get_hint()),
                    transient=True,
            ) as progress:
                progress.add_task(description="Processing...", total=None)

                try:
                    client = OpenAI(timeout=httpx.Timeout(15.0, read=5.0, write=10.0, connect=3.0))
                    assistant = client.beta.assistants.retrieve(get_property("openai_assistant_id"))
                    my_thread = client.beta.threads.create()

                    for m in messages:
                        client.beta.threads.messages.create(thread_id=my_thread.id, role="user", content=m["content"])

                    run = client.beta.threads.runs.create(thread_id=my_thread.id, assistant_id=assistant.id)

                    while run.status != "completed":
                        keep_retrieving_run = client.beta.threads.runs.retrieve(thread_id=my_thread.id, run_id=run.id)
                        if keep_retrieving_run.status == "completed":
                            break

                    assistant_result = client.beta.threads.messages.list(thread_id=my_thread.id)

                    result = assistant_result.data[0].content[0].text.value
                except Exception:
                    print(
                        "Something happened when calling ChatGPT API. Make sure you defined the environment variable "
                        "OPENAI_API_KEY and that an OpenAI Assistant ID has been selected in the configuration."
                    )
                    raise typer.Exit(-1)
        else:
            with Progress(
                    SpinnerColumn(),
                    TextColumn(get_hint()),
                    transient=True,
            ) as progress:
                progress.add_task(description="Processing...", total=None)

                try:
                    client = OpenAI()

                    completion = client.chat.completions.create(
                        model=get_property("gpt_model"),
                        messages=messages
                    )

                    result = completion.choices[0].message.content

                    # Enable this for the lolz
                    # calculate_message_cost(get_property("gpt_model"), completion.usage.prompt_tokens,
                    #                      completion.usage.completion_tokens)
                except Exception:
                    print(
                        "Something happened when calling ChatGPT API. Make sure you defined the environment variable "
                        "OPENAI_API_KEY and that a GPT model has been selected in the configuration")
                    raise typer.Exit(-1)

    return replace_non_ascii(result)


def get_prompt(prompt):
    prompts_text = get_resource(os.path.join(PROMPTS_DIR, prompt), filetype="text")
    return prompts_text
