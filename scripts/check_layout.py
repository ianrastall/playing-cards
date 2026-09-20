"""Verify the byte-preserving multi-design migration against its historical baseline."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    migration = json.loads((ROOT/'docs/layout-migration.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
    current = {asset['path']: asset for asset in catalog['assets']}
    assert len(migration['assets']) == 408
    assert len({asset['path'] for asset in migration['assets']}) == 408
    for record in migration['assets']:
        path = (ROOT/record['path']).resolve()
        assert path.is_relative_to(ROOT/'designs'), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], path
        assert current[record['path']]['sha256'] == record['sha256'], path
    assert not (ROOT/'cards').exists()
    assert not (ROOT/'deck.json').exists()
    print('PASS migration: all 408 finished PNGs preserve their original bytes and resolve in the catalog')


if __name__ == '__main__':
    main()
