from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from core.base_section import BaseSection
from core.i18n import tr


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
# Прагматика и дискурс
# ═══════════════════════════════════════════════════════════════════════════
_EVID = [("prag_evid_none","none"), ("prag_evid_verb","in-verb"),
         ("prag_evid_particle","particle"), ("prag_evid_other","other")]

class PragmaticsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16); root.setSpacing(8)
        form = QFormLayout(); form.setSpacing(8)

        self._sp    = QTextEdit(); self._sp.setFixedHeight(60)
        self._tm    = QTextEdit(); self._tm.setFixedHeight(60)
        self._ps    = QTextEdit(); self._ps.setFixedHeight(60)
        self._topic = QTextEdit(); self._topic.setFixedHeight(60)
        self._focus = QTextEdit(); self._focus.setFixedHeight(60)

        self._evid  = QComboBox()
        for lk, v in _EVID: self._evid.addItem(tr(lk), v)

        self._polite = QSpinBox(); self._polite.setRange(0, 10); self._polite.setFixedWidth(60)

        self._registers  = QTextEdit(); self._registers.setFixedHeight(80)
        self._registers.setPlaceholderText("Нейтральный=повседневная речь\nФормальный=официальные документы")
        self._discourse  = QLineEdit()
        self._notes      = QTextEdit(); self._notes.setFixedHeight(70)

        self._labels = {}
        rows = [
            ("prag_deixis_sp", self._sp),
            ("prag_deixis_tm", self._tm),
            ("prag_deixis_ps", self._ps),
            ("prag_topic",     self._topic),
            ("prag_focus",     self._focus),
            ("prag_evid",      self._evid),
            ("prag_polite",    self._polite),
            ("prag_registers", self._registers),
            ("prag_discourse", self._discourse),
            ("prag_notes",     self._notes),
        ]
        for lk, w in rows:
            lbl = QLabel(tr(lk)); self._labels[lk] = lbl
            form.addRow(lbl, w)

        root.addLayout(form); root.addStretch()

        for w in (self._sp, self._tm, self._ps, self._topic,
                  self._focus, self._notes, self._registers):
            w.textChanged.connect(self._mark)
        self._evid.currentIndexChanged.connect(self._mark)
        self._polite.valueChanged.connect(self._mark)
        self._discourse.textChanged.connect(self._mark)

    def load(self):
        p = self._s.lang.pragmatics
        self._sp.setPlainText(p.deixis_spatial)
        self._tm.setPlainText(p.deixis_temporal)
        self._ps.setPlainText(p.deixis_personal)
        self._topic.setPlainText(p.topic_marking)
        self._focus.setPlainText(p.focus_marking)
        _set_combo(self._evid, p.evidentiality)
        self._polite.setValue(p.politeness_levels)
        lines = [f"{r.name}={r.description}" if r.description else r.name
                 for r in p.registers]
        self._registers.setPlainText("\n".join(lines))
        self._discourse.setText(", ".join(p.discourse_markers))
        self._notes.setPlainText(p.notes)

    def save(self):
        from core.model import Register
        p = self._s.lang.pragmatics
        p.deixis_spatial   = self._sp.toPlainText()
        p.deixis_temporal  = self._tm.toPlainText()
        p.deixis_personal  = self._ps.toPlainText()
        p.topic_marking    = self._topic.toPlainText()
        p.focus_marking    = self._focus.toPlainText()
        p.evidentiality    = self._evid.currentData()
        p.politeness_levels= self._polite.value()
        p.registers = []
        for line in self._registers.toPlainText().split("\n"):
            line = line.strip()
            if not line: continue
            if "=" in line:
                name, desc = line.split("=", 1)
                p.registers.append(Register(name=name.strip(), description=desc.strip()))
            else:
                p.registers.append(Register(name=line))
        p.discourse_markers = [t.strip() for t in self._discourse.text().split(",") if t.strip()]
        p.notes = self._notes.toPlainText()

    def retranslate(self):
        for lk, lbl in self._labels.items(): lbl.setText(tr(lk))
        _retranslate_combo(self._evid, _EVID)

    def _mark(self): self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Письменность
# ═══════════════════════════════════════════════════════════════════════════
_SCRIPT_TYPES = [("wr_type_alpha","alphabetic"), ("wr_type_syll","syllabic"),
                 ("wr_type_cons","consonantal"),  ("wr_type_logo","logographic"),
                 ("wr_type_mixed","mixed")]

_DIRECTIONS   = [("wr_dir_ltr","ltr"), ("wr_dir_rtl","rtl"),
                 ("wr_dir_ttb","ttb"), ("wr_dir_boustro","boustrophedon")]

_NUMERALS     = [("wr_num_arabic","arabic"), ("wr_num_roman","roman"),
                 ("wr_num_custom","custom")]

class WritingSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16); root.setSpacing(8)
        form = QFormLayout(); form.setSpacing(8)

        self._type    = QComboBox()
        for lk, v in _SCRIPT_TYPES: self._type.addItem(tr(lk), v)

        self._dir     = QComboBox()
        for lk, v in _DIRECTIONS: self._dir.addItem(tr(lk), v)

        self._alphabet   = QLineEdit()
        self._diacr_cb   = QCheckBox()
        self._diacr_notes= QTextEdit(); self._diacr_notes.setFixedHeight(60)
        self._punct      = QTextEdit(); self._punct.setFixedHeight(60)

        self._numerals   = QComboBox()
        for lk, v in _NUMERALS: self._numerals.addItem(tr(lk), v)

        self._ortho      = QTextEdit(); self._ortho.setFixedHeight(80)

        self._labels = {}
        rows = [
            ("wr_type_lbl",       self._type),
            ("wr_dir_lbl",        self._dir),
            ("wr_alphabet_lbl",   self._alphabet),
            ("wr_diacritics_cb",  self._diacr_cb),
            ("wr_diacritics_lbl", self._diacr_notes),
            ("wr_punct_lbl",      self._punct),
            ("wr_numerals_lbl",   self._numerals),
            ("wr_ortho_lbl",      self._ortho),
        ]
        for lk, w in rows:
            lbl = QLabel(tr(lk)); self._labels[lk] = lbl
            form.addRow(lbl, w)

        root.addLayout(form); root.addStretch()

        for w in (self._type, self._dir, self._numerals):
            w.currentIndexChanged.connect(self._mark)
        self._alphabet.textChanged.connect(self._mark)
        self._diacr_cb.toggled.connect(self._mark)
        for w in (self._diacr_notes, self._punct, self._ortho):
            w.textChanged.connect(self._mark)

    def load(self):
        w = self._s.lang.writing
        _set_combo(self._type,    w.script_type)
        _set_combo(self._dir,     w.direction)
        _set_combo(self._numerals,w.numeral_system)
        self._alphabet.setText(w.alphabet)
        self._diacr_cb.setChecked(w.has_diacritics)
        self._diacr_notes.setPlainText(w.diacritics_notes)
        self._punct.setPlainText(w.punctuation_notes)
        self._ortho.setPlainText(w.orthography_notes)

    def save(self):
        w = self._s.lang.writing
        w.script_type        = self._type.currentData()
        w.direction          = self._dir.currentData()
        w.alphabet           = self._alphabet.text().strip()
        w.has_diacritics     = self._diacr_cb.isChecked()
        w.diacritics_notes   = self._diacr_notes.toPlainText()
        w.punctuation_notes  = self._punct.toPlainText()
        w.numeral_system     = self._numerals.currentData()
        w.orthography_notes  = self._ortho.toPlainText()

    def retranslate(self):
        for lk, lbl in self._labels.items(): lbl.setText(tr(lk))
        _retranslate_combo(self._type,     _SCRIPT_TYPES)
        _retranslate_combo(self._dir,      _DIRECTIONS)
        _retranslate_combo(self._numerals, _NUMERALS)

    def _mark(self): self._s.mark_dirty()
