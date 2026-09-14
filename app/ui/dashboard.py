from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("dashboard")

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(24)

        # Header
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Buat dan kelola materi edukasi anak dengan mudah."
        )
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        create_button = QPushButton("+  Buat Materi")
        create_button.setObjectName("primaryButton")
        create_button.setCursor(Qt.PointingHandCursor)

        header_layout.addWidget(create_button)

        main_layout.addLayout(header_layout)

        # Statistics
        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(16)
        stats_layout.setVerticalSpacing(16)

        stats_layout.addWidget(
            self._create_stat_card(
                "Materi",
                "0",
                "Materi edukasi yang dibuat",
            ),
            0,
            0,
        )

        stats_layout.addWidget(
            self._create_stat_card(
                "Template",
                "0",
                "Template yang tersedia",
            ),
            0,
            1,
        )

        stats_layout.addWidget(
            self._create_stat_card(
                "Asset",
                "0",
                "Gambar dan asset",
            ),
            0,
            2,
        )

        main_layout.addLayout(stats_layout)

        # Recent materials
        recent_frame = QFrame()
        recent_frame.setObjectName("contentCard")

        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(24, 24, 24, 24)
        recent_layout.setSpacing(12)

        recent_title = QLabel("Materi Terakhir")
        recent_title.setObjectName("sectionTitle")

        recent_description = QLabel(
            "Belum ada materi. Buat materi pertama untuk memulai."
        )
        recent_description.setObjectName("emptyText")

        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(recent_description)
        recent_layout.addStretch()

        main_layout.addWidget(recent_frame, 1)

    def _create_stat_card(
        self,
        title: str,
        value: str,
        description: str,
    ):
        card = QFrame()
        card.setObjectName("statCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        description_label = QLabel(description)
        description_label.setObjectName("statDescription")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)

        return card