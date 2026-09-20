"""Design-local catalog entry point; shared validation lives in the repository scripts."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('collection_catalog', ROOT.parents[1] / 'scripts/catalog.py')
_shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_shared)


def build_catalog():
    return _shared.build_design_catalog(ROOT)


if __name__ == '__main__':
    _shared.main(ROOT)
