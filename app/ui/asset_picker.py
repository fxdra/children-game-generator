from collections import OrderedDict

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QSize,
    Qt,
    QSortFilterProxyModel,
    Signal,
)
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QStyle,
    QVBoxLayout,
)

from app.services.openmoji_asset import OpenMojiAssetService


class _AssetListModel(QAbstractListModel):
    AssetNameRole = Qt.ItemDataRole.UserRole + 1
    AssetPathRole = Qt.ItemDataRole.UserRole + 2
    SearchRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, assets=None, parent=None):
        super().__init__(parent)
        self._assets = assets or []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._assets)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._assets)):
            return None

        asset = self._assets[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            # Asset names are intentionally not displayed; the picker is visual-only.
            return ""
        if role == self.AssetNameRole:
            return asset["name"]
        if role == self.AssetPathRole:
            return str(asset["path"])
        if role == self.SearchRole:
            return f'{asset["name"]} {asset["filename"]}'.lower()
        if role == Qt.ItemDataRole.ToolTipRole:
            return None
        return None

    def set_assets(self, assets):
        self.beginResetModel()
        self._assets = assets
        self.endResetModel()


class _AssetFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterRole(_AssetListModel.SearchRole)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)


class _LazySvgDelegate(QStyledItemDelegate):
    """Render only visible SVG thumbnails and keep them in a bounded LRU cache."""

    _pixmap_cache = OrderedDict()
    _cache_limit = 512
    _thumbnail_size = QSize(76, 76)

    @classmethod
    def _thumbnail(cls, asset_path):
        key = (asset_path, cls._thumbnail_size.width(), cls._thumbnail_size.height())
        cached = cls._pixmap_cache.get(key)
        if cached is not None:
            cls._pixmap_cache.move_to_end(key)
            return cached

        renderer = QSvgRenderer(asset_path)
        if not renderer.isValid():
            return QPixmap()

        pixmap = QPixmap(cls._thumbnail_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        cls._pixmap_cache[key] = pixmap
        cls._pixmap_cache.move_to_end(key)
        while len(cls._pixmap_cache) > cls._cache_limit:
            cls._pixmap_cache.popitem(last=False)
        return pixmap

    def paint(self, painter, option, index):
        painter.save()
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)

        if selected:
            painter.fillRect(option.rect, option.palette.highlight())
        elif hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())

        asset_path = index.data(_AssetListModel.AssetPathRole)
        pixmap = self._thumbnail(asset_path) if asset_path else QPixmap()
        if not pixmap.isNull():
            x = option.rect.center().x() - pixmap.width() // 2
            y = option.rect.center().y() - pixmap.height() // 2
            painter.drawPixmap(x, y, pixmap)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(100, 100)


class AssetPickerDialog(QDialog):
    asset_selected = Signal(str)

    def __init__(self, parent=None, item_label="gambar"):
        super().__init__(parent)
        self.item_label = item_label
        self.selected_asset = None
        self.all_assets = []
        self.target_index = 0
        self.total_targets = 1

        self.setWindowTitle("Pilih Gambar")
        self.resize(720, 600)
        self._setup_ui()
        self._load_assets()
        self._update_target_indicator()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        title = QLabel("Pilih Gambar")
        title.setObjectName("pickerTitle")
        main_layout.addWidget(title)

        self.target_label = QLabel()
        self.target_label.setObjectName("sectionTitle")
        main_layout.addWidget(self.target_label)

        self.target_description = QLabel()
        self.target_description.setObjectName("pageSubtitle")
        main_layout.addWidget(self.target_description)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Cari gambar...")
        self.search_input.textChanged.connect(self._filter_assets)
        main_layout.addWidget(self.search_input)

        self.asset_view = QListView()
        self.asset_view.setObjectName("assetGridView")
        self.asset_view.setViewMode(QListView.ViewMode.IconMode)
        self.asset_view.setFlow(QListView.Flow.LeftToRight)
        self.asset_view.setWrapping(True)
        self.asset_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.asset_view.setMovement(QListView.Movement.Static)
        self.asset_view.setSpacing(8)
        self.asset_view.setUniformItemSizes(True)
        self.asset_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.asset_view.setLayoutMode(QListView.LayoutMode.Batched)
        self.asset_view.setBatchSize(48)
        self.asset_view.setItemDelegate(_LazySvgDelegate(self.asset_view))

        self.asset_model = _AssetListModel(parent=self)
        self.asset_proxy = _AssetFilterProxyModel(self)
        self.asset_proxy.setSourceModel(self.asset_model)
        self.asset_view.setModel(self.asset_proxy)
        self.asset_view.selectionModel().currentChanged.connect(self._on_current_changed)
        main_layout.addWidget(self.asset_view, 1)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        cancel_button = QPushButton("Batal")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)

        self.select_button = QPushButton("Gunakan gambar")
        self.select_button.setObjectName("primaryButton")
        self.select_button.setEnabled(False)
        self.select_button.clicked.connect(self._confirm_selection)

        footer_layout.addWidget(cancel_button)
        footer_layout.addWidget(self.select_button)
        main_layout.addLayout(footer_layout)

    def _load_assets(self, assets=None):
        if assets is None:
            self.all_assets = OpenMojiAssetService.get_all_assets()
            assets = self.all_assets
        self.asset_model.set_assets(assets)
        self.asset_proxy.setFilterFixedString(self.search_input.text().strip().lower())

    def _filter_assets(self, text):
        self.asset_proxy.setFilterFixedString(text.strip().lower())

    def _on_current_changed(self, current, previous):
        self.selected_asset = (
            current.data(_AssetListModel.AssetNameRole) if current.isValid() else None
        )
        self.select_button.setEnabled(bool(self.selected_asset))

    def _update_target_indicator(self):
        current = min(self.target_index + 1, self.total_targets)
        self.target_label.setText(f"Pasangan {current} dari {self.total_targets}")
        self.target_description.setText(
            "Pilih gambar, lalu konfirmasi. Picker akan lanjut ke pasangan berikutnya."
        )
        self.select_button.setText(f"Gunakan gambar untuk pasangan {current}")

    def _confirm_selection(self):
        if not self.selected_asset:
            return

        asset_name = self.selected_asset
        current_target = self.target_index
        reply = QMessageBox.question(
            self,
            "Konfirmasi Gambar",
            f"Gunakan gambar yang dipilih untuk pasangan {current_target + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Emit while target_index still points to the current pair. The dialog
        # remains open and then advances to the next pair automatically.
        self.asset_selected.emit(asset_name)

        if current_target < self.total_targets - 1:
            self.target_index = current_target + 1
        self._clear_selection()

    def _clear_selection(self):
        self.selected_asset = None
        self.asset_view.clearSelection()
        self.asset_view.setCurrentIndex(QModelIndex())
        self.select_button.setEnabled(False)
        self._update_target_indicator()

    def set_target(self, target_index: int, total_targets: int):
        self.total_targets = max(1, int(total_targets))
        self.target_index = max(0, min(int(target_index), self.total_targets - 1))
        self._clear_selection()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = AssetPickerDialog()
    dialog.exec()
    sys.exit(0)
