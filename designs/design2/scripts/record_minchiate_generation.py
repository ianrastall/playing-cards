"""Record a built-in ImageGen result without overwriting an existing master."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'sources/generated/minchiate-poker-v1'
p=argparse.ArgumentParser();p.add_argument('identifier');p.add_argument('source');args=p.parse_args()
manifest=RAW/'completion-prompts.json';data=json.loads(manifest.read_text(encoding='utf-8'))
job=next(j for j in data['jobs'] if j['id']==args.identifier)
source=Path(args.source);destination=RAW/(job['id']+'.png')
with Image.open(source) as im:
    assert im.mode=='RGBA', 'Need transparent RGBA component'
    assert np.count_nonzero(np.asarray(im)[:,:,3]==0)>100,'Missing transparent background'
    pixels=list(im.size);mode=im.mode
checksum=hashlib.sha256(source.read_bytes()).hexdigest()
if destination.exists(): assert hashlib.sha256(destination.read_bytes()).hexdigest()==checksum,'Refusing to overwrite master'
else: shutil.copy2(source,destination)
job.update(status='generated',output=dict(path=destination.name,pixels=pixels,mode=mode,sha256=checksum),generation_file=source.name)
manifest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Saved',destination.name,pixels,checksum[:12])
