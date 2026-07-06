from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import get_lang, tr
from core.model import CompoundRule, Word
from core.table_editor import ColDef, TableEditor


def _forms_btn_label(): return "Формы ▾"


def _set_combo(combo, value):
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)

def _retranslate_combo(combo, items):
    cur = combo.currentData()
    combo.blockSignals(True); combo.clear()
    for lk, v in items: combo.addItem(tr(lk), v)
    idx = combo.findData(cur)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    combo.blockSignals(False)


# ═══════════════════════════════════════════════════════════════════════════
# Диалог редактирования слова
# ═══════════════════════════════════════════════════════════════════════════
class WordDialog(QDialog):
    def __init__(self, parent, storage, word: Word | None = None):
        super().__init__(parent)
        self._s = storage
        self._word = word
        self.setWindowTitle(tr("lex_dlg_edit") if word else tr("lex_dlg_new"))
        self.setMinimumWidth(500)
        self._build()
        if word:
            self._load(word)

    def _build(self):
        root = QVBoxLayout(self)
        tabs = QTabWidget()

        # ── вкладка «Основное» ────────────────────────────────────────────
        basic = QWidget(); form = QFormLayout(basic); form.setSpacing(8)

        self._conword = QLineEdit()
        self._local   = QLineEdit()
        self._lemma   = QLineEdit()
        self._lemma.setPlaceholderText(tr("lex_lemma_ph"))

        self._pos = QComboBox()
        self._pos.addItem("", "")
        for pos_id, config in self._s.lang.pos_configs.items():
            self._pos.addItem(config.display(get_lang()), pos_id)

        pronun_row = QWidget(); pr = QHBoxLayout(pronun_row); pr.setContentsMargins(0,0,0,0)
        self._pronun   = QLineEdit(); self._pronun.setEnabled(False)
        self._override = QCheckBox(tr("lex_override"))
        self._lbl_auto = QLabel(tr("lex_auto_ph")); self._lbl_auto.setStyleSheet("color:gray")
        pr.addWidget(self._pronun, 1); pr.addWidget(self._override); pr.addWidget(self._lbl_auto)

        self._definition = QTextEdit(); self._definition.setFixedHeight(70)
        self._etymology  = QLineEdit()
        self._notes      = QTextEdit(); self._notes.setFixedHeight(60)

        self._l_cw = QLabel(tr("lex_conword")); self._l_lc = QLabel(tr("lex_local"))
        self._l_lemma = QLabel(tr("lex_lemma"))
        self._l_ps = QLabel(tr("lex_pos"));     self._l_pr = QLabel(tr("lex_pronun"))
        self._l_df = QLabel(tr("lex_definition")); self._l_et = QLabel(tr("lex_etymology"))
        self._l_no = QLabel(tr("lex_notes"))

        form.addRow(self._l_cw, self._conword)
        form.addRow(self._l_lc, self._local)
        form.addRow(self._l_lemma, self._lemma)
        form.addRow(self._l_ps, self._pos)
        form.addRow(self._l_pr, pronun_row)
        form.addRow(self._l_df, self._definition)
        form.addRow(self._l_et, self._etymology)
        form.addRow(self._l_no, self._notes)

        # ── вкладка «Грамматика» ──────────────────────────────────────────
        gram = QWidget(); gv = QVBoxLayout(gram); gv.setContentsMargins(8,8,8,8)
        gv.addWidget(QLabel(tr("lex_gram_vals")))
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner = QWidget(); self._gram_form = QFormLayout(inner)
        self._gram_combos: dict[str, QComboBox] = {}
        self._rebuild_gram_form()
        scroll.setWidget(inner)
        gv.addWidget(scroll)

        tabs.addTab(basic, tr("lex_tab_basic"))
        tabs.addTab(gram,  tr("lex_tab_gram"))
        root.addWidget(tabs)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                              QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)

        self._override.toggled.connect(self._on_override)
        self._conword.textChanged.connect(self._auto_pronun)

    def _rebuild_gram_form(self):
        while self._gram_form.rowCount():
            self._gram_form.removeRow(0)
        self._gram_combos.clear()
        for gc in self._s.lang.morphology.gram_categories:
            combo = QComboBox()
            combo.addItem("—", "")
            for v in gc.values:
                combo.addItem(v.name, v.name)
            self._gram_combos[gc.name] = combo
            self._gram_form.addRow(QLabel(gc.name + ":"), combo)

    def _on_override(self, checked):
        self._pronun.setEnabled(checked)
        self._lbl_auto.setVisible(not checked)
        if not checked:
            self._auto_pronun(self._conword.text())

    def _auto_pronun(self, text):
        if not self._override.isChecked():
            self._pronun.setText(self._s.lang.phonology.generate_pronunciation(text))

    def _load(self, w: Word):
        self._conword.setText(w.conword)
        self._local.setText(w.localword)
        self._lemma.setText(w.lemma or w.localword.lower())
        _set_combo(self._pos, w.pos_id)
        self._pronun.setText(w.pronunciation)
        self._override.setChecked(w.override_pronun)
        self._pronun.setEnabled(w.override_pronun)
        self._definition.setPlainText(w.definition)
        self._etymology.setText(w.etymology)
        self._notes.setPlainText(w.notes)
        for cat_name, val in w.gram_values.items():
            if cat_name in self._gram_combos:
                _set_combo(self._gram_combos[cat_name], val)

    def get_word(self) -> Word:
        w = Word(
            conword    = self._conword.text().strip(),
            localword  = self._local.text().strip(),
            lemma      = self._lemma.text().strip() or self._local.text().strip().lower(),
            pos_id     = self._pos.currentData() or "",
            pronunciation = self._pronun.text().strip(),
            override_pronun = self._override.isChecked(),
            definition = self._definition.toPlainText().strip(),
            etymology  = self._etymology.text().strip(),
            notes      = self._notes.toPlainText().strip(),
        )
        if not w.override_pronun:
            w.pronunciation = self._s.lang.phonology.generate_pronunciation(w.conword)
        w.gram_values = {k: c.currentData() for k, c in self._gram_combos.items()
                         if c.currentData()}
        return w


# ═══════════════════════════════════════════════════════════════════════════
# Раздел: Словарь
# ═══════════════════════════════════════════════════════════════════════════
class LexiconSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,8,8,8); root.setSpacing(4)

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("lex_search_ph"))
        self._search.textChanged.connect(self._populate)
        root.addWidget(self._search)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(5)
        self._tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        hh = self._tbl.horizontalHeader()
        for i, w in enumerate([100, 100, 110, 110, 0]):
            if w:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self._tbl.setColumnWidth(i, w)
            else:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self._tbl.doubleClicked.connect(self._edit)
        root.addWidget(self._tbl)

        brow = QHBoxLayout()
        self._btn_add  = QPushButton(tr("lex_add"))
        self._btn_edit = QPushButton(tr("lex_edit"))
        self._btn_del  = QPushButton(tr("lex_del"))
        self._btn_forms= QPushButton("Формы ▾")
        self._btn_edit.setEnabled(False); self._btn_del.setEnabled(False)
        self._btn_forms.setEnabled(False)
        for b in (self._btn_add, self._btn_edit, self._btn_del, self._btn_forms):
            brow.addWidget(b)
        brow.addStretch()
        root.addLayout(brow)

        self._btn_add.clicked.connect(self._add)
        self._btn_edit.clicked.connect(self._edit)
        self._btn_del.clicked.connect(self._del)
        self._btn_forms.clicked.connect(self._open_forms)
        self._tbl.itemSelectionChanged.connect(self._on_select)
        self._update_headers()

    def _update_headers(self):
        self._tbl.setHorizontalHeaderLabels([
            tr("lex_col_conword"), tr("lex_col_local"),
            tr("lex_col_pos"), tr("lex_col_pronun"), tr("lex_col_def"),
        ])

    def load(self):
        self._search.clear()
        self._populate()

    def save(self): pass

    def retranslate(self):
        self._search.setPlaceholderText(tr("lex_search_ph"))
        self._btn_add.setText(tr("lex_add"))
        self._btn_edit.setText(tr("lex_edit"))
        self._btn_del.setText(tr("lex_del"))
        self._update_headers()
        self._populate()

    def showEvent(self, event):
        super().showEvent(event)
        self._populate()

    def _populate(self):
        lang = get_lang()
        ft = self._search.text().lower().strip()

        self._visible: list[int] = []
        for i, w in enumerate(self._s.lang.words):
            if not ft:
                self._visible.append(i)
            elif ft in w.conword.lower() or ft in w.localword.lower():
                self._visible.append(i)

        self._tbl.setRowCount(len(self._visible))
        for row, idx in enumerate(self._visible):
            w = self._s.lang.words[idx]

            pos_label = w.pos_id
            if w.pos_id and w.pos_id in self._s.lang.pos_configs:
                pos_label = self._s.lang.pos_configs[w.pos_id].display(lang)

            for col, txt in enumerate([w.conword, w.localword, pos_label,
                                        w.pronunciation, w.definition]):
                item = QTableWidgetItem(txt[:80] if col == 4 else txt)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._tbl.setItem(row, col, item)

        self._tbl.resizeRowsToContents()
        self._btn_edit.setEnabled(False)
        self._btn_del.setEnabled(False)

    def _on_select(self):
        has = self._tbl.currentRow() >= 0
        self._btn_edit.setEnabled(has)
        self._btn_del.setEnabled(has)
        self._btn_forms.setEnabled(has)

    def _open_forms(self):
        from sections.paradigms import WordFormsDialog
        idx = self._selected_data_idx()
        if idx < 0:
            return
        dlg = WordFormsDialog(self, self._s, idx)
        dlg.exec()

    def _selected_data_idx(self) -> int:
        r = self._tbl.currentRow()
        if 0 <= r < len(self._visible):
            return self._visible[r]
        return -1

    def _add(self):
        dlg = WordDialog(self, self._s)
        if dlg.exec():
            w = dlg.get_word()
            if not w.conword:
                return
            if self._s.lang.word_unique and any(
                    x.conword == w.conword for x in self._s.lang.words):
                QMessageBox.warning(self, "", tr("lex_word_exists"))
                return
            self._s.lang.words.append(w)
            self._s.mark_dirty()
            self._populate()

    def _edit(self):
        idx = self._selected_data_idx()
        if idx < 0: return
        dlg = WordDialog(self, self._s, self._s.lang.words[idx])
        if dlg.exec():
            self._s.lang.words[idx] = dlg.get_word()
            self._s.mark_dirty()
            self._populate()

    def _del(self):
        idx = self._selected_data_idx()
        if idx < 0: return
        ans = QMessageBox.question(self, "", tr("confirm_del"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ans == QMessageBox.StandardButton.Yes:
            del self._s.lang.words[idx]
            self._s.mark_dirty()
            self._populate()


# ═══════════════════════════════════════════════════════════════════════════
# Раздел: Словообразование (только Словосложение и Конверсия/Сокращения)
# ═══════════════════════════════════════════════════════════════════════════
class WordFormationSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,8,8,8)
        tabs = QTabWidget(); self._tabs = tabs

        # ── Словосложение ─────────────────────────────────────────────────
        comp_w = QWidget(); QVBoxLayout(comp_w)
        comp_cols = [
            ColDef("wf_col_pattern", "pattern",     "str", 120),
            ColDef("wf_col_desc",    "description", "str",   0),
            ColDef("wf_col_example", "example",     "str", 160),
        ]
        self._comp_editor = TableEditor(comp_cols, CompoundRule, self._mark)
        comp_w.layout().addWidget(self._comp_editor)

        # ── Конверсия / сокращения ────────────────────────────────────────
        other_w = QWidget(); ov = QFormLayout(other_w); ov.setContentsMargins(12,12,12,12)
        self._conv = QTextEdit(); self._conv.setFixedHeight(100)
        self._abbr = QTextEdit(); self._abbr.setFixedHeight(100)
        self._l_conv = QLabel(); self._l_abbr = QLabel()
        ov.addRow(self._l_conv, self._conv)
        ov.addRow(self._l_abbr, self._abbr)
        self._conv.textChanged.connect(self._mark)
        self._abbr.textChanged.connect(self._mark)

        tabs.addTab(comp_w,  tr("wf_tab_compounds"))
        tabs.addTab(other_w, tr("wf_tab_other"))
        root.addWidget(tabs)
        self._relabel()

    def _relabel(self):
        self._tabs.setTabText(0, tr("wf_tab_compounds"))
        self._tabs.setTabText(1, tr("wf_tab_other"))
        self._l_conv.setText(tr("wf_conv_lbl"))
        self._l_abbr.setText(tr("wf_abbr_lbl"))

    def load(self):
        wf = self._s.lang.word_formation
        self._comp_editor.set_rows(wf.compound_rules)
        self._conv.setPlainText(wf.conversion_notes)
        self._abbr.setPlainText(wf.abbreviation_notes)

    def save(self):
        wf = self._s.lang.word_formation
        wf.compound_rules   = self._comp_editor.get_rows()
        wf.conversion_notes    = self._conv.toPlainText()
        wf.abbreviation_notes  = self._abbr.toPlainText()

    def retranslate(self):
        self._relabel()
        self._comp_editor.retranslate()

    def _mark(self): self._s.mark_dirty()
