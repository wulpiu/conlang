from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
)

from core.base_section import BaseSection
from core.i18n import tr

# ── данные для combo ──────────────────────────────────────────────────────────
_ORDERS = [("SOV","SOV"),("SVO","SVO"),("VSO","VSO"),
           ("VOS","VOS"),("OVS","OVS"),("OSV","OSV"),
           ("syn_order_free","free")]

_ALIGNS = [("syn_align_nom_acc","nominative-accusative"),
           ("syn_align_erg_abs","ergative-absolutive"),
           ("syn_align_active","active-stative"),
           ("syn_align_split","split")]

_HEAD = [("syn_head_init","head-initial"),
         ("syn_head_final","head-final"),
         ("syn_head_mixed","mixed")]

_ADJ  = [("syn_adj_before","before"),("syn_adj_after","after")]
_GEN  = [("syn_gen_before","before"),("syn_gen_after","after")]
_ADP  = [("syn_adp_pre","preposition"),("syn_adp_post","postposition"),("syn_adp_both","both")]
_Q    = [("syn_q_particle","particle"),("syn_q_intonation","intonation"),
         ("syn_q_inversion","inversion"),("syn_q_mixed","mixed")]
_NEG  = [("syn_neg_particle","particle"),("syn_neg_morpheme","morpheme"),
         ("syn_neg_double","double-negation")]
_REL  = [("syn_rel_pre","pre-nominal"),("syn_rel_post","post-nominal"),("syn_rel_nom","nominalization")]


def _set_combo(combo, value):
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)

def _retranslate_combo(combo, items):
    cur = combo.currentData()
    combo.blockSignals(True); combo.clear()
    for lk, v in items: combo.addItem(tr(lk) if not lk[0].isupper() else lk, v)
    idx = combo.findData(cur)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    combo.blockSignals(False)


def _make_combo(items):
    c = QComboBox()
    for lk, v in items:
        c.addItem(tr(lk) if not lk[0].isupper() else lk, v)
    return c


# ═══════════════════════════════════════════════════════════════════════════
# Порядок слов
# ═══════════════════════════════════════════════════════════════════════════
class WordOrderSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(10)
        form = QFormLayout(); form.setSpacing(8)

        self._order = _make_combo(_ORDERS)
        self._head  = _make_combo(_HEAD)
        self._adj   = _make_combo(_ADJ)
        self._gen   = _make_combo(_GEN)
        self._adp   = _make_combo(_ADP)
        self._q     = _make_combo(_Q)
        self._neg   = _make_combo(_NEG)
        self._rel   = _make_combo(_REL)
        self._notes = QTextEdit(); self._notes.setFixedHeight(80)

        self._labels = {}
        rows = [
            ("syn_order_lbl", self._order),
            ("syn_head_lbl",  self._head),
            ("syn_adj_lbl",   self._adj),
            ("syn_gen_lbl",   self._gen),
            ("syn_adp_lbl",   self._adp),
            ("syn_q_lbl",     self._q),
            ("syn_neg_lbl",   self._neg),
            ("syn_rel_lbl",   self._rel),
            ("syn_notes_lbl", self._notes),
        ]
        for lk, w in rows:
            lbl = QLabel(tr(lk))
            self._labels[lk] = lbl
            form.addRow(lbl, w)

        root.addLayout(form); root.addStretch()

        for w in (self._order, self._head, self._adj, self._gen,
                  self._adp, self._q, self._neg, self._rel):
            w.currentIndexChanged.connect(self._mark)
        self._notes.textChanged.connect(self._mark)

    def load(self):
        s = self._s.lang.syntax
        _set_combo(self._order, s.basic_order)
        _set_combo(self._head,  s.head_direction)
        _set_combo(self._adj,   s.adj_position)
        _set_combo(self._gen,   s.gen_position)
        _set_combo(self._adp,   s.adposition_type)
        _set_combo(self._q,     s.question_formation)
        _set_combo(self._neg,   s.negation_type)
        _set_combo(self._rel,   s.relative_clause)
        self._notes.setPlainText(s.notes)

    def save(self):
        s = self._s.lang.syntax
        s.basic_order        = self._order.currentData()
        s.head_direction     = self._head.currentData()
        s.adj_position       = self._adj.currentData()
        s.gen_position       = self._gen.currentData()
        s.adposition_type    = self._adp.currentData()
        s.question_formation = self._q.currentData()
        s.negation_type      = self._neg.currentData()
        s.relative_clause    = self._rel.currentData()
        s.notes              = self._notes.toPlainText()

    def retranslate(self):
        for lk, lbl in self._labels.items():
            lbl.setText(tr(lk))
        _retranslate_combo(self._order, _ORDERS)
        _retranslate_combo(self._head,  _HEAD)
        _retranslate_combo(self._adj,   _ADJ)
        _retranslate_combo(self._gen,   _GEN)
        _retranslate_combo(self._adp,   _ADP)
        _retranslate_combo(self._q,     _Q)
        _retranslate_combo(self._neg,   _NEG)
        _retranslate_combo(self._rel,   _REL)

    def _mark(self): self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Строй (эргативность)
# ═══════════════════════════════════════════════════════════════════════════
class AlignmentSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(10)
        form = QFormLayout(); form.setSpacing(8)

        self._align = _make_combo(_ALIGNS)
        self._split = QTextEdit(); self._split.setFixedHeight(80)
        self._agr   = QTextEdit(); self._agr.setFixedHeight(100)

        self._labels = {}
        for lk, w in [("syn_align_lbl", self._align),
                       ("syn_split_lbl", self._split),
                       ("syn_agr_lbl",   self._agr)]:
            lbl = QLabel(tr(lk)); self._labels[lk] = lbl
            form.addRow(lbl, w)

        root.addLayout(form); root.addStretch()
        self._align.currentIndexChanged.connect(self._mark)
        self._split.textChanged.connect(self._mark)
        self._agr.textChanged.connect(self._mark)

    def load(self):
        s = self._s.lang.syntax
        _set_combo(self._align, s.alignment)
        self._split.setPlainText(s.split_ergativity)
        self._agr.setPlainText(s.agreement_notes)

    def save(self):
        s = self._s.lang.syntax
        s.alignment         = self._align.currentData()
        s.split_ergativity  = self._split.toPlainText()
        s.agreement_notes   = self._agr.toPlainText()

    def retranslate(self):
        for lk, lbl in self._labels.items(): lbl.setText(tr(lk))
        _retranslate_combo(self._align, _ALIGNS)

    def _mark(self): self._s.mark_dirty()
