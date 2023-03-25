"""TcEx Framework Module"""

# standard library
from typing import Literal

from .render_panel import RenderPanel
from .render_prompt import RenderPrompt
from .render_table import RenderTable

AlignMethod = Literal['left', 'center', 'right']


class Render:
    """Render CLI Output"""

    accent = 'dark_orange'
    accent2 = 'dodger_blue2'
    panel = RenderPanel
    prompt = RenderPrompt
    table = RenderTable
    title_align: AlignMethod = 'left'
