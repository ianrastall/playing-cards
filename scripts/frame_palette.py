"""Explicit pigment treatment of the shared frame's dark ground."""
import numpy as np
from PIL import Image

from recolor_card_backs import recolor

# Dark digital grounds, not measured historical ink specifications.
GROUNDS = {
    'lamp-black': (5, 5, 5),
    'madder-lake': (78, 9, 23),
    'manganese-violet': (43, 16, 58),
    'prussian-blue': (7, 29, 46),
    'verdigris': (8, 53, 49),
}


def face_color(suit, rank):
    return 'madder-lake' if suit in ('hearts','diamonds') or (suit=='jokers' and rank=='red') else 'lamp-black'


def color_frame(frame, color):
    """Color low-light neutral ground and source blue without moving artwork.

    Gold, ivory, red flowers, and chromatic green foliage are protected by the
    neutral-chroma weight. Alpha and geometry are unchanged.
    """
    if color not in GROUNDS:
        raise ValueError(f'Unknown frame palette: {color}')
    source=np.array(frame)
    rgb=source[:,:,:3].astype(float)
    hi=rgb.max(axis=2)
    lo=rgb.min(axis=2)
    weight=np.clip((65-hi)/30,0,1)*np.clip((27-(hi-lo))/18,0,1)
    result=source.copy() if color=='prussian-blue' else recolor(source,color)[0]
    mapped=np.clip(rgb+np.array(GROUNDS[color])-5,0,255)
    result[:,:,:3]=np.rint(result[:,:,:3]*(1-weight[:,:,None])+mapped*weight[:,:,None]).astype(np.uint8)
    return Image.fromarray(result)
