"""Preserve one built-in ImageGen cultural revision and record its provenance."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'sources/generated/minchiate-poker-v1'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identifier')
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    path = RAW/'chinese-v2-prompts.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    job = next(j for j in data['jobs'] if j['id'] == args.identifier)
    if job.get('status') == 'selected':
        parser.error('This revision is already selected; record further edits separately.')
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    with Image.open(args.source) as im:
        assert im.mode == 'RGBA' and im.getchannel('A').getextrema() == (0, 255)
        pixels = list(im.size)
    destination = RAW/(args.identifier+'-chinese-v2.png')
    if destination.exists():
        assert hashlib.sha256(destination.read_bytes()).hexdigest() == digest
    else:
        shutil.copy2(args.source, destination)
    job.update(status='generated', output=dict(path=destination.name, pixels=pixels,
               mode='RGBA', sha256=digest), generation_file=args.source.name)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print('Preserved', destination.name, pixels)

if __name__ == '__main__':
    main()
