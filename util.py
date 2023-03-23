"""TcEx Utilities"""
# standard library
import ast
import ipaddress
import re
from re import Pattern
from typing import Any

# third-party
import astunparse

from .aes_operation import AesOperation
from .datetime_operation import DatetimeOperation
from .string_operation import StringOperation
from .variable import Variable

# import jmespath


class Util(AesOperation, DatetimeOperation, StringOperation, Variable):
    """TcEx Utilities Class"""

    @staticmethod
    def find_line_in_code(
        needle: str | Pattern,
        code: str,
        trigger_start: Pattern | str | None = None,
        trigger_stop: Pattern | str | None = None,
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
        trigger_start: Pattern | str | None = None,
        trigger_stop: Pattern | str | None = None,
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
    def flatten_list(lst: list[Any]) -> list[Any]:
        """Flatten a list

        Will work for lists of lists to arbitrary depth
        and for lists with a mix of lists and single values
        """
        flat_list = []
        for sublist in lst:
            if isinstance(sublist, list):
                for item in Util.flatten_list(sublist):
                    flat_list.append(item)
            else:
                flat_list.append(sublist)
        return flat_list

    @staticmethod
    def is_cidr(possible_cidr_range: str) -> bool:
        """Return True if the provided value is a valid CIDR block."""
        try:
            ipaddress.ip_address(possible_cidr_range)
        except ValueError:
            try:
                ipaddress.ip_interface(possible_cidr_range)
            except Exception:
                return False
            return True
        return False

    @staticmethod
    def is_ip(possible_ip: str) -> bool:
        """Return True if the provided value is a valid IP address."""
        try:
            ipaddress.ip_address(possible_ip)
        except ValueError:
            return False
        return True

    @staticmethod
    def printable_cred(
        cred: str,
        visible: int = 1,
        mask_char: str = '*',
        mask_char_count: int = 4,
    ) -> str:
        """Return a printable (masked) version of the provided credential.

        Args:
            cred: The cred to print.
            visible: The number of characters at the beginning and ending of the cred to not mask.
            mask_char: The character to use in the mask.
            mask_char_count: How many mask character to insert (obscure cred length).
        """
        visible = max(visible, 1)
        if isinstance(cred, str):
            mask_char = mask_char or '*'
            if cred is not None and len(cred) >= visible * 2:
                cred = f'{cred[:visible]}{mask_char * mask_char_count}{cred[-visible:]}'
        return cred

    @staticmethod
    def remove_none(dict_: dict[Any, Any | None]) -> dict[Any, Any]:
        """Remove any mapping from a single level dict with a None value."""
        return {k: v for k, v in dict_.items() if v is not None}

    @staticmethod
    def standardize_asn(asn: str) -> str:
        """Return the ASN formatted for ThreatConnect."""
        numbers = re.findall('[0-9]+', asn)
        if len(numbers) == 1:
            asn = f'ASN{numbers[0]}'
        return asn