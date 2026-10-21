"""Package integrity only; these checks do not evaluate agent/model behavior."""
import ast
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

SKILL = Path(__file__).resolve().parents[2]
REPO = SKILL.parent


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


class PackageTests(unittest.TestCase):
    def test_metadata_and_name(self):
        text = (SKILL / 'SKILL.md').read_text()
        front = re.match(r'---\n(.*?)\n---\n', text, re.S).group(1)
        name = re.search(r'^name: (.+)$', front, re.M).group(1)
        description = front.split('description: |\n', 1)[1]
        description = '\n'.join(line[2:] for line in description.splitlines())
        self.assertEqual(name, SKILL.name)
        self.assertRegex(name, r'^clickzetta-[a-z0-9-]+$')
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(description), 1024)
        self.assertIn('\n\nKeywords: ', description)
        self.assertIn('\n\nTrigger when ', description)

    def test_relative_markdown_links_resolve_inside_package(self):
        for path in [SKILL / 'SKILL.md', *sorted((SKILL / 'references').glob('*.md'))]:
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if '://' in link or link.startswith('#'):
                    continue
                target = (path.parent / unquote(link.split('#', 1)[0])).resolve()
                with self.subTest(file=path.name, link=link):
                    self.assertTrue(target.is_relative_to(SKILL.resolve()))
                    self.assertTrue(target.is_file(), str(target))

    def test_python_examples_parse(self):
        for path in (SKILL / 'references').glob('*.md'):
            for example in re.findall(r'```python\n(.*?)\n```', path.read_text(), re.S):
                with self.subTest(file=path.name):
                    ast.parse(example)

    def test_registry_ships_entire_package(self):
        index = json.loads((REPO / '.well-known/skills/index.json').read_text())
        entries = [s for s in index['skills'] if s['name'] == SKILL.name]
        self.assertEqual(len(entries), 1)
        files = entries[0]['files']
        self.assertEqual(len(files), len(set(files)))
        actual = {str(p.relative_to(SKILL)) for p in SKILL.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
        self.assertEqual(set(files), actual)
        self.assertTrue(all((SKILL / p).is_file() for p in files))

    def test_catalog_and_routing(self):
        text = (REPO / 'README.md').read_text()
        self.assertIn(f'[{SKILL.name}](./{SKILL.name}/)', text)
        self.assertIn(f'`{SKILL.name}`', text.split('## Routing Guide', 1)[1])

    def test_corpus_ids_evidence_and_fixture_rules(self):
        cases = json.loads((SKILL / 'scripts/evals/cases.json').read_text())
        expected = json.loads((SKILL / 'scripts/evals/expected.json').read_text())
        self.assertEqual(cases['version'], expected['version'])
        ids = [c['id'] for c in cases['cases']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {c['id'] for c in expected['expected']})
        self.assertEqual(sum(c['kind'] == 'sql' for c in cases['cases']), 18)
        self.assertEqual(sum(c['kind'] == 'workflow' for c in cases['cases']), 15)
        cases_by_id = {c['id']: c for c in cases['cases']}
        impacts = {'execution_failure', 'silent_result_change', 'unaffected', 'insufficient_evidence'}
        for e in expected['expected']:
            with self.subTest(case=e['id']):
                case = cases_by_id[e['id']]
                if 'impact' in e:
                    self.assertIn(e['impact'], impacts)
                for fragment in e.get('evidence', []):
                    self.assertTrue(any(fragment in text for text in strings(case['state'])), fragment)
                for rule in case['state'].get('engine_rules', []):
                    self.assertIs(rule['fixture_only'], True)
                    self.assertTrue(rule['rule'].startswith('Fixture only:'))


if __name__ == '__main__':
    unittest.main()
