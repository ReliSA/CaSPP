from utils.constants import LoaderConstants
from utils.parsers.template_parser import ContentRules, DocumentRules, HeadingRules, TemplateRules

FACETS_INDEX_TEMPLATE_NAME = "template-facets-index"
PUBLICATIONS_INDEX_TEMPLATE_NAME = "template-publications-index"

_BREADCRUMBS = ["*home*", "*catalogue*", "*facets*", "*name*"]


def make_facets_index_rules() -> TemplateRules:
    """In-memory template for facets folder-index files (stem == parent folder).

    Accepts: breadcrumbs, variable H1, any content (flat or nested bullet list).
    """
    rules = TemplateRules()
    rules.name = FACETS_INDEX_TEMPLATE_NAME
    rules.document_rules = DocumentRules(breadcrumbs=_BREADCRUMBS, h1_prefix=None)
    rules.headings = [
        HeadingRules(
            level=1,
            text="*Title*",
            is_variable=True,
            content_rules=ContentRules(expected_types={"text"}),
        )
    ]
    return rules


def make_publications_index_rules() -> TemplateRules:
    """In-memory template for publications/publications.md.

    Accepts: breadcrumbs, variable H1, text, A-Z grouped H2 sections with links.
    group_members=[] means no specific letters are required.
    """
    rules = TemplateRules()
    rules.name = PUBLICATIONS_INDEX_TEMPLATE_NAME
    rules.document_rules = DocumentRules(breadcrumbs=_BREADCRUMBS, h1_prefix=None)
    rules.headings = [
        HeadingRules(
            level=1,
            text="*Title*",
            is_variable=True,
            content_rules=ContentRules(expected_types={"text"}),
        ),
        HeadingRules(
            level=2,
            text="[A-Z]",
            is_group=True,
            optional=True,
            group_members=[],
            content_rules=ContentRules(expected_types={"text"}),
        ),
    ]
    return rules