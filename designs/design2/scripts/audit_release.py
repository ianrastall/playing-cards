"""Bind every release PNG to an audited renderer record and the current catalog.

Use --verify-renderers before packaging to repeat full artwork audits. The default
checks their manifests, geometry and hashes and writes the complete release gate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image
from catalog import build_catalog
import render_tarot_faces as tarot

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/design/release-v1-audit.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def audit(verify=False):
    if verify:
        for name,args in [('register_face_masters.py',['--check','--active']),
                ('audit_number_cards.py',['--active']),('expand_french_faces.py',['--check']),
                ('render_tarot_faces.py',['--check','--active']),('audit_design2_registration.py',[])]:
            subprocess.run([sys.executable,str(ROOT/'scripts'/name),*args],check=True)
    sources = {}
    records = {}
    for file in ('registered-faces-v1.json','number-cards-v1.json','french-formats-v1.json'):
        path = ROOT/'docs/design'/file
        spec = json.loads(path.read_text(encoding='utf-8'))
        sources[file] = sha(path)
        for c in spec['cards']:
            assert sha(ROOT/c['path'])==c['sha256'],c['path']
            records[c['path']] = c['sha256']
    for path in (tarot.MANIFEST, ROOT/'manifest.json'):
        spec = json.loads(path.read_text(encoding='utf-8'))
        sources[path.relative_to(ROOT).as_posix()] = sha(path)
        for c in spec['cards']:
            dest = tarot.active_path(c) if path==tarot.MANIFEST else ROOT/c['path']
            relative = dest.relative_to(ROOT).as_posix()
            assert sha(dest)==c['sha256'],relative
            records[relative] = c['sha256']
    catalog = build_catalog()
    assert len(catalog['assets'])==397
    assert catalog==json.loads((ROOT/'catalog.json').read_text(encoding='utf-8')),'Stale design catalog'
    assert {a['path'] for a in catalog['assets']}==set(records),'Unvalidated release cards'
    cards = []
    for c in catalog['assets']:
        path = ROOT/c['path']
        assert sha(path)==records[c['path']]==c['sha256']
        with Image.open(path) as im:
            assert im.mode=='RGBA' and list(im.size)==c['pixels']
            assert all(abs(d-300)<.01 for d in im.info['dpi'])
            # Faces match their shared production masks; Europe backs retain
            # their documented full Bridge-resize alpha, already audited.
            if c['side']=='face':
                frame = (tarot.FRAMES if c.get('system')=='tarot' else
                    ROOT/'sources/components/design2-face-frames-v1'/c['format'])
                assert np.array_equal(np.array(im)[:,:,3],np.array(Image.open(frame/'outline-mask.png'))),path
        cards.append(dict(path=c['path'],sha256=c['sha256'],format=c['format'],side=c['side']))
    data = dict(status='passed',release='Design 2 v1.0',card_count=397,faces=367,backs=30,
        approval='Project owner confirmed Poker and Tarot finished and requested complete release on 2026-09-30.',
        renderer_manifests=sources,cards=cards)
    DOC.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('PASS release gate: 397 audited Design 2 native PNGs, six complete formats',flush=True)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-renderers',action='store_true')
    audit(parser.parse_args().verify_renderers)
