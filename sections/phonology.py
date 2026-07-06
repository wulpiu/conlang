"""
Четыре раздела фонологии:
  VowelsSection, ConsonantsSection, ProsodySection, PhonotacticsSection
  + PhonRulesSection (правила транскрипции, встроены в каждый раздел как вкладка).
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import tr
from core.model import Consonant, PhonemeRule, Vowel
from core.table_editor import ColDef, TableEditor

# ── выборы для combo-колонок ─────────────────────────────────────────────────
_V_HEIGHT  = [("v_height_high","high"),("v_height_mid","mid"),("v_height_low","low")]
_V_BACK    = [("v_back_front","front"),("v_back_central","central"),("v_back_back","back")]

_C_PLACE   = [(f"c_place_{v}", v) for v in (
    "bilabial","labiodental","dental","alveolar",
    "postalveolar","retroflex","palatal","velar",
    "uvular","pharyngeal","glottal")]
_C_MANNER  = [(f"c_manner_{v}", v) for v in (
    "stop","fricative","affricate","nasal",
    "lateral","trill","approximant","click")]


# ═══════════════════════════════════════════════════════════════════════════════
# Вспомогательный виджет: таблица правил транскрипции (переиспользуется)
# ═══════════════════════════════════════════════════════════════════════════════
class _RulesWidget(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._s = storage
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 8, 0, 0)

        # таблица
        self._tbl = QTableWidget()
        self._tbl.setColumnCount(3)
        self._tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        hh = self._tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(2, 70)
        root.addWidget(self._tbl)

        # форма добавления
        form_w = QWidget()
        fl = QFormLayout(form_w)
        fl.setContentsMargins(0, 4, 0, 0)
        self._f_chars  = QLineEdit()
        self._f_pronun = QLineEdit()
        self._f_prio   = QLineEdit("0")
        self._f_prio.setValidator(QIntValidator(-99, 99))
        self._f_prio.setFixedWidth(50)
        self._lbl_chars  = QLabel(); self._lbl_pronun = QLabel(); self._lbl_prio = QLabel()
        fl.addRow(self._lbl_chars,  self._f_chars)
        fl.addRow(self._lbl_pronun, self._f_pronun)
        fl.addRow(self._lbl_prio,   self._f_prio)
        root.addWidget(form_w)

        # кнопка + тест
        row = QHBoxLayout()
        self._btn_add = QPushButton()
        self._btn_del = QPushButton(tr("delete"))
        row.addWidget(self._btn_add); row.addWidget(self._btn_del); row.addStretch()
        root.addLayout(row)

        test_row = QHBoxLayout()
        self._lbl_test   = QLabel()
        self._f_test     = QLineEdit()
        self._f_test.setPlaceholderText(tr("phon_test_ph"))
        self._lbl_result = QLabel()
        self._lbl_result.setStyleSheet("font-weight:bold;")
        test_row.addWidget(self._lbl_test)
        test_row.addWidget(self._f_test, 1)
        test_row.addWidget(self._lbl_result, 2)
        root.addLayout(test_row)

        self._btn_add.clicked.connect(self._add)
        self._btn_del.clicked.connect(self._del)
        self._f_test.textChanged.connect(self._test)
        self._retranslate_labels()

    def _retranslate_labels(self):
        self._tbl.setHorizontalHeaderLabels(
            [tr("phon_col_chars"), tr("phon_col_pronun"), tr("phon_col_prio")])
        self._lbl_chars.setText(tr("phon_chars_lbl"))
        self._lbl_pronun.setText(tr("phon_pronun_lbl"))
        self._lbl_prio.setText(tr("phon_prio_lbl"))
        self._btn_add.setText(tr("phon_add"))
        self._btn_del.setText(tr("delete"))
        self._lbl_test.setText(tr("phon_test_lbl"))
        self._f_test.setPlaceholderText(tr("phon_test_ph"))

    def load(self):
        rules = self._s.lang.phonology.phoneme_rules
        self._tbl.setRowCount(len(rules))
        for i, r in enumerate(rules):
            self._tbl.setItem(i, 0, QTableWidgetItem(r.chars))
            self._tbl.setItem(i, 1, QTableWidgetItem(r.pronun))
            it = QTableWidgetItem(str(r.priority))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._tbl.setItem(i, 2, it)

    def save(self):
        rules = []
        for i in range(self._tbl.rowCount()):
            chars  = (self._tbl.item(i,0) or QTableWidgetItem("")).text().strip()
            pronun = (self._tbl.item(i,1) or QTableWidgetItem("")).text().strip()
            try:
                prio = int((self._tbl.item(i,2) or QTableWidgetItem("0")).text())
            except ValueError:
                prio = 0
            if chars:
                rules.append(PhonemeRule(chars=chars, pronun=pronun, priority=prio))
        self._s.lang.phonology.phoneme_rules = rules
        self._s.mark_dirty()

    def _add(self):
        chars  = self._f_chars.text().strip()
        pronun = self._f_pronun.text().strip()
        if not chars:
            return
        try: prio = int(self._f_prio.text())
        except ValueError: prio = 0
        self._s.lang.phonology.phoneme_rules.append(
            PhonemeRule(chars=chars, pronun=pronun, priority=prio))
        self._f_chars.clear(); self._f_pronun.clear(); self._f_prio.setText("0")
        self.load()
        self._s.mark_dirty()

    def _del(self):
        r = self._tbl.currentRow()
        if 0 <= r < len(self._s.lang.phonology.phoneme_rules):
            self._s.lang.phonology.phoneme_rules.pop(r)
            self.load()
            self._s.mark_dirty()

    def _test(self, word: str):
        result = self._s.lang.phonology.generate_pronunciation(word)
        self._lbl_result.setText(tr("phon_test_result") + result)

    def retranslate(self):
        self._retranslate_labels()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Гласные
# ═══════════════════════════════════════════════════════════════════════════════
class VowelsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        tabs = QTabWidget()
        root.addWidget(tabs)

        # ── вкладка инвентаря ────────────────────────────────────────────────
        inv_w = QWidget()
        QVBoxLayout(inv_w)
        cols = [
            ColDef("v_symbol",  "symbol",   "str",  60),
            ColDef("v_height",  "height",   "combo", 130, _V_HEIGHT),
            ColDef("v_backness","backness",  "combo", 130, _V_BACK),
            ColDef("v_rounded", "rounded",  "bool",  60),
            ColDef("v_nasal",   "nasal",    "bool",  60),
            ColDef("v_long",    "long",     "bool",  60),
            ColDef("v_notes",   "notes",    "str",    0),
        ]
        self._editor = TableEditor(cols, Vowel, self._mark)
        inv_w.layout().addWidget(self._editor)
        self._tab_inv_key = "v_title"

        # ── вкладка правил транскрипции ──────────────────────────────────────
        self._rules = _RulesWidget(self._s)

        tabs.addTab(inv_w, tr("v_title"))
        tabs.addTab(self._rules, tr("phon_rules_title"))
        self._tabs = tabs

    def load(self):
        self._editor.set_rows(self._s.lang.phonology.vowels)
        self._rules.load()

    def save(self):
        self._s.lang.phonology.vowels = self._editor.get_rows()
        self._rules.save()

    def retranslate(self):
        self._tabs.setTabText(0, tr("v_title"))
        self._tabs.setTabText(1, tr("phon_rules_title"))
        self._editor.retranslate()
        self._rules.retranslate()

    def _mark(self):
        self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Согласные
# ═══════════════════════════════════════════════════════════════════════════════
class ConsonantsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        tabs = QTabWidget()
        root.addWidget(tabs)

        inv_w = QWidget()
        QVBoxLayout(inv_w)
        cols = [
            ColDef("c_symbol",      "symbol",      "str",  50),
            ColDef("c_place",       "place",       "combo", 140, _C_PLACE),
            ColDef("c_manner",      "manner",      "combo", 120, _C_MANNER),
            ColDef("c_voiced",      "voiced",      "bool",  55),
            ColDef("c_aspirated",   "aspirated",   "bool",  55),
            ColDef("c_palatalized", "palatalized", "bool",  55),
            ColDef("c_labialized",  "labialized",  "bool",  55),
            ColDef("c_ejective",    "ejective",    "bool",  55),
            ColDef("c_notes",       "notes",       "str",    0),
        ]
        self._editor = TableEditor(cols, Consonant, self._mark)
        inv_w.layout().addWidget(self._editor)

        self._rules = _RulesWidget(self._s)
        tabs.addTab(inv_w, tr("c_title"))
        tabs.addTab(self._rules, tr("phon_rules_title"))
        self._tabs = tabs

    def load(self):
        self._editor.set_rows(self._s.lang.phonology.consonants)
        self._rules.load()

    def save(self):
        self._s.lang.phonology.consonants = self._editor.get_rows()
        self._rules.save()

    def retranslate(self):
        self._tabs.setTabText(0, tr("c_title"))
        self._tabs.setTabText(1, tr("phon_rules_title"))
        self._editor.retranslate()
        self._rules.retranslate()

    def _mark(self):
        self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Просодия
# ═══════════════════════════════════════════════════════════════════════════════
class ProsodySection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        # Тип ударения
        self._stress_type = QComboBox()
        for lk, v in (("pr_st_dynamic","dynamic"),("pr_st_pitch","pitch"),("pr_st_none","none")):
            self._stress_type.addItem(tr(lk), v)

        # Позиция ударения
        self._stress_pos = QComboBox()
        for lk, v in (("pr_sp_initial","fixed-initial"),("pr_sp_final","fixed-final"),
                      ("pr_sp_penult","penult"),("pr_sp_antepenult","antepenult"),
                      ("pr_sp_free","free")):
            self._stress_pos.addItem(tr(lk), v)

        # Тоны
        self._tone_count = QSpinBox()
        self._tone_count.setRange(0, 12)
        self._tone_count.setFixedWidth(60)

        self._tone_names = QLineEdit()

        # Долгота
        self._length_cb = QCheckBox()

        # Примечания
        self._notes = QTextEdit(); self._notes.setFixedHeight(80)

        self._l_st = QLabel(); self._l_sp = QLabel()
        self._l_tc = QLabel(); self._l_tn = QLabel()
        self._l_len = QLabel(); self._l_notes = QLabel()

        form.addRow(self._l_st,   self._stress_type)
        form.addRow(self._l_sp,   self._stress_pos)
        form.addRow(self._l_tc,   self._tone_count)
        form.addRow(self._l_tn,   self._tone_names)
        form.addRow(self._l_len,  self._length_cb)
        form.addRow(self._l_notes,self._notes)
        root.addLayout(form)
        root.addStretch()

        for w in (self._stress_type, self._stress_pos):
            w.currentIndexChanged.connect(self._mark)
        self._tone_count.valueChanged.connect(self._mark)
        self._tone_names.textChanged.connect(self._mark)
        self._length_cb.toggled.connect(self._mark)
        self._notes.textChanged.connect(self._mark)
        self._retranslate_labels()

    def _retranslate_labels(self):
        self._l_st.setText(tr("pr_stress_type"))
        self._l_sp.setText(tr("pr_stress_pos"))
        self._l_tc.setText(tr("pr_tone_count"))
        self._l_tn.setText(tr("pr_tone_names"))
        self._l_len.setText(tr("pr_length_phonemic"))
        self._l_notes.setText(tr("pr_notes"))

    def load(self):
        p = self._s.lang.phonology.prosody
        _set_combo(self._stress_type, p.stress_type)
        _set_combo(self._stress_pos,  p.stress_position)
        self._tone_count.setValue(p.tone_count)
        self._tone_names.setText(", ".join(p.tone_names))
        self._length_cb.setChecked(p.length_phonemic)
        self._notes.setPlainText(p.notes)

    def save(self):
        p = self._s.lang.phonology.prosody
        p.stress_type     = self._stress_type.currentData()
        p.stress_position = self._stress_pos.currentData()
        p.tone_count      = self._tone_count.value()
        p.tone_names      = [t.strip() for t in self._tone_names.text().split(",") if t.strip()]
        p.length_phonemic = self._length_cb.isChecked()
        p.notes           = self._notes.toPlainText()

    def retranslate(self):
        self._retranslate_labels()
        _retranslate_combo(self._stress_type,
            [("pr_st_dynamic","dynamic"),("pr_st_pitch","pitch"),("pr_st_none","none")])
        _retranslate_combo(self._stress_pos,
            [("pr_sp_initial","fixed-initial"),("pr_sp_final","fixed-final"),
             ("pr_sp_penult","penult"),("pr_sp_antepenult","antepenult"),
             ("pr_sp_free","free")])

    def _mark(self):
        self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Фонотактика
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# 4. Фонотактика
# ═══════════════════════════════════════════════════════════════════════════════
class PhonotacticsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        # Шаблоны слогов (несколько через пробел или запятую)
        self._syllable = QLineEdit()
        self._syllable.setPlaceholderText(tr("pt_syllable_ph"))
        self._l_syl = QLabel()
        form.addRow(self._l_syl, self._syllable)

        # Пояснение
        hint = QLabel(tr("pt_syllable_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        form.addRow("", hint)

        # Максимальные кластеры
        onset_row = QHBoxLayout()
        self._max_onset = QSpinBox()
        self._max_onset.setRange(0, 6)
        self._max_onset.setFixedWidth(60)
        self._max_coda = QSpinBox()
        self._max_coda.setRange(0, 6)
        self._max_coda.setFixedWidth(60)
        self._l_mo = QLabel()
        self._l_mc = QLabel()
        onset_row.addWidget(self._l_mo)
        onset_row.addWidget(self._max_onset)
        onset_row.addSpacing(20)
        onset_row.addWidget(self._l_mc)
        onset_row.addWidget(self._max_coda)
        onset_row.addStretch()
        form.addRow("", onset_row)

        # Сингармонизм
        harmony_row = QHBoxLayout()
        self._vharmony = QCheckBox()
        self._harmony_type = QComboBox()
        self._harmony_type.addItem(tr("pt_harmony_vowel"), "vowel")
        self._harmony_type.addItem(tr("pt_harmony_cons"), "consonant")
        self._harmony_type.setEnabled(False)
        self._l_vh = QLabel()
        self._l_ht = QLabel()
        harmony_row.addWidget(self._l_vh)
        harmony_row.addWidget(self._vharmony)
        harmony_row.addSpacing(20)
        harmony_row.addWidget(self._l_ht)
        harmony_row.addWidget(self._harmony_type)
        harmony_row.addStretch()
        form.addRow("", harmony_row)
        self._vharmony.toggled.connect(self._harmony_type.setEnabled)

        # Запрещённые кластеры
        self._forbidden = QTextEdit()
        self._forbidden.setFixedHeight(80)
        self._forbidden.setPlaceholderText(tr("pt_forbidden_ph"))
        self._l_fb = QLabel()
        form.addRow(self._l_fb, self._forbidden)

        # Примечания
        self._notes = QTextEdit()
        self._notes.setFixedHeight(80)
        self._notes.setPlaceholderText(tr("pt_notes_ph"))
        self._l_no = QLabel()
        form.addRow(self._l_no, self._notes)

        root.addLayout(form)
        root.addStretch()

        # Сигналы
        self._syllable.textChanged.connect(self._mark)
        self._max_onset.valueChanged.connect(self._mark)
        self._max_coda.valueChanged.connect(self._mark)
        self._vharmony.toggled.connect(self._mark)
        self._harmony_type.currentIndexChanged.connect(self._mark)
        self._forbidden.textChanged.connect(self._mark)
        self._notes.textChanged.connect(self._mark)

        self._retranslate_labels()

    def _retranslate_labels(self):
        self._l_syl.setText(tr("pt_syllable"))
        self._l_mo.setText(tr("pt_max_onset"))
        self._l_mc.setText(tr("pt_max_coda"))
        self._l_vh.setText(tr("pt_vharmony"))
        self._l_ht.setText(tr("pt_harmony_type"))
        self._l_fb.setText(tr("pt_forbidden"))
        self._l_no.setText(tr("pt_notes"))
        self._syllable.setPlaceholderText(tr("pt_syllable_ph"))
        self._forbidden.setPlaceholderText(tr("pt_forbidden_ph"))
        self._notes.setPlaceholderText(tr("pt_notes_ph"))

    def load(self):
        pt = self._s.lang.phonology.phonotactics
        # Поддержка множественных шаблонов: в модели храним как список, в UI — строка через пробел
        if isinstance(pt.syllable_templates, list):
            self._syllable.setText(" ".join(pt.syllable_templates))
        else:
            # Обратная совместимость со старым форматом
            self._syllable.setText(pt.syllable_template if hasattr(pt, 'syllable_template') else "CV")

        self._max_onset.setValue(pt.max_onset)
        self._max_coda.setValue(pt.max_coda)
        self._vharmony.setChecked(pt.vowel_harmony)
        self._harmony_type.setEnabled(pt.vowel_harmony)
        _set_combo(self._harmony_type, pt.harmony_type)
        self._forbidden.setPlainText("\n".join(pt.forbidden_clusters))
        self._notes.setPlainText(pt.notes)

    def save(self):
        pt = self._s.lang.phonology.phonotactics
        # Парсим шаблоны: разделители — пробел, запятая, точка с запятой
        raw = self._syllable.text().strip()
        if raw:
            # Разделяем по пробелам, запятым, точкам с запятой
            import re
            templates = re.split(r'[ ,;]+', raw)
            pt.syllable_templates = [t.strip() for t in templates if t.strip()]
        else:
            pt.syllable_templates = ["CV"]

        pt.max_onset = self._max_onset.value()
        pt.max_coda = self._max_coda.value()
        pt.vowel_harmony = self._vharmony.isChecked()
        pt.harmony_type = self._harmony_type.currentData()
        pt.forbidden_clusters = [line.strip() for line in self._forbidden.toPlainText().split("\n") if line.strip()]
        pt.notes = self._notes.toPlainText()

    def retranslate(self):
        self._retranslate_labels()
        _retranslate_combo(self._harmony_type, [
            ("pt_harmony_vowel", "vowel"),
            ("pt_harmony_cons", "consonant")
        ])

    def _mark(self):
        self._s.mark_dirty()


# ── утилиты ──────────────────────────────────────────────────────────────────
def _set_combo(combo: QComboBox, value: str):
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)

def _retranslate_combo(combo: QComboBox, items: list[tuple[str,str]]):
    cur = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    for lk, v in items:
        combo.addItem(tr(lk), v)
    idx = combo.findData(cur)
    if idx >= 0:
        combo.setCurrentIndex(idx)
    combo.blockSignals(False)
