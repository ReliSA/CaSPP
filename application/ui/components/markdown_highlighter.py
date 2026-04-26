"""
Markdown syntax highlighter for QPlainTextEdit.
"""
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

from core.constants import SyntaxHighlighterConstants

class MarkdownHighlighter(QSyntaxHighlighter):
    """Applies markdown syntax highlighting to a QTextDocument."""

    def __init__(self, document=None):
        """Initializes the markdown syntax highlighter.

        Args:
            document: The QTextDocument to apply the highlighting to. Defaults to None.

        Returns:
            None.
        """
        super().__init__(document)
        self.highlighting_rules = []
        
        # Headings
        heading_format = QTextCharFormat()
        heading_format.setFontWeight(QFont.Weight.Bold)
        heading_format.setForeground(QColor(SyntaxHighlighterConstants.HEADINGS_COLOR)) 

        # Bold Text
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)

        # Italic Text
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)

        # Code blocks/inline code
        code_format = QTextCharFormat()
        code_format.setFontFamily("Consolas")
        code_format.setForeground(QColor(SyntaxHighlighterConstants.CODE_BLOCK_COLOR))

        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(SyntaxHighlighterConstants.LINK_COLOR))
        link_format.setFontUnderline(True)

        # Lists (- or * or 1.)
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(SyntaxHighlighterConstants.LIST_COLOR))
        list_format.setFontWeight(QFont.Weight.Bold)

        # Blockquotes
        blockquote_format = QTextCharFormat()
        blockquote_format.setForeground(QColor(SyntaxHighlighterConstants.BLOCKQUOTE_COLOR))
        blockquote_format.setFontItalic(True)

        # Horizontal Rules
        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor(SyntaxHighlighterConstants.HR_COLOR))

        # Strikethrough
        strikethrough_format = QTextCharFormat()
        strikethrough_format.setForeground(QColor(SyntaxHighlighterConstants.STRIKETHROUGH_COLOR))
        strikethrough_format.setFontStrikeOut(True)

        # Task Lists
        task_list_format = QTextCharFormat()
        task_list_format.setForeground(QColor(SyntaxHighlighterConstants.TASK_LIST_COLOR))
        task_list_format.setFontWeight(QFont.Weight.Bold)

        # HTML Tags
        html_tag_format = QTextCharFormat()
        html_tag_format.setForeground(QColor(SyntaxHighlighterConstants.HTML_TAG_COLOR))

        # Table Pipes
        table_pipe_format = QTextCharFormat()
        table_pipe_format.setForeground(QColor(SyntaxHighlighterConstants.TABLE_PIPE_COLOR))
        table_pipe_format.setFontWeight(QFont.Weight.Bold)

        # Regular Expressions from Constants to Formats
        
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HEADING), heading_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BOLD_AST), bold_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BOLD_UND), bold_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_ITALIC_AST), italic_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_ITALIC_UND), italic_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_CODE), code_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LINK), link_format))
        
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BLOCKQUOTE), blockquote_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HR), hr_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_STRIKETHROUGH), strikethrough_format))

        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LIST_UNORDERED), list_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LIST_ORDERED), list_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_TASK_LIST), task_list_format))

        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HTML_TAG), html_tag_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_TABLE_PIPE), table_pipe_format))

    def highlightBlock(self, text: str) -> None:
        """Applies syntax highlighting to a given block of text.
        
        This method is called automatically by PyQt's underlying text engine 
        whenever the text in the document changes.

        Args:
            text: The text block (usually a single line) to be highlighted.

        Returns:
            None.
        """
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)