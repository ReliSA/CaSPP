"""Shared Markdown parsing primitives.

Both template_loader and document_loader import from here so that
every regex and classification rule lives in exactly one place.
"""

import re
from dataclasses import dataclass
from typing import Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Compiled regexes
# ---------------------------------------------------------------------------

# Heading line:  ### Some text
RE_HEADING = re.compile(r'^(#{1,6})\s+(.+)$')

# Markdown link anywhere in a string:  [label](url)
RE_LINK = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')

# Italic placeholder wrapping the *whole* remaining text, or inline:  *Name*
RE_ITALIC = re.compile(r'\*([^*]+)\*')

# Optional marker in template headings:  *(optional)* or (optional)
RE_OPTIONAL = re.compile(r'\s*\*?\(optional\)\*?', re.IGNORECASE)

# H1 prefix before a colon:  "Category: …" or "Project Methodology: …"
RE_H1_PREFIX = re.compile(r'^([A-Za-z][A-Za-z ]+?):\s*(.*)$')

# Table separator row:  |---|---|
RE_TABLE_SEP = re.compile(r'^\|[-:\s|]+\|$')

# Bullet / unordered list item:  - … or * …
RE_BULLET = re.compile(r'^[-*]\s+')

# Parenthesised bullet prefix:  - (+) …  or  - (-) …
RE_BULLET_PREFIX = re.compile(r'^[-*]\s+(\([^)]+\))')

# Exact link-style list prefix:  - [Label](url): …
RE_EXACT_LIST_PREFIX = re.compile(r'^[-*]\s+(\[[^\]]+\]\([^)]+\):)')

# Horizontal rule:  ---  ___  ***  (optionally wrapped in asterisks in templates)
RE_HR_TEMPLATE = re.compile(r'^\*?(---|___|\*\*\*)\*?$')
RE_HR_DOCUMENT = re.compile(r'^(---|___|\*\*\*)$')

# Footnote definition:  [^1]: …  (optionally wrapped in asterisks in templates)
RE_FOOTNOTE_TEMPLATE = re.compile(r'^\*?\[\^[^\]]+\]:')
RE_FOOTNOTE_DOCUMENT = re.compile(r'^\[\^[^\]]+\]:')

# Image:  ![alt](url)
RE_IMAGE = re.compile(r'^!\[')

# Breadcrumb line guard — italic-only lines are template instructions, not breadcrumbs
RE_ITALIC_ONLY = re.compile(r'^\*[^*].*[^*]\*$|^\*[^*]\*$')

# Content-type string constants — single source of truth for the vocabulary
# used in both ContentRules.expected_types and ContentInfo.found_types.
CT_TEXT            = 'text'
CT_BULLET_LIST     = 'bullet_list'
CT_TABLE           = 'table'
CT_HORIZONTAL_RULE = 'horizontal_rule'
CT_FOOTNOTE        = 'footnote'
CT_LINKS           = 'links'
CT_IMAGE           = 'image'


@dataclass
class ParsedHeading:
    """Raw result of parsing a single heading line — shared by both loaders."""
    level: int
    text: str           # cleaned: links resolved to label, asterisks stripped
    raw_text: str       # original text after the hashes
    is_link: bool
    link_target: Optional[str]
    # Template-specific fields (None when parsing a real document)
    is_optional: bool = False
    is_variable: bool = False
    variable_part: Optional[str] = None


def parse_heading_line(hashes: str, raw_text: str, is_template: bool = False) -> ParsedHeading:
    """Parse the text part of a Markdown heading line.

    Args:
        hashes:      The # characters that opened the heading (e.g. '##').
        raw_text:    Everything after the hashes and the space.
        is_template: When True, also strip *(optional)* markers and detect
                     italic variable placeholders (*Name*).

    Returns:
        A :class:ParsedHeading with all fields populated.
    """
    level = len(hashes)
    text = raw_text.strip()

    # Template-only: optional marker
    is_optional = False
    if is_template:
        is_optional = bool(RE_OPTIONAL.search(text))
        if is_optional:
            text = RE_OPTIONAL.sub('', text).strip()

    # Link inside heading:  [label](url)
    link_target: Optional[str] = None
    link_match = RE_LINK.search(text)
    if link_match:
        link_target = link_match.group(2)
        text = RE_LINK.sub(r'\1', text).strip()

    # Template-only: italic variable placeholder
    is_variable = False
    variable_part: Optional[str] = None
    if is_template:
        italic_match = RE_ITALIC.search(text)
        if italic_match:
            is_variable = True
            variable_part = italic_match.group(1).strip()

    # Strip remaining asterisks (template placeholders or stray formatting)
    clean_text = RE_ITALIC.sub(r'\1', text).strip()

    return ParsedHeading(
        level=level,
        text=clean_text,
        raw_text=raw_text.strip(),
        is_link=link_target is not None,
        link_target=link_target,
        is_optional=is_optional,
        is_variable=is_variable,
        variable_part=variable_part,
    )


def split_h1(text: str) -> Tuple[Optional[str], str]:
    """Split an H1 text into (prefix, value).

    Examples::

        split_h1("Category: Name")       → ("Category", "Name")
        split_h1("Tracking progress")    → (None, "Tracking progress")

    Args:
        text: Cleaned H1 heading text (no asterisks, no link markup).

    Returns:
        A tuple of (prefix, value) where *prefix* is None for plain titles.
    """
    match = RE_H1_PREFIX.match(text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, text.strip()


def parse_breadcrumbs(line: str) -> Optional[list]:
    """Return breadcrumb parts if *line* looks like a breadcrumb trail, else None.

    Args:
        line: A stripped source line from the file preamble.

    Returns:
        List of breadcrumb part strings, or None if the line is not a breadcrumb.
    """
    min_len = 2
    if '>' not in line or '[' not in line:
        return None
    # Italic-only lines are template instructions ("*remove or replace…*"), not breadcrumbs.
    if line.startswith('*') and line.endswith('*'):
        return None
    parts = [p.strip() for p in line.split('>')]
    return parts if len(parts) >= min_len else None


def classify_content_line(
    line: str,
    is_template: bool = False,
) -> Tuple[Set[str], Optional[str], Optional[str], Optional[list]]:
    """Classify a single content line and extract relevant details.

    This function encodes every detection rule exactly once.  Both loaders
    call it and map the results onto their own data structures.

    Args:
        line:        A stripped, non-empty content line.
        is_template: When True, use the looser HR / footnote patterns that
                     allow surrounding asterisks (*---*, *[^1]:…*).

    Returns:
        A 4-tuple of:
        - content_types      – set of content-type strings to add
        - bullet_prefix      – parenthesised prefix string, e.g. '(+)', or None
        - exact_list_prefix  – link-style prefix string, or None
        - table_headers      – list of header strings if this is a table header row, else None
    """
    content_types: Set[str] = set()
    bullet_prefix: Optional[str] = None
    exact_list_prefix: Optional[str] = None
    table_headers: Optional[list] = None

    # Image (must precede generic link check)
    if RE_IMAGE.match(line):
        content_types.add(CT_IMAGE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Table row
    if line.startswith('|'):
        content_types.add(CT_TABLE)
        if not RE_TABLE_SEP.match(line):
            table_headers = [c.strip() for c in line.split('|') if c.strip()]
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Bullet / unordered list
    if RE_BULLET.match(line):
        content_types.add(CT_BULLET_LIST)
        m = RE_BULLET_PREFIX.match(line)
        if m:
            bullet_prefix = m.group(1)
        m = RE_EXACT_LIST_PREFIX.match(line)
        if m:
            exact_list_prefix = m.group(1)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Horizontal rule
    hr_re = RE_HR_TEMPLATE if is_template else RE_HR_DOCUMENT
    if hr_re.match(line):
        content_types.add(CT_HORIZONTAL_RULE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Footnote definition
    fn_re = RE_FOOTNOTE_TEMPLATE if is_template else RE_FOOTNOTE_DOCUMENT
    if fn_re.match(line):
        content_types.add(CT_FOOTNOTE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Inline link (fall-through to text)
    if RE_LINK.search(line):
        content_types.add(CT_LINKS)

    # Plain text
    content_types.add(CT_TEXT)
    return content_types, bullet_prefix, exact_list_prefix, table_headers