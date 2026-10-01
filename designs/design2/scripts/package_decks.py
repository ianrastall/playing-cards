"""Build/check six Design 2 v1.0 packages using the audited common print workflow."""
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0,str(REPO/'designs/design1/scripts'))
import package_decks as shared

spec = importlib.util.spec_from_file_location('release_collection_catalog',REPO/'scripts/catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)
shared.ROOT = ROOT
shared.OUT = ROOT/'build/releases'
shared.RELEASE_VERSION = '1.0'
shared.DESIGN_ID = 'design2'
shared.DESIGN_NAME = 'Design 2'
shared.VALIDATION_REPORTS = ('docs/design/release-v1-audit.json',)
shared.EXTRA_FILES = {'licenses/LXGW-WenKai-TC-OFL.txt': ROOT/'sources/fonts/lxgw-wenkai-tc-v1.522/OFL.txt'}
shared.build_catalog = lambda: catalog.build_design_catalog(ROOT)
original_readme = shared.readme


def readme(fmt, geometry):
    content = original_readme(fmt,geometry).replace('Design 1','Design 2')
    content = content.replace('python scripts/package_decks.py', 'python designs/design2/scripts/package_decks.py')
    content = content.replace('Faces use paired side indices; court and trump art is upright.',
        'Tarot faces use paired index panels and paired traditional Chinese name panels; court and trump art is upright.')
    return content + '''
## Design 2 artwork and typography

French courts use the approved Ming-inspired silk-floral paintings. Bridge,
Travel and Jumbo are composed from saved portrait and pip components with their
own positions, shared frames and centered decorative stones. European Standard
derives from finished Bridge with its common frame and indices reapplied.
Poker and the separate 97-card Tarot deck retain their approved source pixels.
Even pip ranks, courts and Jokers are exact half-turns; odd pip ranks retain
one upright center pip, and aces retain upright suit shapes.

Tarot names use traditional Chinese. The current artwork and names were accepted
for this release by the project owner; release acceptance is not a claim of an
independent linguistic or historical review. The bundled font notice is in
`licenses/LXGW-WenKai-TC-OFL.txt`; font binaries are not included in this package.
'''


shared.readme = readme

if __name__ == '__main__':
    shared.main()
