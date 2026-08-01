#!/usr/bin/env python3
"""Auto validation checks for the git-based PKM vault (AGENTS.md section 2)."""
import os
import re
import sys
from datetime import date

SECTIONS = {
    'Knowledge': 'knowledge.md',
    'Research': 'research.md',
    'Projects': 'projects.md',
    'Ideas': 'ideas.md',
}

STATUSES = {
    'knowledge': ['fleeting', 'literature', 'permanent'],
    'research': ['active', 'on-hold', 'completed'],
    'projects': ['planning', 'active', 'done', 'archived'],
    'ideas': ['seed', 'sprouting', 'evergreen'],
}

STRING_FIELDS = ['title', 'date', 'author', 'last_audited', 'status']
LIST_FIELDS = ['tags', 'aliases', 'sources', 'references']
EXTRA_TYPES = {
    'research': {'lead': 'str', 'findings': 'str'},
    'projects': {'deadline': 'str', 'priority': 'str', 'lead': 'str', 'milestones': 'list'},
    'ideas': {'mood': 'str', 'related': 'list'},
}

FM_LINE_RE = re.compile(r'^([A-Za-z0-9_]+)\s*:\s*(.*)$')
WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
CHANGELOG_BULLET_RE = re.compile(r'^-\s*(\d{4})-(\d{2})-(\d{2}):')


def split_list_items(text):
    items = []
    buf = ''
    quoted = False
    for ch in text:
        if ch == '"':
            quoted = not quoted
            buf += ch
        elif ch == ',' and not quoted:
            items.append(buf)
            buf = ''
        else:
            buf += ch
    items.append(buf)
    return [item.strip().strip('"') for item in items]


def parse_value(value):
    value = value.strip()
    if value == '':
        raise ValueError('missing value after colon')
    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise ValueError('unterminated quoted value: %r' % value)
        return value[1:-1]
    if value.startswith('['):
        if not value.endswith(']'):
            raise ValueError('unterminated list value: %r' % value)
        inner = value[1:-1].strip()
        if inner == '':
            return []
        return split_list_items(inner)
    return value


def parse_frontmatter(text):
    """Return (frontmatter dict or None, closing fence line index or None)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return None, None
    data = {}
    for i in range(1, end):
        line = lines[i]
        if not line.strip():
            continue
        m = FM_LINE_RE.match(line)
        if not m:
            raise ValueError('malformed frontmatter line %d: %r' % (i + 1, line))
        data[m.group(1)] = parse_value(m.group(2))
    return data, end


def extract_body(text, end):
    if end is None:
        return text
    return '\n'.join(text.splitlines()[end + 1:])


def derive_section(path):
    p = path.replace(os.sep, '/')
    best = None
    last = -1
    for sec in SECTIONS:
        marker = '/' + sec + '/'
        idx = p.rfind(marker)
        if idx > last:
            last = idx
            best = sec
    return best


def field_types(section):
    types = dict.fromkeys(STRING_FIELDS, 'str')
    types.update(dict.fromkeys(LIST_FIELDS, 'list'))
    types.update(EXTRA_TYPES.get(section.lower(), {}))
    return types


def check_discoverable(doc_path, section):
    if not os.path.isfile(doc_path):
        return False, 'file does not exist'
    p = doc_path.replace(os.sep, '/')
    marker = '/' + section + '/'
    idx = p.rfind(marker)
    if idx == -1:
        return False, 'path does not contain the %s section folder' % section
    tail = p[idx + len(marker):]
    parts = tail.split('/')
    if len(parts) != 2 or not parts[0] or not parts[1].endswith('.md'):
        return False, 'expected %s/<Area>/<topic>.md, got %r' % (section, tail)
    return True, None


def check_atomic(body, doc_path):
    h1s = [line[2:].strip() for line in body.splitlines() if line.startswith('# ')]
    if len(h1s) != 1:
        return False, 'expected exactly one H1 heading, found %d' % len(h1s)
    stem = os.path.splitext(os.path.basename(doc_path))[0]
    normalize = lambda s: re.sub(r'[\s-]+', '', s.lower())
    if normalize(h1s[0]) != normalize(stem):
        return False, 'H1 %r does not match filename stem %r' % (h1s[0], stem)
    return True, None


def check_audited(body):
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == '## Changelog':
            start = i
            break
    if start is None:
        return False, 'missing ## Changelog section'
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        m = CHANGELOG_BULLET_RE.match(line.strip())
        if m:
            try:
                date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                continue
            return True, None
    return False, 'Changelog contains no bullet with a valid YYYY-MM-DD date'


def check_yaml(text, data, end, error):
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return False, 'frontmatter fence missing at start of document'
    if end is None:
        return False, 'frontmatter not closed with a --- fence'
    if error:
        return False, error
    return True, None


def check_template_compliance(data, template_data):
    if data is None:
        return False, 'no frontmatter to compare'
    missing = sorted(set(template_data) - set(data))
    extra = sorted(set(data) - set(template_data))
    if missing or extra:
        msg = []
        if missing:
            msg.append('missing keys: ' + ', '.join(missing))
        if extra:
            msg.append('extra keys: ' + ', '.join(extra))
        return False, '; '.join(msg)
    return True, None


def body_headings(body):
    return [line[3:].strip() for line in body.splitlines() if line.startswith('## ')]


def check_required_headings(body, template_body):
    missing = [h for h in body_headings(template_body) if not has_heading(body, h)]
    if missing:
        return False, 'missing headings: ' + ', '.join(missing)
    return True, None


def has_heading(body, heading):
    for line in body.splitlines():
        if line.strip() == '## ' + heading:
            return True
    return False


def check_metadata(data, section):
    if data is None:
        return False, 'no frontmatter present'
    problems = []
    types = field_types(section)
    for key, expected in types.items():
        if key not in data:
            continue
        value = data[key]
        if expected == 'str':
            if not isinstance(value, str):
                problems.append('%s must be a string' % key)
        elif not isinstance(value, list):
            problems.append('%s must be a list' % key)
    title = data.get('title')
    if not isinstance(title, str) or title.strip() == '':
        problems.append('title must be a non-empty string')
    if problems:
        return False, '; '.join(problems)
    return True, None


def resolve_wikilink(target, vault_root):
    if '/' in target:
        return os.path.isfile(os.path.join(vault_root, target + '.md'))
    for sec in SECTIONS:
        base = os.path.join(vault_root, sec)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            if target + '.md' in files:
                return True
    return False


def check_references(body, data, vault_root):
    problems = []
    if data is None:
        problems.append('no frontmatter to validate sources')
    else:
        sources = data.get('sources', [])
        if not isinstance(sources, list):
            problems.append('sources must be a list')
        else:
            for i, s in enumerate(sources):
                if not isinstance(s, str) or s.strip() == '':
                    problems.append('source %d is empty' % (i + 1))
    for m in WIKILINK_RE.finditer(body):
        target = m.group(1).strip()
        if '|' in target:
            target = target.split('|', 1)[0].strip()
        if '#' in target:
            target = target.split('#', 1)[0].strip()
        if target and not resolve_wikilink(target, vault_root):
            problems.append('unresolved wikilink [[%s]]' % target)
    if problems:
        return False, '; '.join(problems)
    return True, None


def check_status(data, section):
    if data is None:
        return False, 'no frontmatter present'
    status = data.get('status')
    allowed = STATUSES[section.lower()]
    if status not in allowed:
        return False, 'status %r not in %s' % (status, ' | '.join(allowed))
    return True, None


def print_report(results):
    ok = True
    for name, (passed, note) in results:
        if passed:
            print('[PASS] %s' % name)
        else:
            print('[FAIL] %s: %s' % (name, note))
            ok = False
    print('OVERALL: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(argv):
    args = argv[1:]
    template_override = None
    if args and args[0] == '--template':
        if len(args) != 3:
            print('usage: validator.py [--template <path>] <document.md>', file=sys.stderr)
            return 1
        template_override = args[1]
        doc_arg = args[2]
    else:
        if len(args) != 1:
            print('usage: validator.py [--template <path>] <document.md>', file=sys.stderr)
            return 1
        doc_arg = args[0]

    vault_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_path = os.path.abspath(doc_arg)
    if not os.path.isfile(doc_path):
        print('ERROR: document not found: %s' % doc_arg, file=sys.stderr)
        return 1

    section = derive_section(doc_path)
    if section is None:
        print('ERROR: path does not belong to a known section '
              '(Knowledge/Research/Projects/Ideas): %s' % doc_arg, file=sys.stderr)
        return 1

    template_path = template_override or os.path.join(vault_root, 'Templates', SECTIONS[section])
    if not os.path.isfile(template_path):
        print('ERROR: template not found: %s' % template_path, file=sys.stderr)
        return 1

    with open(doc_path, encoding='utf-8') as f:
        text = f.read()
    with open(template_path, encoding='utf-8') as f:
        template_text = f.read()

    fm_error = None
    try:
        doc_data, doc_end = parse_frontmatter(text)
    except ValueError as e:
        doc_data, doc_end = None, None
        fm_error = str(e)
    try:
        template_data, template_end = parse_frontmatter(template_text)
    except ValueError:
        template_data, template_end = {}, None

    body = extract_body(text, doc_end)
    template_body = extract_body(template_text, template_end)

    results = [
        ('DISCOVERABLE', check_discoverable(doc_path, section)),
        ('ATOMIC', check_atomic(body, doc_path)),
        ('AUDITED', check_audited(body)),
        ('YAML FRONTMATTER', check_yaml(text, doc_data, doc_end, fm_error)),
        ('TEMPLATE COMPLIANCE', check_template_compliance(doc_data, template_data)),
        ('REQUIRED HEADINGS', check_required_headings(body, template_body)),
        ('REQUIRED METADATA', check_metadata(doc_data, section)),
        ('REFERENCES', check_references(body, doc_data, vault_root)),
        ('VALID STATUS', check_status(doc_data, section)),
    ]
    return 0 if print_report(results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
