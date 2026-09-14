from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Materials(QWidget):
    create_requested = Signal()
    def __init__(self):
        super().__init__()

        self.setObjectName("materials")

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 32, 36, 32)
        main_layout.setSpacing(24)

        # =========================
        # HEADER
        # =========================

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Materi")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Kelola materi edukasi yang akan dibuat dan dicetak."
        )
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        create_button = QPushButton("+  Buat Materi")
        create_button.clicked.connect(self.create_requested.emit)
        create_button.setObjectName("primaryButton")
        create_button.setCursor(Qt.PointingHandCursor)

        header_layout.addWidget(create_button)

        main_layout.addLayout(header_layout)

        # =========================
        # FILTER
        # =========================

        filter_frame = QFrame()
        filter_frame.setObjectName("filterCard")

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.setSpacing(12)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Cari materi...")
        search_input.setObjectName("searchInput")

        category_button = QPushButton("Semua Kategori")
        category_button.setObjectName("filterButton")

        age_button = QPushButton("Semua Usia")
        age_button.setObjectName("filterButton")

        filter_layout.addWidget(search_input, 1)
        filter_layout.addWidget(category_button)
        filter_layout.addWidget(age_button)

        main_layout.addWidget(filter_frame)

        # =========================
        # EMPTY STATE
        # =========================

        empty_card = QFrame()
        empty_card.setObjectName("contentCard")

        empty_layout = QVBoxLayout(empty_card)
        empty_layout.setContentsMargins(30, 40, 30, 40)
        empty_layout.setSpacing(12)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_title = QLabel("Belum ada materi")
        empty_title.setObjectName("emptyTitle")
        empty_title.setAlignment(Qt.AlignCenter)

        empty_description = QLabel(
            "Buat materi pertama untuk mulai menyusun "
            "worksheet edukasi anak."
        )
        empty_description.setObjectName("emptyText")
        empty_description.setAlignment(Qt.AlignCenter)

        empty_create_button = QPushButton("+  Buat Materi Pertama")
        empty_create_button.clicked.connect(self.create_requested.emit)
        empty_create_button.setObjectName("primaryButton")
        empty_create_button.setCursor(Qt.PointingHandCursor)

        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_description)
        empty_layout.addSpacing(8)
        empty_layout.addWidget(
            empty_create_button,
            alignment=Qt.AlignCenter,
        )

        main_layout.addWidget(empty_card, 1)