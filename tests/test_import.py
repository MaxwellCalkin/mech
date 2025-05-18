import importlib
import pytest


@pytest.mark.parametrize("module", ["mech_arena", "mech_arena.game"])
def test_import(module):
    importlib.import_module(module)
