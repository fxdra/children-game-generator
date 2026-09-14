from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QWidget,
)

from app.ui.dashboard import Dashboard
from app.ui.material_editor import MaterialEditor
from app.ui.materials import Materials
from app.ui.sidebar import Sidebar
from app.ui.worksheet_editor import WorksheetEditor
from app.ui.worksheet_preview import WorksheetPreviewDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Game Edukasi Anak")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 650)

        self._setup_ui()
        self._setup_style()

    def _setup_ui(self):
        # =========================
        # CENTRAL WIDGET
        # =========================

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================
        # SIDEBAR
        # =========================

        self.sidebar = Sidebar()

        # =========================
        # PAGE CONTAINER
        # =========================

        self.pages = QStackedWidget()

        # =========================
        # PAGES
        # =========================

        self.dashboard = Dashboard()
        self.materials = Materials()
        self.material_editor = MaterialEditor()
        self.worksheet_editor = WorksheetEditor()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.materials)
        self.pages.addWidget(self.material_editor)
        self.pages.addWidget(self.worksheet_editor)

        # =========================
        # MAIN LAYOUT
        # =========================

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages, 1)

        self.setCentralWidget(central_widget)

        # =========================
        # SIGNALS
        # =========================

        self.sidebar.navigation_changed.connect(
            self._change_page
        )

        self.materials.create_requested.connect(
            self._open_material_editor
        )

        self.material_editor.back_requested.connect(
            self._back_to_materials
        )

        self.material_editor.setup_completed.connect(
            self._material_setup_completed
        )

        self.worksheet_editor.back_requested.connect(
            self._back_to_material_editor
        )

        self.worksheet_editor.preview_requested.connect(
            self._worksheet_preview
        )

    # =========================
    # PAGE NAVIGATION
    # =========================

    def _change_page(self, page_name: str):
        if page_name == "dashboard":
            self.pages.setCurrentWidget(self.dashboard)

        elif page_name == "materials":
            self.pages.setCurrentWidget(self.materials)

    def _open_material_editor(self):
        self.material_editor.reset_form()
        self.pages.setCurrentWidget(self.material_editor)

    def _back_to_materials(self):
        self.pages.setCurrentWidget(self.materials)

    def _back_to_material_editor(self):
        self.pages.setCurrentWidget(self.material_editor)

    # =========================
    # MATERIAL SETUP
    # =========================

    def _material_setup_completed(self, material_data: dict):
        if material_data["activity_type"] == "Worksheet":
            self.worksheet_editor.reset_form()
            self.worksheet_editor.set_material_data(material_data)
            self.pages.setCurrentWidget(self.worksheet_editor)

        else:
            QMessageBox.information(
                self,
                "Belum Tersedia",
                (
                    f"Editor untuk aktivitas "
                    f"'{material_data['activity_type']}' "
                    "belum tersedia."
                ),
            )

    def _worksheet_preview(self, worksheet_data: dict):
        dialog = WorksheetPreviewDialog(
            worksheet_data,
            self,
        )

        dialog.exec()

    # =========================
    # STYLE
    # =========================

    def _setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }

            QWidget#centralWidget {
                background-color: #F5F7FA;
            }

            /* =========================
               SIDEBAR
               ========================= */

            QFrame#sidebar {
                background-color: #172033;
                border: none;
            }

            QLabel#brand {
                color: #FFFFFF;
                font-size: 26px;
                font-weight: 700;
            }

            QLabel#brandSubtitle {
                color: #9DA8BA;
                font-size: 12px;
            }

            QPushButton#navButton {
                color: #C7D0DE;
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton#navButton:hover {
                background-color: #222E44;
                color: #FFFFFF;
            }

            QPushButton#navButton:checked {
                background-color: #30415F;
                color: #FFFFFF;
                font-weight: 600;
            }

            /* =========================
               DASHBOARD
               ========================= */

            QLabel#pageTitle {
                color: #172033;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #6B7688;
                font-size: 14px;
            }

            QPushButton#primaryButton {
                color: #FFFFFF;
                background-color: #2F6FED;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#primaryButton:hover {
                background-color: #255ED0;
            }

            QPushButton#primaryButton:pressed {
                background-color: #1E4FAF;
            }

            QFrame#statCard {
                background-color: #FFFFFF;
                border: 1px solid #E3E7ED;
                border-radius: 10px;
            }

            QLabel#statTitle {
                color: #6B7688;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#statValue {
                color: #172033;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#statDescription {
                color: #9AA4B2;
                font-size: 12px;
            }

            QFrame#contentCard {
                background-color: #FFFFFF;
                border: 1px solid #E3E7ED;
                border-radius: 10px;
            }

            QLabel#sectionTitle {
                color: #172033;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#emptyText {
                color: #8A95A5;
                font-size: 13px;
            }

            /* =========================
               MATERIALS
               ========================= */

            QFrame#filterCard {
                background-color: #FFFFFF;
                border: 1px solid #E3E7ED;
                border-radius: 10px;
            }

            QLineEdit#searchInput {
                color: #172033;
                background-color: #F8F9FB;
                border: 1px solid #DCE1E8;
                border-radius: 7px;
                padding: 10px 12px;
                font-size: 13px;
            }

            QLineEdit#searchInput:focus {
                border: 1px solid #2F6FED;
                background-color: #FFFFFF;
            }

            QPushButton#filterButton {
                color: #4D596B;
                background-color: #F8F9FB;
                border: 1px solid #DCE1E8;
                border-radius: 7px;
                padding: 10px 14px;
                font-size: 13px;
            }

            QPushButton#filterButton:hover {
                background-color: #F0F3F7;
            }

            QLabel#emptyTitle {
                color: #172033;
                font-size: 18px;
                font-weight: 700;
            }

            /* =========================
               MATERIAL EDITOR
               ========================= */

            QLabel#formLabel {
                color: #172033;
                font-size: 13px;
                font-weight: 600;
            }

            QLineEdit#formInput,
            QComboBox#formCombo {
                color: #172033;
                background-color: #F8F9FB;
                border: 1px solid #DCE1E8;
                border-radius: 7px;
                padding: 10px 12px;
                font-size: 13px;
                min-height: 18px;
            }

            QLineEdit#formInput:focus,
            QComboBox#formCombo:focus {
                border: 1px solid #2F6FED;
                background-color: #FFFFFF;
            }

            QPushButton#secondaryButton {
                color: #4D596B;
                background-color: #FFFFFF;
                border: 1px solid #DCE1E8;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#secondaryButton:hover {
                background-color: #F5F7FA;
            }

            /* =========================
            WORKSHEET EDITOR
            ========================= */

            QLabel#materialInfo {
                color: #4D596B;
                font-size: 13px;
            }

            QTextEdit#formTextEdit {
                color: #172033;
                background-color: #F8F9FB;
                border: 1px solid #DCE1E8;
                border-radius: 7px;
                padding: 10px 12px;
                font-size: 13px;
            }

            QTextEdit#formTextEdit:focus {
                border: 1px solid #2F6FED;
                background-color: #FFFFFF;
            }
        """)