"""Release integration checks for the three dictation forms."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = {'carte':'italiano-flashcards.html','articoli':'articoli-esercizi.html','aggettivi':'articoli-aggettivi.html','verbi':'verbi-tempi.html','coppie':'coppie.html'}

class DictationReleaseTests(unittest.TestCase):
    def test_runtime(self):
        subprocess.run(['node', str(ROOT/'tests/dictation-runtime.cjs')], check=True)

    def test_top_window_bridge(self):
        subprocess.run(['node', str(ROOT/'tests/dictation-bridge-runtime.cjs')], check=True)

    def test_release_and_embedded_apps(self):
        hub=(ROOT/'index.html').read_text()
        self.assertIn('content="v47"',hub)
        self.assertIn("frame.src=files[key]+'?v=47'",hub)
        for key,file in APPS.items():
            app=(ROOT/file).read_text()
            payload=re.search(r'<script type="application/json" id="app-'+key+r'">([\s\S]*?)</script>',hub)[1]
            self.assertEqual(json.loads(payload),app)
            for folder in ['www','anki-html']:
                self.assertEqual(app,(ROOT/folder/file).read_text())
            if key in ['articoli','aggettivi','verbi']:
                self.assertRegex(app,r'<button id="speak"[^>]*type="button"[^>]*>Parla</button>')
                self.assertIn('#speak{min-width:44px;min-height:44px',app)
                self.assertRegex(app,r'</button></div><p id="speech-status"[^>]*aria-live="polite"')
            else:
                self.assertNotIn('id="speak"',app)
        for folder in ['www','anki-html']:
            self.assertEqual(hub,(ROOT/folder/'index.html').read_text())

if __name__=='__main__': unittest.main()
