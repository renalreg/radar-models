"""Check that every <Name>Base model has a <Name> model and a <Name>Read model.

The models module is imported to find its source file, which is then parsed
with ast to list the classes it defines, in file order with line numbers.
"""

import ast
import inspect
from pathlib import Path

import pytest

from radar_models import radar3 as models


# Base classes that are not expected to have a table or Read version,
# e.g. shared mixins that other Bases inherit from. Add names here to skip them.
IGNORED_BASES: set[str] = {"TestBase", "CystinosisVisitBase"}

MODELS_FILE = Path(inspect.getsourcefile(models))

BASE_SUFFIX = "Base"
READ_SUFFIX = "Read"


def top_level_classes(path: Path) -> dict[str, int]:
    """Class name -> line number for every class defined at the top of the file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name: node.lineno for node in tree.body if isinstance(node, ast.ClassDef)
    }


def base_classes(classes: dict[str, int]) -> dict[str, int]:
    """The <Name>Base classes that are not in IGNORED_BASES."""
    return {
        name: line
        for name, line in classes.items()
        if name.endswith(BASE_SUFFIX)
        and name != BASE_SUFFIX
        and name not in IGNORED_BASES
    }


def find_missing(classes: dict[str, int]) -> dict[str, list[str]]:
    """Base class name -> the versions of it that are not defined."""
    missing: dict[str, list[str]] = {}
    for base in base_classes(classes):
        stem = base[: -len(BASE_SUFFIX)]
        absent = [name for name in (stem, stem + READ_SUFFIX) if name not in classes]
        if absent:
            missing[base] = absent
    return missing


def test_models_file_defines_base_classes():
    assert base_classes(top_level_classes(MODELS_FILE)), (
        f"no *{BASE_SUFFIX} classes found in {MODELS_FILE}"
    )


def test_every_base_has_table_and_read_version():
    classes = top_level_classes(MODELS_FILE)
    missing = find_missing(classes)

    if missing:
        width = max(len(base) for base in missing)
        lines = [
            f"  {base:<{width}}  (line {classes[base]:>4})  missing: {', '.join(absent)}"
            for base, absent in missing.items()
        ]
        checked = len(base_classes(classes))
        pytest.fail(
            f"{len(missing)} of {checked} {BASE_SUFFIX} classes in {MODELS_FILE.name} "
            f"are missing a version:\n" + "\n".join(lines),
            pytrace=False,
        )
