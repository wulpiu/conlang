from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,  # ← Добавлен QGridLayout
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import get_lang, tr
from core.model import FunctionWord, GramCategory, GramCategoryGroup, PartOfSpeech


def _set_combo(combo, value):
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def _retranslate_combo(combo, items):
    cur = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    for lk, v in items:
        combo.addItem(tr(lk), v)
    idx = combo.findData(cur)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    combo.blockSignals(False)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Тип языка (расширенный)
# ═══════════════════════════════════════════════════════════════════════════
class LangTypeSection(BaseSection):
    _TYPES = [
        ("lt_analytic", "analytic"),
        ("lt_agglutinative", "agglutinative"),
        ("lt_fusional", "fusional"),
        ("lt_polysynthetic", "polysynthetic"),
        ("lt_isolating", "isolating"),
    ]

    _STRATEGIES = [
        ("lt_use_affixes", "use_affixes", "Использовать аффиксы"),
        ("lt_use_particles", "use_particles", "Использовать служебные слова"),
        ("lt_use_fusion", "use_fusion", "Использовать флексию (слияние)"),
        ("lt_use_incorporation", "use_incorporation", "Использовать инкорпорацию"),
    ]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self._type = QComboBox()
        for lk, v in self._TYPES:
            self._type.addItem(tr(lk), v)
        self._type.currentIndexChanged.connect(self._on_type_changed)

        self._l_type = QLabel()
        form.addRow(self._l_type, self._type)

        hint = QLabel(tr("lt_type_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        hint.setWordWrap(True)
        form.addRow("", hint)

        root.addLayout(form)

        strategies_group = QGroupBox(tr("lt_strategies"))
        strategies_layout = QVBoxLayout(strategies_group)

        strategies_hint = QLabel(tr("lt_strategies_hint"))
        strategies_hint.setStyleSheet("color: #666; font-style: italic; margin-bottom: 8px;")
        strategies_hint.setWordWrap(True)
        strategies_layout.addWidget(strategies_hint)

        self._strategy_checkboxes = {}
        strategy_form = QFormLayout()

        for i18n_key, field_name, _ in self._STRATEGIES:
            cb = QCheckBox()
            cb.toggled.connect(self._mark)
            self._strategy_checkboxes[field_name] = cb
            strategy_form.addRow(tr(i18n_key) + ":", cb)

        strategies_layout.addLayout(strategy_form)
        root.addWidget(strategies_group)

        defaults_group = QGroupBox(tr("lt_defaults"))
        defaults_layout = QHBoxLayout(defaults_group)

        self._btn_apply_recommended = QPushButton(tr("lt_apply_recommended"))
        self._btn_apply_recommended.clicked.connect(self._apply_recommended)
        defaults_layout.addWidget(self._btn_apply_recommended)
        defaults_layout.addStretch()

        root.addWidget(defaults_group)

        notes_group = QGroupBox(tr("lt_notes"))
        notes_layout = QVBoxLayout(notes_group)

        self._notes = QTextEdit()
        self._notes.setFixedHeight(120)
        self._notes.setPlaceholderText(tr("lt_notes_ph"))
        self._notes.textChanged.connect(self._mark)
        notes_layout.addWidget(self._notes)

        self._l_notes = QLabel(tr("lt_notes_label"))
        root.addWidget(self._l_notes)
        root.addWidget(self._notes)

        root.addStretch()
        self._relabel()

    def _relabel(self):
        self._l_type.setText(tr("lt_primary"))
        self._l_notes.setText(tr("lt_notes_label"))
        self._btn_apply_recommended.setText(tr("lt_apply_recommended"))

    def _on_type_changed(self):
        self._mark()

    def _apply_recommended(self):
        current_type = self._type.currentData()

        recommendations = {
            "analytic": {"use_affixes": False, "use_particles": True, "use_fusion": False, "use_incorporation": False},
            "agglutinative": {"use_affixes": True, "use_particles": False, "use_fusion": False, "use_incorporation": False},
            "fusional": {"use_affixes": True, "use_particles": False, "use_fusion": True, "use_incorporation": False},
            "polysynthetic": {"use_affixes": True, "use_particles": False, "use_fusion": True, "use_incorporation": True},
            "isolating": {"use_affixes": False, "use_particles": True, "use_fusion": False, "use_incorporation": False},
        }

        rec = recommendations.get(current_type, {})
        for field_name, cb in self._strategy_checkboxes.items():
            if field_name in rec:
                cb.setChecked(rec[field_name])

        self._mark()

    def load(self):
        lt = self._s.lang.morphology.lang_type
        _set_combo(self._type, lt.primary)

        extra = self._s.lang.extra.get("lang_type_strategies", {})
        for field_name, cb in self._strategy_checkboxes.items():
            cb.setChecked(extra.get(field_name, False))

        self._notes.setPlainText(lt.notes)

    def save(self):
        lt = self._s.lang.morphology.lang_type
        lt.primary = self._type.currentData()
        lt.notes = self._notes.toPlainText()

        strategies = {field_name: cb.isChecked() for field_name, cb in self._strategy_checkboxes.items()}
        if not hasattr(self._s.lang, "extra") or not isinstance(self._s.lang.extra, dict):
            self._s.lang.extra = {}
        self._s.lang.extra["lang_type_strategies"] = strategies

    def retranslate(self):
        self._relabel()
        _retranslate_combo(self._type, self._TYPES)
        self._notes.setPlaceholderText(tr("lt_notes_ph"))

    def _mark(self):
        self._s.mark_strategies_changed()


# ═══════════════════════════════════════════════════════════════════════════
# Виджет для вкладки "Служебные слова"
# ═══════════════════════════════════════════════════════════════════════════

# Типы служебных слов для выпадающего списка
FUNCTION_WORD_TYPES = [
    ("fw_type_preposition", "preposition"),
    ("fw_type_postposition", "postposition"),
    ("fw_type_particle", "particle"),
    ("fw_type_article", "article"),
    ("fw_type_auxiliary", "auxiliary"),
    ("fw_type_conjunction", "conjunction"),
    ("fw_type_classifier", "classifier"),
    ("fw_type_copula", "copula"),
]


class FunctionWordsWidget(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._s = storage
        self._updating = False
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        hint = QLabel(tr("fw_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; margin-bottom: 8px;")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # Таблица: Смысловая нагрузка | Форма | Применяется к | Тип | Примечания
        self._tbl = QTableWidget()
        self._tbl.setColumnCount(5)
        self._tbl.setHorizontalHeaderLabels([
            tr("fw_col_function"),      # Смысловая нагрузка
            tr("fw_col_form"),          # Форма
            tr("fw_col_applies_to"),    # Применяется к (грам. категория)
            tr("fw_col_type"),          # Тип служебного слова
            tr("fw_col_notes"),         # Примечания
        ])
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        hh = self._tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(0, 200)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(1, 120)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(2, 180)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(3, 120)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        root.addWidget(self._tbl)

        # Кнопки
        btn_row = QHBoxLayout()
        self._btn_add = QPushButton(tr("add"))
        self._btn_del = QPushButton(tr("delete"))
        self._btn_up = QPushButton(tr("move_up"))
        self._btn_dn = QPushButton(tr("move_down"))

        for b in (self._btn_add, self._btn_del, self._btn_up, self._btn_dn):
            b.setFixedHeight(28)
            btn_row.addWidget(b)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)
        self._btn_up.clicked.connect(lambda: self._move(-1))
        self._btn_dn.clicked.connect(lambda: self._move(1))

    def _get_all_functions(self) -> list:
        """Возвращает список всех уникальных смысловых нагрузок."""
        from core.linguistic_data import get_all_functions, get_function_display
        lang = get_lang()
        return [(fid, get_function_display(fid, lang)) for fid in get_all_functions()]

    def _get_function_category(self, function_id: str) -> str:
        """Возвращает ID грамматической категории для данной смысловой нагрузки."""
        from core.linguistic_data import get_function_category
        return get_function_category(function_id)

    def _get_category_values(self, category_id: str) -> list:
        """
        Возвращает список значений для указанной грамматической категории.
        Это значения из CATEGORY_VALUES, а не из настроек пользователя.
        """
        from core.linguistic_data import CATEGORY_VALUES, get_value_display, get_value_id
        lang = get_lang()
        values = []
        for v in CATEGORY_VALUES.get(category_id, []):
            value_id = get_value_id(v)
            display = get_value_display(v, lang)
            values.append((value_id, display))
        return values

    def _populate_table(self):
        """Заполняет таблицу данными."""
        self._updating = True
        self._tbl.setRowCount(len(self._s.lang.function_words))

        for i, fw in enumerate(self._s.lang.function_words):
            self._fill_row(i, fw)

        self._updating = False

    def _fill_row(self, row: int, fw: FunctionWord):
        """Заполняет одну строку таблицы."""

        # Колонка 0: Смысловая нагрузка (выпадающий список ВСЕХ функций)
        function_combo = QComboBox()
        for fid, display in self._get_all_functions():
            function_combo.addItem(display, fid)
        idx = function_combo.findData(fw.function)
        if idx >= 0:
            function_combo.setCurrentIndex(idx)
        elif function_combo.count() > 0:
            function_combo.setCurrentIndex(0)
            fw.function = function_combo.currentData()
        function_combo.currentIndexChanged.connect(lambda: self._on_function_changed(row))
        self._tbl.setCellWidget(row, 0, function_combo)

        # Колонка 1: Форма (текстовое поле)
        form_item = QTableWidgetItem(fw.form)
        self._tbl.setItem(row, 1, form_item)

        # Колонка 2: Применяется к (выпадающий список значений категории)
        self._update_applies_to_combo(row, fw.function, fw.applies_to_value)

        # Колонка 3: Тип служебного слова (выпадающий список)
        type_combo = QComboBox()
        for i18n_key, type_id in FUNCTION_WORD_TYPES:
            type_combo.addItem(tr(i18n_key), type_id)
        idx = type_combo.findData(fw.word_type)
        if idx >= 0:
            type_combo.setCurrentIndex(idx)
        type_combo.currentIndexChanged.connect(lambda: self._save_row(row))
        self._tbl.setCellWidget(row, 3, type_combo)

        # Колонка 4: Примечания (текстовое поле)
        notes_item = QTableWidgetItem(fw.notes)
        self._tbl.setItem(row, 4, notes_item)

    def _update_applies_to_combo(self, row: int, function_id: str, current_value: str = ""):
        """Обновляет выпадающий список «Применяется к» для указанной строки."""
        combo = QComboBox()
        combo.addItem("—", "")

        if function_id:
            category_id = self._get_function_category(function_id)
            if category_id:
                values = self._get_category_values(category_id)
                for value_id, display in values:
                    combo.addItem(display, value_id)

        idx = combo.findData(current_value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

        combo.currentIndexChanged.connect(lambda: self._save_row(row))

        # Удаляем старый виджет если есть
        old_widget = self._tbl.cellWidget(row, 2)
        if old_widget:
            old_widget.deleteLater()

        self._tbl.setCellWidget(row, 2, combo)

    def _on_function_changed(self, row: int):
        """Вызывается при изменении смысловой нагрузки."""
        if self._updating:
            return

        combo = self._tbl.cellWidget(row, 0)
        if combo:
            function_id = combo.currentData()
            self._s.lang.function_words[row].function = function_id
            # Обновляем список "Применяется к"
            self._update_applies_to_combo(row, function_id, "")
            self._save_row(row)
            self._s.mark_dirty()

    def _save_row(self, row: int):
        """Сохраняет данные из строки в модель."""
        if self._updating or row >= len(self._s.lang.function_words):
            return

        fw = self._s.lang.function_words[row]

        # Смысловая нагрузка
        combo = self._tbl.cellWidget(row, 0)
        if combo:
            fw.function = combo.currentData()

        # Форма
        item = self._tbl.item(row, 1)
        if item:
            fw.form = item.text().strip()

        # Применяется к (значение категории)
        combo = self._tbl.cellWidget(row, 2)
        if combo:
            fw.applies_to_value = combo.currentData() or ""
            if fw.function:
                fw.applies_to_category = self._get_function_category(fw.function)

        # Тип служебного слова
        combo = self._tbl.cellWidget(row, 3)
        if combo:
            fw.word_type = combo.currentData() or ""

        # Примечания
        item = self._tbl.item(row, 4)
        if item:
            fw.notes = item.text().strip()

        self._s.mark_dirty()

    def _add(self):
        fw = FunctionWord(
            name="",
            form="",
            function="locative",
            applies_to_category="case",
            applies_to_value="",
            word_type="preposition",
            position="before",
            notes=""
        )
        self._s.lang.function_words.append(fw)
        self._populate_table()
        self._tbl.selectRow(len(self._s.lang.function_words) - 1)
        self._s.mark_dirty()

    def _del(self):
        row = self._tbl.currentRow()
        if 0 <= row < len(self._s.lang.function_words):
            self._s.lang.function_words.pop(row)
            self._populate_table()
            self._s.mark_dirty()

    def _move(self, delta: int):
        row = self._tbl.currentRow()
        new_row = row + delta
        if 0 <= row < len(self._s.lang.function_words) and 0 <= new_row < len(self._s.lang.function_words):
            self._s.lang.function_words[row], self._s.lang.function_words[new_row] = \
                self._s.lang.function_words[new_row], self._s.lang.function_words[row]
            self._populate_table()
            self._tbl.selectRow(new_row)
            self._s.mark_dirty()

    def load(self):
        if not hasattr(self._s.lang, 'function_words'):
            self._s.lang.function_words = []
        # Обратная совместимость: добавляем поле word_type если его нет
        for fw in self._s.lang.function_words:
            if not hasattr(fw, 'word_type'):
                fw.word_type = ""
        self._populate_table()

    def save(self):
        for row in range(self._tbl.rowCount()):
            self._save_row(row)

    def retranslate(self):
        self._tbl.setHorizontalHeaderLabels([
            tr("fw_col_function"),
            tr("fw_col_form"),
            tr("fw_col_applies_to"),
            tr("fw_col_type"),
            tr("fw_col_notes"),
        ])
        self._btn_add.setText(tr("add"))
        self._btn_del.setText(tr("delete"))
        self._btn_up.setText(tr("move_up"))
        self._btn_dn.setText(tr("move_down"))
        self._populate_table()


# ═══════════════════════════════════════════════════════════════════════════
# 2. Типы морфем (с вкладками)
# ═══════════════════════════════════════════════════════════════════════════
class MorphemeTypesSection(BaseSection):
    _REDUPL = [("mt_redupl_none","none"), ("mt_redupl_full","full"),
               ("mt_redupl_part","partial")]

    # Добавлено поле для формулы (пример)
    _BOOL_FIELDS = [
        ("mt_prefixes",    "has_prefixes",     "пере-", "префикс-корень"),
        ("mt_suffixes",    "has_suffixes",     "-чик",  "корень-суффикс"),
        ("mt_postfixes",   "has_postfixes",    "-ся",   "корень-постфикс"),
        ("mt_infixes",     "has_infixes",      "2-um",  "ко<инфикс>рень"),
        ("mt_circumfixes", "has_circumfixes",  "ge- -t","циркум-корень-фикс"),
        ("mt_interfixes",  "has_interfixes",   "-о-",   "корень-интерфикс-корень"),
        ("mt_transfixes",  "has_transfixes",   "1-a-1-i-1", "прерывистый аффикс"),
        ("mt_duplifixes",  "has_duplifixes",   "2-~",   "удвоение части корня"),
        ("mt_simulfixes",  "has_simulfixes",   "a→e",   "замена сегмента"),
        ("mt_disfixes",    "has_disfixes",     "2-",    "удаление части корня"),
        ("mt_suprafixes",  "has_suprafixes",   "1→2",   "смена ударения"),
        ("mt_clitics",     "has_clitics",      "-ка",   "клитика"),
    ]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        tabs = QTabWidget()

        # ── Вкладка «Аффиксы» ────────────────────────────────────────────────
        affix_widget = QWidget()
        affix_layout = QVBoxLayout(affix_widget)

        hint = QLabel(tr("mt_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; margin-bottom: 8px;")
        hint.setWordWrap(True)
        affix_layout.addWidget(hint)

        affix_group = QGroupBox(tr("mt_group_affixes"))
        affix_group_layout = QVBoxLayout(affix_group)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_widget = QWidget()

        # Используем QGridLayout вместо QFormLayout для трёх колонок
        grid = QGridLayout(scroll_widget)
        grid.setSpacing(6)
        grid.setContentsMargins(8, 8, 8, 8)

        # Заголовки колонок
        grid.addWidget(QLabel(tr("mt_col_enabled")), 0, 0)
        grid.addWidget(QLabel(tr("mt_col_affix_type")), 0, 1)
        grid.addWidget(QLabel(tr("mt_col_formula")), 0, 2)

        self._cbs: dict[str, QCheckBox] = {}
        self._cb_labels: dict[str, QLabel] = {}
        self._formula_labels: dict[str, QLabel] = {}

        for i, (lk, field, formula, desc) in enumerate(self._BOOL_FIELDS, start=1):
            cb = QCheckBox()
            lbl = QLabel(tr(lk))
            lbl.setToolTip(f"{tr(lk)}\n{desc}\n{tr('mt_example')}: {formula}")

            formula_lbl = QLabel(formula)
            formula_lbl.setStyleSheet("font-family: monospace; color: #1a1a8c;")
            formula_lbl.setToolTip(f"{desc}\n{tr('mt_example')}: {formula}")

            self._cbs[field] = cb
            self._cb_labels[lk] = lbl
            self._formula_labels[lk] = formula_lbl

            grid.addWidget(cb, i, 0)
            grid.addWidget(lbl, i, 1)
            grid.addWidget(formula_lbl, i, 2)

            cb.toggled.connect(self._mark)

        # Растягиваем колонки
        grid.setColumnStretch(0, 0)  # чекбокс — фиксированная ширина
        grid.setColumnStretch(1, 1)  # название — растягивается
        grid.setColumnStretch(2, 0)  # формула — фиксированная ширина

        scroll.setWidget(scroll_widget)
        affix_group_layout.addWidget(scroll)
        affix_layout.addWidget(affix_group)

        # Редупликация
        redupl_group = QGroupBox(tr("mt_group_redupl"))
        redupl_layout = QFormLayout(redupl_group)
        redupl_layout.setSpacing(6)

        self._redupl = QComboBox()
        for lk, v in self._REDUPL:
            self._redupl.addItem(tr(lk), v)
        self._l_redupl = QLabel()
        redupl_layout.addRow(self._l_redupl, self._redupl)
        affix_layout.addWidget(redupl_group)

        # Примечания
        notes_group = QGroupBox(tr("mt_notes"))
        notes_layout = QVBoxLayout(notes_group)
        self._notes = QTextEdit()
        self._notes.setFixedHeight(80)
        self._notes.setPlaceholderText(tr("mt_notes_ph"))
        notes_layout.addWidget(self._notes)
        affix_layout.addWidget(notes_group)

        affix_layout.addStretch()

        tabs.addTab(affix_widget, tr("mt_tab_affixes"))

        # ── Вкладка «Служебные слова» ─────────────────────────────────────────
        self._function_words_widget = FunctionWordsWidget(self._s)
        tabs.addTab(self._function_words_widget, tr("mt_tab_function_words"))

        root.addWidget(tabs)

        self._redupl.currentIndexChanged.connect(self._mark)
        self._notes.textChanged.connect(self._mark)
        self._relabel()

    def _relabel(self):
        for lk, field, formula, desc in self._BOOL_FIELDS:
            if lk in self._cb_labels:
                self._cb_labels[lk].setText(tr(lk))
                self._cb_labels[lk].setToolTip(f"{tr(lk)}\n{desc}\n{tr('mt_example')}: {formula}")
            if lk in self._formula_labels:
                self._formula_labels[lk].setText(formula)
                self._formula_labels[lk].setToolTip(f"{desc}\n{tr('mt_example')}: {formula}")
        self._l_redupl.setText(tr("mt_redupl"))
        self._redupl.setToolTip(tr("mt_redupl_hint"))

    def load(self):
        mt = self._s.lang.morphology.morpheme_types
        for _, field, _, _ in self._BOOL_FIELDS:
            if field in self._cbs:
                self._cbs[field].setChecked(getattr(mt, field, False))
        _set_combo(self._redupl, mt.reduplication)
        self._notes.setPlainText(mt.notes)
        self._function_words_widget.load()

    def save(self):
        mt = self._s.lang.morphology.morpheme_types
        for _, field, _, _ in self._BOOL_FIELDS:
            if field in self._cbs:
                setattr(mt, field, self._cbs[field].isChecked())
        mt.reduplication = self._redupl.currentData()
        mt.notes = self._notes.toPlainText()
        self._function_words_widget.save()

    def retranslate(self):
        self._relabel()
        _retranslate_combo(self._redupl, self._REDUPL)
        self._notes.setPlaceholderText(tr("mt_notes_ph"))
        self._function_words_widget.retranslate()

    def _mark(self):
        self._s.mark_morpheme_types_changed()

# ═══════════════════════════════════════════════════════════════════════════
# 3. Части речи (старая, оставлена для обратной совместимости)
# ═══════════════════════════════════════════════════════════════════════════
_POS_DEFAULTS = [
    ("noun",        "Существительное", "Noun",        "content"),
    ("pronoun",     "Местоимение",     "Pronoun",     "content"),
    ("verb",        "Глагол",          "Verb",        "content"),
    ("adjective",   "Прилагательное",  "Adjective",   "content"),
    ("numeral",     "Числительное",    "Numeral",     "content"),
    ("adverb",      "Наречие",         "Adverb",      "content"),
    ("gerund",      "Герундий",        "Gerund",      "content"),
    ("participle",  "Причастие",       "Participle",  "content"),
    ("gerundive",   "Деепричастие",    "Gerundive",   "content"),
    ("adposition",  "Адпозиция",       "Adposition",  "function"),
    ("conjunction", "Союз",            "Conjunction", "function"),
    ("particle",    "Частица",         "Particle",    "function"),
    ("interjection","Междометие",      "Interjection","function"),
]


class POSSection(BaseSection):
    _CLASS = [("pos_class_content","content"), ("pos_class_function","function")]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 4, 0)
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_select)
        lv.addWidget(self._list)

        brow = QHBoxLayout()
        self._btn_add = QPushButton("+")
        self._btn_add.setFixedWidth(32)
        self._btn_del = QPushButton("−")
        self._btn_del.setFixedWidth(32)
        self._btn_def = QPushButton("↺")
        self._btn_def.setFixedWidth(32)
        self._btn_def.setToolTip(tr("pos_load_defaults"))
        for b in (self._btn_add, self._btn_del, self._btn_def):
            brow.addWidget(b)
        brow.addStretch()
        lv.addLayout(brow)

        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)
        self._btn_def.clicked.connect(self._load_defaults)

        right = QWidget()
        rv = QFormLayout(right)
        rv.setContentsMargins(4, 0, 0, 0)
        self._f_name_ru = QLineEdit()
        self._f_name_en = QLineEdit()
        self._f_id      = QLineEdit()
        self._f_class   = QComboBox()
        for lk, v in self._CLASS:
            self._f_class.addItem(tr(lk), v)
        self._f_notes   = QTextEdit()
        self._f_notes.setFixedHeight(80)

        self._l_ru = QLabel()
        self._l_en = QLabel()
        self._l_id = QLabel()
        self._l_cl = QLabel()
        self._l_no = QLabel()
        rv.addRow(self._l_ru, self._f_name_ru)
        rv.addRow(self._l_en, self._f_name_en)
        rv.addRow(self._l_id, self._f_id)
        rv.addRow(self._l_cl, self._f_class)
        rv.addRow(self._l_no, self._f_notes)

        self._btn_apply = QPushButton(tr("gc_save_btn"))
        self._btn_apply.clicked.connect(self._apply)
        rv.addRow("", self._btn_apply)
        self._set_editor_enabled(False)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([200, 400])
        root.addWidget(splitter)
        self._relabel()

    def _relabel(self):
        self._l_ru.setText(tr("pos_col_name_ru"))
        self._l_en.setText(tr("pos_col_name_en"))
        self._l_id.setText(tr("pos_col_id"))
        self._l_cl.setText(tr("pos_col_class"))
        self._l_no.setText(tr("pos_notes"))
        self._btn_apply.setText(tr("gc_save_btn"))
        self._btn_def.setToolTip(tr("pos_load_defaults"))

    def _set_editor_enabled(self, en):
        for w in (self._f_name_ru, self._f_name_en, self._f_id,
                  self._f_class, self._f_notes, self._btn_apply):
            w.setEnabled(en)

    def load(self):
        if not self._s.lang.morphology.parts_of_speech:
            self._load_defaults(silent=True)
        self._refresh_list()

    def save(self): pass

    def retranslate(self):
        self._relabel()
        _retranslate_combo(self._f_class, self._CLASS)
        self._refresh_list()

    def _refresh_list(self):
        from core.i18n import get_lang
        lang = get_lang()
        self._list.clear()
        for pos in self._s.lang.morphology.parts_of_speech:
            self._list.addItem(pos.display(lang))

    def _on_select(self, row):
        pos_list = self._s.lang.morphology.parts_of_speech
        if row < 0 or row >= len(pos_list):
            self._set_editor_enabled(False)
            return
        self._set_editor_enabled(True)
        p = pos_list[row]
        self._f_name_ru.setText(p.name_ru)
        self._f_name_en.setText(p.name_en)
        self._f_id.setText(p.id)
        _set_combo(self._f_class, p.pos_class)
        self._f_notes.setPlainText(p.notes)

    def _apply(self):
        row = self._list.currentRow()
        pos_list = self._s.lang.morphology.parts_of_speech
        if row < 0 or row >= len(pos_list):
            return
        p = pos_list[row]
        p.name_ru  = self._f_name_ru.text().strip()
        p.name_en  = self._f_name_en.text().strip()
        p.id       = self._f_id.text().strip()
        p.pos_class= self._f_class.currentData()
        p.notes    = self._f_notes.toPlainText()
        self._refresh_list()
        self._list.setCurrentRow(row)
        self._s.mark_dirty()

    def _add(self):
        p = PartOfSpeech(id=f"pos{len(self._s.lang.morphology.parts_of_speech)+1}",
                         name_ru="Новая", name_en="New")
        self._s.lang.morphology.parts_of_speech.append(p)
        self._refresh_list()
        self._list.setCurrentRow(self._list.count()-1)
        self._s.mark_dirty()

    def _del(self):
        row = self._list.currentRow()
        pos_list = self._s.lang.morphology.parts_of_speech
        if 0 <= row < len(pos_list):
            pos_list.pop(row)
            self._refresh_list()
            self._s.mark_dirty()

    def _load_defaults(self, silent=False):
        self._s.lang.morphology.parts_of_speech = [
            PartOfSpeech(id=i, name_ru=ru, name_en=en, pos_class=cls)
            for i, ru, en, cls in _POS_DEFAULTS
        ]
        self._refresh_list()
        self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# 4. Грамматические категории (старая)
# ═══════════════════════════════════════════════════════════════════════════
_GC_TYPES = [("gc_type_case","case"), ("gc_type_gender","gender"),
             ("gc_type_number","number"), ("gc_type_tense","tense"),
             ("gc_type_aspect","aspect"), ("gc_type_mood","mood"),
             ("gc_type_voice","voice"), ("gc_type_person","person"),
             ("gc_type_other","other")]


class GramCatsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 4, 0)
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_select)
        lv.addWidget(self._list)

        brow = QHBoxLayout()
        self._btn_add = QPushButton("+")
        self._btn_add.setFixedWidth(32)
        self._btn_del = QPushButton("−")
        self._btn_del.setFixedWidth(32)
        for b in (self._btn_add, self._btn_del):
            brow.addWidget(b)
        brow.addStretch()
        lv.addLayout(brow)
        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(4, 0, 0, 0)
        form = QFormLayout()

        self._f_name  = QLineEdit()
        self._f_type  = QComboBox()
        for lk, v in _GC_TYPES:
            self._f_type.addItem(tr(lk), v)
        self._f_vals  = QTextEdit()
        self._f_vals.setFixedHeight(160)
        self._f_vals.setPlaceholderText(tr("gc_values_ph"))

        self._l_name = QLabel()
        self._l_type = QLabel()
        self._l_vals = QLabel()
        form.addRow(self._l_name, self._f_name)
        form.addRow(self._l_type, self._f_type)
        form.addRow(self._l_vals, self._f_vals)

        self._btn_apply = QPushButton()
        self._btn_apply.clicked.connect(self._apply)

        rv.addLayout(form)
        rv.addWidget(self._btn_apply)
        rv.addStretch()
        self._set_editor_enabled(False)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([180, 420])
        root.addWidget(splitter)
        self._relabel()

    def _relabel(self):
        self._l_name.setText(tr("gc_name_lbl"))
        self._l_type.setText(tr("gc_type_lbl"))
        self._l_vals.setText(tr("gc_values_lbl"))
        self._btn_apply.setText(tr("gc_save_btn"))
        self._f_vals.setPlaceholderText(tr("gc_values_ph"))

    def _set_editor_enabled(self, en):
        for w in (self._f_name, self._f_type, self._f_vals, self._btn_apply):
            w.setEnabled(en)

    def load(self):
        self._refresh_list()

    def save(self): pass

    def retranslate(self):
        self._relabel()
        _retranslate_combo(self._f_type, _GC_TYPES)
        self._refresh_list()

    def _refresh_list(self):
        self._list.clear()
        for gc in self._s.lang.morphology.gram_categories:
            self._list.addItem(f"{gc.name}  ({len(gc.values)})")

    def _on_select(self, row):
        cats = self._s.lang.morphology.gram_categories
        if row < 0 or row >= len(cats):
            self._set_editor_enabled(False)
            return
        self._set_editor_enabled(True)
        gc = cats[row]
        self._f_name.setText(gc.name)
        _set_combo(self._f_type, gc.cat_type)
        lines = [f"{v.name}={v.abbr}" if v.abbr else v.name for v in gc.values]
        self._f_vals.setPlainText("\n".join(lines))

    def _apply(self):
        row = self._list.currentRow()
        cats = self._s.lang.morphology.gram_categories
        if row < 0 or row >= len(cats):
            return
        gc = cats[row]
        gc.name     = self._f_name.text().strip()
        gc.cat_type = self._f_type.currentData()
        gc.values   = []
        for line in self._f_vals.toPlainText().split("\n"):
            line = line.strip()
            if not line:
                continue
            if "=" in line:
                name, abbr = line.split("=", 1)
                gc.values.append(GramCategory(name=name.strip(), abbr=abbr.strip()))
            else:
                gc.values.append(GramCategory(name=line))
        self._refresh_list()
        self._list.setCurrentRow(row)
        self._s.mark_dirty()

    def _add(self):
        self._s.lang.morphology.gram_categories.append(
            GramCategoryGroup(name=tr("gc_new"), cat_type="other"))
        self._refresh_list()
        self._list.setCurrentRow(self._list.count()-1)
        self._s.mark_dirty()

    def _del(self):
        row = self._list.currentRow()
        cats = self._s.lang.morphology.gram_categories
        if 0 <= row < len(cats):
            cats.pop(row)
            self._refresh_list()
            self._s.mark_dirty()
