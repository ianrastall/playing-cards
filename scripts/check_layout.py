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
    ledger = json.loads(revisions_path.read_text(encoding='utf-8')) if revisions_path.exists() else {}
    revisions = ledger.get('assets', [])
    archives = {}
    for release in ledger.get('archived_releases', []):
        archive_root = (ROOT/release['archive_root']).resolve()
        assert archive_root.is_relative_to(ROOT/'designs')
        manifest = json.loads((archive_root/'manifest.json').read_text(encoding='utf-8'))
        assert len(manifest['cards']) == manifest['card_count']
        for card in manifest['cards']:
            old_path = release['original_root']+'/'+card['path']
            archived = (archive_root/card['path']).resolve()
            assert archived.is_relative_to(archive_root)
            assert old_path not in archives
            archives[old_path] = (archived, card['sha256'])
        report_path = ROOT/release['replacement_report']
        report = json.loads(report_path.read_text(encoding='utf-8'))
        assert report['status'] == 'promoted-and-validated'
        design_root = report_path.parents[2]
        replacements = {(design_root/c['path']).relative_to(ROOT).as_posix(): c['sha256'] for c in report['cards']}
        assert len(replacements) == report['card_count']
        actual = {p for p in current if p.startswith(release['original_root']+'/')}
        assert actual == set(replacements), 'Replacement inventory mismatch'
        for path, checksum in replacements.items():
            assert current[path]['sha256'] == checksum
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == checksum
    updates = {record['path']: record for record in revisions}
    assert len(updates) == len(revisions), 'Duplicate artwork revision paths'
    assert len(migration['assets']) == 408
    assert len({asset['path'] for asset in migration['assets']}) == 408
    for record in migration['assets']:
        path = (ROOT/record['path']).resolve()
        assert path.is_relative_to(ROOT/'designs'), path
        expected = record['sha256']
        if record['path'] in archives:
            archived, checksum = archives[record['path']]
            assert checksum == expected
            assert hashlib.sha256(archived.read_bytes()).hexdigest() == expected
            continue
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
    assert set(archives) <= {r['path'] for r in migration['assets']}
    print(f'PASS layout: 408 migration PNGs accounted for; {len(archives)} archived originals, {len(updates)} recorded revisions; replacement inventories and hashes match')


if __name__ == '__main__':
    main()
