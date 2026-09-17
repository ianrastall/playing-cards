"""Measure actual exported pip centers, including the Bridge-derived format."""
import argparse
import numpy as np
from PIL import Image
import expand_faces as faces


def audit(root):
    records=[]
    manifest=faces.base.load_manifest()
    for fmt in faces.FORMATS:
        size=np.array(faces.size_for(fmt))
        for suit in faces.base.SUITS:
            for rank,spec in manifest['ranks'].items():
                path=root/faces.relative(fmt,suit,rank)
                im=Image.open(path)
                for pip in spec['pips']:
                    if fmt=='european-standard':
                        bridge=np.array(faces.size_for('bridge'))
                        point=(np.array(faces.native_point(pip['center'],bridge))+.5)*size/bridge-.5
                        tolerance=.5
                    else:
                        point=np.array(faces.native_point(pip['center'],size))
                        tolerance=.000001
                    x,y=point
                    radius=max(20,round(min(size)/30))
                    box=(int(x)-radius,int(y)-radius,int(x)+radius+2,int(y)+radius+2)
                    local,_=faces.base.turquoise(im.crop(box))
                    measured=np.array(local)+box[:2]
                    error=float(np.max(np.abs(measured-point)))
                    assert error<=tolerance,(path,pip,measured,point,error)
                    records.append(dict(format=fmt,suit=suit,rank=rank,pip=pip['id'],
                                        expected=point.tolist(),measured=measured.tolist(),error_px=error))
    result=dict(pip_centers_checked=len(records),max_error_native_px=max(r['error_px'] for r in records if r['format']!='european-standard'),
                max_error_european_px=max(r['error_px'] for r in records if r['format']=='european-standard'),
                european_tolerance_px=.5,records=records)
    faces.base.write_json(faces.ROOT/'docs/design/pip-alignment-audit-v2.json',result)
    print({k:v for k,v in result.items() if k!='records'},flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged',action='store_true')
    args=parser.parse_args()
    audit(faces.WORK/'cards' if args.staged else faces.ROOT/'cards')
