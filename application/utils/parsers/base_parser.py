"""Shared Markdown parsing primitives.

Both template_loader and document_loader import from here so that
every regex and classification rule lives in exactly one place.
"""
from dataclasses import dataclass
from typing import Optional, Set, Tuple

from utils.constants import LoaderConstants


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
        hashes: The # characters that opened the heading (e.g. '##').
        raw_text: Everything after the hashes and the space.
        is_template: When True, also strip *(optional)* markers and detect italic variable placeholders (*Name*).

    Returns:
        A ParsedHeading with all fields populated.
    """
    level = len(hashes)
    text = raw_text.strip()

    # Template-only: optional marker
    is_optional = False
    if is_template:
        is_optional = bool(LoaderConstants.RE_OPTIONAL.search(text))
        if is_optional:
            text = LoaderConstants.RE_OPTIONAL.sub('', text).strip()

    # Link inside heading:  [label](url)
    link_target: Optional[str] = None
    link_match = LoaderConstants.RE_LINK.search(text)
    if link_match:
        link_target = link_match.group(2)
        text = LoaderConstants.RE_LINK.sub(r'\1', text).strip()

    # Template-only: italic variable placeholder
    is_variable = False
    variable_part: Optional[str] = None
    if is_template:
        italic_match = LoaderConstants.RE_ITALIC.search(text)
        if italic_match:
            is_variable = True
            variable_part = italic_match.group(1).strip()

    # Strip remaining asterisks (template placeholders or stray formatting)
    clean_text = LoaderConstants.RE_ITALIC.sub(r'\1', text).strip()

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

    Args:
        text: Cleaned H1 heading text (no asterisks, no link markup).

    Returns:
        A tuple of (prefix, value) where *prefix* is None for plain titles.
    """
    match = LoaderConstants.RE_H1_PREFIX.match(text)
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
    if '>' not in line or '[' not in line:
        return None
    # Italic-only lines are template instructions ("*remove or replace…*"), not breadcrumbs.
    if line.startswith('*') and line.endswith('*'):
        return None
    parts = [p.strip() for p in line.split('>')]
    return parts if len(parts) >= LoaderConstants.BREADCRUMBS_MIN_LENGTH else None


def classify_content_line(line: str, is_template: bool = False) -> Tuple[Set[str], Optional[str], Optional[str], Optional[list]]:
    """Classify a single content line and extract relevant details.

    Args:
        line: A stripped, non-empty content line.
        is_template: When True, use the looser HR / footnote patterns that allow surrounding asterisks (*---*, *[^1]:…*).

    Returns:
        A 4-tuple of: - content_types      – set of content-type strings to add - bullet_prefix      – parenthesised prefix string, e.g. '(+)', or None - exact_list_prefix  – link-style prefix string, or None - table_headers      – list of header strings if this is a table header row, else None.
    """
    content_types: Set[str] = set()
    bullet_prefix: Optional[str] = None
    exact_list_prefix: Optional[str] = None
    table_headers: Optional[list] = None

    # Image (must precede generic link check)
    if LoaderConstants.RE_IMAGE.match(line):
        content_types.add(LoaderConstants.CT_IMAGE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Table row
    if line.startswith('|'):
        content_types.add(LoaderConstants.CT_TABLE)
        if not LoaderConstants.RE_TABLE_SEP.match(line):
            table_headers = [c.strip() for c in line.split('|') if c.strip()]
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Bullet / unordered list
    if LoaderConstants.RE_BULLET.match(line):
        content_types.add(LoaderConstants.CT_BULLET_LIST)
        m = LoaderConstants.RE_BULLET_PREFIX.match(line)
        if m:
            bullet_prefix = m.group(1)
        m = LoaderConstants.RE_EXACT_LIST_PREFIX.match(line)
        if m:
            exact_list_prefix = m.group(1)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Horizontal rule
    hr_re = LoaderConstants.RE_HR_TEMPLATE if is_template else LoaderConstants.RE_HR_DOCUMENT
    if hr_re.match(line):
        content_types.add(LoaderConstants.CT_HORIZONTAL_RULE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Footnote definition
    fn_re = LoaderConstants.RE_FOOTNOTE_TEMPLATE if is_template else LoaderConstants.RE_FOOTNOTE_DOCUMENT
    if fn_re.match(line):
        content_types.add(LoaderConstants.CT_FOOTNOTE)
        return content_types, bullet_prefix, exact_list_prefix, table_headers

    # Inline link (fall-through to text)
    if LoaderConstants.RE_LINK.search(line):
        content_types.add(LoaderConstants.CT_LINKS)

    # Plain text
    content_types.add(LoaderConstants.CT_TEXT)
    return content_types, bullet_prefix, exact_list_prefix, table_headers