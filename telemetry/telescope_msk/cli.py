import fire
from rich.console import Console
from rich.markdown import Markdown


def display(lines, out):
    text = "\n".join(lines) + "\n"
    out.write(text)


def cli(target):
    fire.core.Display = display
    fire.Fire(target)


def get_console():
    console = Console()

    return console


def print_markdown(content):
    console = Console()
    markdown = Markdown(content)
    console.print(markdown)
