"""TcEx Framework Module"""
# standard library
from typing import Literal

# third-party
from rich import print  # pylint: disable=redefined-builtin
from rich.panel import Panel
from rich.prompt import Prompt

AlignMethod = Literal['left', 'center', 'right']


class RenderPrompt:
    """Render Prompt"""

    title_align: AlignMethod = 'left'

    @staticmethod
    def ask(
        text: str,
        choices: list[str] | None = None,
        default: str | None = None,
        password: bool = False,
        show_choices: bool = True,
        show_default: bool = True,
    ) -> str | None:
        """Render a prompt"""
        return Prompt.ask(
            text,
            choices=choices,
            default=default,
            password=password,
            show_choices=show_choices,
            show_default=show_default,
        )

    @classmethod
    def input(cls, prompt_text: str, prompt_default: str, subtitle: str = '') -> str:
        """Render a prompt"""
        prompt_text = f'[white]{prompt_text}[/white][bold white]{prompt_default}[/bold white]'
        print(Panel(prompt_text, title='Input', title_align=cls.title_align, subtitle=subtitle))

        # collect input
        return input('> ').strip()  # nosec
