"""
Унифицированные парадигмы — конструктор грамматики конланга.
Объединяет части речи, грамматические категории и правила словоизменения
в единый трёхпанельный интерфейс.

Левая панель: список частей речи (добавление, удаление, сброс)
Средняя панель: грамматические категории для выбранной части речи (включение/выключение, порядок)
Правая панель: вкладки «Категория» и «Инкорпорация»
  - Вкладка «Категория»: выбор значений, аффиксы/служебные слова, флексия (в мини-окошечке)
  - Вкладка «Инкорпорация»: настройки инкорпорации для полисинтетических языков

Связи:
- Типы аффиксов динамически берутся из MorphemeTypes
- Стратегии языка (аффиксы/служебные слова/флексия/инкорпорация) влияют на доступные опции
- Служебные слова фильтруются по applies_to_category и applies_to_value
- Поддерживаются словообразовательные функции (категория derivation)
- Приоритеты категорий из универсальных иерархий (Greenberg, Bybee)
- Автоматическое обновление при изменении настроек через сигналы Storage
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import get_lang, tr
from core.linguistic_data import (
    CATEGORY_VALUES,
    UNIVERSAL_CATEGORIES,
    get_category_display,
    get_category_priority,
    get_default_category_order,
    get_value_display,
    get_value_id,
    is_derivation_function,
)
from core.model import GrammarRule, GrammaticalCategory, PartOfSpeechConfig

# ── Полный список всех возможных типов аффиксов с их привязкой к MorphemeTypes ─
_ALL_AFFIX_TYPES = [
    ("pf_prefix", "prefix", "has_prefixes"),
    ("pf_suffix", "suffix", "has_suffixes"),
    ("pf_postfix", "postfix", "has_postfixes"),
    ("pf_infix", "infix", "has_infixes"),
    ("pf_circumfix", "circumfix", "has_circumfixes"),
    ("pf_interfix", "interfix", "has_interfixes"),
    ("pf_transfix", "transfix", "has_transfixes"),
    ("pf_duplifix", "duplifix", "has_duplifixes"),
    ("pf_simulfix", "simulfix", "has_simulfixes"),
    ("pf_disfix", "disfix", "has_disfixes"),
    ("pf_suprafix", "suprafix", "has_suprafixes"),
]


# ── Диалог добавления/редактирования части речи ─────────────────────────────
class POSDialog(QDialog):
    def __init__(self, parent, pos_config: PartOfSpeechConfig = None):
        super().__init__(parent)
        self._config = pos_config
        self.setWindowTitle(tr("pos_edit_title") if pos_config else tr("pos_add_title"))
        self.setMinimumWidth(400)
        self._build()
        if pos_config:
            self._load()

    def _build(self):
        root = QVBoxLayout(self)
        form = QFormLayout()

        self._id_edit = QLineEdit()
        self._id_edit.setPlaceholderText("noun, verb, adj...")
        self._name_ru = QLineEdit()
        self._name_en = QLineEdit()
        self._class_combo = QComboBox()
        self._class_combo.addItem(tr("pos_class_content"), "content")
        self._class_combo.addItem(tr("pos_class_function"), "function")
        self._notes_edit = QLineEdit()

        form.addRow("ID:", self._id_edit)
        form.addRow(tr("pos_col_name_ru") + ":", self._name_ru)
        form.addRow(tr("pos_col_name_en") + ":", self._name_en)
        form.addRow(tr("pos_col_class") + ":", self._class_combo)
        form.addRow(tr("pos_notes") + ":", self._notes_edit)

        root.addLayout(form)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)

    def _load(self):
        self._id_edit.setText(self._config.pos_id)
        self._name_ru.setText(self._config.name_ru)
        self._name_en.setText(self._config.name_en)
        idx = self._class_combo.findData(self._config.pos_class)
        if idx >= 0:
            self._class_combo.setCurrentIndex(idx)
        self._notes_edit.setText(self._config.notes)
        self._id_edit.setReadOnly(True)

    def get_config(self) -> PartOfSpeechConfig:
        return PartOfSpeechConfig(
            pos_id=self._id_edit.text().strip(),
            name_ru=self._name_ru.text().strip(),
            name_en=self._name_en.text().strip(),
            pos_class=self._class_combo.currentData(),
            notes=self._notes_edit.text().strip(),
        )


# ── Виджет настройки инкорпорации ───────────────────────────────────────────
class IncorporationWidget(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._s = storage
        self._pos_config: PartOfSpeechConfig = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        title = QLabel(tr("incorporation_title"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        root.addWidget(title)

        hint = QLabel(tr("incorporation_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; margin-bottom: 8px;")
        hint.setWordWrap(True)
        root.addWidget(hint)

        self._enabled_check = QCheckBox(tr("incorporation_enabled"))
        self._enabled_check.toggled.connect(self._on_enabled_toggled)
        root.addWidget(self._enabled_check)

        settings_group = QGroupBox(tr("incorporation_settings"))
        settings_layout = QFormLayout(settings_group)

        self._position_combo = QComboBox()
        self._position_combo.addItem(tr("incorporation_before"), "before")
        self._position_combo.addItem(tr("incorporation_after"), "after")
        self._position_combo.currentIndexChanged.connect(self._on_position_changed)
        settings_layout.addRow(tr("incorporation_position") + ":", self._position_combo)

        self._pattern_edit = QLineEdit()
        self._pattern_edit.setPlaceholderText("{object}-{verb}")
        self._pattern_edit.textChanged.connect(self._on_pattern_changed)
        settings_layout.addRow(tr("incorporation_pattern") + ":", self._pattern_edit)

        example_row = QHBoxLayout()
        self._example_input1 = QLineEdit()
        self._example_input1.setPlaceholderText(tr("incorporation_obj_ph"))
        self._example_input1.textChanged.connect(self._update_example)
        example_row.addWidget(self._example_input1)
        example_row.addWidget(QLabel("+"))
        self._example_input2 = QLineEdit()
        self._example_input2.setPlaceholderText(tr("incorporation_verb_ph"))
        self._example_input2.textChanged.connect(self._update_example)
        example_row.addWidget(self._example_input2)
        example_row.addWidget(QLabel("→"))
        self._example_output = QLabel("—")
        self._example_output.setStyleSheet("font-family: monospace; color: #1a1a8c; font-weight: bold;")
        example_row.addWidget(self._example_output)
        example_row.addStretch()
        settings_layout.addRow(tr("example") + ":", example_row)

        self._settings_widgets = [self._position_combo, self._pattern_edit,
                                   self._example_input1, self._example_input2]

        root.addWidget(settings_group)

        notes_group = QGroupBox(tr("notes"))
        notes_layout = QVBoxLayout(notes_group)
        self._notes_edit = QTextEdit()
        self._notes_edit.setFixedHeight(80)
        self._notes_edit.setPlaceholderText(tr("incorporation_notes_ph"))
        self._notes_edit.textChanged.connect(self._on_notes_changed)
        notes_layout.addWidget(self._notes_edit)
        root.addWidget(notes_group)

        root.addStretch()
        self._set_settings_enabled(False)

    def set_pos_config(self, pos_config: PartOfSpeechConfig):
        self._pos_config = pos_config
        self._enabled_check.setChecked(pos_config.incorporation_enabled)
        idx = self._position_combo.findData(pos_config.incorporation_position)
        if idx >= 0:
            self._position_combo.setCurrentIndex(idx)
        self._pattern_edit.setText(pos_config.incorporation_pattern)
        self._notes_edit.setPlainText(pos_config.incorporation_notes)
        self._set_settings_enabled(pos_config.incorporation_enabled)
        self._update_example()

    def _set_settings_enabled(self, enabled: bool):
        for w in self._settings_widgets:
            w.setEnabled(enabled)
        self._notes_edit.setEnabled(enabled)

    def _on_enabled_toggled(self, checked: bool):
        self._set_settings_enabled(checked)
        if self._pos_config:
            self._pos_config.incorporation_enabled = checked
            self._update_example()

    def _on_position_changed(self):
        if self._pos_config:
            self._pos_config.incorporation_position = self._position_combo.currentData()
            self._update_example()

    def _on_pattern_changed(self):
        if self._pos_config:
            self._pos_config.incorporation_pattern = self._pattern_edit.text()
            self._update_example()

    def _on_notes_changed(self):
        if self._pos_config:
            self._pos_config.incorporation_notes = self._notes_edit.toPlainText()

    def _update_example(self):
        obj = self._example_input1.text() or tr("incorporation_obj_ph")
        verb = self._example_input2.text() or tr("incorporation_verb_ph")
        if self._pos_config and self._pos_config.incorporation_enabled:
            pattern = self._pos_config.incorporation_pattern
            if pattern:
                result = pattern.replace("{object}", obj).replace("{verb}", verb)
                self._example_output.setText(result)
            else:
                if self._pos_config.incorporation_position == "before":
                    self._example_output.setText(f"{obj}-{verb}")
                else:
                    self._example_output.setText(f"{verb}-{obj}")
        else:
            self._example_output.setText("—")


# ── Виджет детальной настройки категории (с флексией в мини-окошечке) ────────
class CategoryDetailWidget(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._s = storage
        self._pos_config: PartOfSpeechConfig = None
        self._category_id: str = ""
        self._category: GrammaticalCategory = None
        self._current_value_id: str = ""
        self._updating = False
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        self._title_label = QLabel()
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self._title_label.setFont(font)
        root.addWidget(self._title_label)

        self._enabled_check = QCheckBox(tr("category_enabled"))
        self._enabled_check.toggled.connect(self._on_enabled_toggled)
        root.addWidget(self._enabled_check)

        # Таблица значений
        values_group = QGroupBox(tr("category_values"))
        values_layout = QVBoxLayout(values_group)

        self._values_table = QTableWidget()
        self._values_table.setColumnCount(3)
        self._values_table.setHorizontalHeaderLabels([
            tr("value_enabled"), tr("value_name"), tr("value_affix")
        ])
        self._values_table.verticalHeader().setVisible(False)
        self._values_table.setAlternatingRowColors(True)
        hh = self._values_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._values_table.setColumnWidth(0, 60)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._values_table.setColumnWidth(2, 100)
        self._values_table.itemSelectionChanged.connect(self._on_value_selected)
        values_layout.addWidget(self._values_table)

        root.addWidget(values_group)

        # Мини-окошечко для настройки выбранного значения
        detail_group = QGroupBox(tr("value_settings"))
        detail_layout = QFormLayout(detail_group)

        self._value_name_label = QLabel()
        self._value_name_label.setStyleSheet("font-weight: bold;")
        detail_layout.addRow("", self._value_name_label)

        # Тип аффикса
        self._affix_type_combo = QComboBox()
        self._affix_type_combo.currentIndexChanged.connect(self._on_affix_type_changed)
        detail_layout.addRow(tr("affix_type") + ":", self._affix_type_combo)

        # Служебное слово (если выбрано)
        self._function_word_combo = QComboBox()
        self._function_word_combo.setVisible(False)
        self._function_word_combo.currentIndexChanged.connect(self._on_function_word_changed)
        detail_layout.addRow(tr("fw_col_function") + ":", self._function_word_combo)

        # Формула аффикса
        self._affix_pattern_edit = QLineEdit()
        self._affix_pattern_edit.setPlaceholderText(tr("affix_pattern_ph"))
        self._affix_pattern_edit.textChanged.connect(self._on_pattern_changed)
        detail_layout.addRow(tr("affix_pattern") + ":", self._affix_pattern_edit)

        # Пример аффикса
        self._example_input = QLineEdit()
        self._example_input.setPlaceholderText(tr("example_root_ph"))
        self._example_input.textChanged.connect(self._update_example)
        detail_layout.addRow(tr("example_root") + ":", self._example_input)

        self._example_output = QLabel("—")
        self._example_output.setStyleSheet("font-family: monospace; color: #1a1a8c;")
        detail_layout.addRow(tr("example_result") + ":", self._example_output)

        # ── ФЛЕКСИЯ ──────────────────────────────────────────────────────
        self._fusion_combo = QComboBox()
        self._fusion_combo.addItem(tr("fusion_none"), "")
        self._fusion_combo.currentIndexChanged.connect(self._on_fusion_combo_changed)
        detail_layout.addRow(tr("fuses_with") + ":", self._fusion_combo)

        self._fusion_pattern_edit = QLineEdit()
        self._fusion_pattern_edit.setPlaceholderText(tr("fusion_pattern_ph"))
        self._fusion_pattern_edit.textChanged.connect(self._on_fusion_pattern_changed)
        self._fusion_pattern_edit.setEnabled(False)
        detail_layout.addRow(tr("fusion_pattern") + ":", self._fusion_pattern_edit)

        # Пример флексии
        fusion_example_label = QLabel(tr("fusion_example") + ":")
        fusion_example_label.setStyleSheet("margin-top: 8px;")
        detail_layout.addRow(fusion_example_label, QLabel(""))

        self._fusion_example_input = QLineEdit()
        self._fusion_example_input.setPlaceholderText(tr("fusion_example_ph"))
        self._fusion_example_input.textChanged.connect(self._update_fusion_example)
        detail_layout.addRow(tr("example_root") + ":", self._fusion_example_input)

        self._fusion_example_output = QLabel("—")
        self._fusion_example_output.setStyleSheet("font-family: monospace; color: #1a1a8c;")
        detail_layout.addRow(tr("fusion_example_result") + ":", self._fusion_example_output)

        self._detail_widgets = [
            self._affix_type_combo, self._function_word_combo,
            self._affix_pattern_edit, self._example_input, self._example_output,
            self._fusion_combo, self._fusion_pattern_edit,
            self._fusion_example_input, self._fusion_example_output
        ]
        self._set_detail_enabled(False)

        root.addWidget(detail_group)
        root.addStretch()

    def _get_lang_strategies(self) -> dict:
        default_strategies = {
            "use_affixes": True,
            "use_particles": False,
            "use_fusion": False,
            "use_incorporation": False,
        }
        if hasattr(self._s.lang, "extra") and isinstance(self._s.lang.extra, dict):
            return self._s.lang.extra.get("lang_type_strategies", default_strategies)
        return default_strategies

    def _get_available_affix_types(self) -> list:
        mt = self._s.lang.morphology.morpheme_types
        available = []
        always_available = ["suffix", "prefix"]
        for i18n_key, type_id, field_name in _ALL_AFFIX_TYPES:
            if type_id in always_available:
                available.append((i18n_key, type_id))
            elif hasattr(mt, field_name) and getattr(mt, field_name):
                available.append((i18n_key, type_id))
        return available

    def _get_function_words_for_category(self) -> list:
        if not self._category_id:
            return []
        result = []
        for fw in self._s.lang.function_words:
            if fw.applies_to_category == self._category_id:
                result.append(fw)
        return result

    def _rebuild_affix_combo(self):
        self._updating = True

        strategies = self._get_lang_strategies()
        current_type = self._affix_type_combo.currentData()
        self._affix_type_combo.clear()

        if not strategies.get("use_affixes", True) and strategies.get("use_particles", False):
            self._affix_type_combo.addItem(tr("pf_function_word"), "function_word")
        else:
            for i18n_key, type_id in self._get_available_affix_types():
                self._affix_type_combo.addItem(tr(i18n_key), type_id)

        idx = self._affix_type_combo.findData(current_type)
        if idx >= 0:
            self._affix_type_combo.setCurrentIndex(idx)
        elif self._affix_type_combo.count() > 0:
            self._affix_type_combo.setCurrentIndex(0)

        self._update_function_word_combo_visibility()
        self._updating = False

    def _update_function_word_combo_visibility(self):
        current_type = self._affix_type_combo.currentData()
        self._function_word_combo.setVisible(current_type == "function_word")
        self._affix_pattern_edit.setVisible(current_type != "function_word")

    def _populate_function_word_combo(self, current_value: str = ""):
        self._function_word_combo.clear()
        self._function_word_combo.addItem("—", "")

        for fw in self._get_function_words_for_category():
            if self._current_value_id and fw.applies_to_value:
                if fw.applies_to_value != self._current_value_id:
                    continue
            display = f"{fw.form} ({fw.function})" if fw.name else fw.form
            self._function_word_combo.addItem(display, fw.form)

        idx = self._function_word_combo.findData(current_value)
        if idx >= 0:
            self._function_word_combo.setCurrentIndex(idx)

    def _update_fusion_combo(self):
        """Обновляет выпадающий список доступных значений для флексии."""
        self._fusion_combo.blockSignals(True)
        self._fusion_combo.clear()
        self._fusion_combo.addItem(tr("fusion_none"), "")

        if self._pos_config and self._category_id:
            lang = get_lang()
            for other_cat_id, other_cat in self._pos_config.categories.items():
                if other_cat_id == self._category_id or not other_cat.enabled:
                    continue
                for value_id, rule in other_cat.rules.items():
                    if not rule.enabled:
                        continue
                    value_display = value_id
                    cat_values = CATEGORY_VALUES.get(other_cat_id, [])
                    for v in cat_values:
                        if get_value_id(v) == value_id:
                            value_display = get_value_display(v, lang)
                            break
                    cat_display = get_category_display(other_cat_id, lang)
                    display = f"{cat_display}: {value_display}"
                    self._fusion_combo.addItem(display, (other_cat_id, value_id))

        self._fusion_combo.blockSignals(False)

    def refresh_affix_types(self):
        self._rebuild_affix_combo()

    def refresh_strategies(self):
        self._rebuild_affix_combo()
        strategies = self._get_lang_strategies()
        is_deriv = is_derivation_function(self._category_id) if self._category_id else False
        show_fusion = strategies.get("use_fusion", False) and not is_deriv

        # Скрываем/показываем все элементы флексии
        self._fusion_combo.setVisible(show_fusion)
        self._fusion_pattern_edit.setVisible(show_fusion)
        self._fusion_example_input.setVisible(show_fusion)
        self._fusion_example_output.setVisible(show_fusion)

    def set_category(self, pos_config: PartOfSpeechConfig, category_id: str):
        self._updating = True

        self._pos_config = pos_config
        self._category_id = category_id
        self._category = pos_config.categories.get(category_id)

        if self._category is None:
            self._category = GrammaticalCategory(category_id=category_id, enabled=False)
            pos_config.categories[category_id] = self._category

        self._rebuild_affix_combo()
        strategies = self._get_lang_strategies()
        is_deriv = is_derivation_function(category_id)
        show_fusion = strategies.get("use_fusion", False) and not is_deriv

        self._fusion_combo.setVisible(show_fusion)
        self._fusion_pattern_edit.setVisible(show_fusion)
        self._fusion_example_input.setVisible(show_fusion)
        self._fusion_example_output.setVisible(show_fusion)

        lang = get_lang()
        pos_name = pos_config.display(lang)
        cat_name = get_category_display(category_id, lang)
        self._title_label.setText(f"{pos_name} → {cat_name}")

        self._enabled_check.setChecked(self._category.enabled)

        self._populate_values_table()

        self._set_detail_enabled(False)
        self._values_table.setEnabled(self._category.enabled)

        self._updating = False

    def _populate_values_table(self):
        values = CATEGORY_VALUES.get(self._category_id, [])
        self._values_table.setRowCount(len(values))
        lang = get_lang()

        for i, value in enumerate(values):
            value_id = get_value_id(value)
            display = get_value_display(value, lang)

            check = QCheckBox()
            check.setStyleSheet("margin-left: 8px;")

            rule = self._category.rules.get(value_id)
            if rule:
                check.setChecked(rule.enabled)
            else:
                rule = GrammarRule(value_id=value_id, enabled=False)
                self._category.rules[value_id] = rule

            check.toggled.connect(lambda checked, vid=value_id: self._on_value_enabled(vid, checked))
            self._values_table.setCellWidget(i, 0, check)

            name_item = QTableWidgetItem(display)
            name_item.setData(Qt.ItemDataRole.UserRole, value_id)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._values_table.setItem(i, 1, name_item)

            affix_text = rule.affix_pattern if rule and rule.affix_pattern else "—"
            affix_item = QTableWidgetItem(affix_text)
            affix_item.setFlags(affix_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            affix_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._values_table.setItem(i, 2, affix_item)

    def _on_enabled_toggled(self, checked: bool):
        if self._updating:
            return
        self._category.enabled = checked
        self._values_table.setEnabled(checked)
        self._set_detail_enabled(False)

    def _on_value_enabled(self, value_id: str, checked: bool):
        if value_id in self._category.rules:
            self._category.rules[value_id].enabled = checked
        else:
            self._category.rules[value_id] = GrammarRule(value_id=value_id, enabled=checked)
        if self._current_value_id:
            self._update_fusion_combo()

    def _on_value_selected(self):
        row = self._values_table.currentRow()
        if row < 0:
            self._set_detail_enabled(False)
            return

        item = self._values_table.item(row, 1)
        if not item:
            return

        value_id = item.data(Qt.ItemDataRole.UserRole)
        self._current_value_id = value_id

        rule = self._category.rules.get(value_id)
        if not rule:
            rule = GrammarRule(value_id=value_id, enabled=False)
            self._category.rules[value_id] = rule

        self._updating = True

        lang = get_lang()
        values = CATEGORY_VALUES.get(self._category_id, [])
        display = value_id
        for v in values:
            if get_value_id(v) == value_id:
                display = get_value_display(v, lang)
                break
        self._value_name_label.setText(display)

        # Обновляем комбо флексии
        self._update_fusion_combo()

        idx = self._affix_type_combo.findData(rule.affix_type)
        self._affix_type_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._update_function_word_combo_visibility()

        self._populate_function_word_combo(rule.affix_pattern if rule.affix_type == "function_word" else "")

        self._affix_pattern_edit.setText(rule.affix_pattern if rule.affix_type != "function_word" else "")
        self._affix_pattern_edit.setVisible(rule.affix_type != "function_word")

        self._example_input.setText(rule.example_input or "root")
        self._update_example()

        # Загружаем сохранённую флексию
        if hasattr(rule, 'fusion_category') and hasattr(rule, 'fusion_value'):
            idx = self._fusion_combo.findData((rule.fusion_category, rule.fusion_value))
            if idx >= 0:
                self._fusion_combo.setCurrentIndex(idx)
        if hasattr(rule, 'fusion_pattern'):
            self._fusion_pattern_edit.setText(rule.fusion_pattern)
            self._fusion_pattern_edit.setEnabled(self._fusion_combo.currentData() != "")

        self._update_fusion_example()

        self._set_detail_enabled(rule.enabled)
        self._updating = False

    def _set_detail_enabled(self, enabled: bool):
        for w in self._detail_widgets:
            w.setEnabled(enabled)
        if not enabled:
            self._value_name_label.setText(tr("select_value_hint"))
            self._affix_pattern_edit.clear()
            self._example_input.clear()
            self._example_output.setText("—")
            self._fusion_combo.setCurrentIndex(0)
            self._fusion_pattern_edit.clear()
            self._fusion_pattern_edit.setEnabled(False)
            self._fusion_example_input.clear()
            self._fusion_example_output.setText("—")

    def _on_affix_type_changed(self):
        if self._updating:
            return
        self._update_function_word_combo_visibility()
        self._save_current_rule()

    def _on_function_word_changed(self):
        if self._updating:
            return
        self._save_current_rule()

    def _on_pattern_changed(self):
        if self._updating:
            return
        self._save_current_rule()

    def _on_fusion_combo_changed(self):
        if self._updating:
            return
        data = self._fusion_combo.currentData()
        self._fusion_pattern_edit.setEnabled(data != "" and data is not None)
        self._save_current_rule()
        self._update_fusion_example()

    def _on_fusion_pattern_changed(self):
        if self._updating:
            return
        self._save_current_rule()
        self._update_fusion_example()

    def _save_current_rule(self):
        if not self._current_value_id:
            return
        rule = self._category.rules.get(self._current_value_id)
        if rule:
            rule.affix_type = self._affix_type_combo.currentData()
            if rule.affix_type == "function_word":
                rule.affix_pattern = self._function_word_combo.currentData() or ""
            else:
                rule.affix_pattern = self._affix_pattern_edit.text()

            # Сохраняем флексию
            data = self._fusion_combo.currentData()
            if data and isinstance(data, tuple) and len(data) == 2:
                rule.fusion_category, rule.fusion_value = data
                rule.fusion_pattern = self._fusion_pattern_edit.text()
            else:
                rule.fusion_category = ""
                rule.fusion_value = ""
                rule.fusion_pattern = ""

            self._update_example()
            self._update_affix_display()

    def _update_example(self):
        if self._updating or not self._current_value_id:
            return
        rule = self._category.rules.get(self._current_value_id)
        if rule:
            root = self._example_input.text() or "root"
            rule.example_input = root

            if rule.affix_type == "function_word":
                fw_form = rule.affix_pattern
                if fw_form:
                    fw = next((f for f in self._s.lang.function_words if f.form == fw_form), None)
                    if fw and fw.position == "before":
                        result = f"{fw_form} {root}"
                    elif fw:
                        result = f"{root} {fw_form}"
                    else:
                        result = f"{fw_form} {root}"
                else:
                    result = root
            else:
                try:
                    from sections.paradigms import AffixEngine
                    result = AffixEngine.apply(root, rule.affix_type, rule.affix_pattern)
                except Exception:
                    result = root + rule.affix_pattern

            rule.example_output = result
            self._example_output.setText(result)

    def _update_fusion_example(self):
        """Обновляет пример для флексии."""
        if self._updating:
            return

        root = self._fusion_example_input.text() or "root"
        if not root:
            self._fusion_example_output.setText("—")
            return

        rule = self._category.rules.get(self._current_value_id) if self._current_value_id else None
        if not rule or not rule.fusion_pattern:
            # Показываем обычный аффикс
            if rule and rule.affix_pattern:
                self._fusion_example_output.setText(root + rule.affix_pattern)
            else:
                self._fusion_example_output.setText(root)
            return

        # Показываем флексию
        result = root + rule.fusion_pattern
        self._fusion_example_output.setText(result)

    def _update_affix_display(self):
        row = self._values_table.currentRow()
        if row >= 0:
            rule = self._category.rules.get(self._current_value_id)
            if rule:
                affix_text = rule.affix_pattern if rule.affix_pattern else "—"
                item = self._values_table.item(row, 2)
                if item:
                    item.setText(affix_text)


# ── Основной раздел ─────────────────────────────────────────────────────────
class UnifiedParadigmSection(BaseSection):
    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель: Части речи
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)

        left_header = QHBoxLayout()
        left_header.addWidget(QLabel(tr("parts_of_speech")))
        left_header.addStretch()

        self._add_pos_btn = QPushButton("+")
        self._add_pos_btn.setFixedSize(28, 28)
        self._add_pos_btn.clicked.connect(self._add_pos)
        left_header.addWidget(self._add_pos_btn)

        self._del_pos_btn = QPushButton("−")
        self._del_pos_btn.setFixedSize(28, 28)
        self._del_pos_btn.clicked.connect(self._del_pos)
        left_header.addWidget(self._del_pos_btn)

        self._reset_pos_btn = QPushButton("↺")
        self._reset_pos_btn.setFixedSize(28, 28)
        self._reset_pos_btn.setToolTip(tr("pos_load_defaults"))
        self._reset_pos_btn.clicked.connect(self._reset_default_pos)
        left_header.addWidget(self._reset_pos_btn)

        left_layout.addLayout(left_header)

        self._pos_list = QListWidget()
        self._pos_list.currentRowChanged.connect(self._on_pos_selected)
        left_layout.addWidget(self._pos_list)

        splitter.addWidget(left_widget)

        # Средняя панель: Грамматические категории (с приоритетами)
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(4, 4, 4, 4)

        middle_header = QHBoxLayout()
        middle_header.addWidget(QLabel(tr("grammatical_categories")))
        middle_header.addStretch()

        self._move_up_btn = QPushButton("↑")
        self._move_up_btn.setFixedSize(28, 28)
        self._move_up_btn.setToolTip(tr("move_up"))
        self._move_up_btn.clicked.connect(lambda: self._move_category(-1))
        middle_header.addWidget(self._move_up_btn)

        self._move_down_btn = QPushButton("↓")
        self._move_down_btn.setFixedSize(28, 28)
        self._move_down_btn.setToolTip(tr("move_down"))
        self._move_down_btn.clicked.connect(lambda: self._move_category(1))
        middle_header.addWidget(self._move_down_btn)

        self._reset_order_btn = QPushButton("↺")
        self._reset_order_btn.setFixedSize(28, 28)
        self._reset_order_btn.setToolTip(tr("reset_order"))
        self._reset_order_btn.clicked.connect(self._reset_category_order)
        middle_header.addWidget(self._reset_order_btn)

        middle_layout.addLayout(middle_header)

        self._categories_table = QTableWidget()
        self._categories_table.setColumnCount(3)
        self._categories_table.setHorizontalHeaderLabels([
            tr("category_enabled"), tr("category_name"), ""
        ])
        self._categories_table.verticalHeader().setVisible(False)
        self._categories_table.setAlternatingRowColors(True)
        hh = self._categories_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._categories_table.setColumnWidth(0, 60)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._categories_table.setColumnWidth(2, 30)
        self._categories_table.itemSelectionChanged.connect(self._on_category_selected)
        middle_layout.addWidget(self._categories_table)

        splitter.addWidget(middle_widget)

        # Правая панель: Вкладки
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 4, 4, 4)

        self._right_tabs = QTabWidget()

        self._detail_widget = CategoryDetailWidget(self._s)
        self._right_tabs.addTab(self._detail_widget, tr("tab_category"))

        self._incorporation_widget = IncorporationWidget(self._s)
        self._right_tabs.addTab(self._incorporation_widget, tr("tab_incorporation"))

        right_layout.addWidget(self._right_tabs)

        splitter.addWidget(right_widget)

        splitter.setSizes([200, 300, 500])
        root.addWidget(splitter)

        self._current_pos_id: str = ""

        # Подписка на сигналы
        self._s.morpheme_types_changed.connect(self._on_morpheme_types_changed)
        self._s.strategies_changed.connect(self._on_strategies_changed)

    def load(self):
        self._refresh_pos_list()
        if self._pos_list.count() > 0:
            self._pos_list.setCurrentRow(0)
        self._update_tabs_visibility()

    def save(self):
        pass

    def retranslate(self):
        self._add_pos_btn.setToolTip(tr("add"))
        self._del_pos_btn.setToolTip(tr("delete"))
        self._reset_pos_btn.setToolTip(tr("pos_load_defaults"))
        self._move_up_btn.setToolTip(tr("move_up"))
        self._move_down_btn.setToolTip(tr("move_down"))
        self._reset_order_btn.setToolTip(tr("reset_order"))
        self._right_tabs.setTabText(0, tr("tab_category"))
        self._right_tabs.setTabText(1, tr("tab_incorporation"))
        self._refresh_pos_list()
        self._refresh_categories_table()
        self._detail_widget.refresh_affix_types()

    def _on_morpheme_types_changed(self):
        self._detail_widget.refresh_affix_types()

    def _on_strategies_changed(self):
        self.refresh_strategies()

    def refresh_strategies(self):
        self._detail_widget.refresh_strategies()
        self._update_tabs_visibility()

    def _update_tabs_visibility(self):
        strategies = self._s.lang.extra.get("lang_type_strategies", {})
        self._right_tabs.setTabVisible(1, strategies.get("use_incorporation", False))

    def _refresh_pos_list(self):
        self._pos_list.clear()
        lang = get_lang()
        for pos_id, config in self._s.lang.pos_configs.items():
            item = QListWidgetItem(config.display(lang))
            item.setData(Qt.ItemDataRole.UserRole, pos_id)
            self._pos_list.addItem(item)

    def _add_pos(self):
        dlg = POSDialog(self)
        if dlg.exec():
            config = dlg.get_config()
            if config.pos_id and config.pos_id not in self._s.lang.pos_configs:
                available_cats = UNIVERSAL_CATEGORIES.get(config.pos_id, [])
                config.category_order = get_default_category_order(config.pos_id)
                for cat_id in available_cats:
                    config.categories[cat_id] = GrammaticalCategory(category_id=cat_id, enabled=False)
                self._s.lang.pos_configs[config.pos_id] = config
                self._refresh_pos_list()
                self._s.mark_dirty()

    def _del_pos(self):
        row = self._pos_list.currentRow()
        if row < 0:
            return
        item = self._pos_list.item(row)
        pos_id = item.data(Qt.ItemDataRole.UserRole)
        ans = QMessageBox.question(
            self, tr("confirm_del_title"),
            tr("confirm_del_pos").format(pos_id),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            del self._s.lang.pos_configs[pos_id]
            self._refresh_pos_list()
            self._categories_table.setRowCount(0)
            self._s.mark_dirty()

    def _reset_default_pos(self):
        ans = QMessageBox.question(
            self, tr("confirm_reset_title"),
            tr("confirm_reset_pos"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            self._s.lang._init_default_pos_configs()
            self._refresh_pos_list()
            self._categories_table.setRowCount(0)
            self._s.mark_dirty()

    def _on_pos_selected(self, row: int):
        if row < 0:
            self._current_pos_id = ""
            self._categories_table.setRowCount(0)
            return
        item = self._pos_list.item(row)
        self._current_pos_id = item.data(Qt.ItemDataRole.UserRole)
        self._refresh_categories_table()
        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if config:
            self._incorporation_widget.set_pos_config(config)

    def _refresh_categories_table(self):
        if not self._current_pos_id:
            self._categories_table.setRowCount(0)
            return
        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if not config:
            return

        lang = get_lang()

        # Получаем категории в заданном порядке
        ordered_cats = []
        if config.category_order:
            for cat_id in config.category_order:
                if cat_id in config.categories:
                    ordered_cats.append((cat_id, config.categories[cat_id]))
        # Добавляем те, что не попали в order (сортируем по приоритету)
        remaining = [(cat_id, cat) for cat_id, cat in config.categories.items()
                     if cat_id not in config.category_order]
        remaining.sort(key=lambda x: get_category_priority(x[0]))
        ordered_cats.extend(remaining)

        # Обновляем category_order в модели
        config.category_order = [cat_id for cat_id, _ in ordered_cats]

        self._categories_table.setRowCount(len(ordered_cats))

        for i, (cat_id, cat) in enumerate(ordered_cats):
            # Чекбокс
            check = QCheckBox()
            check.setChecked(cat.enabled)
            check.setStyleSheet("margin-left: 8px;")
            check.toggled.connect(lambda checked, cid=cat_id: self._on_category_enabled(cid, checked))
            self._categories_table.setCellWidget(i, 0, check)

            # Название
            display = get_category_display(cat_id, lang)
            item = QTableWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, cat_id)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._categories_table.setItem(i, 1, item)

            # Индикатор приоритета
            priority_label = QLabel(str(i + 1))
            priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            priority_label.setStyleSheet("color: #666; font-size: 10px;")
            self._categories_table.setCellWidget(i, 2, priority_label)

    def _move_category(self, delta: int):
        """Перемещает выбранную категорию вверх/вниз по приоритету."""
        row = self._categories_table.currentRow()
        if row < 0:
            return

        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if not config or not config.category_order:
            return

        new_row = row + delta
        if 0 <= new_row < len(config.category_order):
            config.category_order[row], config.category_order[new_row] = \
                config.category_order[new_row], config.category_order[row]
            self._refresh_categories_table()
            self._categories_table.selectRow(new_row)
            self._s.mark_dirty()

    def _reset_category_order(self):
        """Сбрасывает порядок категорий на универсальный по умолчанию."""
        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if config:
            config.category_order = get_default_category_order(config.pos_id)
            self._refresh_categories_table()
            self._s.mark_dirty()

    def _on_category_enabled(self, category_id: str, checked: bool):
        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if config and category_id in config.categories:
            config.categories[category_id].enabled = checked
            self._s.mark_dirty()
            if self._detail_widget._category_id == category_id:
                self._detail_widget.set_category(config, category_id)

    def _on_category_selected(self):
        row = self._categories_table.currentRow()
        if row < 0:
            return
        item = self._categories_table.item(row, 1)
        if not item:
            return
        category_id = item.data(Qt.ItemDataRole.UserRole)
        config = self._s.lang.pos_configs.get(self._current_pos_id)
        if config:
            self._detail_widget.set_category(config, category_id)
            self._right_tabs.setCurrentIndex(0)
