"""TcEx Framework Module"""
# standard library
import ipaddress
import re
from typing import Any

from .aes_operation import AesOperation
from .datetime_operation import DatetimeOperation
from .string_operation import StringOperation
from .variable import Variable


class Util(AesOperation, DatetimeOperation, StringOperation, Variable):
    """TcEx Utilities Class"""

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
