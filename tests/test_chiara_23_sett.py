import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GROUP = "23 sett · Chiara · Nuovo Espresso 1"
EXPECTED_FRONTS = [
    "italiana / italiano", "irlandese", "austriaco", "australiana",
    "di Verona", "di Dublino", "di Genova", "di Melbourne",
    "la Germania → tedesco / tedesca", "l’Italia → italiano / italiana",
    "la Francia → francese", "la Spagna → spagnolo / spagnola",
    "il Portogallo → portoghese", "la Svizzera → svizzero / svizzera",
    "l’Irlanda → irlandese", "l’Inghilterra → inglese",
    "Ciao", "Buongiorno", "Buonasera", "Salve", "Arrivederci",
    "A domani", "Buona notte", "Piacere",
    "Come ti chiami?", "Mi chiamo…", "Lei", "tu",
    "Che cosa studi?", "Lavoro part time.", "baby sitter", "Abito in centro.",
    "Buongiorno, desidera?",
    "caffè", "medico", "chitarra", "giornale", "zucchero",
    "spaghetti", "gatto", "cinema",
    "Io sono italiana.", "Tu sei irlandese.", "Lei è australiana.",
]


class Chiara23SettTests(unittest.TestCase):
    def test_cards_and_filter(self):
        html = (ROOT / "index.html").read_text()
        cards, _ = json.JSONDecoder().raw_decode(html.split("const ALL=", 1)[1])
        target = [card for card in cards if card["group"] == GROUP]
        self.assertEqual(len(cards), 1010)
        self.assertEqual([card["it"] for card in target], EXPECTED_FRONTS)
        self.assertTrue(all(card["lang"] == "EN" for card in target))
        self.assertTrue(all("Chiara" in card["note"] and "Liam" not in card["note"] and "Lisa" not in card["note"] for card in target))
        self.assertFalse(any(re.search(r"[А-Яа-яЁё]", json.dumps(card, ensure_ascii=False)) for card in target))
        self.assertIn("['chiara-23-sett','23 sett · Chiara · Nuovo Espresso 1']", html)
        self.assertIn("'chiara-23-sett':'23 sett · Chiara · Nuovo Espresso 1'", html)
        self.assertIn("const isChiara23=c.group==='23 sett · Chiara · Nuovo Espresso 1';", html)
        self.assertIn("$('direction').disabled=isLisa||isChiara23||isGrammar;", html)

    def test_version_and_copies(self):
        html = (ROOT / "index.html").read_bytes()
        self.assertIn(b'<meta name="build-version" content="v28">', html)
        self.assertNotIn(b"v24", html)
        self.assertEqual(html, (ROOT / "www/index.html").read_bytes())
        self.assertEqual(html, (ROOT / "anki-html/italiano-flashcards.html").read_bytes())
        self.assertEqual(html, Path("/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html/italiano-flashcards.html").read_bytes())
        self.assertEqual(html, Path("/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html/www/index.html").read_bytes())


if __name__ == "__main__":
    unittest.main()
