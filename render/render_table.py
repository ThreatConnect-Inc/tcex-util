"""TcEx Framework Module"""

# standard library
from typing import Literal

# third-party
from rich import print  # pylint: disable=redefined-builtin
from rich.panel import Panel
from rich.table import Table

AlignMethod = Literal['left', 'center', 'right']


class RenderTable:
    """Render Table"""

    title_align: AlignMethod = 'left'

    @classmethod
    def key_value(
        cls,
        title: str,
        kv_data: dict[str, str | None] | list[dict[str, str | None]],
        border_style: str = '',
        key_style: str = 'dodger_blue1',
        key_width: int = 20,
        value_style: str = 'bold',
        value_width: int = 80,
    ):
        """Render key/value table.

        Accepts the following structuresL
        {
            'key': 'value',
        }
        or
        [
            {
                'key': 'my key',
                'value': 'my_value'
            }
        ]
        """
        table = Table(
            border_style=border_style,
            expand=True,
            show_edge=False,
            show_header=False,
        )

        table.add_column(
            'key',
            justify='left',
            max_width=key_width,
            min_width=key_width,
            style=key_style,
        )
        table.add_column(
            'value',
            justify='left',
            max_width=value_width,
            min_width=value_width,
            style=value_style,
        )

        if isinstance(kv_data, dict):
            for key, value in kv_data.items():
                table.add_row(key, value)
        elif isinstance(kv_data, list):
            for item in kv_data:
                table.add_row(item['key'], item['value'])

        # render panel->table
        if kv_data:
            print(Panel(table, border_style=border_style, title=title, title_align=cls.title_align))
