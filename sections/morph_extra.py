"""
Четыре недоделанных раздела морфологии и синтаксиса:
  VerbCatsSection, AdjectiveSection, NumeralSection, AgreementSection
Данные хранятся в Language.morphology (в поле notes каждой GramCategoryGroup
и в отдельных полях Morphology — добавляем через расширение dict в JSON).
Для простоты используем отдельный dict extra в Storage.lang — он уже есть
в model через **kwargs → нет. Используем pragmatics.notes как scratch-pad? Нет.
Правильнее: добавим поле extra: dict в Language и сохраним туда.
"""
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.i18n import tr


# ── Language.extra ─────────────────────────────────────────────────────────
# Мы добавим поле extra: dict в Language. Пока используем хелпер:
def _get(storage, *keys):
    d = storage.lang.__dict__.get("extra", {})
    for k in keys:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if isinstance(d, (str, int, bool)) else d

def _set(storage, value, *keys):
    if not hasattr(storage.lang, "extra") or not isinstance(storage.lang.extra, dict):
        storage.lang.extra = {}
    d = storage.lang.extra
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value
    storage.mark_dirty()

def _exget(storage, section, key, default=""):
    ex = getattr(storage.lang, "extra", {}) or {}
    return ex.get(section, {}).get(key, default)

def _exset(storage, section, key, value):
    if not hasattr(storage.lang, "extra") or not isinstance(storage.lang.extra, dict):
        storage.lang.extra = {}
    storage.lang.extra.setdefault(section, {})[key] = value
    storage.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Глагольные категории
# ═══════════════════════════════════════════════════════════════════════════
class VerbCatsSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(8,8,8,8)
        tabs = QTabWidget(); self._tabs = tabs; root.addWidget(tabs)

        # ── Время ────────────────────────────────────────────────────────
        tw = QWidget(); tf = QFormLayout(tw); tf.setSpacing(8); tf.setContentsMargins(12,12,12,12)
        self._tense_count = QSpinBox(); self._tense_count.setRange(0,12); self._tense_count.setFixedWidth(60)
        self._tense_names = QLineEdit()
        self._tense_past  = QLineEdit(); self._tense_past.setPlaceholderText("ближнее, дальнее, мифологическое")
        self._tense_fut   = QLineEdit(); self._tense_fut.setPlaceholderText("ближнее, отдалённое")
        self._tense_notes = QTextEdit(); self._tense_notes.setFixedHeight(70)
        self._l_tc = QLabel(); self._l_tn = QLabel(); self._l_tp = QLabel()
        self._l_tf = QLabel(); self._l_tno = QLabel()
        tf.addRow(self._l_tc, self._tense_count)
        tf.addRow(self._l_tn, self._tense_names)
        tf.addRow(self._l_tp, self._tense_past)
        tf.addRow(self._l_tf, self._tense_fut)
        tf.addRow(self._l_tno, self._tense_notes)

        # ── Вид ──────────────────────────────────────────────────────────
        aw = QWidget(); af = QFormLayout(aw); af.setSpacing(8); af.setContentsMargins(12,12,12,12)
        self._asp_types = QLineEdit(); self._asp_types.setPlaceholderText("совершенный, несовершенный, прогрессив, хабитуалис")
        self._asp_notes = QTextEdit(); self._asp_notes.setFixedHeight(80)
        self._l_at = QLabel(); self._l_an = QLabel()
        af.addRow(self._l_at, self._asp_types)
        af.addRow(self._l_an, self._asp_notes)

        # ── Наклонение ───────────────────────────────────────────────────
        mw = QWidget(); mf = QFormLayout(mw); mf.setSpacing(8); mf.setContentsMargins(12,12,12,12)
        self._mood_types = QLineEdit(); self._mood_types.setPlaceholderText("индикатив, императив, субъюнктив, кондиционалис, оптатив")
        self._mood_notes = QTextEdit(); self._mood_notes.setFixedHeight(80)
        self._l_mt = QLabel(); self._l_mn = QLabel()
        mf.addRow(self._l_mt, self._mood_types)
        mf.addRow(self._l_mn, self._mood_notes)

        # ── Залог ────────────────────────────────────────────────────────
        vw = QWidget(); vf = QFormLayout(vw); vf.setSpacing(8); vf.setContentsMargins(12,12,12,12)
        self._voice_types = QLineEdit(); self._voice_types.setPlaceholderText("актив, пассив, медиопассив, каузатив, реципрок")
        self._voice_notes = QTextEdit(); self._voice_notes.setFixedHeight(80)
        self._l_vt = QLabel(); self._l_vn = QLabel()
        vf.addRow(self._l_vt, self._voice_types)
        vf.addRow(self._l_vn, self._voice_notes)

        # ── Согласование и прочее ────────────────────────────────────────
        xw = QWidget(); xf = QFormLayout(xw); xf.setSpacing(8); xf.setContentsMargins(12,12,12,12)
        self._agr_subj = QCheckBox(); self._agr_obj = QCheckBox(); self._evid = QCheckBox()
        self._agr_notes = QTextEdit(); self._agr_notes.setFixedHeight(70)
        self._vc_notes  = QTextEdit(); self._vc_notes.setFixedHeight(70)
        self._l_as = QLabel(); self._l_ao = QLabel(); self._l_ev = QLabel()
        self._l_an2 = QLabel(); self._l_vcn = QLabel()
        xf.addRow(self._l_as,  self._agr_subj)
        xf.addRow(self._l_ao,  self._agr_obj)
        xf.addRow(self._l_ev,  self._evid)
        xf.addRow(self._l_an2, self._agr_notes)
        xf.addRow(self._l_vcn, self._vc_notes)

        tabs.addTab(tw, ""); tabs.addTab(aw, "")
        tabs.addTab(mw, ""); tabs.addTab(vw, ""); tabs.addTab(xw, "")
        self._relabel()

        for w in (self._tense_names, self._tense_past, self._tense_fut,
                  self._asp_types, self._mood_types, self._voice_types,
                  self._agr_notes, self._vc_notes):
            w.textChanged.connect(self._mark)
        for w in (self._tense_notes, self._asp_notes, self._mood_notes, self._voice_notes):
            w.textChanged.connect(self._mark)
        for w in (self._agr_subj, self._agr_obj, self._evid):
            w.toggled.connect(self._mark)
        self._tense_count.valueChanged.connect(self._mark)

    def _relabel(self):
        self._tabs.setTabText(0, tr("vc_tab_tense")); self._tabs.setTabText(1, tr("vc_tab_aspect"))
        self._tabs.setTabText(2, tr("vc_tab_mood"));  self._tabs.setTabText(3, tr("vc_tab_voice"))
        self._tabs.setTabText(4, tr("vc_agr_notes").rstrip(":"))
        self._l_tc.setText(tr("vc_tense_count")); self._l_tn.setText(tr("vc_tense_names"))
        self._l_tp.setText(tr("vc_tense_past_grades")); self._l_tf.setText(tr("vc_tense_fut_grades"))
        self._l_tno.setText(tr("vc_notes"))
        self._l_at.setText(tr("vc_aspect_types")); self._l_an.setText(tr("vc_aspect_notes"))
        self._l_mt.setText(tr("vc_mood_types"));   self._l_mn.setText(tr("vc_mood_notes"))
        self._l_vt.setText(tr("vc_voice_types"));  self._l_vn.setText(tr("vc_voice_notes"))
        self._l_as.setText(tr("vc_agr_subject")); self._l_ao.setText(tr("vc_agr_object"))
        self._l_ev.setText(tr("vc_evid_in_verb"))
        self._l_an2.setText(tr("vc_agr_notes")); self._l_vcn.setText(tr("vc_notes"))

    def load(self):
        S = "verb_cats"
        self._tense_count.setValue(int(_exget(self._s, S, "tense_count", 0)))
        self._tense_names.setText(_exget(self._s, S, "tense_names"))
        self._tense_past.setText(_exget(self._s, S, "tense_past"))
        self._tense_fut.setText(_exget(self._s, S, "tense_fut"))
        self._tense_notes.setPlainText(_exget(self._s, S, "tense_notes"))
        self._asp_types.setText(_exget(self._s, S, "asp_types"))
        self._asp_notes.setPlainText(_exget(self._s, S, "asp_notes"))
        self._mood_types.setText(_exget(self._s, S, "mood_types"))
        self._mood_notes.setPlainText(_exget(self._s, S, "mood_notes"))
        self._voice_types.setText(_exget(self._s, S, "voice_types"))
        self._voice_notes.setPlainText(_exget(self._s, S, "voice_notes"))
        self._agr_subj.setChecked(bool(_exget(self._s, S, "agr_subj", False)))
        self._agr_obj.setChecked(bool(_exget(self._s, S, "agr_obj", False)))
        self._evid.setChecked(bool(_exget(self._s, S, "evid", False)))
        self._agr_notes.setPlainText(_exget(self._s, S, "agr_notes"))
        self._vc_notes.setPlainText(_exget(self._s, S, "notes"))

    def save(self):
        S = "verb_cats"
        _exset(self._s, S, "tense_count", self._tense_count.value())
        _exset(self._s, S, "tense_names", self._tense_names.text())
        _exset(self._s, S, "tense_past",  self._tense_past.text())
        _exset(self._s, S, "tense_fut",   self._tense_fut.text())
        _exset(self._s, S, "tense_notes", self._tense_notes.toPlainText())
        _exset(self._s, S, "asp_types",   self._asp_types.text())
        _exset(self._s, S, "asp_notes",   self._asp_notes.toPlainText())
        _exset(self._s, S, "mood_types",  self._mood_types.text())
        _exset(self._s, S, "mood_notes",  self._mood_notes.toPlainText())
        _exset(self._s, S, "voice_types", self._voice_types.text())
        _exset(self._s, S, "voice_notes", self._voice_notes.toPlainText())
        _exset(self._s, S, "agr_subj",    self._agr_subj.isChecked())
        _exset(self._s, S, "agr_obj",     self._agr_obj.isChecked())
        _exset(self._s, S, "evid",        self._evid.isChecked())
        _exset(self._s, S, "agr_notes",   self._agr_notes.toPlainText())
        _exset(self._s, S, "notes",       self._vc_notes.toPlainText())

    def retranslate(self): self._relabel()
    def _mark(self): self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Прилагательное
# ═══════════════════════════════════════════════════════════════════════════
_ADJ_DEG = [("adj_deg_none","none"),("adj_deg_synthetic","synthetic"),
            ("adj_deg_analytic","analytic"),("adj_deg_both","both")]

class AdjectiveSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(8)
        form = QFormLayout(); form.setSpacing(8)

        self._agr    = QCheckBox()
        self._agr_g  = QCheckBox(); self._agr_n = QCheckBox(); self._agr_c = QCheckBox()
        self._deg    = QComboBox()
        for lk, v in _ADJ_DEG: self._deg.addItem(tr(lk), v)
        self._pred   = QCheckBox(); self._subs = QCheckBox()
        self._notes  = QTextEdit(); self._notes.setFixedHeight(100)

        self._l_agr = QLabel(); self._l_ag = QLabel(); self._l_an = QLabel()
        self._l_ac  = QLabel(); self._l_deg = QLabel(); self._l_pred = QLabel()
        self._l_subs= QLabel(); self._l_no = QLabel()

        form.addRow(self._l_agr, self._agr)
        form.addRow(self._l_ag,  self._agr_g)
        form.addRow(self._l_an,  self._agr_n)
        form.addRow(self._l_ac,  self._agr_c)
        form.addRow(self._l_deg, self._deg)
        form.addRow(self._l_pred,self._pred)
        form.addRow(self._l_subs,self._subs)
        form.addRow(self._l_no,  self._notes)
        root.addLayout(form); root.addStretch()

        for w in (self._agr,self._agr_g,self._agr_n,self._agr_c,self._pred,self._subs):
            w.toggled.connect(self._mark)
        self._deg.currentIndexChanged.connect(self._mark)
        self._notes.textChanged.connect(self._mark)
        self._relabel()

    def _relabel(self):
        self._l_agr.setText(tr("adj_agreement")); self._l_ag.setText(tr("adj_agr_gender"))
        self._l_an.setText(tr("adj_agr_number")); self._l_ac.setText(tr("adj_agr_case"))
        self._l_deg.setText(tr("adj_degrees")); self._l_pred.setText(tr("adj_predicative"))
        self._l_subs.setText(tr("adj_substantive")); self._l_no.setText(tr("adj_notes"))

    def _rc(self, key, default=False):
        return bool(_exget(self._s, "adj", key, default))

    def load(self):
        self._agr.setChecked(self._rc("agr"))
        self._agr_g.setChecked(self._rc("agr_g")); self._agr_n.setChecked(self._rc("agr_n"))
        self._agr_c.setChecked(self._rc("agr_c"))
        v = _exget(self._s, "adj", "deg", "none")
        idx = self._deg.findData(v); self._deg.setCurrentIndex(idx if idx>=0 else 0)
        self._pred.setChecked(self._rc("pred")); self._subs.setChecked(self._rc("subs"))
        self._notes.setPlainText(_exget(self._s, "adj", "notes"))

    def save(self):
        for key, w in (("agr",self._agr),("agr_g",self._agr_g),("agr_n",self._agr_n),
                        ("agr_c",self._agr_c),("pred",self._pred),("subs",self._subs)):
            _exset(self._s, "adj", key, w.isChecked())
        _exset(self._s, "adj", "deg",   self._deg.currentData())
        _exset(self._s, "adj", "notes", self._notes.toPlainText())

    def retranslate(self):
        self._relabel()
        cur = self._deg.currentData()
        self._deg.blockSignals(True); self._deg.clear()
        for lk, v in _ADJ_DEG: self._deg.addItem(tr(lk), v)
        idx = self._deg.findData(cur); self._deg.setCurrentIndex(idx if idx>=0 else 0)
        self._deg.blockSignals(False)

    def _mark(self): self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Числительное
# ═══════════════════════════════════════════════════════════════════════════
_NUM_BASES = [("num_base_10","10"),("num_base_20","20"),
              ("num_base_12","12"),("num_base_60","60"),("num_base_other","other")]

class NumeralSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(8)
        form = QFormLayout(); form.setSpacing(8)

        self._base   = QComboBox()
        for lk, v in _NUM_BASES: self._base.addItem(tr(lk), v)
        self._custom = QLineEdit(); self._custom.setPlaceholderText("напр. 8")
        self._has_ord= QCheckBox(); self._has_frac= QCheckBox(); self._has_dist= QCheckBox()
        self._ord_how= QLineEdit(); self._ord_how.setPlaceholderText("суффикс -ий, или супплетив")
        self._notes  = QTextEdit(); self._notes.setFixedHeight(100)

        self._l_base=QLabel(); self._l_cust=QLabel(); self._l_ord=QLabel()
        self._l_frac=QLabel(); self._l_dist=QLabel(); self._l_oh=QLabel(); self._l_no=QLabel()
        form.addRow(self._l_base, self._base)
        form.addRow(self._l_cust, self._custom)
        form.addRow(self._l_ord,  self._has_ord)
        form.addRow(self._l_frac, self._has_frac)
        form.addRow(self._l_dist, self._has_dist)
        form.addRow(self._l_oh,   self._ord_how)
        form.addRow(self._l_no,   self._notes)
        root.addLayout(form); root.addStretch()

        self._base.currentIndexChanged.connect(self._mark)
        self._custom.textChanged.connect(self._mark)
        for w in (self._has_ord,self._has_frac,self._has_dist): w.toggled.connect(self._mark)
        self._ord_how.textChanged.connect(self._mark); self._notes.textChanged.connect(self._mark)
        self._relabel()

    def _relabel(self):
        self._l_base.setText(tr("num_system")); self._l_cust.setText(tr("num_base_custom"))
        self._l_ord.setText(tr("num_has_ordinal")); self._l_frac.setText(tr("num_has_fraction"))
        self._l_dist.setText(tr("num_has_distrib")); self._l_oh.setText(tr("num_ordinal_how"))
        self._l_no.setText(tr("num_notes"))

    def load(self):
        v = _exget(self._s,"num","base","10")
        idx = self._base.findData(v); self._base.setCurrentIndex(idx if idx>=0 else 0)
        self._custom.setText(_exget(self._s,"num","custom"))
        self._has_ord.setChecked(bool(_exget(self._s,"num","has_ord",False)))
        self._has_frac.setChecked(bool(_exget(self._s,"num","has_frac",False)))
        self._has_dist.setChecked(bool(_exget(self._s,"num","has_dist",False)))
        self._ord_how.setText(_exget(self._s,"num","ord_how"))
        self._notes.setPlainText(_exget(self._s,"num","notes"))

    def save(self):
        _exset(self._s,"num","base",   self._base.currentData())
        _exset(self._s,"num","custom", self._custom.text())
        _exset(self._s,"num","has_ord",self._has_ord.isChecked())
        _exset(self._s,"num","has_frac",self._has_frac.isChecked())
        _exset(self._s,"num","has_dist",self._has_dist.isChecked())
        _exset(self._s,"num","ord_how", self._ord_how.text())
        _exset(self._s,"num","notes",   self._notes.toPlainText())

    def retranslate(self):
        self._relabel()
        cur = self._base.currentData()
        self._base.blockSignals(True); self._base.clear()
        for lk,v in _NUM_BASES: self._base.addItem(tr(lk), v)
        idx = self._base.findData(cur); self._base.setCurrentIndex(idx if idx>=0 else 0)
        self._base.blockSignals(False)

    def _mark(self): self._s.mark_dirty()


# ═══════════════════════════════════════════════════════════════════════════
# Синтаксическое согласование
# ═══════════════════════════════════════════════════════════════════════════
class AgreementSection(BaseSection):

    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(8)
        form = QFormLayout(); form.setSpacing(8)

        self._vs = QCheckBox(); self._vo = QCheckBox()
        self._an = QCheckBox(); self._dn = QCheckBox(); self._rc = QCheckBox()
        self._notes = QTextEdit(); self._notes.setFixedHeight(120)

        self._l_vs=QLabel(); self._l_vo=QLabel(); self._l_an=QLabel()
        self._l_dn=QLabel(); self._l_rc=QLabel(); self._l_no=QLabel()
        form.addRow(self._l_vs, self._vs); form.addRow(self._l_vo, self._vo)
        form.addRow(self._l_an, self._an); form.addRow(self._l_dn, self._dn)
        form.addRow(self._l_rc, self._rc); form.addRow(self._l_no, self._notes)
        root.addLayout(form); root.addStretch()

        for w in (self._vs,self._vo,self._an,self._dn,self._rc): w.toggled.connect(self._mark)
        self._notes.textChanged.connect(self._mark)
        self._relabel()

    def _relabel(self):
        self._l_vs.setText(tr("agr_verb_subj")); self._l_vo.setText(tr("agr_verb_obj"))
        self._l_an.setText(tr("agr_adj_noun"));  self._l_dn.setText(tr("agr_det_noun"))
        self._l_rc.setText(tr("agr_rel_clause")); self._l_no.setText(tr("agr_notes"))

    def load(self):
        for key, w in (("vs",self._vs),("vo",self._vo),("an",self._an),
                        ("dn",self._dn),("rc",self._rc)):
            w.setChecked(bool(_exget(self._s,"agr",key,False)))
        self._notes.setPlainText(_exget(self._s,"agr","notes"))

    def save(self):
        for key, w in (("vs",self._vs),("vo",self._vo),("an",self._an),
                        ("dn",self._dn),("rc",self._rc)):
            _exset(self._s,"agr",key,w.isChecked())
        _exset(self._s,"agr","notes",self._notes.toPlainText())

    def retranslate(self): self._relabel()
    def _mark(self): self._s.mark_dirty()
