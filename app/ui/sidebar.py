from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Sidebar(QFrame):
    navigation_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)

        # Brand
        brand = QLabel("Game Anak")
        brand.setObjectName("brand")

        subtitle = QLabel("Pembuat Materi Edukasi")
        subtitle.setObjectName("brandSubtitle")

        layout.addWidget(brand)
        layout.addWidget(subtitle)

        layout.addSpacing(28)

        # Navigation
        self.dashboard_button = self._create_nav_button(
            "Dashboard",
            "dashboard",
        )

        self.material_button = self._create_nav_button(
            "Materi",
            "materials",
        )

        self.template_button = self._create_nav_button(
            "Template",
            "templates",
        )

        self.asset_button = self._create_nav_button(
            "Asset",
            "assets",
        )

        layout.addWidget(self.dashboard_button)
        layout.addWidget(self.material_button)
        layout.addWidget(self.template_button)
        layout.addWidget(self.asset_button)

        layout.addStretch()

        # Bottom section
        self.settings_button = self._create_nav_button(
            "Pengaturan",
            "settings",
        )

        layout.addWidget(self.settings_button)

        self.dashboard_button.setChecked(True)

    def _create_nav_button(self, text: str, page_name: str):
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)

        button.clicked.connect(
            lambda: self._handle_navigation(button, page_name)
        )

        return button

    def _handle_navigation(self, button: QPushButton, page_name: str):
        for child in self.findChildren(QPushButton):
            if child.objectName() == "navButton":
                child.setChecked(child is button)

        self.navigation_changed.emit(page_name)