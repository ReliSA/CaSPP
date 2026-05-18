"""
Markdown syntax highlighter for QPlainTextEdit.
"""
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

from utils.constants import SyntaxHighlighterConstants, EditorConstants

class MarkdownHighlighter(QSyntaxHighlighter):
    """Applies markdown syntax highlighting to a QTextDocument."""

    def __init__(self, document=None):
        """Initializes the markdown syntax highlighter.

        Args:
            document: The QTextDocument to apply the highlighting to. Defaults to None.
        """
        super().__init__(document)
        self.highlighting_rules = []
        
        heading_format = QTextCharFormat()
        heading_format.setFontWeight(QFont.Weight.Bold)
        heading_format.setForeground(QColor(SyntaxHighlighterConstants.HEADINGS_COLOR)) 

        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)

        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)

        self.code_format = QTextCharFormat()
        self.code_format.setFontFamily(EditorConstants.FONT_FAMILY)
        self.code_format.setForeground(QColor(SyntaxHighlighterConstants.CODE_BLOCK_COLOR))

        link_format = QTextCharFormat()
        link_format.setForeground(QColor(SyntaxHighlighterConstants.LINK_COLOR))
        link_format.setFontUnderline(True)

        list_format = QTextCharFormat()
        list_format.setForeground(QColor(SyntaxHighlighterConstants.LIST_COLOR))
        list_format.setFontWeight(QFont.Weight.Bold)

        blockquote_format = QTextCharFormat()
        blockquote_format.setForeground(QColor(SyntaxHighlighterConstants.BLOCKQUOTE_COLOR))
        blockquote_format.setFontItalic(True)

        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor(SyntaxHighlighterConstants.HR_COLOR))

        strikethrough_format = QTextCharFormat()
        strikethrough_format.setForeground(QColor(SyntaxHighlighterConstants.STRIKETHROUGH_COLOR))
        strikethrough_format.setFontStrikeOut(True)

        task_list_format = QTextCharFormat()
        task_list_format.setForeground(QColor(SyntaxHighlighterConstants.TASK_LIST_COLOR))
        task_list_format.setFontWeight(QFont.Weight.Bold)

        html_tag_format = QTextCharFormat()
        html_tag_format.setForeground(QColor(SyntaxHighlighterConstants.HTML_TAG_COLOR))

        table_pipe_format = QTextCharFormat()
        table_pipe_format.setForeground(QColor(SyntaxHighlighterConstants.TABLE_PIPE_COLOR))
        table_pipe_format.setFontWeight(QFont.Weight.Bold)
        
        footnote_format = QTextCharFormat()
        footnote_format.setForeground(QColor(SyntaxHighlighterConstants.FOOTNOTE_COLOR))

        emoji_format = QTextCharFormat()
        emoji_format.setForeground(QColor(SyntaxHighlighterConstants.EMOJI_COLOR))

        highlight_mark_format = QTextCharFormat()
        highlight_mark_format.setBackground(QColor(SyntaxHighlighterConstants.HIGHLIGHT_BG_COLOR))
        highlight_mark_format.setForeground(QColor(SyntaxHighlighterConstants.HIGHLIGHT_FG_COLOR))

        subscript_format = QTextCharFormat()
        subscript_format.setForeground(QColor(SyntaxHighlighterConstants.SUB_SUPER_COLOR))
        subscript_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)

        superscript_format = QTextCharFormat()
        superscript_format.setForeground(QColor(SyntaxHighlighterConstants.SUB_SUPER_COLOR))
        superscript_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)

        # Map Regular Expressions to Formats
        
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HEADING), heading_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BOLD_AST), bold_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BOLD_UND), bold_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_ITALIC_AST), italic_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_ITALIC_UND), italic_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_CODE), self.code_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LINK), link_format))
        
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_BLOCKQUOTE), blockquote_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HR), hr_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_STRIKETHROUGH), strikethrough_format))

        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LIST_UNORDERED), list_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_LIST_ORDERED), list_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_TASK_LIST), task_list_format))

        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HTML_TAG), html_tag_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_TABLE_PIPE), table_pipe_format))

        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_FOOTNOTE), footnote_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_EMOJI), emoji_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_HIGHLIGHT), highlight_mark_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_SUBSCRIPT), subscript_format))
        self.highlighting_rules.append((QRegularExpression(SyntaxHighlighterConstants.REGEX_SUPERSCRIPT), superscript_format))

    def highlightBlock(self, text: str) -> None:
        """Applies syntax highlighting to a given block of text.

        Args:
            text: The text block (usually a single line) to be highlighted.
        """
        # 1. Apply all single-line regex rules
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        self.setCurrentBlockState(0)
        
        in_code_block = (self.previousBlockState() == 1)
        delimiter = "```"

        if not in_code_block:
            start_index = text.find(delimiter)
            if start_index >= 0:
                end_index = text.find(delimiter, start_index + 3)
                if end_index >= 0:
                    self.setFormat(start_index, end_index + 3 - start_index, self.code_format)
                else:
                    self.setCurrentBlockState(1)
                    self.setFormat(start_index, len(text) - start_index, self.code_format)
        else:
            end_index = text.find(delimiter)
            if end_index >= 0:
                self.setCurrentBlockState(0)
                self.setFormat(0, end_index + 3, self.code_format)
            else:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self.code_format)