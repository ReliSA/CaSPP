"""
UI Widget for the Markdown Editor with a line number gutter.
"""
from PyQt6.QtWidgets import QPlainTextEdit, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPaintEvent, QResizeEvent
from PyQt6.QtCore import Qt, QRect, QSize

from core.constants import EditorConstants

class MarkdownEditorWidget(QPlainTextEdit):
    """A UI text editor widget with built-in line numbers and active line highlighting."""

    def __init__(self, parent: QWidget = None) -> None:
        """Initializes the Markdown editor widget.

        Args:
            parent: Parent widget. Defaults to None.

        Returns:
            None.
        """
        super().__init__(parent)
        
        # Setup font
        self.editor_font = QFont(EditorConstants.FONT_FAMILY, EditorConstants.FONT_SIZE)
        self.setFont(self.editor_font)

        # Initialize the gutter widget
        self.line_number_area = LineNumberArea(self)

        # Internal signals to keep the gutter painted correctly when scrolling/typing
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._update_current_line)

        self._update_line_number_area_width(0)
        self._update_current_line()

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """Handles paint events for the line number gutter.

        This method draws the gutter background, the line numbers, and the 
        highlighted background for the currently active line.

        Args:
            event: The QPaintEvent triggered by the UI update.

        Returns:
            None.
        """
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(EditorConstants.GUTTER_BACKGROUND))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        current_block_number = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number_str = str(block_number + 1)
                is_active_line = (block_number == current_block_number)
                
                if is_active_line:
                    highlight_rect = QRect(0, top, self.line_number_area.width(), self.fontMetrics().height())
                    painter.fillRect(highlight_rect, QColor(EditorConstants.ACTIVE_GUTTER_BACK_COLOR))
                    painter.setPen(QColor(EditorConstants.ACTIVE_LINE_NUMBER_COLOR))
                else:
                    painter.setPen(QColor(EditorConstants.LINE_NUMBER_COLOR))

                painter.drawText(
                    0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, number_str
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def _line_number_area_width(self) -> int:
        """Calculates the required width for the line number gutter.

        The width scales dynamically based on how many digits are needed 
        for the total line count (e.g., 1-9 vs 10-99).

        Returns:
            int: The calculated width in pixels.
        """
        digits = 1
        max_blocks = max(1, self.blockCount())
        while max_blocks >= 10:
            max_blocks /= 10
            digits += 1
        return 8 + self.fontMetrics().horizontalAdvance('9') * digits

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles resize events for the text editor.

        Ensures the gutter widget is properly resized and positioned 
        on the left side whenever the editor dimensions change.

        Args:
            event: The QResizeEvent.

        Returns:
            None.
        """
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self._line_number_area_width(), cr.height()))

    def _update_line_number_area_width(self, _) -> None:
        """Updates the viewport margins when the block count changes.

        This pushes the text to the right so it doesn't overlap with the gutter.

        Returns:
            None.
        """
        self.setViewportMargins(self._line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, deltaY: int) -> None:
        """Updates the gutter position and bounds during scroll events.

        Args:
            rect: The updated visible rectangle.
            dy: The vertical scroll delta.

        Returns:
            None.
        """
        if deltaY:
            self.line_number_area.scroll(0, deltaY)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def _update_current_line(self) -> None:
        """Forces the gutter to repaint when the cursor moves.

        This ensures the active line highlighting updates properly.

        Returns:
            None.
        """
        self.line_number_area.update()


class LineNumberArea(QWidget):
    """Sub-widget responsible for the actual paint surface of the gutter."""

    def __init__(self, editor: MarkdownEditorWidget) -> None:
        """Initializes the LineNumberArea.

        Args:
            editor: The parent MarkdownEditorWidget instance.

        Returns:
            None.
        """
        super().__init__(editor)
        self.editor = editor
        self.setFont(self.editor.font())

    def sizeHint(self) -> QSize:
        """Provides a size hint to Qt based on the calculated gutter width.

        Returns:
            QSize: The suggested dimensions for this widget.
        """
        return QSize(self.editor._line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Passes the paint event back to the parent editor's rendering logic.

        Args:
            event: The QPaintEvent triggering the redraw.

        Returns:
            None.
        """
        self.editor.line_number_area_paint_event(event)