"""
Универсальный табличный редактор.
Колонки задаются списком ColDef. Поддерживает QLineEdit, QComboBox, QCheckBox в ячейках.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr


@dataclass
class ColDef:
    key: str              # ключ i18n для заголовка
    field: str            # имя поля датакласса
    col_type: str = "str" # str | bool | combo
    width: int = 0        # 0 = stretch
    choices: list[tuple[str,str]] | None = None  # [(label_key, value), ...]


class TableEditor(QWidget):
    """
    Параметры:
      cols       — список ColDef
      factory    — callable() → новый объект строки
      on_change  — callable() → вызывается при любом изменении
    """

    def __init__(self,
                 cols: list[ColDef],
                 factory: Callable,
                 on_change: Callable | None = None,
                 parent=None):
        super().__init__(parent)
        self._cols = cols
        self._factory = factory
        self._on_change = on_change
        self._rows: list[Any] = []
        self._updating = False
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(len(self._cols))
        self._tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.horizontalHeader().setHighlightSections(False)
        self._update_headers()
        self._apply_widths()
        root.addWidget(self._tbl)

        btn_row = QHBoxLayout()
        self._btn_add = QPushButton(tr("add"))
        self._btn_del = QPushButton(tr("delete"))
        self._btn_up  = QPushButton(tr("move_up"))
        self._btn_dn  = QPushButton(tr("move_down"))
        for b in (self._btn_add, self._btn_del, self._btn_up, self._btn_dn):
            b.setFixedHeight(26)
            btn_row.addWidget(b)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)
        self._btn_up.clicked.connect(lambda: self._move(-1))
        self._btn_dn.clicked.connect(lambda: self._move(+1))

    def _update_headers(self):
        self._tbl.setHorizontalHeaderLabels([tr(c.key) for c in self._cols])

    def _apply_widths(self):
        hh = self._tbl.horizontalHeader()
        for i, col in enumerate(self._cols):
            if col.width:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self._tbl.setColumnWidth(i, col.width)
            else:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    # ── данные ───────────────────────────────────────────────────────────────
    def set_rows(self, rows: list):
        self._rows = rows
        self._repopulate()

    def get_rows(self) -> list:
        return self._rows

    def _repopulate(self):
        self._updating = True
        self._tbl.setRowCount(len(self._rows))
        for r, obj in enumerate(self._rows):
            for c, col in enumerate(self._cols):
                val = getattr(obj, col.field, "")
                self._set_cell(r, c, col, val)
        self._updating = False

    def _set_cell(self, row: int, col_idx: int, col: ColDef, val):
        if col.col_type == "bool":
            cb = QCheckBox()
            cb.setChecked(bool(val))
            cb.setStyleSheet("margin-left:8px;")
            cb.toggled.connect(lambda v, r=row, f=col.field: self._write_bool(r, f, v))
            self._tbl.setCellWidget(row, col_idx, cb)
        elif col.col_type == "combo" and col.choices:
            combo = QComboBox()
            for lkey, lval in col.choices:
                combo.addItem(tr(lkey), lval)
            idx = combo.findData(val)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.currentIndexChanged.connect(
                lambda _, r=row, f=col.field, cmb=combo: self._write_combo(r, f, cmb)
            )
            self._tbl.setCellWidget(row, col_idx, combo)
        else:
            item = QTableWidgetItem(str(val))
            self._tbl.setItem(row, col_idx, item)
            # подключаем сигнал один раз через itemChanged
        # Для str-ячеек используем itemChanged
        if col.col_type == "str" and not self._tbl.cellWidget(row, col_idx):
            pass  # handled by itemChanged below

        if col.col_type == "str":
            self._tbl.itemChanged.connect(self._on_item_changed)

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._updating:
            return
        r, c = item.row(), item.column()
        if r >= len(self._rows):
            return
        col = self._cols[c]
        if col.col_type == "str":
            setattr(self._rows[r], col.field, item.text())
            self._notify()

    def _write_bool(self, row: int, field: str, val: bool):
        if not self._updating and row < len(self._rows):
            setattr(self._rows[row], field, val)
            self._notify()

    def _write_combo(self, row: int, field: str, combo: QComboBox):
        if not self._updating and row < len(self._rows):
            setattr(self._rows[row], field, combo.currentData())
            self._notify()

    def _notify(self):
        if self._on_change:
            self._on_change()

    # ── кнопки ───────────────────────────────────────────────────────────────
    def _add(self):
        obj = self._factory()
        self._rows.append(obj)
        self._repopulate()
        self._tbl.selectRow(len(self._rows) - 1)
        self._notify()

    def _del(self):
        r = self._tbl.currentRow()
        if 0 <= r < len(self._rows):
            self._rows.pop(r)
            self._repopulate()
            self._notify()

    def _move(self, delta: int):
        r = self._tbl.currentRow()
        nr = r + delta
        if 0 <= r < len(self._rows) and 0 <= nr < len(self._rows):
            self._rows[r], self._rows[nr] = self._rows[nr], self._rows[r]
            self._repopulate()
            self._tbl.selectRow(nr)
            self._notify()

    # ── перевод ──────────────────────────────────────────────────────────────
    def retranslate(self):
        self._update_headers()
        self._btn_add.setText(tr("add"))
        self._btn_del.setText(tr("delete"))
        self._btn_up.setText(tr("move_up"))
        self._btn_dn.setText(tr("move_down"))
        # перерисовываем combo-ячейки с новыми текстами
        self._updating = True
        for r, obj in enumerate(self._rows):
            for c, col in enumerate(self._cols):
                if col.col_type == "combo":
                    w = self._tbl.cellWidget(r, c)
                    if isinstance(w, QComboBox):
                        cur = w.currentData()
                        w.blockSignals(True)
                        w.clear()
                        for lkey, lval in (col.choices or []):
                            w.addItem(tr(lkey), lval)
                        idx = w.findData(cur)
                        if idx >= 0:
                            w.setCurrentIndex(idx)
                        w.blockSignals(False)
        self._updating = False
