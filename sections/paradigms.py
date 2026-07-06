"""
Парадигмы — таблицы аффиксов для каждой части речи.
Раздел «Парадигмы» в дереве навигации (внутри Морфологии).
Кнопка «Формы ▾» в лексиконе открывает WordFormsDialog.

Поддерживаемые типы аффиксов (фильтруются по настройкам в "Типах морфем"):
- suffix (суффикс): всегда доступен
- prefix (приставка): если has_prefixes = True
- infix (инфикс): если has_infixes = True
- circumfix (циркумфикс): если has_circumfixes = True
- postfix (постфикс): всегда доступен
- interfix (интерфикс): если has_interfixes = True (добавь в модель если нужно)
- duplifix (дуплификс): если has_reduplication != "none"
- transfix (трансфикс): если has_transfixes = True
- simulfix (симульфикс): всегда доступен
- disfix (дисфикс): всегда доступен
- suprafix (супрафикс): всегда доступен
"""
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import get_lang, tr
from core.model import AffixRule, Paradigm

# ── Полный список типов аффиксов с примерами и подсказками ─────────────────
_ALL_AFFIX_TYPES = [
    ("pf_suffix",     "suffix",      "-чик",         "корень-суффикс\nПример: лёт + -чик = лётчик"),
    ("pf_prefix",     "prefix",      "пере-",        "префикс-корень\nПример: пере- + дел = передел"),
    ("pf_postfix",    "postfix",     "-ся",          "корень-постфикс (после окончаний)\nПример: задерживаем + -ся = задерживаемся"),
    ("pf_infix",      "infix",       "2-um",         "ко<инфикс>рень\nФормат: позиция-вставка\nПример: sax + 3-om + aphone = saxomaphone"),
    ("pf_circumfix",  "circumfix",   "ge- -t",       "циркум-корень-фикс\nФормат: префикс- -суффикс\nПример: ge- + mach + -t = gemacht"),
    ("pf_interfix",   "interfix",    "-о-",          "корень1-интерфикс-корень2\nВведите два корня через пробел: «сам лёт»\nПример: сам + -о- + лёт = самолёт"),
    ("pf_duplifix",   "duplifix",    "2-~",          "удвоение части корня\nФормат: N-~ (с начала) или ~-N (с конца)\nПример: teeny + 2-~ = teenyte"),
    ("pf_transfix",   "transfix",    "1-a-1-i-1",    "прерывистый аффикс\nФормат: длина-гласная-длина-гласная...\nПример: ktb + 1-a-1-i-1 = katib"),
    ("pf_simulfix",   "simulfix",    "ou→i",         "замена сегмента\nФормат: старый→новый\nПример: mouse + ou→i = mice"),
    ("pf_disfix",     "disfix",      "2-",           "удаление части корня\nФормат: N- (с начала) или -N (с конца)\nПример: tipasli + 2- = pasli"),
    ("pf_suprafix",   "suprafix",    "1→2",          "смена ударения\nФормат: слог1→слог2\nПример: produce + 1→2 = prodUce"),
]

# Стандартные формы для частей речи
_DEFAULT_FORMS = {
    "noun": [
        "Им.п. ед.ч.", "Род.п. ед.ч.", "Дат.п. ед.ч.", "Вин.п. ед.ч.",
        "Твор.п. ед.ч.", "Предл.п. ед.ч.", "Им.п. мн.ч.", "Род.п. мн.ч.",
    ],
    "verb": [
        "Инфинитив", "Наст.вр. 1л.ед.ч.", "Наст.вр. 2л.ед.ч.", "Наст.вр. 3л.ед.ч.",
        "Прош.вр. ед.ч.", "Прош.вр. мн.ч.", "Повел.накл. ед.ч.", "Повел.накл. мн.ч.",
    ],
    "adjective": [
        "М.р. ед.ч. Им.п.", "Ж.р. ед.ч. Им.п.", "Ср.р. ед.ч. Им.п.", "Мн.ч. Им.п.",
        "Сравн.степень", "Превосх.степень", "Краткая форма м.р.", "Краткая форма ж.р.",
    ],
}


def _set_combo(combo, value):
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


# ═══════════════════════════════════════════════════════════════════════════════
# Движок применения аффиксов
# ═══════════════════════════════════════════════════════════════════════════════
class AffixEngine:
    """Применяет аффикс по схеме к корню."""

    @staticmethod
    def apply(root: str, affix_type: str, pattern: str) -> str:
        if not root or not pattern:
            return root

        methods = {
            "prefix": AffixEngine._apply_prefix,
            "suffix": AffixEngine._apply_suffix,
            "postfix": AffixEngine._apply_suffix,
            "interfix": AffixEngine._apply_interfix,
            "infix": AffixEngine._apply_infix,
            "circumfix": AffixEngine._apply_circumfix,
            "duplifix": AffixEngine._apply_duplifix,
            "transfix": AffixEngine._apply_transfix,
            "simulfix": AffixEngine._apply_simulfix,
            "disfix": AffixEngine._apply_disfix,
            "suprafix": AffixEngine._apply_suprafix,
        }

        method = methods.get(affix_type)
        return method(root, pattern) if method else root

    @staticmethod
    def _apply_prefix(root: str, pattern: str) -> str:
        return pattern.rstrip("-") + root

    @staticmethod
    def _apply_suffix(root: str, pattern: str) -> str:
        return root + pattern.lstrip("-")

    @staticmethod
    def _apply_interfix(root: str, pattern: str) -> str:
        parts = root.split()
        interfix = pattern.strip("-")
        if len(parts) >= 2:
            return parts[0] + interfix + parts[1]
        else:
            return root + interfix

    @staticmethod
    def _apply_infix(root: str, pattern: str) -> str:
        parts = pattern.split("-")
        if len(parts) == 2:
            try:
                pos = int(parts[0])
                infix = parts[1]
                if 0 <= pos <= len(root):
                    return root[:pos] + infix + root[pos:]
            except ValueError:
                pass
        return root + pattern

    @staticmethod
    def _apply_circumfix(root: str, pattern: str) -> str:
        parts = re.split(r"[-…]+", pattern)
        if len(parts) >= 2:
            prefix = parts[0].strip()
            suffix = parts[-1].strip()
            return prefix + root + suffix
        return pattern + root

    @staticmethod
    def _apply_duplifix(root: str, pattern: str) -> str:
        if "-~" in pattern:
            try:
                pos = int(pattern.replace("-~", ""))
                part = root[:pos]
                return root + part
            except ValueError:
                pass
        elif "~-" in pattern:
            try:
                pos = int(pattern.replace("~-", ""))
                part = root[-pos:]
                return part + root
            except ValueError:
                pass
        return root + root

    @staticmethod
    def _apply_transfix(root: str, pattern: str) -> str:
        parts = pattern.split("-")
        if len(parts) >= 3:
            result = []
            pos = 0
            for i in range(0, len(parts) - 1, 2):
                try:
                    n = int(parts[i])
                    v = parts[i + 1]
                    if pos + n <= len(root):
                        result.append(root[pos:pos + n] + v)
                        pos += n
                except (ValueError, IndexError):
                    pass
            if pos < len(root):
                result.append(root[pos:])
            return "".join(result)
        return root

    @staticmethod
    def _apply_simulfix(root: str, pattern: str) -> str:
        if "→" in pattern:
            old, new = pattern.split("→")
            return root.replace(old.strip(), new.strip())
        return root

    @staticmethod
    def _apply_disfix(root: str, pattern: str) -> str:
        if pattern.endswith("-") and not pattern.startswith("-"):
            try:
                n = int(pattern[:-1])
                return root[n:]
            except ValueError:
                pass
        elif pattern.startswith("-") and not pattern.endswith("-"):
            try:
                n = int(pattern[1:])
                return root[:-n]
            except ValueError:
                pass
        return root

    @staticmethod
    def _apply_suprafix(root: str, pattern: str) -> str:
        return root


# ═══════════════════════════════════════════════════════════════════════════════
# Диалог редактирования списка форм для части речи
# ═══════════════════════════════════════════════════════════════════════════════
class FormListDialog(QDialog):
    def __init__(self, parent, forms: list[str], pos_name: str):
        super().__init__(parent)
        self._forms = forms.copy()
        self._pos_name = pos_name
        self.setWindowTitle(tr("pf_edit_forms_title").format(pos_name))
        self.setMinimumSize(400, 350)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)

        lbl = QLabel(tr("pf_edit_forms_hint"))
        lbl.setStyleSheet("color: #555; margin-bottom: 8px;")
        root.addWidget(lbl)

        self._list = QTableWidget()
        self._list.setColumnCount(1)
        self._list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._list.verticalHeader().setVisible(False)
        self._list.horizontalHeader().setVisible(False)
        self._list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._list.setAlternatingRowColors(True)
        self._populate()
        root.addWidget(self._list)

        btn_row = QHBoxLayout()
        self._btn_add = QPushButton(tr("add"))
        self._btn_del = QPushButton(tr("delete"))
        self._btn_up = QPushButton(tr("move_up"))
        self._btn_dn = QPushButton(tr("move_down"))
        for b in (self._btn_add, self._btn_del, self._btn_up, self._btn_dn):
            btn_row.addWidget(b)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)
        self._btn_up.clicked.connect(lambda: self._move(-1))
        self._btn_dn.clicked.connect(lambda: self._move(+1))

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)

    def _populate(self):
        self._list.setRowCount(len(self._forms))
        for i, form in enumerate(self._forms):
            item = QTableWidgetItem(form)
            self._list.setItem(i, 0, item)

    def _add(self):
        self._forms.append(tr("pf_new_form"))
        self._populate()
        self._list.editItem(self._list.item(len(self._forms) - 1, 0))

    def _del(self):
        r = self._list.currentRow()
        if 0 <= r < len(self._forms):
            self._forms.pop(r)
            self._populate()

    def _move(self, delta: int):
        r = self._list.currentRow()
        nr = r + delta
        if 0 <= r < len(self._forms) and 0 <= nr < len(self._forms):
            self._forms[r], self._forms[nr] = self._forms[nr], self._forms[r]
            self._populate()
            self._list.setCurrentCell(nr, 0)

    def get_forms(self) -> list[str]:
        for i in range(self._list.rowCount()):
            item = self._list.item(i, 0)
            if item and i < len(self._forms):
                self._forms[i] = item.text().strip()
        return [f for f in self._forms if f.strip()]


# ═══════════════════════════════════════════════════════════════════════════════
# Диалог форм конкретного слова
# ═══════════════════════════════════════════════════════════════════════════════
class WordFormsDialog(QDialog):
    def __init__(self, parent, storage, word_idx: int):
        super().__init__(parent)
        self._s = storage
        self._idx = word_idx
        self._word = storage.lang.words[word_idx]
        self._rules = []
        self.setWindowTitle(tr("par_forms_title"))
        self.setMinimumSize(650, 450)
        self._build()
        self._populate()

    def _build(self):
        root = QVBoxLayout(self)
        lang = get_lang()
        pos = self._s.lang.morphology.pos_by_id(self._word.pos_id)
        pos_name = pos.display(lang) if pos else self._word.pos_id
        info = QLabel(f"<b>{self._word.conword}</b>"
                      f"  <span style='color:gray'>({pos_name}) {self._word.localword}</span>")
        info.setStyleSheet("font-size:13px; margin-bottom:4px;")
        root.addWidget(info)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(4)
        hh = self._tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 140), (2, 120), (3, 140)]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._tbl.setColumnWidth(col, w)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.setHorizontalHeaderLabels([
            tr("par_col_name"), tr("par_col_auto"),
            tr("par_col_override"), tr("par_col_final"),
        ])
        root.addWidget(self._tbl)

        hint = QLabel(tr("par_override_hint"))
        hint.setStyleSheet("color:gray; font-size:10px;")
        root.addWidget(hint)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self._save_and_accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)
        self._tbl.itemChanged.connect(self._on_edit)

    def _populate(self):
        paradigm = next(
            (p for p in self._s.lang.paradigms if p.pos_id == self._word.pos_id), None)

        if not paradigm:
            pos = self._s.lang.morphology.pos_by_id(self._word.pos_id)
            pos_name = pos.display(get_lang()) if pos else self._word.pos_id
            self._tbl.setRowCount(1)
            msg = QTableWidgetItem(tr("par_no_paradigm").format(pos_name))
            msg.setForeground(Qt.GlobalColor.red)
            msg.setFlags(msg.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._tbl.setItem(0, 0, msg)
            return

        overrides = {}
        if isinstance(self._word.gram_values, dict):
            overrides = self._word.gram_values.get("_forms", {})

        self._rules = paradigm.rules
        self._tbl.setRowCount(len(self._rules))

        for i, rule in enumerate(self._rules):
            auto = AffixEngine.apply(
                self._word.conword,
                rule.affix_type,
                rule.affix_pattern
            )
            override = overrides.get(rule.form_name, "")
            final = override if override else auto

            for col, txt, editable, color in [
                (0, rule.form_name, False, None),
                (1, auto, False, Qt.GlobalColor.darkGray),
                (2, override, True, None),
                (3, final, False, Qt.GlobalColor.darkBlue if override else None),
            ]:
                item = QTableWidgetItem(txt)
                if not editable:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if color is not None:
                    item.setForeground(color)
                self._tbl.setItem(i, col, item)

    def _on_edit(self, item: QTableWidgetItem):
        if item.column() != 2:
            return
        row = item.row()
        override = item.text().strip()
        auto_item = self._tbl.item(row, 1)
        auto = auto_item.text() if auto_item else ""
        final = override if override else auto
        fi = self._tbl.item(row, 3)
        if fi:
            self._tbl.blockSignals(True)
            fi.setText(final)
            fi.setForeground(Qt.GlobalColor.darkBlue if override else Qt.GlobalColor.black)
            self._tbl.blockSignals(False)

    def _save_and_accept(self):
        overrides = {}
        for i, rule in enumerate(self._rules):
            item = self._tbl.item(i, 2)
            val = item.text().strip() if item else ""
            if val:
                overrides[rule.form_name] = val
        w = self._s.lang.words[self._idx]
        if not isinstance(w.gram_values, dict):
            w.gram_values = {}
        w.gram_values["_forms"] = overrides
        self._s.mark_dirty()
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Раздел: Парадигмы
# ═══════════════════════════════════════════════════════════════════════════════
class ParadigmsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Левая: список ЧР с кнопками редактирования форм ─────────────────
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 4, 0)
        self._lbl_pos = QLabel(tr("par_pos_lbl"))
        lv.addWidget(self._lbl_pos)

        self._pos_tbl = QTableWidget()
        self._pos_tbl.setColumnCount(3)
        self._pos_tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._pos_tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._pos_tbl.verticalHeader().setVisible(False)
        self._pos_tbl.setAlternatingRowColors(True)
        ph = self._pos_tbl.horizontalHeader()
        ph.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 40), (2, 32)]:
            ph.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._pos_tbl.setColumnWidth(col, w)
        lv.addWidget(self._pos_tbl)

        # ── Правая: редактор правил ─────────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(4, 0, 0, 0)

        # Заголовок с названием ЧР и кнопкой форм
        header = QHBoxLayout()
        self._pos_name_lbl = QLabel()
        self._pos_name_lbl.setStyleSheet("font-weight:bold; font-size:13px;")
        header.addWidget(self._pos_name_lbl)
        header.addStretch()
        self._btn_edit_forms = QPushButton(tr("pf_edit_forms_btn"))
        self._btn_edit_forms.setFixedHeight(26)
        self._btn_edit_forms.clicked.connect(self._edit_forms)
        header.addWidget(self._btn_edit_forms)
        rv.addLayout(header)

        # Таблица правил
        self._rules_tbl = QTableWidget()
        self._rules_tbl.setColumnCount(5)
        self._rules_tbl.verticalHeader().setVisible(False)
        self._rules_tbl.setAlternatingRowColors(True)
        rh = self._rules_tbl.horizontalHeader()
        rh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1, 120), (2, 110), (3, 100), (4, 120)]:
            rh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self._rules_tbl.setColumnWidth(col, w)
        rv.addWidget(self._rules_tbl)

        # Тестовая панель
        test_box = QGroupBox(tr("pf_test_group"))
        tv = QVBoxLayout(test_box)
        test_row = QHBoxLayout()
        self._test_input = QLineEdit()
        self._test_input.setPlaceholderText(tr("par_test_ph"))
        self._btn_test = QPushButton(tr("par_test_btn"))
        self._btn_test.clicked.connect(self._run_test)
        test_row.addWidget(self._test_input, 1)
        test_row.addWidget(self._btn_test)
        tv.addLayout(test_row)
        self._test_result = QLabel()
        self._test_result.setStyleSheet("font-family: monospace; padding: 4px;")
        self._test_result.setWordWrap(True)
        tv.addWidget(self._test_result)
        rv.addWidget(test_box)

        # CRUD кнопки
        btn_row = QHBoxLayout()
        self._btn_add = QPushButton(tr("par_add_rule"))
        self._btn_del = QPushButton(tr("delete"))
        self._btn_up = QPushButton(tr("move_up"))
        self._btn_dn = QPushButton(tr("move_down"))
        for b in (self._btn_add, self._btn_del, self._btn_up, self._btn_dn):
            b.setFixedHeight(26)
            btn_row.addWidget(b)
        btn_row.addStretch()
        rv.addLayout(btn_row)

        self._btn_add.clicked.connect(self._add_rule)
        self._btn_del.clicked.connect(self._del_rule)
        self._btn_up.clicked.connect(lambda: self._move_rule(-1))
        self._btn_dn.clicked.connect(lambda: self._move_rule(+1))

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([220, 580])
        root.addWidget(splitter)

        self._current_pos_id = ""
        self._updating = False
        self._form_lists: dict[str, list[str]] = {}

        self._pos_tbl.currentCellChanged.connect(self._on_pos_select)
        self._rules_tbl.itemChanged.connect(self._on_rule_text_edited)
        self._update_headers()

    # ── публичные методы ────────────────────────────────────────────────────
    def load(self):
        self._load_form_lists()
        self._refresh_pos_list()

    def save(self):
        self._flush_rules()
        self._save_form_lists()

    def retranslate(self):
        self._lbl_pos.setText(tr("par_pos_lbl"))
        self._btn_edit_forms.setText(tr("pf_edit_forms_btn"))
        self._btn_add.setText(tr("par_add_rule"))
        self._btn_del.setText(tr("delete"))
        self._btn_up.setText(tr("move_up"))
        self._btn_dn.setText(tr("move_down"))
        self._btn_test.setText(tr("par_test_btn"))
        self._test_input.setPlaceholderText(tr("par_test_ph"))
        self._update_headers()
        self._refresh_pos_list()

    def _update_headers(self):
        self._pos_tbl.setHorizontalHeaderLabels([
            tr("par_col_pos"), tr("par_col_count"), "",
        ])
        self._rules_tbl.setHorizontalHeaderLabels([
            tr("par_col_name"), tr("pf_col_pattern"),
            tr("par_col_type"), tr("pf_col_example_in"),
            tr("pf_col_example_out"),
        ])

    # ── Работа со списками форм ─────────────────────────────────────────────
    def _load_form_lists(self):
        extra = self._s.lang.extra
        saved = extra.get("paradigm_forms", {})
        self._form_lists = {}

        for pos in self._s.lang.morphology.parts_of_speech:
            if pos.id in saved:
                self._form_lists[pos.id] = saved[pos.id]
            elif pos.id in _DEFAULT_FORMS:
                self._form_lists[pos.id] = _DEFAULT_FORMS[pos.id].copy()
            else:
                self._form_lists[pos.id] = [tr("pf_new_form")]

    def _save_form_lists(self):
        if not hasattr(self._s.lang, "extra") or not isinstance(self._s.lang.extra, dict):
            self._s.lang.extra = {}
        self._s.lang.extra["paradigm_forms"] = self._form_lists
        self._s.mark_dirty()

    def _edit_forms(self):
        if not self._current_pos_id:
            return
        pos = self._s.lang.morphology.pos_by_id(self._current_pos_id)
        pos_name = pos.display(get_lang()) if pos else self._current_pos_id
        forms = self._form_lists.get(self._current_pos_id, [])
        dlg = FormListDialog(self, forms, pos_name)
        if dlg.exec():
            self._form_lists[self._current_pos_id] = dlg.get_forms()
            self._save_form_lists()
            self._load_rules(self._current_pos_id)

    # ── список ЧР ───────────────────────────────────────────────────────────
    def _refresh_pos_list(self):
        lang = get_lang()
        pos_list = self._s.lang.morphology.parts_of_speech
        self._pos_tbl.setRowCount(len(pos_list))
        for i, pos in enumerate(pos_list):
            p = self._paradigm_for(pos.id)
            count = len(p.rules) if p else 0

            ni = QTableWidgetItem(pos.display(lang))
            ni.setData(Qt.ItemDataRole.UserRole, pos.id)

            ci = QTableWidgetItem(str(count))
            ci.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton("✎")
            edit_btn.setFixedSize(24, 24)
            edit_btn.setToolTip(tr("pf_edit_forms_btn"))
            edit_btn.clicked.connect(lambda checked, pid=pos.id: self._edit_forms_for(pid))

            self._pos_tbl.setItem(i, 0, ni)
            self._pos_tbl.setItem(i, 1, ci)
            self._pos_tbl.setCellWidget(i, 2, edit_btn)

    def _edit_forms_for(self, pos_id: str):
        self._current_pos_id = pos_id
        self._edit_forms()

    def _on_pos_select(self, row: int, *_):
        self._flush_rules()
        item = self._pos_tbl.item(row, 0)
        if not item:
            return
        pos_id = item.data(Qt.ItemDataRole.UserRole)
        self._current_pos_id = pos_id
        pos = self._s.lang.morphology.pos_by_id(pos_id)
        self._pos_name_lbl.setText(pos.display(get_lang()) if pos else pos_id)
        self._load_rules(pos_id)

    # ── правила ─────────────────────────────────────────────────────────────
    def _paradigm_for(self, pos_id: str) -> Paradigm | None:
        return next((p for p in self._s.lang.paradigms if p.pos_id == pos_id), None)

    def _ensure_paradigm(self, pos_id: str) -> Paradigm:
        p = self._paradigm_for(pos_id)
        if not p:
            p = Paradigm(pos_id=pos_id)
            self._s.lang.paradigms.append(p)
        return p

    def _load_rules(self, pos_id: str):
        self._updating = True
        p = self._paradigm_for(pos_id)
        rules = p.rules if p else []
        self._rules_tbl.setRowCount(len(rules))
        for i, rule in enumerate(rules):
            self._fill_row(i, rule)
        self._updating = False

    def _get_available_affix_types(self):
        """Возвращает только те типы аффиксов, которые отмечены в настройках."""
        mt = self._s.lang.morphology.morpheme_types
        available = []

        # Словарь соответствия: тип аффикса -> поле в MorphemeTypes
        type_to_field = {
            "prefix":    mt.has_prefixes,
            "suffix":    mt.has_suffixes,
            "postfix":   mt.has_postfixes,
            "infix":     mt.has_infixes,
            "circumfix": mt.has_circumfixes,
            "interfix":  mt.has_interfixes,
            "transfix":  mt.has_transfixes,
            "duplifix":  mt.has_duplifixes,
            "simulfix":  mt.has_simulfixes,
            "disfix":    mt.has_disfixes,
            "suprafix":  mt.has_suprafixes,
        }

        for lk, atype, example, desc in _ALL_AFFIX_TYPES:
            # Проверяем, отмечен ли этот тип в настройках
            if atype in type_to_field:
                if type_to_field[atype]:
                    available.append((lk, atype, example, desc))
            else:
                # Если типа нет в словаре (на всякий случай), добавляем
                available.append((lk, atype, example, desc))

        # Если ни один тип не отмечен, добавляем хотя бы суффикс (чтобы не было пусто)
        if not available:
            for lk, atype, example, desc in _ALL_AFFIX_TYPES:
                if atype == "suffix":
                    available.append((lk, atype, example, desc))
                    break

        return available

    def _fill_row(self, i: int, rule: AffixRule):
        forms = self._form_lists.get(self._current_pos_id, [tr("pf_new_form")])

        # Столбец 0: выпадающий список форм
        combo_form = QComboBox()
        combo_form.addItems(forms)
        idx = combo_form.findText(rule.form_name)
        if idx >= 0:
            combo_form.setCurrentIndex(idx)
        elif rule.form_name:
            combo_form.addItem(rule.form_name)
            combo_form.setCurrentIndex(combo_form.count() - 1)
        combo_form.currentTextChanged.connect(lambda txt, r=i: self._on_form_changed(r, txt))
        self._rules_tbl.setCellWidget(i, 0, combo_form)

        # Столбец 1: схема аффикса
        item_pattern = QTableWidgetItem(rule.affix_pattern)
        self._rules_tbl.setItem(i, 1, item_pattern)

        # Столбец 2: тип аффикса (только доступные)
        combo_type = QComboBox()
        for lk, atype, _, _ in self._get_available_affix_types():
            combo_type.addItem(tr(lk), atype)
        _set_combo(combo_type, rule.affix_type)
        combo_type.currentIndexChanged.connect(lambda _, r=i: self._on_type_changed(r))
        self._rules_tbl.setCellWidget(i, 2, combo_type)

        self._update_pattern_tooltip(i, rule.affix_type)

        # Столбец 3: пример входа
        item_ex_in = QTableWidgetItem(rule.example_input)
        self._rules_tbl.setItem(i, 3, item_ex_in)

        # Столбец 4: пример выхода
        output = AffixEngine.apply(rule.example_input, rule.affix_type, rule.affix_pattern)
        item_ex_out = QTableWidgetItem(output)
        item_ex_out.setFlags(item_ex_out.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item_ex_out.setForeground(Qt.GlobalColor.darkGreen)
        self._rules_tbl.setItem(i, 4, item_ex_out)

    def _update_pattern_tooltip(self, row: int, affix_type: str):
        item = self._rules_tbl.item(row, 1)
        if item:
            for _, atype, example, desc in _ALL_AFFIX_TYPES:
                if atype == affix_type:
                    item.setToolTip(f"{desc}")
                    break

    def _on_form_changed(self, row: int, text: str):
        if self._updating:
            return
        p = self._paradigm_for(self._current_pos_id)
        if p and row < len(p.rules):
            p.rules[row].form_name = text
            self._s.mark_dirty()

    def _on_type_changed(self, row: int):
        if self._updating:
            return
        p = self._paradigm_for(self._current_pos_id)
        if not p or row >= len(p.rules):
            return
        combo = self._rules_tbl.cellWidget(row, 2)
        if combo:
            new_type = combo.currentData()
            p.rules[row].affix_type = new_type
            self._update_pattern_tooltip(row, new_type)
            self._recalc_example(row)
            self._s.mark_dirty()

    def _recalc_example(self, row: int):
        p = self._paradigm_for(self._current_pos_id)
        if not p or row >= len(p.rules):
            return
        rule = p.rules[row]
        output = AffixEngine.apply(rule.example_input, rule.affix_type, rule.affix_pattern)
        item_out = self._rules_tbl.item(row, 4)
        if item_out:
            self._updating = True
            item_out.setText(output)
            self._updating = False

    def _on_rule_text_edited(self, item: QTableWidgetItem):
        if self._updating or not self._current_pos_id:
            return
        p = self._paradigm_for(self._current_pos_id)
        if not p or item.row() >= len(p.rules):
            return
        rule = p.rules[item.row()]
        col = item.column()

        if col == 1:
            rule.affix_pattern = item.text()
            self._update_pattern_tooltip(item.row(), rule.affix_type)
            self._recalc_example(item.row())
        elif col == 3:
            rule.example_input = item.text()
            self._recalc_example(item.row())

        self._s.mark_dirty()

    def _flush_rules(self):
        if not self._current_pos_id:
            return
        p = self._paradigm_for(self._current_pos_id)
        if not p:
            return
        for i, rule in enumerate(p.rules):
            combo_form = self._rules_tbl.cellWidget(i, 0)
            if combo_form:
                rule.form_name = combo_form.currentText()
            item = self._rules_tbl.item(i, 1)
            if item:
                rule.affix_pattern = item.text()
            combo_type = self._rules_tbl.cellWidget(i, 2)
            if combo_type:
                rule.affix_type = combo_type.currentData()
            item = self._rules_tbl.item(i, 3)
            if item:
                rule.example_input = item.text()

    # ── CRUD ─────────────────────────────────────────────────────────────────
    def _add_rule(self):
        if not self._current_pos_id:
            return
        p = self._ensure_paradigm(self._current_pos_id)
        forms = self._form_lists.get(self._current_pos_id, [tr("pf_new_form")])
        first_form = forms[0] if forms else tr("pf_new_form")
        p.rules.append(AffixRule(
            form_name=first_form,
            affix_type="suffix",
            affix_pattern="-a",
            example_input="kor",
        ))
        self._load_rules(self._current_pos_id)
        self._rules_tbl.selectRow(len(p.rules) - 1)
        self._refresh_pos_list()
        self._s.mark_dirty()

    def _del_rule(self):
        row = self._rules_tbl.currentRow()
        if not self._current_pos_id or row < 0:
            return
        p = self._paradigm_for(self._current_pos_id)
        if p and 0 <= row < len(p.rules):
            p.rules.pop(row)
            self._load_rules(self._current_pos_id)
            self._refresh_pos_list()
            self._s.mark_dirty()

    def _move_rule(self, delta: int):
        row = self._rules_tbl.currentRow()
        if not self._current_pos_id or row < 0:
            return
        p = self._paradigm_for(self._current_pos_id)
        if not p:
            return
        nr = row + delta
        if 0 <= nr < len(p.rules):
            p.rules[row], p.rules[nr] = p.rules[nr], p.rules[row]
            self._load_rules(self._current_pos_id)
            self._rules_tbl.selectRow(nr)
            self._s.mark_dirty()

    # ── тест ─────────────────────────────────────────────────────────────────
    def _run_test(self):
        if not self._current_pos_id:
            return
        root_text = self._test_input.text().strip()
        if not root_text:
            return
        p = self._paradigm_for(self._current_pos_id)
        if not p or not p.rules:
            QMessageBox.information(self, tr("par_test_title"), tr("par_no_rules"))
            return

        lines = []
        for r in p.rules:
            result = AffixEngine.apply(root_text, r.affix_type, r.affix_pattern)
            lines.append(f"{r.form_name}: {result}")

        self._test_result.setText("\n".join(lines))
