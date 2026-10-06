"""The third frequency deck adds exactly 100 unused lemmas, no extra top-level tab."""
import hashlib,json,re,unittest,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def tokens(s):return set(re.findall(r'[a-zà-öø-ÿ]+',unicodedata.normalize('NFKC',s).casefold()))
class Parole3Tests(unittest.TestCase):
 def test_no_duplicate_hub_entry_point(self):
  h=(ROOT/'index.html').read_text()
  self.assertEqual(re.findall(r'data-app="([^"]+)">',h),['carte','articoli','aggettivi','verbi'])
  self.assertNotIn('panel-parole-2',h);self.assertNotIn('frame-parole-2',h)
 def test_known_feminine_adjective_alias_is_not_reimported(self):
  # Existing frozen card: "Perché è un’umana, è normale." Human is not new vocabulary.
  manifest=json.loads((ROOT/'scripts/100-parole-3.json').read_text())
  for lemma in ['umano','ricordare','esistere','formare','migliore']:
   self.assertNotIn(lemma, [w['lemma'] for w in manifest['words']])
 def test_exactly_100_unique_new_frequency_words(self):
  h=(ROOT/'italiano-flashcards.html').read_text();cards=json.JSONDecoder().raw_decode(h.split('const ALL=',1)[1])[0]
  new=[c for c in cards if c['group']=='100 parole 3'];self.assertEqual(len(new),100)
  self.assertEqual(len({c['it'] for c in new}),100)
  old=[c for c in cards if c['group']!='100 parole 3']
  used=set().union(*(tokens(c['it']+' '+c['other']) for c in old))
  for file in ['articoli-esercizi.html','articoli-aggettivi.html','verbi-tempi.html']:
   page=(ROOT/file).read_text()
   for name in ['NOUNS','VERBS']:
    if 'const '+name+'=' in page:
     x=json.JSONDecoder().raw_decode(page.split('const '+name+'=',1)[1])[0]
     used.update(tokens(json.dumps(x,ensure_ascii=False)))
  manifest=json.loads((ROOT/'scripts/100-parole-3.json').read_text())
  self.assertEqual(len(manifest['words']),100)
  self.assertEqual([(c['it'],c['other']) for c in new],[(w['front'],w['english']) for w in manifest['words']])
  self.assertEqual(manifest['frequencySourceSha256'],'da5173ee23a9545fd80f88adc7a3d2f2bdc2e07a4fbd199eeefba2fc48748540')
  ranks=[w['rank'] for w in manifest['words']];self.assertEqual(ranks,sorted(ranks));self.assertGreater(min(ranks),268)
  families={t[:-1] if len(t)>=4 and t[-1] in 'aoie' else t for t in used}
  for c,w in zip(new,manifest['words']):
   stem=w['lemma'][:-1] if len(w['lemma'])>=4 and w['lemma'][-1] in 'aoie' else w['lemma']
   self.assertNotIn(stem,families,w['lemma'])
   self.assertNotIn(w['lemma'],used,w['lemma']);self.assertEqual(c['lang'],'EN');self.assertNotIn('direction',c)
   self.assertTrue(c['other']);self.assertNotRegex(json.dumps(c,ensure_ascii=False),'[\u0400-\u04ff]')
  self.assertEqual(len([c for c in old if c['group']=='100 parole']),100)
  self.assertEqual(len([c for c in old if c['group']=='100 parole 2']),100)
if __name__=='__main__':unittest.main()
