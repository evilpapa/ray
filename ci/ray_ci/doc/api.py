import re
import importlib

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


_SPHINX_AUTOSUMMARY_HEADER = ".. autosummary::"
_SPHINX_AUTOCLASS_HEADER = ".. autoclass::"


class AnnotationType(Enum):
    PUBLIC_API = "PublicAPI"
    DEVELOPER_API = "DeveloperAPI"
    DEPRECATED = "Deprecated"
    UNKNOWN = "Unknown"


class CodeType(Enum):
    CLASS = "Class"
    FUNCTION = "Function"


@dataclass
class API:
    name: str
    annotation_type: AnnotationType
    code_type: CodeType

    @staticmethod
    def from_autosummary(doc: str, current_module: Optional[str] = None) -> List["API"]:
        """
        Parse API from the following autosummary sphinx block.

        .. autosummary::
            :option_01
            :option_02

            api_01
            api_02
        """
        apis = []
        lines = doc.splitlines()
        if not lines:
            return apis

        if lines[0].strip() != _SPHINX_AUTOSUMMARY_HEADER:
            return apis

        for line in lines:
            if line == _SPHINX_AUTOSUMMARY_HEADER:
                continue
            if line.strip().startswith(":"):
                # option lines
                continue
            if not line.strip():
                # empty lines
                continue
            if not re.match(r"\s", line):
                # end of autosummary, \s means empty space, this line is checking if
                # the line is not empty and not starting with empty space
                break
            api_name = (
                f"{current_module}.{line.strip()}" if current_module else line.strip()
            )
            apis.append(
                API(
                    name=API._fullname(api_name),
                    annotation_type=AnnotationType.PUBLIC_API,
                    code_type=CodeType.FUNCTION,
                )
            )

        return apis

    @staticmethod
    def from_autoclass(
        doc: str, current_module: Optional[str] = None
    ) -> Optional["API"]:
        """
        Parse API from the following autoclass sphinx block.

        .. autoclass:: api_01
        """
        doc = doc.strip()
        if not doc.startswith(_SPHINX_AUTOCLASS_HEADER):
            return None
        cls = doc[len(_SPHINX_AUTOCLASS_HEADER) :].strip()
        api_name = f"{current_module}.{cls}" if current_module else cls

        return API(
            name=API._fullname(api_name),
            annotation_type=AnnotationType.PUBLIC_API,
            code_type=CodeType.CLASS,
        )

    @staticmethod
    def _fullname(name: str) -> str:
        """
        Some APIs have aliases declared in __init__.py file (see ray/data/__init__.py
        for example). This method converts the alias to full name. This is to make sure
        out analysis can be performed on the same set of canonial names.
        """
        tokens = name.split(".")
        if len(tokens) == 1:
            return name
        module_name = ".".join(tokens[:-1])
        attribute_name = tokens[-1]
        module = importlib.import_module(module_name)
        attribute = getattr(module, attribute_name)

        return f"{attribute.__module__}.{attribute.__qualname__}"
