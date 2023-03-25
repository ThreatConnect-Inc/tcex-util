"""TcEx Framework Module"""

# standard library
import sys
from typing import Literal, NoReturn

# third-party
from rich import print  # pylint: disable=redefined-builtin
from rich.columns import Columns
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

AlignMethod = Literal['left', 'center', 'right']


class RenderPanel:
    """Render Panel"""

    accent = 'dark_orange'
    title_align: AlignMethod = 'left'

    @classmethod
    def column(
        cls,
        column_data: list[str],
        title: str,
        subtitle: str | None = None,
        equal: bool = False,
        expand: bool = True,
    ):
        """Render Column with index in a panel."""
        columns = Columns(column_data, equal=equal, expand=expand)
        print(
            Panel(
                columns,
                title=title,
                title_align=cls.title_align,
                subtitle=subtitle,
            )
        )

    @classmethod
    def column_index(
        cls,
        column_data: list[str],
        title: str,
        subtitle: str | None = None,
        equal: bool = False,
        expand: bool = True,
    ):
        """Render Column with index in a panel."""
        column_data = [f'[{cls.accent}]{i}.[/{cls.accent}] {o}' for i, o in enumerate(column_data)]
        columns = Columns(column_data, equal=equal, expand=expand)
        print(
            Panel(
                columns,
                title=title,
                title_align=cls.title_align,
                subtitle=subtitle,
            )
        )

    @classmethod
    def error(cls, message: str):
        """Render error panel."""
        print(
            Panel(
                Text(
                    f'{message}',
                    style='bold red',
                ),
                expand=True,
                title='Error',
                title_align=cls.title_align,
            )
        )

    @classmethod
    def failure(cls, message: str) -> NoReturn:
        """Render failure panel."""
        print(
            Panel(
                Text(
                    f'{message}',
                    style='bold red',
                ),
                expand=True,
                title='Failure',
                title_align=cls.title_align,
            )
        )
        sys.exit(1)

    @staticmethod
    def info(message: str, title: str = 'Info', title_align: AlignMethod = 'left'):
        """Render info panel."""
        print(
            Panel(
                f'{message}',
                expand=True,
                title=title,
                title_align=title_align,
            )
        )

    @staticmethod
    def invalid_value(message: str, title: str, title_align: AlignMethod = 'left'):
        """Render invalid values panel."""
        print(
            Panel(
                Text(
                    f'{message}',
                    style='bold yellow',
                ),
                expand=True,
                title=title,
                title_align=title_align,
            )
        )

    @classmethod
    def list(cls, title: str, items: list[str], style: str = ''):
        """Render list panel."""
        items = [f'[white]•[/white] {i}' for i in items]
        item_list = '\n'.join(items)

        # render error panel
        if item_list:
            print(
                Panel(
                    item_list,
                    border_style='',
                    style=style,
                    title=title,
                    title_align=cls.title_align,
                )
            )

    @staticmethod
    def rule(title: str, align: AlignMethod = 'center', style: str = ''):
        """Render a horizontal rule."""
        print(
            Panel(
                Rule(
                    title=title,
                    align=align,
                    style=style,
                )
            )
        )

    @classmethod
    def success(cls, message: str):
        """Render success panel."""
        print(
            Panel(
                Text(
                    f'{message}',
                    style='bold green',
                ),
                expand=True,
                title='Success',
                title_align=cls.title_align,
            )
        )

    @classmethod
    def warning(cls, message: str):
        """Render warning panel."""
        print(
            Panel(
                Text(
                    f'{message}',
                    style='bold yellow',
                ),
                expand=True,
                title='Warning',
                title_align=cls.title_align,
            )
        )
