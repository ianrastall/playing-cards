"""Verify the migration baseline and explicitly recorded subsequent artwork revisions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    migration = json.loads((ROOT/'docs/layout-migration.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
    current = {asset['path']: asset for asset in catalog['assets']}
    revisions_path = ROOT/'docs/asset-revisions.json'
    revisions = json.loads(revisions_path.read_text(encoding='utf-8'))['assets'] if revisions_path.exists() else []
    updates = {record['path']: record for record in revisions}
    assert len(updates) == len(revisions), 'Duplicate artwork revision paths'
    assert len(migration['assets']) == 408
    assert len({asset['path'] for asset in migration['assets']}) == 408
    for record in migration['assets']:
        path = (ROOT/record['path']).resolve()
        assert path.is_relative_to(ROOT/'designs'), path
        expected = record['sha256']
        if record['path'] in updates:
            update = updates[record['path']]
            assert update['migration_sha256'] == expected, path
            manifest_path = (ROOT/update['manifest']).resolve()
            assert manifest_path.is_relative_to(ROOT/'designs'), manifest_path
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            assert manifest['status'] == 'approved' and manifest['revision'] == update['revision']
            approved = {str((manifest_path.parent/card['path']).resolve()): card['sha256'] for card in manifest['cards']}
            expected = update['sha256']
            assert approved[str(path)] == expected, path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
        assert current[record['path']]['sha256'] == expected, path
    assert set(updates) <= {record['path'] for record in migration['assets']}
    assert not (ROOT/'cards').exists()
    assert not (ROOT/'deck.json').exists()
    print(f'PASS layout: 408 finished PNGs; {408-len(updates)} migration hashes preserved, {len(updates)} documented approved revisions; catalog paths and hashes match')


if __name__ == '__main__':
    main()
