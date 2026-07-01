#!/usr/bin/env python3
"""Regenerate .well-known/skills/index.json from main branch skill directories."""

import json, os, re

def extract_description(content):
    """Extract the first sentence of the frontmatter `description` as a summary.

    Handles block scalars (| and >), plain, and quoted styles. Collapses the
    summary paragraph to one line, then keeps only the first sentence (up to the
    first sentence-ending punctuation) so the value stays a complete sentence
    within Anthropic's ~250-byte guideline instead of dumping the whole
    multi-line trigger/keywords block.
    """
    fm = re.match(r'---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm:
        return ''

    def join_lines(parts):
        # Join wrapped lines with a space, but not after a trailing '/' so
        # slash-separated enumerations like "real-time sync/multi-table" stay intact.
        out = ''
        for p in parts:
            if out and not out.endswith('/'):
                out += ' '
            out += p
        return out

    block = fm.group(1)
    m = re.search(r'^description:[ \t]*(.*)$', block, re.MULTILINE)
    if not m:
        return ''
    inline = m.group(1).strip()
    lines = block[m.end():].lstrip('\n').split('\n')

    if inline and inline[0] not in '|>':
        # Plain or quoted single-line start; may continue onto indented lines.
        parts = [inline]
        for ln in lines:
            if re.match(r'^\w[\w-]*:', ln) or ln.strip() == '':
                break
            parts.append(ln.strip())
        text = join_lines(parts)
    else:
        # Block scalar (| or >): collect indented lines until first blank line.
        parts = []
        for ln in lines:
            if ln.strip() == '' or re.match(r'^\w[\w-]*:', ln):
                break
            parts.append(ln.strip())
        text = join_lines(parts)

    text = text.strip().strip('"').strip("'").strip()
    text = re.sub(r'\s+', ' ', text)
    # Keep only the first sentence to stay concise (Anthropic suggests ~250 bytes).
    sentence = re.match(r'.*?[.。!?！？]', text)
    return sentence.group(0).strip() if sentence else text



root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

skills = []
for d in sorted(os.listdir('.')):
    if not d.startswith('clickzetta-') and not d.startswith('cz-') or not os.path.isdir(d):
        continue
    skill_md = os.path.join(d, 'SKILL.md')
    if not os.path.exists(skill_md):
        continue
    content = open(skill_md).read()
    desc = extract_description(content)
    # Collect files
    files = ['SKILL.md']
    refs_dir = os.path.join(d, 'references')
    if os.path.isdir(refs_dir):
        for f in sorted(os.listdir(refs_dir)):
            if f.endswith('.md'):
                files.append(f'references/{f}')
    skills.append({'name': d, 'description': desc, 'files': files})

os.makedirs('.well-known/skills', exist_ok=True)
with open('.well-known/skills/index.json', 'w') as f:
    json.dump({'skills': skills}, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'✓ Generated .well-known/skills/index.json ({len(skills)} skills)')
