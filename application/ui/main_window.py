from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from ui.components.top_menu import TopMenuBar
from ui.components.sidebar import SidebarMenu
from ui.components.md_scene import MarkdownScene
from ui.components.git_scene import GitScene
from core.constants import UIConstants

class MainWindow(QMainWindow):
    """Handles main window layout setup."""

    def __init__(self) -> None:
        """
        Initializes main window.
        """
        super().__init__()

        self.setWindowTitle(UIConstants.APP_WINDOW_TITLE)
        self.setMinimumSize(UIConstants.MIN_WINDOW_WIDTH, UIConstants.MIN_WINDOW_HEIGHT)
        self.resize(UIConstants.DEFAULT_WINDOW_WIDTH, UIConstants.DEFAULT_WINDOW_HEIGHT)

        # Top menu setup
        self.top_menu = TopMenuBar(self)
        self.setMenuBar(self.top_menu)

        # Central widget and layout setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Components setup
        self.sidebar = SidebarMenu()
        self.md_scene = MarkdownScene()
        self.git_scene = GitScene()

        self.stacked_scenes = QStackedWidget()
        self.stacked_scenes.addWidget(self.md_scene)
        self.stacked_scenes.addWidget(self.git_scene)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_scenes)

        # Sidebar scene switch setup
        self.sidebar.btn_md.clicked.connect(lambda: self.stacked_scenes.setCurrentIndex(0))
        self.sidebar.btn_git.clicked.connect(lambda: self.stacked_scenes.setCurrentIndex(1))

    def get_toolbar(self) -> TopMenuBar:
        """
        Returns top menu.
        """
        return self.top_menu

    def get_markdown_viewer(self) -> MarkdownScene:
        """
        Returns markdown scene.
        """
        return self.md_scene