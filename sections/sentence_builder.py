"""
Конструктор предложений с автоматическим переводом.
Пользователь вводит предложение на русском или английском,
система анализирует его, находит слова в лексиконе,
применяет парадигмы (включая флексию и служебные слова) и синтаксис,
выдаёт перевод на конланг.

Использует новую модель pos_configs и GrammaticalRelations.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.base_section import BaseSection
from core.grammatical_relations import (
    GrammaticalRelation,
    SentenceAnalysis,
    get_case_for_relation,
    get_default_position,
)
from core.i18n import get_lang, tr
from core.linguistic_data import CATEGORY_VALUES, get_value_display, get_value_id
from core.model import Word
from core.text_analyzer import TextAnalyzer, Token


class SentenceBuilderSection(BaseSection):

    def __init__(self, storage):
        super().__init__(storage)
        self._analyzer = None
        self._tokens: list[Token] = []
        self._sentence_analysis: SentenceAnalysis = None
        self._found_words: dict[int, Word | None] = {}
        self._translated_words: dict[int, str] = {}

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ── Заголовок и пояснение ───────────────────────────────────────────
        title = QLabel(tr("sb_title"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        root.addWidget(title)

        hint = QLabel(tr("sb_hint"))
        hint.setStyleSheet("color: #666; font-style: italic; margin-bottom: 8px;")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # ── Панель ввода ─────────────────────────────────────────────────────
        input_group = QGroupBox(tr("sb_input_label"))
        input_layout = QVBoxLayout(input_group)

        # Выбор языка
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(tr("sb_lang_label") + ":"))
        self._lang_ru = QRadioButton(tr("sb_lang_ru"))
        self._lang_en = QRadioButton(tr("sb_lang_en"))
        self._lang_ru.setChecked(True)
        lang_layout.addWidget(self._lang_ru)
        lang_layout.addWidget(self._lang_en)
        lang_layout.addStretch()
        input_layout.addLayout(lang_layout)

        # Поле ввода
        input_row = QHBoxLayout()
        self._input_text = QLineEdit()
        self._input_text.setPlaceholderText(tr("sb_input_ph"))
        self._input_text.returnPressed.connect(self._analyze)
        input_row.addWidget(self._input_text, 1)

        self._btn_analyze = QPushButton(tr("sb_analyze_btn"))
        self._btn_analyze.clicked.connect(self._analyze)
        input_row.addWidget(self._btn_analyze)

        input_layout.addLayout(input_row)
        root.addWidget(input_group)

        # ── Сплиттер для результатов ─────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Панель анализа ───────────────────────────────────────────────────
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(0, 0, 0, 0)

        self._analysis_lbl = QLabel(tr("sb_analysis_result"))
        self._analysis_lbl.setStyleSheet("font-weight: bold; margin-top: 8px;")
        analysis_layout.addWidget(self._analysis_lbl)

        self._analysis_tbl = QTableWidget()
        self._analysis_tbl.setColumnCount(5)
        self._analysis_tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._analysis_tbl.verticalHeader().setVisible(False)
        self._analysis_tbl.setAlternatingRowColors(True)
        ah = self._analysis_tbl.horizontalHeader()
        ah.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._analysis_tbl.setColumnWidth(0, 100)
        ah.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._analysis_tbl.setColumnWidth(1, 100)
        ah.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._analysis_tbl.setColumnWidth(2, 80)
        ah.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._analysis_tbl.setColumnWidth(3, 100)
        ah.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._analysis_tbl.setMinimumHeight(150)
        analysis_layout.addWidget(self._analysis_tbl)

        splitter.addWidget(analysis_widget)

        # ── Панель перевода ──────────────────────────────────────────────────
        translate_widget = QWidget()
        translate_layout = QVBoxLayout(translate_widget)
        translate_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка перевода
        self._btn_translate = QPushButton(tr("sb_translate_btn"))
        self._btn_translate.setFixedHeight(36)
        self._btn_translate.setEnabled(False)
        font = self._btn_translate.font()
        font.setBold(True)
        self._btn_translate.setFont(font)
        self._btn_translate.clicked.connect(self._translate)
        translate_layout.addWidget(self._btn_translate)

        # Таблица соответствия слов
        self._match_lbl = QLabel(tr("sb_lexicon_match"))
        self._match_lbl.setStyleSheet("font-weight: bold; margin-top: 8px;")
        translate_layout.addWidget(self._match_lbl)

        self._match_tbl = QTableWidget()
        self._match_tbl.setColumnCount(5)
        self._match_tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._match_tbl.verticalHeader().setVisible(False)
        self._match_tbl.setAlternatingRowColors(True)
        mh = self._match_tbl.horizontalHeader()
        mh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._match_tbl.setColumnWidth(0, 100)
        mh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._match_tbl.setColumnWidth(1, 120)
        mh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._match_tbl.setColumnWidth(2, 80)
        mh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._match_tbl.setColumnWidth(3, 80)
        mh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._match_tbl.setMinimumHeight(150)
        translate_layout.addWidget(self._match_tbl)

        # Кнопка добавления отсутствующих слов
        self._btn_add_missing = QPushButton(tr("sb_add_missing"))
        self._btn_add_missing.clicked.connect(self._add_missing_words)
        self._btn_add_missing.setEnabled(False)
        translate_layout.addWidget(self._btn_add_missing)

        splitter.addWidget(translate_widget)

        # ── Панель результата ────────────────────────────────────────────────
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(0, 0, 0, 0)

        self._result_lbl = QLabel(tr("sb_final_result"))
        self._result_lbl.setStyleSheet("font-weight: bold; margin-top: 8px;")
        result_layout.addWidget(self._result_lbl)

        result_box = QGroupBox()
        rb_layout = QVBoxLayout(result_box)

        self._result_text = QTextEdit()
        self._result_text.setReadOnly(True)
        self._result_text.setFixedHeight(80)
        self._result_text.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1a1a8c;
            background: #f5f5f5;
            padding: 8px;
        """)
        rb_layout.addWidget(self._result_text)

        copy_row = QHBoxLayout()
        copy_row.addStretch()
        self._btn_copy = QPushButton(tr("sb_copy_btn"))
        self._btn_copy.clicked.connect(self._copy_result)
        self._btn_copy.setEnabled(False)
        copy_row.addWidget(self._btn_copy)
        rb_layout.addLayout(copy_row)

        result_layout.addWidget(result_box)
        splitter.addWidget(result_widget)

        splitter.setSizes([200, 250, 150])
        root.addWidget(splitter)

        self._update_headers()

    def _update_headers(self):
        self._analysis_tbl.setHorizontalHeaderLabels([
            tr("sb_col_word"),
            tr("sb_col_lemma"),
            tr("sb_col_pos"),
            tr("sb_col_relation"),
            tr("sb_col_features"),
        ])
        self._match_tbl.setHorizontalHeaderLabels([
            tr("sb_col_lemma"),
            tr("sb_col_conword"),
            tr("sb_col_found"),
            tr("sb_col_rule"),
            tr("sb_col_fusion"),
        ])

    def _get_analyzer(self) -> TextAnalyzer:
        """Возвращает анализатор для выбранного языка."""
        lang = "ru" if self._lang_ru.isChecked() else "en"
        if self._analyzer is None or self._analyzer.lang != lang:
            try:
                self._analyzer = TextAnalyzer(lang)
            except RuntimeError as e:
                QMessageBox.warning(self, tr("sb_title"), str(e))
                self._analyzer = None
        return self._analyzer

    def _analyze(self):
        """Анализирует введённый текст."""
        text = self._input_text.text().strip()
        if not text:
            return

        analyzer = self._get_analyzer()
        if analyzer is None:
            return

        try:
            self._tokens = analyzer.analyze(text)
            self._build_sentence_analysis()
            self._display_analysis()
            self._btn_translate.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, tr("sb_title"), f"Ошибка анализа: {e}")

    def _build_sentence_analysis(self):
        """Строит синтаксический анализ предложения."""
        from core.grammatical_relations import SentenceAnalysis

        analysis = SentenceAnalysis()
        analysis.tokens = [t for t in self._tokens if not t.is_punctuation]

        if not analysis.tokens:
            self._sentence_analysis = analysis
            return

        # Простое определение отношений (пока без полноценного парсера)
        # Ищем глагол (предикат)
        verb_idx = -1
        for i, token in enumerate(analysis.tokens):
            if token.pos == 'verb':
                verb_idx = i
                break

        if verb_idx >= 0:
            # Глагол - корень предложения
            analysis.root_index = verb_idx
            analysis.relations.append(GrammaticalRelation(
                relation_type="pred",
                head_index=-1,
                dependent_index=verb_idx
            ))

            # Ищем субъект (первое существительное или местоимение перед глаголом)
            for i, token in enumerate(analysis.tokens):
                if i < verb_idx and token.pos in ('noun', 'pronoun'):
                    if token.has_feature('case', 'nom') or 'nom' not in str(token.features):
                        analysis.relations.append(GrammaticalRelation(
                            relation_type="subj",
                            head_index=verb_idx,
                            dependent_index=i
                        ))
                        break

            # Ищем объект (существительное после глагола)
            for i, token in enumerate(analysis.tokens):
                if i > verb_idx and token.pos in ('noun', 'pronoun'):
                    if token.has_feature('case', 'acc'):
                        analysis.relations.append(GrammaticalRelation(
                            relation_type="obj",
                            head_index=verb_idx,
                            dependent_index=i
                        ))
                        break

        self._sentence_analysis = analysis

    def _display_analysis(self):
        """Отображает результат анализа в таблице."""
        if not self._sentence_analysis:
            return

        words = self._sentence_analysis.tokens
        self._analysis_tbl.setRowCount(len(words))

        for i, token in enumerate(words):
            self._analysis_tbl.setItem(i, 0, QTableWidgetItem(token.word))
            self._analysis_tbl.setItem(i, 1, QTableWidgetItem(token.lemma))
            self._analysis_tbl.setItem(i, 2, QTableWidgetItem(self._get_pos_display(token.pos)))

            # Находим отношение для этого токена
            relation = ""
            for rel in self._sentence_analysis.relations:
                if rel.dependent_index == i:
                    relation = rel.relation_type
                    break
            self._analysis_tbl.setItem(i, 3, QTableWidgetItem(relation))

            features_str = ", ".join(f"{k}={v}" for k, v in token.features.items())
            self._analysis_tbl.setItem(i, 4, QTableWidgetItem(features_str))

    def _get_pos_display(self, pos_id: str) -> str:
        """Возвращает отображаемое название части речи."""
        if pos_id in self._s.lang.pos_configs:
            return self._s.lang.pos_configs[pos_id].display(get_lang())

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

    def _translate(self):
        """Выполняет перевод проанализированного предложения."""
        if not self._sentence_analysis:
            return

        self._found_words.clear()
        self._translated_words.clear()

        words = self._sentence_analysis.tokens
        missing_lemmas = []

        for i, token in enumerate(words):
            # Определяем синтаксическую роль
            relation = ""
            for rel in self._sentence_analysis.relations:
                if rel.dependent_index == i:
                    relation = rel.relation_type
                    break

            # Ищем слово в лексиконе по лемме
            found = self._find_word_by_lemma(token.lemma, token.pos)
            self._found_words[i] = found

            if found:
                # Применяем парадигму для получения правильной формы
                translated = self._apply_paradigm(found, token, relation)
                self._translated_words[i] = translated
            else:
                self._translated_words[i] = f"[{token.lemma}]"
                missing_lemmas.append(token.lemma)

        self._display_match_table(words)
        self._build_sentence(words)

        self._btn_add_missing.setEnabled(len(missing_lemmas) > 0)

        if missing_lemmas:
            QMessageBox.information(
                self, tr("sb_title"),
                tr("sb_missing_words").format(", ".join(set(missing_lemmas)))
            )

    def _find_word_by_lemma(self, lemma: str, pos: str) -> Word | None:
        """Ищет слово в лексиконе по лемме и части речи."""
        lemma_lower = lemma.lower()

        # Сначала ищем точное совпадение леммы и части речи
        for w in self._s.lang.words:
            if w.lemma.lower() == lemma_lower and w.pos_id == pos:
                return w

        # Затем только по лемме
        for w in self._s.lang.words:
            if w.lemma.lower() == lemma_lower:
                return w

        # Затем по переводу
        for w in self._s.lang.words:
            if w.localword.lower() == lemma_lower:
                return w

        return None

    def _apply_paradigm(self, word: Word, token: Token, relation: str) -> str:
        """Применяет парадигму к слову на основе грамматических признаков и синтаксической роли."""
        pos_config = self._s.lang.pos_configs.get(word.pos_id)
        if not pos_config:
            return word.conword

        # Определяем целевые значения для каждой категории
        target_values = {}

        # Из признаков токена
        for key, value in token.features.items():
            target_values[key] = value

        # Из синтаксической роли (определяем падеж)
        if relation:
            alignment = self._s.lang.syntax.alignment or "nominative-accusative"
            # Определяем, переходный ли глагол
            is_transitive = any(
                rel.relation_type == "obj" for rel in self._sentence_analysis.relations
            )
            case_value = get_case_for_relation(relation, alignment, is_transitive)
            if case_value:
                target_values['case'] = case_value

        # Собираем результат
        result = word.conword

        # Применяем категории в порядке приоритета
        ordered_categories = pos_config.category_order or list(pos_config.categories.keys())

        for cat_id in ordered_categories:
            if cat_id not in pos_config.categories:
                continue

            cat = pos_config.categories[cat_id]
            if not cat.enabled:
                continue

            # Ищем целевое значение для этой категории
            target_value = None
            if cat_id in target_values:
                target_value = target_values[cat_id]

            if not target_value:
                continue

            # Находим правило для целевого значения
            rule = None
            for value_id, r in cat.rules.items():
                if not r.enabled:
                    continue
                # Проверяем, соответствует ли значение целевому
                if self._value_matches(value_id, target_value, cat_id):
                    rule = r
                    break

            if rule:
                # Проверяем, есть ли флексия
                if rule.fusion_category and rule.fusion_value and rule.fusion_pattern:
                    # Проверяем, совпадает ли второе значение
                    fusion_target = target_values.get(rule.fusion_category)
                    if fusion_target and self._value_matches(rule.fusion_value, fusion_target, rule.fusion_category):
                        result = self._apply_rule(rule, result, use_fusion=True)
                        continue

                result = self._apply_rule(rule, result)

        return result

    def _value_matches(self, value_id: str, target: str, category_id: str) -> bool:
        """Проверяет, соответствует ли ID значения целевому значению."""
        if value_id.lower() == target.lower():
            return True

        # Проверяем через CATEGORY_VALUES
        for v in CATEGORY_VALUES.get(category_id, []):
            if get_value_id(v) == value_id:
                display = get_value_display(v, 'ru').lower()
                if target.lower() in display or display in target.lower():
                    return True
        return False

    def _apply_rule(self, rule, root: str, use_fusion: bool = False) -> str:
        """Применяет правило к корню."""
        if use_fusion:
            pattern = rule.fusion_pattern
        else:
            pattern = rule.affix_pattern

        if not pattern:
            return root

        if rule.affix_type == "function_word":
            # Ищем служебное слово
            fw = next((f for f in self._s.lang.function_words if f.form == pattern), None)
            if fw:
                if fw.position == "before":
                    return f"{pattern} {root}"
                else:
                    return f"{root} {pattern}"
            return f"{pattern} {root}"

        try:
            from sections.paradigms import AffixEngine
            return AffixEngine.apply(root, rule.affix_type, pattern)
        except Exception:
            return root + pattern

    def _display_match_table(self, words: list):
        """Отображает таблицу соответствия слов."""
        self._match_tbl.setRowCount(len(words))

        for i, token in enumerate(words):
            self._match_tbl.setItem(i, 0, QTableWidgetItem(token.lemma))

            found = self._found_words.get(i)
            if found:
                self._match_tbl.setItem(i, 1, QTableWidgetItem(found.conword))
                status = "✓"
                rule, fusion = self._get_rule_description(found, token)
            else:
                self._match_tbl.setItem(i, 1, QTableWidgetItem("—"))
                status = "✗"
                rule, fusion = "—", ""

            status_item = QTableWidgetItem(status)
            if found:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self._match_tbl.setItem(i, 2, status_item)
            self._match_tbl.setItem(i, 3, QTableWidgetItem(rule))
            self._match_tbl.setItem(i, 4, QTableWidgetItem(fusion))

    def _get_rule_description(self, word: Word, token: Token) -> tuple[str, str]:
        """Возвращает описание применённого правила и флексии."""
        pos_config = self._s.lang.pos_configs.get(word.pos_id)
        if not pos_config:
            return "—", ""

        rule_desc = ""
        fusion_desc = ""

        for cat_id, cat in pos_config.categories.items():
            if not cat.enabled:
                continue

            target = token.features.get(cat_id)
            if not target:
                continue

            for value_id, rule in cat.rules.items():
                if rule.enabled and self._value_matches(value_id, target, cat_id):
                    rule_desc = rule.affix_pattern
                    if rule.fusion_pattern:
                        fusion_desc = f"+{rule.fusion_pattern}"
                    break

        return rule_desc or "—", fusion_desc

    def _build_sentence(self, words: list):
        """Собирает предложение с учётом синтаксиса."""
        syntax = self._s.lang.syntax
        order = syntax.basic_order or "SVO"

        # Определяем позиции по синтаксическим отношениям
        parts_with_pos = []

        for i, token in enumerate(words):
            translated = self._translated_words.get(i, f"[{token.lemma}]")

            # Находим отношение
            relation = ""
            for rel in self._sentence_analysis.relations:
                if rel.dependent_index == i:
                    relation = rel.relation_type
                    break

            # Получаем позицию из универсальных правил
            position = get_default_position(relation, order) if relation else 99
            parts_with_pos.append((position, translated, relation))

        # Сортируем по позиции
        parts_with_pos.sort(key=lambda x: x[0])

        # Собираем предложение
        sentence = " ".join(p[1] for p in parts_with_pos)

        # Применяем фонологию
        try:
            sentence = self._s.lang.phonology.generate_pronunciation(sentence)
        except Exception:
            pass

        self._result_text.setText(sentence)
        self._btn_copy.setEnabled(True)

    def _add_missing_words(self):
        """Добавляет отсутствующие слова в лексикон."""
        words = self._sentence_analysis.tokens
        added = 0

        for i, token in enumerate(words):
            if self._found_words.get(i) is None:
                from core.model import Word

                root = self._generate_root()

                w = Word(
                    conword=root,
                    localword=token.word,
                    lemma=token.lemma,
                    pos_id=token.pos,
                    pronunciation=self._s.lang.phonology.generate_pronunciation(root),
                )
                self._s.lang.words.append(w)
                added += 1

        if added > 0:
            self._s.mark_dirty()
            QMessageBox.information(self, tr("sb_title"),
                                   tr("sb_added_words").format(added))
            self._translate()

    def _generate_root(self) -> str:
        """Генерирует простой корень для нового слова."""
        import random
        cons = [c.symbol for c in self._s.lang.phonology.consonants if c.symbol]
        vowels = [v.symbol for v in self._s.lang.phonology.vowels if v.symbol]

        if not cons:
            cons = ["p", "t", "k", "m", "n", "s"]
        if not vowels:
            vowels = ["a", "e", "i", "o", "u"]

        root = ""
        for _ in range(random.randint(2, 3)):
            root += random.choice(cons)
            root += random.choice(vowels)

        return root

    def _copy_result(self):
        """Копирует результат в буфер обмена."""
        text = self._result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)

    def load(self):
        pass

    def save(self):
        pass

    def retranslate(self):
        self._update_headers()
    def _apply_paradigm(self, word: Word, token: Token, relation: str) -> str:
        """Применяет парадигму к слову на основе грамматических признаков и синтаксической роли."""
        pos_config = self._s.lang.pos_configs.get(word.pos_id)
        if not pos_config:
            return word.conword

        # Определяем целевые значения
        target_values = self._get_target_values(token, relation, word)

        # Для прилагательного — находим существительное, с которым оно согласуется
        if word.pos_id == "adjective":
            head_noun = self._find_head_noun(token, relation)
            if head_noun:
                # Копируем признаки от существительного
                noun_word = self._found_words.get(head_noun["index"])
                if noun_word:
                    target_values.update(head_noun["features"])

        # Собираем результат
        result = word.conword

        # Применяем категории в порядке приоритета
        ordered_categories = pos_config.category_order or list(pos_config.categories.keys())

        for cat_id in ordered_categories:
            if cat_id not in pos_config.categories:
                continue

            cat = pos_config.categories[cat_id]
            if not cat.enabled:
                continue

            target_value = target_values.get(cat_id)
            if not target_value:
                continue

            rule = self._find_matching_rule(cat, target_value, cat_id)
            if rule:
                # Проверяем флексию
                if rule.fusion_category and rule.fusion_value and rule.fusion_pattern:
                    fusion_target = target_values.get(rule.fusion_category)
                    if fusion_target and self._value_matches(rule.fusion_value, fusion_target, rule.fusion_category):
                        result = self._apply_rule(rule, result, use_fusion=True)
                        continue

                result = self._apply_rule(rule, result)

        return result

    def _find_head_noun(self, token: Token, relation: str) -> dict | None:
        """Находит существительное, от которого зависит прилагательное."""
        if not self._sentence_analysis:
            return None

        # Ищем отношение "attr" где dependent = наш токен
        for rel in self._sentence_analysis.relations:
            if rel.relation_type == "attr" and rel.dependent_index == self._get_token_index(token):
                head_idx = rel.head_index
                if head_idx < len(self._sentence_analysis.tokens):
                    head_token = self._sentence_analysis.tokens[head_idx]
                    return {
                        "index": head_idx,
                        "features": head_token.features.copy()
                    }
        return None

    def _apply_rule(self, rule, root: str, use_fusion: bool = False) -> str:
        """Применяет правило к корню."""
        if use_fusion:
            pattern = rule.fusion_pattern
        else:
            pattern = rule.affix_pattern

        if not pattern:
            return root

        if rule.affix_type == "function_word":
            # Ищем служебное слово по ID или форме
            fw = None
            for f in self._s.lang.function_words:
                if f.form == pattern or getattr(f, 'id', '') == pattern:
                    fw = f
                    break

            if fw:
                if fw.position == "before":
                    return f"{fw.form} {root}"
                else:
                    return f"{root} {fw.form}"
            return f"{pattern} {root}"

        try:
            from sections.paradigms import AffixEngine
            return AffixEngine.apply(root, rule.affix_type, pattern)
        except Exception:
            if rule.affix_type == "prefix":
                return pattern + root
            else:
                return root + pattern

    def _get_target_values(self, token: Token, relation: str, word: Word) -> dict:
        """Определяет целевые значения для всех категорий."""
        target = {}

        # Из морфологического анализа
        for key, value in token.features.items():
            target[key] = value

        # Падеж из синтаксической роли
        if relation:
            alignment = self._s.lang.syntax.alignment or "nominative-accusative"
            is_transitive = self._sentence_analysis.has_object() if self._sentence_analysis else False

            if relation == "subj":
                if alignment == "ergative-absolutive" and is_transitive:
                    target['case'] = 'ergative'
                elif alignment == "ergative-absolutive":
                    target['case'] = 'absolutive'
                else:
                    target['case'] = 'nominative'
            elif relation == "obj":
                if alignment == "ergative-absolutive":
                    target['case'] = 'absolutive'
                else:
                    target['case'] = 'accusative'
            elif relation == "iobj":
                target['case'] = 'dative'

        # Род и число из словарной формы
        if word.gram_values:
            if 'gender' not in target:
                target['gender'] = word.gram_values.get('gender', '')
            if 'number' not in target:
                target['number'] = word.gram_values.get('number', '')

        return target
