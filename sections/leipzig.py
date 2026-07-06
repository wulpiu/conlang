"""
Генератор корней по списку Лейпциг-Джакарты (100 базовых слов) + возможность загрузки своего списка.
Использует настройки фонотактики для создания реалистичных слов.
"""
import csv
import random
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.base_section import BaseSection
from core.i18n import get_lang, tr
from core.model import Word

try:
    from pymorphy3 import MorphAnalyzer
    MORPH_AVAILABLE = True
except ImportError:
    MORPH_AVAILABLE = False


# ── Полный список Лейпциг-Джакарты (100 слов) с частями речи ────────────────
LJ_LIST = [
    ("1", "рука", "hand", "noun"),
    ("2", "левый", "left", "adjective"),
    ("3", "правый", "right", "adjective"),
    ("4", "нога", "foot/leg", "noun"),
    ("5", "колено", "knee", "noun"),
    ("6", "идти пешком", "walk", "verb"),
    ("7", "дорога", "road", "noun"),
    ("8", "прийти", "come", "verb"),
    ("9", "лежать", "lie", "verb"),
    ("10", "сидеть", "sit", "verb"),
    ("11", "стоять", "stand", "verb"),
    ("12", "человек", "person", "noun"),
    ("13", "мужчина", "man", "noun"),
    ("14", "женщина", "woman", "noun"),
    ("15", "ребёнок", "child", "noun"),
    ("16", "муж", "husband", "noun"),
    ("17", "жена", "wife", "noun"),
    ("18", "мать", "mother", "noun"),
    ("19", "отец", "father", "noun"),
    ("20", "дом", "house", "noun"),
    ("21", "живот", "belly", "noun"),
    ("22", "шея", "neck", "noun"),
    ("23", "грудь", "breast", "noun"),
    ("24", "сердце", "heart", "noun"),
    ("25", "печень", "liver", "noun"),
    ("26", "пить", "drink", "verb"),
    ("27", "есть", "eat", "verb"),
    ("28", "кусать", "bite", "verb"),
    ("29", "видеть", "see", "verb"),
    ("30", "слышать", "hear", "verb"),
    ("31", "знать", "know", "verb"),
    ("32", "спать", "sleep", "verb"),
    ("33", "умирать", "die", "verb"),
    ("34", "убивать", "kill", "verb"),
    ("35", "плавать", "swim", "verb"),
    ("36", "летать", "fly", "verb"),
    ("37", "идти", "walk/go", "verb"),
    ("38", "приходить", "come", "verb"),
    ("39", "лежать", "lie down", "verb"),
    ("40", "солнце", "sun", "noun"),
    ("41", "луна", "moon", "noun"),
    ("42", "звезда", "star", "noun"),
    ("43", "вода", "water", "noun"),
    ("44", "дождь", "rain", "noun"),
    ("45", "камень", "stone", "noun"),
    ("46", "песок", "sand", "noun"),
    ("47", "земля", "earth", "noun"),
    ("48", "облако", "cloud", "noun"),
    ("49", "дым", "smoke", "noun"),
    ("50", "огонь", "fire", "noun"),
    ("51", "пепел", "ash", "noun"),
    ("52", "гореть", "burn", "verb"),
    ("53", "тропа", "path", "noun"),
    ("54", "гора", "mountain", "noun"),
    ("55", "красный", "red", "adjective"),
    ("56", "зелёный", "green", "adjective"),
    ("57", "жёлтый", "yellow", "adjective"),
    ("58", "белый", "white", "adjective"),
    ("59", "чёрный", "black", "adjective"),
    ("60", "ночь", "night", "noun"),
    ("61", "горячий", "hot", "adjective"),
    ("62", "холодный", "cold", "adjective"),
    ("63", "полный", "full", "adjective"),
    ("64", "новый", "new", "adjective"),
    ("65", "хороший", "good", "adjective"),
    ("66", "круглый", "round", "adjective"),
    ("67", "сухой", "dry", "adjective"),
    ("68", "имя", "name", "noun"),
    ("69", "говорить", "say", "verb"),
    ("70", "петь", "sing", "verb"),
    ("71", "играть", "play", "verb"),
    ("72", "плавать", "float", "verb"),
    ("73", "течь", "flow", "verb"),
    ("74", "замерзать", "freeze", "verb"),
    ("75", "набухать", "swell", "verb"),
    ("76", "солнце", "sun", "noun"),
    ("77", "дерево", "tree", "noun"),
    ("78", "палка", "stick", "noun"),
    ("79", "фрукт", "fruit", "noun"),
    ("80", "семя", "seed", "noun"),
    ("81", "лист", "leaf", "noun"),
    ("82", "корень", "root", "noun"),
    ("83", "кора", "bark", "noun"),
    ("84", "цветок", "flower", "noun"),
    ("85", "трава", "grass", "noun"),
    ("86", "верёвка", "rope", "noun"),
    ("87", "кожа", "skin", "noun"),
    ("88", "мясо", "meat", "noun"),
    ("89", "кровь", "blood", "noun"),
    ("90", "кость", "bone", "noun"),
    ("91", "жир", "fat", "noun"),
    ("92", "яйцо", "egg", "noun"),
    ("93", "рог", "horn", "noun"),
    ("94", "хвост", "tail", "noun"),
    ("95", "перо", "feather", "noun"),
    ("96", "волосы", "hair", "noun"),
    ("97", "голова", "head", "noun"),
    ("98", "ухо", "ear", "noun"),
    ("99", "глаз", "eye", "noun"),
    ("100", "нос", "nose", "noun"),
]

_DEFAULT_CONS = "p t k b d g m n s f v r l"
_DEFAULT_VOWELS = "a e i o u"


def _parse_template(template: str):
    """Разбирает шаблон типа "(C)VC" или "CVC" или "CV" в список позиций."""
    positions = []
    t = template.strip().upper()
    i = 0
    while i < len(t):
        ch = t[i]
        if ch == '(':
            j = t.find(')', i)
            if j == -1:
                i += 1
                continue
            inner = t[i+1:j]
            for c in inner:
                if c in ('C', 'V'):
                    positions.append((c, True))
            i = j + 1
        elif ch in ('C', 'V'):
            positions.append((ch, False))
            i += 1
        else:
            i += 1
    return positions


class LeipzigSection(BaseSection):

    def __init__(self, storage):
        self._custom_list: list[tuple[str, str, str, str]] = []
        self._current_list = LJ_LIST.copy()
        self._roots: list[str] = []
        super().__init__(storage)
        if MORPH_AVAILABLE:
            self._morph = MorphAnalyzer()
        else:
            self._morph = None

    def _get_pos_for_word(self, word: str, lang: str = "ru") -> str:
        """Определяет ID части речи по слову."""
        if lang == "ru" and self._morph:
            try:
                parsed = self._morph.parse(word)[0]
                pos_tag = parsed.tag.POS
                pos_map = {
                    'NOUN': 'noun', 'VERB': 'verb', 'INFN': 'verb',
                    'ADJF': 'adjective', 'ADJS': 'adjective',
                    'NUMR': 'numeral', 'ADVB': 'adverb',
                    'NPRO': 'pronoun', 'PREP': 'preposition',
                    'CONJ': 'conjunction', 'PRCL': 'particle',
                    'INTJ': 'interjection',
                }
                return pos_map.get(pos_tag, '')
            except Exception:
                return ''
        else:
            for _, ru, en, pos in self._current_list:
                if (lang == "ru" and ru == word) or (lang == "en" and en == word):
                    return pos
            return ''

    def _get_pos_display(self, pos_id: str) -> str:
        """Возвращает отображаемое название части речи из новой модели."""
        if pos_id in self._s.lang.pos_configs:
            config = self._s.lang.pos_configs[pos_id]
            return config.display(get_lang())
        lang = get_lang()
        pos_names_ru = {
            'noun': 'Сущ.', 'verb': 'Глаг.', 'adjective': 'Прил.',
            'numeral': 'Числ.', 'adverb': 'Нар.', 'pronoun': 'Мест.',
            'preposition': 'Пред.', 'conjunction': 'Союз',
            'particle': 'Част.', 'interjection': 'Межд.',
        }
        pos_names_en = {
            'noun': 'N', 'verb': 'V', 'adjective': 'Adj',
            'numeral': 'Num', 'adverb': 'Adv', 'pronoun': 'Pron',
            'preposition': 'Prep', 'conjunction': 'Conj',
            'particle': 'Prt', 'interjection': 'Int',
        }
        return pos_names_ru.get(pos_id, pos_id) if lang == "ru" else pos_names_en.get(pos_id, pos_id)

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        gen_group = QGroupBox(tr("lj_gen_settings"))
        gf = QFormLayout(gen_group)
        gf.setSpacing(6)

        self._template = QLineEdit()
        self._template.setPlaceholderText(tr("lj_template_ph"))
        self._l_tmpl = QLabel()
        gf.addRow(self._l_tmpl, self._template)

        self._use_phonotactics = QCheckBox(tr("lj_use_phonotactics"))
        self._use_phonotactics.setChecked(True)
        self._use_phonotactics.toggled.connect(self._on_use_phonotactics)
        gf.addRow("", self._use_phonotactics)

        syl_row = QHBoxLayout()
        self._syl_min = QSpinBox()
        self._syl_min.setRange(1, 5)
        self._syl_min.setValue(1)
        self._syl_max = QSpinBox()
        self._syl_max.setRange(1, 5)
        self._syl_max.setValue(2)
        self._l_syl = QLabel()
        syl_row.addWidget(self._l_syl)
        syl_row.addWidget(self._syl_min)
        syl_row.addWidget(QLabel("—"))
        syl_row.addWidget(self._syl_max)
        syl_row.addStretch()
        gf.addRow("", syl_row)

        root.addWidget(gen_group)

        inv_group = QGroupBox(tr("lj_inv_settings"))
        inf = QFormLayout(inv_group)
        inf.setSpacing(6)

        self._cons = QLineEdit(_DEFAULT_CONS)
        self._vowels = QLineEdit(_DEFAULT_VOWELS)
        self._l_cons = QLabel()
        self._l_vow = QLabel()
        inf.addRow(self._l_cons, self._cons)
        inf.addRow(self._l_vow, self._vowels)

        self._use_inv = QCheckBox(tr("lj_use_inventory"))
        self._use_inv.toggled.connect(self._on_use_inv)
        inf.addRow("", self._use_inv)

        root.addWidget(inv_group)

        opt_group = QGroupBox(tr("lj_opt_settings"))
        opf = QFormLayout(opt_group)
        opf.setSpacing(6)

        self._check_clusters = QCheckBox(tr("lj_check_clusters"))
        self._check_clusters.setChecked(True)
        self._auto_pos = QCheckBox(tr("lj_auto_pos"))
        self._auto_pos.setChecked(True)
        if not MORPH_AVAILABLE:
            self._auto_pos.setEnabled(False)
            self._auto_pos.setToolTip(tr("lj_morph_unavailable"))

        opf.addRow("", self._check_clusters)
        opf.addRow("", self._auto_pos)
        root.addWidget(opt_group)

        list_btn_row = QHBoxLayout()
        self._btn_load_list = QPushButton(tr("lj_load_list"))
        self._btn_reset_list = QPushButton(tr("lj_reset_list"))
        self._btn_load_list.clicked.connect(self._load_custom_list)
        self._btn_reset_list.clicked.connect(self._reset_to_default)
        list_btn_row.addWidget(self._btn_load_list)
        list_btn_row.addWidget(self._btn_reset_list)
        list_btn_row.addStretch()
        self._lbl_list_info = QLabel(tr("lj_list_info").format(len(self._current_list)))
        self._lbl_list_info.setStyleSheet("color: #666; font-size: 10px;")
        list_btn_row.addWidget(self._lbl_list_info)
        root.addLayout(list_btn_row)

        btn_row = QHBoxLayout()
        self._btn_gen = QPushButton(tr("lj_generate"))
        self._btn_copy = QPushButton(tr("lj_copy_all"))
        self._btn_import = QPushButton(tr("lj_import_lex"))
        self._btn_gen.setFixedHeight(32)
        self._btn_gen.clicked.connect(self._generate_all)
        self._btn_copy.clicked.connect(self._copy_all)
        self._btn_import.clicked.connect(self._import_to_lex)
        for b in (self._btn_gen, self._btn_copy, self._btn_import):
            btn_row.addWidget(b)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(5)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setAlternatingRowColors(True)
        hh = self._tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(0, 40)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(3, 80)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._tbl.setColumnWidth(4, 40)
        root.addWidget(self._tbl)

        self._relabel()
        self._on_use_phonotactics(True)
        self._rebuild_table()

    def _relabel(self):
        self._tbl.setHorizontalHeaderLabels([
            tr("lj_col_num"), tr("lj_col_meaning"),
            tr("lj_col_root"), tr("lj_col_pos"), "",
        ])
        self._l_tmpl.setText(tr("lj_template_lbl"))
        self._l_syl.setText(tr("lj_syllables"))
        self._l_cons.setText(tr("lj_consonants_lbl"))
        self._l_vow.setText(tr("lj_vowels_lbl"))
        self._use_phonotactics.setText(tr("lj_use_phonotactics"))
        self._use_inv.setText(tr("lj_use_inventory"))
        self._check_clusters.setText(tr("lj_check_clusters"))
        self._auto_pos.setText(tr("lj_auto_pos"))
        self._btn_load_list.setText(tr("lj_load_list"))
        self._btn_reset_list.setText(tr("lj_reset_list"))
        self._btn_gen.setText(tr("lj_generate"))
        self._btn_copy.setText(tr("lj_copy_all"))
        self._btn_import.setText(tr("lj_import_lex"))
        self._lbl_list_info.setText(tr("lj_list_info").format(len(self._current_list)))

    def _rebuild_table(self):
        """Перестраивает таблицу на основе текущего списка."""
        self._tbl.setRowCount(len(self._current_list))
        lang = get_lang()

        for i, (num, ru, en, pos) in enumerate(self._current_list):
            self._tbl.setItem(i, 0, QTableWidgetItem(str(num if num else i+1)))
            meaning = ru if lang == "ru" else en
            self._tbl.setItem(i, 1, QTableWidgetItem(meaning))

            root = self._roots[i] if i < len(self._roots) else ""
            self._tbl.setItem(i, 2, QTableWidgetItem(root))

            pos_item = QTableWidgetItem(self._get_pos_display(pos))
            pos_item.setFlags(pos_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            pos_item.setForeground(Qt.GlobalColor.darkGray)
            self._tbl.setItem(i, 3, pos_item)

            regen = QPushButton(tr("lj_regen_one"))
            regen.setFixedHeight(22)
            regen.clicked.connect(lambda _, row=i: self._regen_one(row))
            self._tbl.setCellWidget(i, 4, regen)

        if len(self._roots) != len(self._current_list):
            self._roots = [""] * len(self._current_list)

    def _load_custom_list(self):
        """Загружает пользовательский список из CSV или TXT файла."""
        path, _ = QFileDialog.getOpenFileName(
            self, tr("lj_load_list_title"), "",
            "CSV/TXT files (*.csv *.txt);;All files (*.*)"
        )
        if not path:
            return

        try:
            new_list = []
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.csv'):
                    reader = csv.reader(f)
                    rows = list(reader)
                else:
                    rows = [line.strip().split('\t') for line in f if line.strip()]

                for i, row in enumerate(rows):
                    if not row:
                        continue

                    num = str(i + 1)
                    if len(row) >= 3:
                        num = row[0].strip()
                        ru = row[1].strip() if len(row) > 1 else ""
                        en = row[2].strip() if len(row) > 2 else ""
                        pos = row[3].strip() if len(row) > 3 else ""
                    elif len(row) == 2:
                        ru = row[0].strip()
                        en = row[1].strip()
                        pos = ""
                    elif len(row) == 1:
                        ru = en = row[0].strip()
                        pos = ""
                    else:
                        continue

                    if ru or en:
                        if not pos and self._auto_pos.isChecked():
                            pos = self._get_pos_for_word(ru, "ru")
                        new_list.append((num, ru, en, pos))

            if new_list:
                self._current_list = new_list
                self._roots = [""] * len(self._current_list)
                self._rebuild_table()
                self._lbl_list_info.setText(tr("lj_list_info").format(len(self._current_list)))
                self._s.mark_dirty()
                QMessageBox.information(self, tr("lj_load_list_title"),
                                       tr("lj_list_loaded").format(len(new_list)))
            else:
                QMessageBox.warning(self, tr("lj_load_list_title"), tr("lj_list_empty"))

        except Exception as e:
            QMessageBox.critical(self, tr("lj_load_list_title"),
                                tr("lj_list_load_error").format(str(e)))

    def _reset_to_default(self):
        """Сбрасывает список на стандартный Лейпциг-Джакарта."""
        self._current_list = LJ_LIST.copy()
        self._roots = [""] * len(self._current_list)
        self._rebuild_table()
        self._lbl_list_info.setText(tr("lj_list_info").format(len(self._current_list)))
        self._s.mark_dirty()

    def _on_use_phonotactics(self, checked: bool):
        self._template.setEnabled(not checked)
        if checked:
            pt = self._s.lang.phonology.phonotactics
            templates = getattr(pt, 'syllable_templates', ["CV"])
            if isinstance(templates, list):
                self._template.setText(" ".join(templates))
            else:
                self._template.setText("CV")

    def _on_use_inv(self, checked: bool):
        if checked:
            ph = self._s.lang.phonology
            cons = [c.symbol for c in ph.consonants if c.symbol]
            vowels = [v.symbol for v in ph.vowels if v.symbol]
            if cons:
                self._cons.setText(" ".join(cons))
            if vowels:
                self._vowels.setText(" ".join(vowels))
        self._cons.setEnabled(not checked)
        self._vowels.setEnabled(not checked)

    def _get_templates(self) -> list[str]:
        raw = self._template.text().strip()
        if not raw:
            return ["CV"]
        return [t.strip() for t in re.split(r'[ ,;]+', raw) if t.strip()]

    def _get_pool(self):
        cons = self._cons.text().split()
        vowels = self._vowels.text().split()
        return cons, vowels

    def _is_valid_word(self, word: str) -> bool:
        if not self._check_clusters.isChecked():
            return True
        pt = self._s.lang.phonology.phonotactics
        for cluster in pt.forbidden_clusters:
            if cluster in word:
                return False
        return True

    def _gen_syllable(self, positions, consonants, vowels):
        result = []
        for ch_type, optional in positions:
            if optional and random.random() < 0.4:
                continue
            pool = consonants if ch_type == 'C' else vowels
            if pool:
                result.append(random.choice(pool))
        return "".join(result)

    def _gen_root(self, templates, syl_min, syl_max, consonants, vowels, max_attempts=100):
        parsed = [_parse_template(t) for t in templates]
        parsed = [p for p in parsed if p]
        if not parsed:
            return "?"

        for _ in range(max_attempts):
            n = random.randint(syl_min, max(syl_min, syl_max))
            syllables = []
            for _ in range(n):
                pos = random.choice(parsed)
                syllables.append(self._gen_syllable(pos, consonants, vowels))
            word = "".join(syllables)
            if self._is_valid_word(word):
                return word
        return "".join(syllables) if syllables else "?"

    def _generate_all(self):
        templates = self._get_templates()
        smin = self._syl_min.value()
        smax = max(smin, self._syl_max.value())
        cons, vowels = self._get_pool()

        self._roots = [""] * len(self._current_list)
        for i in range(len(self._current_list)):
            root = self._gen_root(templates, smin, smax, cons, vowels)
            self._roots[i] = root
            item = self._tbl.item(i, 2)
            if item:
                item.setText(root)
        self._s.mark_dirty()

    def _regen_one(self, row: int):
        templates = self._get_templates()
        smin = self._syl_min.value()
        smax = max(smin, self._syl_max.value())
        cons, vowels = self._get_pool()
        root = self._gen_root(templates, smin, smax, cons, vowels)
        self._roots[row] = root
        item = self._tbl.item(row, 2)
        if item:
            item.setText(root)
        self._s.mark_dirty()

    def _copy_all(self):
        lines = []
        lang = get_lang()
        for i, (num, ru, en, pos) in enumerate(self._current_list):
            root = self._roots[i] if i < len(self._roots) else ""
            meaning = ru if lang == "ru" else en
            lines.append(f"{num}\t{meaning}\t{root}\t{pos}")
        QApplication.clipboard().setText("\n".join(lines))

    def _import_to_lex(self):
        count = 0
        skipped_exists = 0
        skipped_empty = 0
        lang = get_lang()

        for i in range(len(self._current_list)):
            item = self._tbl.item(i, 2)
            if item:
                self._roots[i] = item.text().strip()

        auto_pos = self._auto_pos.isChecked()

        for i, (_, ru, en, default_pos) in enumerate(self._current_list):
            root = self._roots[i]
            if not root:
                skipped_empty += 1
                continue

            localword = ru if lang == "ru" else en

            exists = any(w.conword == root for w in self._s.lang.words)
            if exists:
                skipped_exists += 1
                continue

            if auto_pos:
                if lang == "ru" and self._morph:
                    pos_id = self._get_pos_for_word(ru, "ru")
                else:
                    pos_id = default_pos
            else:
                pos_id = ""

            try:
                pronunciation = self._s.lang.phonology.generate_pronunciation(root)
            except Exception:
                pronunciation = root

            w = Word(
                conword=root,
                localword=localword,
                lemma=localword.lower(),
                pos_id=pos_id,
                pronunciation=pronunciation,
            )
            self._s.lang.words.append(w)
            count += 1

        self._s.mark_dirty()

        if count > 0:
            msg = tr("lj_imported_ok").format(count)
            if skipped_exists > 0:
                msg += f"\n{tr('lj_skipped_exists').format(skipped_exists)}"
            if skipped_empty > 0:
                msg += f"\n{tr('lj_skipped_empty').format(skipped_empty)}"
            QMessageBox.information(self, tr("nav_leipzig"), msg)
        else:
            if skipped_exists > 0:
                QMessageBox.information(self, tr("nav_leipzig"),
                    tr("lj_all_exist").format(skipped_exists))
            elif skipped_empty > 0:
                QMessageBox.warning(self, tr("nav_leipzig"),
                    tr("lj_no_roots"))
            else:
                QMessageBox.information(self, tr("nav_leipzig"),
                    tr("lj_nothing_to_import"))

    def load(self):
        ex = _exget_raw(self._s, "leipzig")
        if isinstance(ex, dict):
            self._template.setText(ex.get("template", "CVC"))
            self._syl_min.setValue(int(ex.get("syl_min", 1)))
            self._syl_max.setValue(int(ex.get("syl_max", 2)))
            self._cons.setText(ex.get("cons", _DEFAULT_CONS))
            self._vowels.setText(ex.get("vowels", _DEFAULT_VOWELS))
            self._use_phonotactics.setChecked(ex.get("use_phonotactics", True))
            self._check_clusters.setChecked(ex.get("check_clusters", True))
            self._auto_pos.setChecked(ex.get("auto_pos", True))

            custom = ex.get("custom_list", [])
            if custom:
                self._current_list = [tuple(item) for item in custom]
            else:
                self._current_list = LJ_LIST.copy()

            saved_roots = ex.get("roots", [])
            self._roots = saved_roots + [""] * (len(self._current_list) - len(saved_roots))
            self._roots = self._roots[:len(self._current_list)]

            self._rebuild_table()
            self._lbl_list_info.setText(tr("lj_list_info").format(len(self._current_list)))
            self._on_use_phonotactics(self._use_phonotactics.isChecked())

    def save(self):
        for i in range(len(self._current_list)):
            item = self._tbl.item(i, 2)
            if item and i < len(self._roots):
                self._roots[i] = item.text().strip()

        _exset_raw(self._s, "leipzig", {
            "template": self._template.text(),
            "syl_min": self._syl_min.value(),
            "syl_max": self._syl_max.value(),
            "cons": self._cons.text(),
            "vowels": self._vowels.text(),
            "use_phonotactics": self._use_phonotactics.isChecked(),
            "check_clusters": self._check_clusters.isChecked(),
            "auto_pos": self._auto_pos.isChecked(),
            "custom_list": self._current_list if self._current_list != LJ_LIST else [],
            "roots": self._roots,
        })

    def retranslate(self):
        self._relabel()
        self._rebuild_table()


# ── утилиты для extra ─────────────────────────────────────────────────────
def _exget_raw(storage, section):
    ex = getattr(storage.lang, "extra", {}) or {}
    return ex.get(section, {})

def _exset_raw(storage, section, value):
    if not hasattr(storage.lang, "extra") or not isinstance(storage.lang.extra, dict):
        storage.lang.extra = {}
    storage.lang.extra[section] = value
    storage.mark_dirty()
