"""TcEx Framework Module"""
# standard library
import ast
import logging
import os
import re

# third-party
import astunparse
import black
import isort
from black.report import NothingChanged

from .render.render import Render

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])


class CodeOperation:
    """TcEx FrameWork Code Operations"""

    @staticmethod
    def find_line_in_code(
        needle: str | re.Pattern,
        code: str,
        trigger_start: re.Pattern | str | None = None,
        trigger_stop: re.Pattern | str | None = None,
    ) -> str | None:
        """Return matching line of code in a class definition.

        Args:
            needle: The string to search for.
            code: The contents of the Python file to search.
            trigger_start: The regex pattern to use to trigger the search.
            trigger_stop: The regex pattern to use to stop the search.
        """
        magnet_on = not trigger_start
        for line in astunparse.unparse(ast.parse(code)).split('\n'):
            if line.lstrip()[:1] not in ("'", '"'):
                # Find class before looking for needle
                if trigger_start is not None and re.match(trigger_start, line):
                    magnet_on = True
                    continue

                # find need now that class definition is found
                if magnet_on is True and re.match(needle, line):
                    line = line.strip()
                    return line

                # break if needle not found before next class definition
                if trigger_stop is not None and re.match(trigger_stop, line) and magnet_on is True:
                    break
        return None

    @staticmethod
    def find_line_number(
        needle: str,
        contents: str,
        trigger_start: re.Pattern | str | None = None,
        trigger_stop: re.Pattern | str | None = None,
    ) -> int | None:
        """Return matching line of code in a class definition.

        Args:
            needle: The string to search for.
            contents: The contents (haystack) to search
            trigger_start: The regex pattern to use to trigger the search.
            trigger_stop: The regex pattern to use to stop the search.
        """
        magnet_on = not trigger_start
        for line_number, line in enumerate(contents.split('\n'), start=1):
            if line.strip():
                # set magnet_on to True if trigger_start is found
                if trigger_start is not None and re.match(trigger_start, line):
                    magnet_on = True
                    continue

                # find needle now that trigger is found
                if magnet_on is True and re.match(needle, line):
                    return line_number

                # break if trigger_stop is defined and found
                if trigger_stop is not None and re.match(trigger_stop, line) and magnet_on is True:
                    break
        return None

    @staticmethod
    def format_code(_code):
        """Return formatted code."""
        # run black formatter on code
        mode = black.FileMode(line_length=100, string_normalization=False)
        try:
            _code = black.format_file_contents(_code, fast=False, mode=mode)
        except ValueError as ex:
            _logger.exception('Formatting of code with black failed.')
            Render.panel.failure(f'Formatting of code with black failed {ex}.')
        except NothingChanged:
            pass

        # run isort on code
        try:
            isort_args = (
                {'settings_file': 'pyproject.toml'} if os.path.isfile('pyproject.toml') else {}
            )
            isort_config = isort.Config(**isort_args)
            _code = isort.code(_code, config=isort_config)
        except Exception as ex:
            _logger.exception('Formatting of code with isort failed.')
            # _logger.debug(_code)
            Render.panel.failure(f'Formatting of code with isort failed {ex}.')

        return _code
