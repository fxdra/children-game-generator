from collections import OrderedDict
from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QModelIndex, QSize, Qt, QSortFilterProxyModel, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QStyle
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QListView,
    QStyledItemDelegate,
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
            return asset["name"]
        if role == self.AssetNameRole:
            return asset["name"]
        if role == self.AssetPathRole:
            return str(asset["path"])
        if role == self.SearchRole:
            return f'{asset["name"]} {asset["filename"]}'.lower()
        if role == Qt.ItemDataRole.ToolTipRole:
            return asset["name"]
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
    """Render SVG thumbnails only when Qt paints a visible list item."""

    _pixmap_cache = OrderedDict()
    _cache_limit = 512
    _thumbnail_size = QSize(64, 64)

    @classmethod
    def clear_cache(cls):
        cls._pixmap_cache.clear()

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

        icon_rect = option.rect.adjusted(8, 7, -8, -31)
        if not pixmap.isNull():
            target = QSize(64, 64)
            x = icon_rect.center().x() - target.width() // 2
            y = icon_rect.center().y() - target.height() // 2
            painter.drawPixmap(x, y, pixmap)

        text_rect = option.rect.adjusted(3, option.rect.height() - 27, -3, -2)
        painter.setPen(option.palette.highlightedText().color() if selected else option.palette.text().color())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, index.data(Qt.ItemDataRole.DisplayRole) or "")
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(104, 112)


class AssetPickerDialog(QDialog):
    asset_selected = Signal(str)

    def __init__(self, parent=None, item_label="Karakter"):
        super().__init__(parent)
        self.item_label = item_label
        self.selected_asset = None
        self.all_assets = []
        self.target_index = 0
        self.total_targets = 6

        self.setWindowTitle(f"Pilih {self.item_label}")
        self.resize(720, 600)
        self._setup_ui()
        self._load_assets()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        title = QLabel(f"Pilih {self.item_label}")
        title.setObjectName("pickerTitle")
        main_layout.addWidget(title)

        self.target_label = QLabel()
        self.target_label.setObjectName("sectionTitle")
        main_layout.addWidget(self.target_label)

        self.target_description = QLabel("Pilih gambar untuk pasangan nomor 1.")
        self.target_description.setObjectName("pageSubtitle")
        main_layout.addWidget(self.target_description)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(f"Cari {self.item_label.lower()}...")
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

        self.select_button = QPushButton(f"Gunakan {self.item_label}")
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
        # Filtering is performed by the proxy model. No buttons or thumbnails
        # are recreated/rendered as the user types.
        self.asset_proxy.setFilterFixedString(text.strip().lower())

    def _on_current_changed(self, current, previous):
        self.selected_asset = current.data(_AssetListModel.AssetNameRole) if current.isValid() else None
        self.select_button.setEnabled(bool(self.selected_asset))

    def _update_target_indicator(self):
        current = self.target_index + 1
        if self.item_label == "Karakter":
            self.target_label.setText(f"Karakter {current} dari {self.total_targets}")
            self.target_description.setText(f"Pilih karakter {self._ordinal(current)}.")
        else:
            self.target_label.setText(f"Pasangan {current} dari {self.total_targets}")
            self.target_description.setText(f"Pilih gambar untuk pasangan nomor {current}.")

    @staticmethod
    def _ordinal(number):
        names = {1: "pertama", 2: "kedua", 3: "ketiga", 4: "keempat", 5: "kelima", 6: "keenam"}
        return names.get(number, f"nomor {number}")

    def _confirm_selection(self):
        if not self.selected_asset:
            return

        asset_name = self.selected_asset
        reply = QMessageBox.question(
            self,
            f"Gunakan {self.item_label}?",
            f'Gunakan {self.item_label.lower()} "{asset_name}" untuk {self._target_confirmation_text()}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.asset_selected.emit(asset_name)
        if self.target_index < self.total_targets - 1:
            self.target_index += 1
        self._clear_selection()

    def _target_confirmation_text(self):
        current = self.target_index + 1
        if self.item_label == "Karakter":
            return f"karakter {current} dari {self.total_targets}"
        return f"pasangan {current} dari {self.total_targets}"

    def _clear_selection(self):
        self.selected_asset = None
        self.asset_view.clearSelection()
        self.asset_view.setCurrentIndex(QModelIndex())
        self.select_button.setEnabled(False)
        self._update_target_indicator()

    def set_target(self, target_index: int, total_targets: int):
        self.target_index = target_index
        self.total_targets = total_targets
        self._clear_selection()
        self._update_target_indicator()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = AssetPickerDialog()
    dialog.exec()
    sys.exit(0)
