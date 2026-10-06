"""Lettura was explicitly removed in v35, including every deployed copy."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
class LetturaRemovalTests(unittest.TestCase):
 def test_no_visible_or_embedded_section(self):
  for name in ['index.html','italiano-flashcards.html']:
   self.assertFalse(re.search('lettura', (ROOT/name).read_text(),re.I),name)
  cards=json.JSONDecoder().raw_decode((ROOT/'italiano-flashcards.html').read_text().split('const ALL=',1)[1])[0]
  self.assertFalse(any(c.get('reading') or c['group']=='Liam · Lettura' for c in cards))
 def test_no_standalone_reading_page(self):
  for base in [ROOT,ROOT/'www',ROOT/'anki-html',CANON,CANON/'www']:
   for name in ['liam-lettura.html','liam-lettura.json']:self.assertFalse((base/name).exists(),str(base/name))
if __name__=='__main__':unittest.main()
