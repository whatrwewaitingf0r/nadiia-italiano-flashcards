"""The article-kind prompt belongs beside the answer, not in the card header."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.nodes = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        node = {'tag': tag, 'attrs': attrs, 'parent': self.stack[-1] if self.stack else None, 'children': []}
        if self.stack:
            self.stack[-1]['children'].append(node)
        if 'id' in attrs:
            self.nodes[attrs['id']] = node
        if tag not in {'meta', 'link', 'input', 'br', 'hr', 'img'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                return

class ArticleLabelTests(unittest.TestCase):
    def test_category_is_immediately_above_answer_label(self):
        dom = Elements((ROOT / 'articoli-aggettivi.html').read_text()).nodes
        category = dom['category']
        self.assertIs(category['parent'], dom['answer-form'], 'Article kind must stay with the answer field')
        children = dom['answer-form']['children']
        self.assertIs(children[0], category)
        self.assertEqual(children[1]['attrs'].get('for'), 'answer')
        self.assertIs(dom['answer']['parent'], children[2])
        self.assertIs(dom['lemma']['parent'], dom['phrase']['parent'])
        self.assertIs(dom['position']['parent']['parent'], dom['lemma']['parent']['parent'])

if __name__ == '__main__':
    unittest.main()
