"""
DNA Language — слепок состояния языка в компактной строке.
Позволяет экспортировать/импортировать все настройки языка одной строкой.
Формат: base64(gzip(json))

Содержит полноценные пресеты для:
- Русского (флективный, 6 падежей, 3 рода, 2 спряжения, вид глагола)
- Английского (аналитический, служебные слова)
- Баскского / Васконского (эргативный, полиперсональное согласование)
"""
import base64
import gzip
import json
from typing import Optional

from core.model import (
    Consonant,
    FunctionWord,
    GrammarRule,
    GrammaticalCategory,
    Language,
    PartOfSpeechConfig,
    Phonotactics,
    Pragmatics,
    Prosody,
    Register,
    Syntax,
    Vowel,
    Word,
    WritingSystem,
)

# ═══════════════════════════════════════════════════════════════════════════
# ПРЕСЕТ: РУССКИЙ ЯЗЫК (исправленный)
# ═══════════════════════════════════════════════════════════════════════════

def generate_russian_preset() -> Language:
    """Генерирует полноценный пресет русского языка с учётом спряжений и приоритетов."""
    lang = Language()
    lang.name = "Русский"
    lang.local_language = "Русский"
    lang.author = "ConLang Studio"
    lang.description = "Флективный славянский язык с трёхродовой системой, шестью падежами, двумя спряжениями, видом глагола"

    # ═══════════════════════════════════════════════════════════════════════
    # ФОНОЛОГИЯ
    # ═══════════════════════════════════════════════════════════════════════

    lang.phonology.vowels = [
        Vowel(symbol="а", height="low", backness="central", rounded=False),
        Vowel(symbol="э", height="mid", backness="front", rounded=False),
        Vowel(symbol="ы", height="high", backness="central", rounded=False),
        Vowel(symbol="о", height="mid", backness="back", rounded=True),
        Vowel(symbol="у", height="high", backness="back", rounded=True),
        Vowel(symbol="и", height="high", backness="front", rounded=False),
    ]

    lang.phonology.consonants = [
        Consonant(symbol="п", place="bilabial", manner="stop", voiced=False),
        Consonant(symbol="б", place="bilabial", manner="stop", voiced=True),
        Consonant(symbol="м", place="bilabial", manner="nasal", voiced=True),
        Consonant(symbol="ф", place="labiodental", manner="fricative", voiced=False),
        Consonant(symbol="в", place="labiodental", manner="fricative", voiced=True),
        Consonant(symbol="т", place="dental", manner="stop", voiced=False),
        Consonant(symbol="д", place="dental", manner="stop", voiced=True),
        Consonant(symbol="с", place="alveolar", manner="fricative", voiced=False),
        Consonant(symbol="з", place="alveolar", manner="fricative", voiced=True),
        Consonant(symbol="ц", place="alveolar", manner="affricate", voiced=False),
        Consonant(symbol="н", place="alveolar", manner="nasal", voiced=True),
        Consonant(symbol="л", place="alveolar", manner="lateral", voiced=True),
        Consonant(symbol="ш", place="postalveolar", manner="fricative", voiced=False),
        Consonant(symbol="ж", place="postalveolar", manner="fricative", voiced=True),
        Consonant(symbol="щ", place="postalveolar", manner="fricative", voiced=False, palatalized=True),
        Consonant(symbol="ч", place="postalveolar", manner="affricate", voiced=False, palatalized=True),
        Consonant(symbol="р", place="alveolar", manner="trill", voiced=True),
        Consonant(symbol="й", place="palatal", manner="approximant", voiced=True),
        Consonant(symbol="к", place="velar", manner="stop", voiced=False),
        Consonant(symbol="г", place="velar", manner="stop", voiced=True),
        Consonant(symbol="х", place="velar", manner="fricative", voiced=False),
    ]

    lang.phonology.prosody = Prosody(
        stress_type="dynamic",
        stress_position="free",
        tone_count=0,
        length_phonemic=False,
    )

    lang.phonology.phonotactics = Phonotactics(
        syllable_templates=["CVC", "CV", "VC", "CCVC", "CVCC"],
        max_onset=4,
        max_coda=4,
        vowel_harmony=False,
        forbidden_clusters=[],
    )

    # ═══════════════════════════════════════════════════════════════════════
    # ТИП ЯЗЫКА И СТРАТЕГИИ
    # ═══════════════════════════════════════════════════════════════════════

    lang.morphology.lang_type.primary = "fusional"
    lang.extra["lang_type_strategies"] = {
        "use_affixes": True,
        "use_particles": False,
        "use_fusion": True,
        "use_incorporation": False,
    }

    # ═══════════════════════════════════════════════════════════════════════
    # ТИПЫ МОРФЕМ
    # ═══════════════════════════════════════════════════════════════════════

    mt = lang.morphology.morpheme_types
    mt.has_prefixes = True
    mt.has_suffixes = True
    mt.has_postfixes = True
    mt.has_infixes = False
    mt.has_circumfixes = False
    mt.has_interfixes = True
    mt.has_transfixes = False
    mt.reduplication = "none"

    # ═══════════════════════════════════════════════════════════════════════
    # СИНТАКСИС
    # ═══════════════════════════════════════════════════════════════════════

    lang.syntax = Syntax(
        basic_order="SVO",
        alignment="nominative-accusative",
        head_direction="mixed",
        adj_position="before",
        gen_position="after",
        adposition_type="preposition",
        question_formation="intonation",
        negation_type="particle",
        relative_clause="post-nominal",
        agreement_notes="Прилагательные согласуются по роду, числу, падежу. Глаголы — по роду в прош. времени, по лицу и числу в наст./буд.",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # ПАРАДИГМЫ: СУЩЕСТВИТЕЛЬНОЕ (приоритет: gender → number → case)
    # ═══════════════════════════════════════════════════════════════════════

    noun_config = PartOfSpeechConfig(
        pos_id="noun",
        name_ru="Существительное",
        name_en="Noun",
        pos_class="content",
        category_order=["gender", "number", "case"],
    )

    # Категория: Род (лексический, самый близкий к корню)
    gender_cat = GrammaticalCategory(category_id="gender", enabled=True)
    gender_cat.rules = {
        "Masculine": GrammarRule(value_id="Masculine", enabled=True, affix_type="suffix", affix_pattern="", example_input="стол"),
        "Feminine": GrammarRule(value_id="Feminine", enabled=True, affix_type="suffix", affix_pattern="-а", example_input="книг"),
        "Neuter": GrammarRule(value_id="Neuter", enabled=True, affix_type="suffix", affix_pattern="-о", example_input="окн"),
    }
    noun_config.categories["gender"] = gender_cat

    # Категория: Число
    number_cat = GrammaticalCategory(category_id="number", enabled=True)
    number_cat.rules = {
        "Singular": GrammarRule(value_id="Singular", enabled=True, affix_type="suffix", affix_pattern=""),
        "Plural": GrammarRule(value_id="Plural", enabled=True, affix_type="suffix", affix_pattern="-ы", example_input="стол"),
    }
    # Флексия для Plural + Masculine
    number_cat.rules["Plural"].fusion_category = "gender"
    number_cat.rules["Plural"].fusion_value = "Masculine"
    number_cat.rules["Plural"].fusion_pattern = "-ы"
    # Флексия для Plural + Feminine
    # (будет переопределено при выборе)
    noun_config.categories["number"] = number_cat

    # Категория: Падеж (самый внешний)
    case_cat = GrammaticalCategory(category_id="case", enabled=True)
    case_cat.rules = {
        "Nominative": GrammarRule(value_id="Nominative", enabled=True, affix_type="suffix", affix_pattern=""),
        "Genitive": GrammarRule(value_id="Genitive", enabled=True, affix_type="suffix", affix_pattern="-а", example_input="стол"),
        "Dative": GrammarRule(value_id="Dative", enabled=True, affix_type="suffix", affix_pattern="-у", example_input="стол"),
        "Accusative": GrammarRule(value_id="Accusative", enabled=True, affix_type="suffix", affix_pattern=""),
        "Instrumental": GrammarRule(value_id="Instrumental", enabled=True, affix_type="suffix", affix_pattern="-ом", example_input="стол"),
        "Prepositional": GrammarRule(value_id="Locative", enabled=True, affix_type="suffix", affix_pattern="-е", example_input="стол"),
    }
    # Флексии для падежей с учётом рода
    case_cat.rules["Genitive"].fusion_category = "gender"
    case_cat.rules["Genitive"].fusion_value = "Masculine"
    case_cat.rules["Genitive"].fusion_pattern = "-а"

    case_cat.rules["Instrumental"].fusion_category = "gender"
    case_cat.rules["Instrumental"].fusion_value = "Masculine"
    case_cat.rules["Instrumental"].fusion_pattern = "-ом"

    noun_config.categories["case"] = case_cat

    lang.pos_configs["noun"] = noun_config

    # ═══════════════════════════════════════════════════════════════════════
    # ПАРАДИГМЫ: ГЛАГОЛ (приоритет: aspect → conjugation → tense → person → number)
    # ═══════════════════════════════════════════════════════════════════════

    verb_config = PartOfSpeechConfig(
        pos_id="verb",
        name_ru="Глагол",
        name_en="Verb",
        pos_class="content",
        category_order=["aspect", "conjugation", "tense", "person", "number", "gender"],
    )

    # Вид (лексический/словообразовательный)
    aspect_cat = GrammaticalCategory(category_id="aspect", enabled=True)
    aspect_cat.rules = {
        "Imperfective": GrammarRule(value_id="Imperfective", enabled=True, affix_type="suffix", affix_pattern=""),
        "Perfective": GrammarRule(value_id="Perfective", enabled=True, affix_type="prefix", affix_pattern="с-", example_input="делать"),
    }
    verb_config.categories["aspect"] = aspect_cat

    # Спряжение (лексический признак, влияет на окончания)
    conj_cat = GrammaticalCategory(category_id="conjugation", enabled=True)
    conj_cat.rules = {
        "1st": GrammarRule(value_id="1st", enabled=True, affix_type="suffix", affix_pattern=""),
        "2nd": GrammarRule(value_id="2nd", enabled=True, affix_type="suffix", affix_pattern=""),
    }
    verb_config.categories["conjugation"] = conj_cat

    # Время
    tense_cat = GrammaticalCategory(category_id="tense", enabled=True)
    tense_cat.rules = {
        "Present": GrammarRule(value_id="Present", enabled=True, affix_type="suffix", affix_pattern=""),
        "Past": GrammarRule(value_id="Past", enabled=True, affix_type="suffix", affix_pattern="-л", example_input="чита"),
        "Future": GrammarRule(value_id="Future", enabled=True, affix_type="suffix", affix_pattern=""),
    }
    verb_config.categories["tense"] = tense_cat

    # Лицо (для наст./буд. времени)
    person_cat = GrammaticalCategory(category_id="person", enabled=True)
    person_cat.rules = {
        "1st": GrammarRule(value_id="1st", enabled=True, affix_type="suffix", affix_pattern="-ю", example_input="чита"),
        "2nd": GrammarRule(value_id="2nd", enabled=True, affix_type="suffix", affix_pattern="-ешь", example_input="чита"),
        "3rd": GrammarRule(value_id="3rd", enabled=True, affix_type="suffix", affix_pattern="-ет", example_input="чита"),
    }
    # Флексия для 2 спряжения
    person_cat.rules["1st"].fusion_category = "conjugation"
    person_cat.rules["1st"].fusion_value = "2nd"
    person_cat.rules["1st"].fusion_pattern = "-у"
    person_cat.rules["2nd"].fusion_category = "conjugation"
    person_cat.rules["2nd"].fusion_value = "2nd"
    person_cat.rules["2nd"].fusion_pattern = "-ишь"
    person_cat.rules["3rd"].fusion_category = "conjugation"
    person_cat.rules["3rd"].fusion_value = "2nd"
    person_cat.rules["3rd"].fusion_pattern = "-ит"
    verb_config.categories["person"] = person_cat

    # Число
    verb_number_cat = GrammaticalCategory(category_id="number", enabled=True)
    verb_number_cat.rules = {
        "Singular": GrammarRule(value_id="Singular", enabled=True, affix_type="suffix", affix_pattern=""),
        "Plural": GrammarRule(value_id="Plural", enabled=True, affix_type="suffix", affix_pattern="-ют", example_input="чита"),
    }
    verb_number_cat.rules["Plural"].fusion_category = "conjugation"
    verb_number_cat.rules["Plural"].fusion_value = "2nd"
    verb_number_cat.rules["Plural"].fusion_pattern = "-ят"
    verb_config.categories["number"] = verb_number_cat

    # Род (для прошедшего времени)
    verb_gender_cat = GrammaticalCategory(category_id="gender", enabled=True)
    verb_gender_cat.rules = {
        "Masculine": GrammarRule(value_id="Masculine", enabled=True, affix_type="suffix", affix_pattern=""),
        "Feminine": GrammarRule(value_id="Feminine", enabled=True, affix_type="suffix", affix_pattern="-а", example_input="читал"),
        "Neuter": GrammarRule(value_id="Neuter", enabled=True, affix_type="suffix", affix_pattern="-о", example_input="читал"),
    }
    verb_config.categories["gender"] = verb_gender_cat

    lang.pos_configs["verb"] = verb_config

    # ═══════════════════════════════════════════════════════════════════════
    # ПАРАДИГМЫ: ПРИЛАГАТЕЛЬНОЕ
    # ═══════════════════════════════════════════════════════════════════════

    adj_config = PartOfSpeechConfig(
        pos_id="adjective",
        name_ru="Прилагательное",
        name_en="Adjective",
        pos_class="content",
        category_order=["gender", "number", "case"],
    )

    adj_gender_cat = GrammaticalCategory(category_id="gender", enabled=True)
    adj_gender_cat.rules = {
        "Masculine": GrammarRule(value_id="Masculine", enabled=True, affix_type="suffix", affix_pattern="-ый", example_input="красн"),
        "Feminine": GrammarRule(value_id="Feminine", enabled=True, affix_type="suffix", affix_pattern="-ая", example_input="красн"),
        "Neuter": GrammarRule(value_id="Neuter", enabled=True, affix_type="suffix", affix_pattern="-ое", example_input="красн"),
    }
    adj_config.categories["gender"] = adj_gender_cat

    adj_number_cat = GrammaticalCategory(category_id="number", enabled=True)
    adj_number_cat.rules = {
        "Singular": GrammarRule(value_id="Singular", enabled=True, affix_type="suffix", affix_pattern=""),
        "Plural": GrammarRule(value_id="Plural", enabled=True, affix_type="suffix", affix_pattern="-ые", example_input="красн"),
    }
    adj_config.categories["number"] = adj_number_cat

    adj_case_cat = GrammaticalCategory(category_id="case", enabled=True)
    adj_case_cat.rules = {
        "Nominative": GrammarRule(value_id="Nominative", enabled=True, affix_type="suffix", affix_pattern=""),
        "Genitive": GrammarRule(value_id="Genitive", enabled=True, affix_type="suffix", affix_pattern="-ого", example_input="красн"),
        "Dative": GrammarRule(value_id="Dative", enabled=True, affix_type="suffix", affix_pattern="-ому", example_input="красн"),
        "Accusative": GrammarRule(value_id="Accusative", enabled=True, affix_type="suffix", affix_pattern="-ого", example_input="красн"),
        "Instrumental": GrammarRule(value_id="Instrumental", enabled=True, affix_type="suffix", affix_pattern="-ым", example_input="красн"),
        "Prepositional": GrammarRule(value_id="Locative", enabled=True, affix_type="suffix", affix_pattern="-ом", example_input="красн"),
    }
    adj_config.categories["case"] = adj_case_cat

    lang.pos_configs["adjective"] = adj_config

    # ═══════════════════════════════════════════════════════════════════════
    # СЛУЖЕБНЫЕ СЛОВА
    # ═══════════════════════════════════════════════════════════════════════

    lang.function_words = [
        FunctionWord(name="Предлог 'в'", form="в", function="locative", applies_to_category="case", applies_to_value="Locative", word_type="preposition", position="before"),
        FunctionWord(name="Предлог 'на'", form="на", function="adessive", applies_to_category="case", applies_to_value="Locative", word_type="preposition", position="before"),
        FunctionWord(name="Предлог 'с'", form="с", function="instrumental", applies_to_category="case", applies_to_value="Instrumental", word_type="preposition", position="before"),
        FunctionWord(name="Предлог 'из'", form="из", function="elative", applies_to_category="case", applies_to_value="Genitive", word_type="preposition", position="before"),
        FunctionWord(name="Предлог 'к'", form="к", function="allative", applies_to_category="case", applies_to_value="Dative", word_type="preposition", position="before"),
        FunctionWord(name="Союз 'и'", form="и", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Союз 'или'", form="или", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Союз 'но'", form="но", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Частица 'не'", form="не", function="negation", applies_to_category="polarity", applies_to_value="Negative", word_type="particle", position="before"),
        FunctionWord(name="Частица 'ли'", form="ли", function="question", applies_to_category="", applies_to_value="", word_type="particle", position="after"),
        FunctionWord(name="Частица 'бы'", form="бы", function="conditional", applies_to_category="mood", applies_to_value="Conditional", word_type="particle", position="after"),
        FunctionWord(name="Частица 'же'", form="же", function="emphasis", applies_to_category="", applies_to_value="", word_type="particle", position="after"),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # ПРАГМАТИКА И ДИСКУРС
    # ═══════════════════════════════════════════════════════════════════════

    lang.pragmatics = Pragmatics(
        deixis_spatial="2 степени: здесь / там, этот / тот",
        deixis_temporal="3 степени: сейчас / тогда / давно",
        deixis_personal="я, ты, он/она/оно, мы, вы, они",
        topic_marking="Порядок слов (тема в начале), частица '-то'",
        focus_marking="Интонация, частица 'именно'",
        evidentiality="none",
        politeness_levels=2,
        registers=[
            Register(name="Нейтральный", description="Повседневное общение"),
            Register(name="Формальный", description="Официальное общение, Вы"),
            Register(name="Фамильярный", description="Близкие, друзья, ты"),
        ],
        discourse_markers=["ну", "вот", "так", "значит", "кстати", "в общем", "типа"],
        notes="Развитая система дискурсивных маркеров и частиц.",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # ПИСЬМЕННОСТЬ
    # ═══════════════════════════════════════════════════════════════════════

    lang.writing = WritingSystem(
        script_type="alphabetic",
        direction="ltr",
        alphabet="а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я",
        has_diacritics=True,
        diacritics_notes="й, ё",
        punctuation_notes="Стандартная европейская пунктуация",
        numeral_system="arabic",
        orthography_notes="Фонетический принцип с морфологическими отклонениями",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # СЛОВАРЬ (Лейпциг-Джакарта)
    # ═══════════════════════════════════════════════════════════════════════

    lang.words = [
        Word(conword="рук", localword="рука", lemma="рука", pos_id="noun"),
        Word(conword="лев", localword="левый", lemma="левый", pos_id="adjective"),
        Word(conword="прав", localword="правый", lemma="правый", pos_id="adjective"),
        Word(conword="ног", localword="нога", lemma="нога", pos_id="noun"),
        Word(conword="колен", localword="колено", lemma="колено", pos_id="noun"),
        Word(conword="ид", localword="идти", lemma="идти", pos_id="verb"),
        Word(conword="дорог", localword="дорога", lemma="дорога", pos_id="noun"),
        Word(conword="прид", localword="прийти", lemma="прийти", pos_id="verb"),
        Word(conword="леж", localword="лежать", lemma="лежать", pos_id="verb"),
        Word(conword="сид", localword="сидеть", lemma="сидеть", pos_id="verb"),
        Word(conword="сто", localword="стоять", lemma="стоять", pos_id="verb"),
        Word(conword="человек", localword="человек", lemma="человек", pos_id="noun"),
        Word(conword="мужчин", localword="мужчина", lemma="мужчина", pos_id="noun"),
        Word(conword="женщин", localword="женщина", lemma="женщина", pos_id="noun"),
        Word(conword="ребёнк", localword="ребёнок", lemma="ребёнок", pos_id="noun"),
        Word(conword="муж", localword="муж", lemma="муж", pos_id="noun"),
        Word(conword="жен", localword="жена", lemma="жена", pos_id="noun"),
        Word(conword="мат", localword="мать", lemma="мать", pos_id="noun"),
        Word(conword="отц", localword="отец", lemma="отец", pos_id="noun"),
        Word(conword="дом", localword="дом", lemma="дом", pos_id="noun"),
        Word(conword="живот", localword="живот", lemma="живот", pos_id="noun"),
        Word(conword="ше", localword="шея", lemma="шея", pos_id="noun"),
        Word(conword="груд", localword="грудь", lemma="грудь", pos_id="noun"),
        Word(conword="сердц", localword="сердце", lemma="сердце", pos_id="noun"),
        Word(conword="печен", localword="печень", lemma="печень", pos_id="noun"),
        Word(conword="пь", localword="пить", lemma="пить", pos_id="verb"),
        Word(conword="ед", localword="есть", lemma="есть", pos_id="verb"),
        Word(conword="кус", localword="кусать", lemma="кусать", pos_id="verb"),
        Word(conword="вид", localword="видеть", lemma="видеть", pos_id="verb"),
        Word(conword="слыш", localword="слышать", lemma="слышать", pos_id="verb"),
        Word(conword="зна", localword="знать", lemma="знать", pos_id="verb"),
        Word(conword="сп", localword="спать", lemma="спать", pos_id="verb"),
        Word(conword="умир", localword="умирать", lemma="умирать", pos_id="verb"),
        Word(conword="убив", localword="убивать", lemma="убивать", pos_id="verb"),
        Word(conword="плав", localword="плавать", lemma="плавать", pos_id="verb"),
        Word(conword="лет", localword="летать", lemma="летать", pos_id="verb"),
        Word(conword="солнц", localword="солнце", lemma="солнце", pos_id="noun"),
        Word(conword="лун", localword="луна", lemma="луна", pos_id="noun"),
        Word(conword="звезд", localword="звезда", lemma="звезда", pos_id="noun"),
        Word(conword="вод", localword="вода", lemma="вода", pos_id="noun"),
        Word(conword="дожд", localword="дождь", lemma="дождь", pos_id="noun"),
        Word(conword="камен", localword="камень", lemma="камень", pos_id="noun"),
        Word(conword="песк", localword="песок", lemma="песок", pos_id="noun"),
        Word(conword="земл", localword="земля", lemma="земля", pos_id="noun"),
        Word(conword="облак", localword="облако", lemma="облако", pos_id="noun"),
        Word(conword="дым", localword="дым", lemma="дым", pos_id="noun"),
        Word(conword="огон", localword="огонь", lemma="огонь", pos_id="noun"),
        Word(conword="пепл", localword="пепел", lemma="пепел", pos_id="noun"),
        Word(conword="гор", localword="гореть", lemma="гореть", pos_id="verb"),
        Word(conword="троп", localword="тропа", lemma="тропа", pos_id="noun"),
        Word(conword="гор", localword="гора", lemma="гора", pos_id="noun"),
        Word(conword="красн", localword="красный", lemma="красный", pos_id="adjective"),
        Word(conword="зелён", localword="зелёный", lemma="зелёный", pos_id="adjective"),
        Word(conword="жёлт", localword="жёлтый", lemma="жёлтый", pos_id="adjective"),
        Word(conword="бел", localword="белый", lemma="белый", pos_id="adjective"),
        Word(conword="чёрн", localword="чёрный", lemma="чёрный", pos_id="adjective"),
        Word(conword="ноч", localword="ночь", lemma="ночь", pos_id="noun"),
        Word(conword="горяч", localword="горячий", lemma="горячий", pos_id="adjective"),
        Word(conword="холодн", localword="холодный", lemma="холодный", pos_id="adjective"),
        Word(conword="полн", localword="полный", lemma="полный", pos_id="adjective"),
        Word(conword="нов", localword="новый", lemma="новый", pos_id="adjective"),
        Word(conword="хорош", localword="хороший", lemma="хороший", pos_id="adjective"),
        Word(conword="кругл", localword="круглый", lemma="круглый", pos_id="adjective"),
        Word(conword="сух", localword="сухой", lemma="сухой", pos_id="adjective"),
        Word(conword="им", localword="имя", lemma="имя", pos_id="noun"),
        Word(conword="говор", localword="говорить", lemma="говорить", pos_id="verb"),
        Word(conword="по", localword="петь", lemma="петь", pos_id="verb"),
        Word(conword="игр", localword="играть", lemma="играть", pos_id="verb"),
        Word(conword="плы", localword="плыть", lemma="плыть", pos_id="verb"),
        Word(conword="тек", localword="течь", lemma="течь", pos_id="verb"),
        Word(conword="замерз", localword="замерзать", lemma="замерзать", pos_id="verb"),
        Word(conword="набух", localword="набухать", lemma="набухать", pos_id="verb"),
        Word(conword="дерев", localword="дерево", lemma="дерево", pos_id="noun"),
        Word(conword="палк", localword="палка", lemma="палка", pos_id="noun"),
        Word(conword="фрукт", localword="фрукт", lemma="фрукт", pos_id="noun"),
        Word(conword="сем", localword="семя", lemma="семя", pos_id="noun"),
        Word(conword="лист", localword="лист", lemma="лист", pos_id="noun"),
        Word(conword="корн", localword="корень", lemma="корень", pos_id="noun"),
        Word(conword="кор", localword="кора", lemma="кора", pos_id="noun"),
        Word(conword="цветк", localword="цветок", lemma="цветок", pos_id="noun"),
        Word(conword="трав", localword="трава", lemma="трава", pos_id="noun"),
        Word(conword="верёвк", localword="верёвка", lemma="верёвка", pos_id="noun"),
        Word(conword="кож", localword="кожа", lemma="кожа", pos_id="noun"),
        Word(conword="мяс", localword="мясо", lemma="мясо", pos_id="noun"),
        Word(conword="кров", localword="кровь", lemma="кровь", pos_id="noun"),
        Word(conword="кост", localword="кость", lemma="кость", pos_id="noun"),
        Word(conword="жир", localword="жир", lemma="жир", pos_id="noun"),
        Word(conword="яйц", localword="яйцо", lemma="яйцо", pos_id="noun"),
        Word(conword="рог", localword="рог", lemma="рог", pos_id="noun"),
        Word(conword="хвост", localword="хвост", lemma="хвост", pos_id="noun"),
        Word(conword="пер", localword="перо", lemma="перо", pos_id="noun"),
        Word(conword="волос", localword="волосы", lemma="волосы", pos_id="noun"),
        Word(conword="голов", localword="голова", lemma="голова", pos_id="noun"),
        Word(conword="ух", localword="ухо", lemma="ухо", pos_id="noun"),
        Word(conword="глаз", localword="глаз", lemma="глаз", pos_id="noun"),
        Word(conword="нос", localword="нос", lemma="нос", pos_id="noun"),
    ]

    for w in lang.words:
        w.pronunciation = lang.phonology.generate_pronunciation(w.conword)

    return lang


# ═══════════════════════════════════════════════════════════════════════════
# ПРЕСЕТ: АНГЛИЙСКИЙ ЯЗЫК
# ═══════════════════════════════════════════════════════════════════════════

def generate_english_preset() -> Language:
    """Генерирует пресет английского языка."""
    lang = Language()
    lang.name = "English"
    lang.local_language = "English"
    lang.author = "ConLang Studio"
    lang.description = "Analytic Germanic language with SVO order, remnants of case in pronouns"

    # Фонология
    lang.phonology.vowels = [
        Vowel(symbol="i", height="high", backness="front", rounded=False),
        Vowel(symbol="ɪ", height="high", backness="front", rounded=False),
        Vowel(symbol="e", height="mid", backness="front", rounded=False),
        Vowel(symbol="æ", height="low", backness="front", rounded=False),
        Vowel(symbol="ʌ", height="mid", backness="central", rounded=False),
        Vowel(symbol="ə", height="mid", backness="central", rounded=False),
        Vowel(symbol="u", height="high", backness="back", rounded=True),
        Vowel(symbol="ʊ", height="high", backness="back", rounded=True),
        Vowel(symbol="o", height="mid", backness="back", rounded=True),
        Vowel(symbol="ɔ", height="low", backness="back", rounded=True),
        Vowel(symbol="ɑ", height="low", backness="back", rounded=False),
    ]

    lang.phonology.consonants = [
        Consonant(symbol="p", place="bilabial", manner="stop", voiced=False),
        Consonant(symbol="b", place="bilabial", manner="stop", voiced=True),
        Consonant(symbol="m", place="bilabial", manner="nasal", voiced=True),
        Consonant(symbol="f", place="labiodental", manner="fricative", voiced=False),
        Consonant(symbol="v", place="labiodental", manner="fricative", voiced=True),
        Consonant(symbol="θ", place="dental", manner="fricative", voiced=False),
        Consonant(symbol="ð", place="dental", manner="fricative", voiced=True),
        Consonant(symbol="t", place="alveolar", manner="stop", voiced=False),
        Consonant(symbol="d", place="alveolar", manner="stop", voiced=True),
        Consonant(symbol="s", place="alveolar", manner="fricative", voiced=False),
        Consonant(symbol="z", place="alveolar", manner="fricative", voiced=True),
        Consonant(symbol="n", place="alveolar", manner="nasal", voiced=True),
        Consonant(symbol="l", place="alveolar", manner="lateral", voiced=True),
        Consonant(symbol="r", place="alveolar", manner="approximant", voiced=True),
        Consonant(symbol="ʃ", place="postalveolar", manner="fricative", voiced=False),
        Consonant(symbol="ʒ", place="postalveolar", manner="fricative", voiced=True),
        Consonant(symbol="tʃ", place="postalveolar", manner="affricate", voiced=False),
        Consonant(symbol="dʒ", place="postalveolar", manner="affricate", voiced=True),
        Consonant(symbol="j", place="palatal", manner="approximant", voiced=True),
        Consonant(symbol="k", place="velar", manner="stop", voiced=False),
        Consonant(symbol="g", place="velar", manner="stop", voiced=True),
        Consonant(symbol="ŋ", place="velar", manner="nasal", voiced=True),
        Consonant(symbol="h", place="glottal", manner="fricative", voiced=False),
    ]

    lang.phonology.phonotactics = Phonotactics(
        syllable_templates=["CVC", "CCVC", "CVCC"],
        max_onset=3,
        max_coda=4,
    )

    # Тип языка
    lang.morphology.lang_type.primary = "analytic"
    lang.extra["lang_type_strategies"] = {
        "use_affixes": False,
        "use_particles": True,
        "use_fusion": False,
        "use_incorporation": False,
    }

    # Типы морфем
    mt = lang.morphology.morpheme_types
    mt.has_suffixes = True
    mt.reduplication = "none"

    # Синтаксис
    lang.syntax = Syntax(
        basic_order="SVO",
        alignment="nominative-accusative",
        adj_position="before",
        gen_position="before",
        adposition_type="preposition",
        question_formation="inversion",
        negation_type="particle",
    )

    # Парадигмы: Существительное (только число)
    noun_config = PartOfSpeechConfig(
        pos_id="noun",
        name_ru="Noun",
        name_en="Noun",
        pos_class="content",
        category_order=["number"],
    )
    number_cat = GrammaticalCategory(category_id="number", enabled=True)
    number_cat.rules = {
        "Singular": GrammarRule(value_id="Singular", enabled=True, affix_type="suffix", affix_pattern=""),
        "Plural": GrammarRule(value_id="Plural", enabled=True, affix_type="suffix", affix_pattern="-s", example_input="cat"),
    }
    noun_config.categories["number"] = number_cat
    lang.pos_configs["noun"] = noun_config

    # Парадигмы: Глагол
    verb_config = PartOfSpeechConfig(
        pos_id="verb",
        name_ru="Verb",
        name_en="Verb",
        pos_class="content",
        category_order=["tense", "person"],
    )
    tense_cat = GrammaticalCategory(category_id="tense", enabled=True)
    tense_cat.rules = {
        "Present": GrammarRule(value_id="Present", enabled=True, affix_type="suffix", affix_pattern=""),
        "Past": GrammarRule(value_id="Past", enabled=True, affix_type="suffix", affix_pattern="-ed", example_input="walk"),
    }
    verb_config.categories["tense"] = tense_cat

    person_cat = GrammaticalCategory(category_id="person", enabled=True)
    person_cat.rules = {
        "3rd": GrammarRule(value_id="3rd", enabled=True, affix_type="suffix", affix_pattern="-s", example_input="walk"),
    }
    verb_config.categories["person"] = person_cat
    lang.pos_configs["verb"] = verb_config

    # Служебные слова
    lang.function_words = [
        FunctionWord(name="Definite article", form="the", function="definite", applies_to_category="definiteness", applies_to_value="Definite", word_type="article", position="before"),
        FunctionWord(name="Indefinite article", form="a", function="indefinite", applies_to_category="definiteness", applies_to_value="Indefinite", word_type="article", position="before"),
        FunctionWord(name="Preposition 'of'", form="of", function="genitive", applies_to_category="case", applies_to_value="Genitive", word_type="preposition", position="before"),
        FunctionWord(name="Preposition 'to'", form="to", function="dative", applies_to_category="case", applies_to_value="Dative", word_type="preposition", position="before"),
        FunctionWord(name="Preposition 'in'", form="in", function="locative", applies_to_category="case", applies_to_value="Locative", word_type="preposition", position="before"),
        FunctionWord(name="Preposition 'on'", form="on", function="adessive", applies_to_category="case", applies_to_value="Locative", word_type="preposition", position="before"),
        FunctionWord(name="Preposition 'from'", form="from", function="ablative", applies_to_category="case", applies_to_value="Ablative", word_type="preposition", position="before"),
        FunctionWord(name="Preposition 'with'", form="with", function="instrumental", applies_to_category="case", applies_to_value="Instrumental", word_type="preposition", position="before"),
        FunctionWord(name="Auxiliary 'will'", form="will", function="temporal_future", applies_to_category="tense", applies_to_value="Future", word_type="auxiliary", position="before"),
        FunctionWord(name="Auxiliary 'have'", form="have", function="aspect_perfect", applies_to_category="aspect", applies_to_value="Perfect", word_type="auxiliary", position="before"),
        FunctionWord(name="Auxiliary 'be'", form="be", function="aspect_progressive", applies_to_category="aspect", applies_to_value="Progressive", word_type="auxiliary", position="before"),
        FunctionWord(name="Negation 'not'", form="not", function="negation", applies_to_category="polarity", applies_to_value="Negative", word_type="particle", position="after"),
        FunctionWord(name="Conjunction 'and'", form="and", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Conjunction 'or'", form="or", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Conjunction 'but'", form="but", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
    ]

    # Прагматика
    lang.pragmatics = Pragmatics(
        deixis_spatial="2 степени: here / there, this / that",
        deixis_temporal="now / then",
        deixis_personal="I, you, he/she/it, we, they",
        topic_marking="Word order, cleft sentences",
        focus_marking="Intonation, 'it is ... that'",
        evidentiality="none",
        politeness_levels=1,
        registers=[
            Register(name="Neutral", description="Everyday communication"),
            Register(name="Formal", description="Official communication"),
        ],
        discourse_markers=["well", "so", "anyway", "actually", "I mean", "you know"],
    )

    # Письменность
    lang.writing = WritingSystem(
        script_type="alphabetic",
        direction="ltr",
        alphabet="a b c d e f g h i j k l m n o p q r s t u v w x y z",
        has_diacritics=False,
        punctuation_notes="Standard European punctuation",
        numeral_system="arabic",
    )

    # Словарь (Лейпциг-Джакарта)
    lang.words = [
        Word(conword="hand", localword="hand", lemma="hand", pos_id="noun"),
        Word(conword="left", localword="left", lemma="left", pos_id="adjective"),
        Word(conword="right", localword="right", lemma="right", pos_id="adjective"),
        Word(conword="foot", localword="foot", lemma="foot", pos_id="noun"),
        Word(conword="knee", localword="knee", lemma="knee", pos_id="noun"),
        Word(conword="walk", localword="walk", lemma="walk", pos_id="verb"),
        Word(conword="road", localword="road", lemma="road", pos_id="noun"),
        Word(conword="come", localword="come", lemma="come", pos_id="verb"),
        Word(conword="lie", localword="lie", lemma="lie", pos_id="verb"),
        Word(conword="sit", localword="sit", lemma="sit", pos_id="verb"),
        Word(conword="stand", localword="stand", lemma="stand", pos_id="verb"),
        Word(conword="person", localword="person", lemma="person", pos_id="noun"),
        Word(conword="man", localword="man", lemma="man", pos_id="noun"),
        Word(conword="woman", localword="woman", lemma="woman", pos_id="noun"),
        Word(conword="child", localword="child", lemma="child", pos_id="noun"),
        Word(conword="husband", localword="husband", lemma="husband", pos_id="noun"),
        Word(conword="wife", localword="wife", lemma="wife", pos_id="noun"),
        Word(conword="mother", localword="mother", lemma="mother", pos_id="noun"),
        Word(conword="father", localword="father", lemma="father", pos_id="noun"),
        Word(conword="house", localword="house", lemma="house", pos_id="noun"),
        Word(conword="belly", localword="belly", lemma="belly", pos_id="noun"),
        Word(conword="neck", localword="neck", lemma="neck", pos_id="noun"),
        Word(conword="breast", localword="breast", lemma="breast", pos_id="noun"),
        Word(conword="heart", localword="heart", lemma="heart", pos_id="noun"),
        Word(conword="liver", localword="liver", lemma="liver", pos_id="noun"),
        Word(conword="drink", localword="drink", lemma="drink", pos_id="verb"),
        Word(conword="eat", localword="eat", lemma="eat", pos_id="verb"),
        Word(conword="bite", localword="bite", lemma="bite", pos_id="verb"),
        Word(conword="see", localword="see", lemma="see", pos_id="verb"),
        Word(conword="hear", localword="hear", lemma="hear", pos_id="verb"),
        Word(conword="know", localword="know", lemma="know", pos_id="verb"),
        Word(conword="sleep", localword="sleep", lemma="sleep", pos_id="verb"),
        Word(conword="die", localword="die", lemma="die", pos_id="verb"),
        Word(conword="kill", localword="kill", lemma="kill", pos_id="verb"),
        Word(conword="swim", localword="swim", lemma="swim", pos_id="verb"),
        Word(conword="fly", localword="fly", lemma="fly", pos_id="verb"),
        Word(conword="sun", localword="sun", lemma="sun", pos_id="noun"),
        Word(conword="moon", localword="moon", lemma="moon", pos_id="noun"),
        Word(conword="star", localword="star", lemma="star", pos_id="noun"),
        Word(conword="water", localword="water", lemma="water", pos_id="noun"),
        Word(conword="rain", localword="rain", lemma="rain", pos_id="noun"),
        Word(conword="stone", localword="stone", lemma="stone", pos_id="noun"),
        Word(conword="sand", localword="sand", lemma="sand", pos_id="noun"),
        Word(conword="earth", localword="earth", lemma="earth", pos_id="noun"),
        Word(conword="cloud", localword="cloud", lemma="cloud", pos_id="noun"),
        Word(conword="smoke", localword="smoke", lemma="smoke", pos_id="noun"),
        Word(conword="fire", localword="fire", lemma="fire", pos_id="noun"),
        Word(conword="ash", localword="ash", lemma="ash", pos_id="noun"),
        Word(conword="burn", localword="burn", lemma="burn", pos_id="verb"),
        Word(conword="path", localword="path", lemma="path", pos_id="noun"),
        Word(conword="mountain", localword="mountain", lemma="mountain", pos_id="noun"),
        Word(conword="red", localword="red", lemma="red", pos_id="adjective"),
        Word(conword="green", localword="green", lemma="green", pos_id="adjective"),
        Word(conword="yellow", localword="yellow", lemma="yellow", pos_id="adjective"),
        Word(conword="white", localword="white", lemma="white", pos_id="adjective"),
        Word(conword="black", localword="black", lemma="black", pos_id="adjective"),
        Word(conword="night", localword="night", lemma="night", pos_id="noun"),
        Word(conword="hot", localword="hot", lemma="hot", pos_id="adjective"),
        Word(conword="cold", localword="cold", lemma="cold", pos_id="adjective"),
        Word(conword="full", localword="full", lemma="full", pos_id="adjective"),
        Word(conword="new", localword="new", lemma="new", pos_id="adjective"),
        Word(conword="good", localword="good", lemma="good", pos_id="adjective"),
        Word(conword="round", localword="round", lemma="round", pos_id="adjective"),
        Word(conword="dry", localword="dry", lemma="dry", pos_id="adjective"),
        Word(conword="name", localword="name", lemma="name", pos_id="noun"),
        Word(conword="say", localword="say", lemma="say", pos_id="verb"),
        Word(conword="sing", localword="sing", lemma="sing", pos_id="verb"),
        Word(conword="play", localword="play", lemma="play", pos_id="verb"),
        Word(conword="float", localword="float", lemma="float", pos_id="verb"),
        Word(conword="flow", localword="flow", lemma="flow", pos_id="verb"),
        Word(conword="freeze", localword="freeze", lemma="freeze", pos_id="verb"),
        Word(conword="swell", localword="swell", lemma="swell", pos_id="verb"),
        Word(conword="tree", localword="tree", lemma="tree", pos_id="noun"),
        Word(conword="stick", localword="stick", lemma="stick", pos_id="noun"),
        Word(conword="fruit", localword="fruit", lemma="fruit", pos_id="noun"),
        Word(conword="seed", localword="seed", lemma="seed", pos_id="noun"),
        Word(conword="leaf", localword="leaf", lemma="leaf", pos_id="noun"),
        Word(conword="root", localword="root", lemma="root", pos_id="noun"),
        Word(conword="bark", localword="bark", lemma="bark", pos_id="noun"),
        Word(conword="flower", localword="flower", lemma="flower", pos_id="noun"),
        Word(conword="grass", localword="grass", lemma="grass", pos_id="noun"),
        Word(conword="rope", localword="rope", lemma="rope", pos_id="noun"),
        Word(conword="skin", localword="skin", lemma="skin", pos_id="noun"),
        Word(conword="meat", localword="meat", lemma="meat", pos_id="noun"),
        Word(conword="blood", localword="blood", lemma="blood", pos_id="noun"),
        Word(conword="bone", localword="bone", lemma="bone", pos_id="noun"),
        Word(conword="fat", localword="fat", lemma="fat", pos_id="noun"),
        Word(conword="egg", localword="egg", lemma="egg", pos_id="noun"),
        Word(conword="horn", localword="horn", lemma="horn", pos_id="noun"),
        Word(conword="tail", localword="tail", lemma="tail", pos_id="noun"),
        Word(conword="feather", localword="feather", lemma="feather", pos_id="noun"),
        Word(conword="hair", localword="hair", lemma="hair", pos_id="noun"),
        Word(conword="head", localword="head", lemma="head", pos_id="noun"),
        Word(conword="ear", localword="ear", lemma="ear", pos_id="noun"),
        Word(conword="eye", localword="eye", lemma="eye", pos_id="noun"),
        Word(conword="nose", localword="nose", lemma="nose", pos_id="noun"),
    ]

    for w in lang.words:
        w.pronunciation = w.conword

    return lang


# ═══════════════════════════════════════════════════════════════════════════
# ПРЕСЕТ: БАСКСКИЙ / ВАСКОНСКИЙ ЯЗЫК
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
# ПРЕСЕТ: БАСКСКИЙ / ВАСКОНСКИЙ ЯЗЫК
# ═══════════════════════════════════════════════════════════════════════════

def generate_basque_preset() -> Language:
    """Генерирует пресет баскского (васконского) языка — эргативный, полиперсональное согласование."""
    lang = Language()
    lang.name = "Euskara"
    lang.local_language = "Русский"  # Язык интерфейса/перевода
    lang.author = "ConLang Studio"
    lang.description = "Эргативный язык-изолят с полиперсональным согласованием, SOV порядок"

    # Фонология (упрощённая)
    lang.phonology.vowels = [
        Vowel(symbol="a", height="low", backness="central", rounded=False),
        Vowel(symbol="e", height="mid", backness="front", rounded=False),
        Vowel(symbol="i", height="high", backness="front", rounded=False),
        Vowel(symbol="o", height="mid", backness="back", rounded=True),
        Vowel(symbol="u", height="high", backness="back", rounded=True),
    ]

    lang.phonology.consonants = [
        Consonant(symbol="p", place="bilabial", manner="stop", voiced=False),
        Consonant(symbol="b", place="bilabial", manner="stop", voiced=True),
        Consonant(symbol="m", place="bilabial", manner="nasal", voiced=True),
        Consonant(symbol="t", place="dental", manner="stop", voiced=False),
        Consonant(symbol="d", place="dental", manner="stop", voiced=True),
        Consonant(symbol="s", place="dental", manner="fricative", voiced=False),
        Consonant(symbol="z", place="dental", manner="fricative", voiced=True),
        Consonant(symbol="n", place="dental", manner="nasal", voiced=True),
        Consonant(symbol="l", place="dental", manner="lateral", voiced=True),
        Consonant(symbol="r", place="alveolar", manner="trill", voiced=True),
        Consonant(symbol="k", place="velar", manner="stop", voiced=False),
        Consonant(symbol="g", place="velar", manner="stop", voiced=True),
        Consonant(symbol="h", place="glottal", manner="fricative", voiced=False),
    ]

    lang.phonology.phonotactics = Phonotactics(
        syllable_templates=["CV", "CVC"],
        max_onset=1,
        max_coda=1,
    )

    # Тип языка
    lang.morphology.lang_type.primary = "agglutinative"
    lang.extra["lang_type_strategies"] = {
        "use_affixes": True,
        "use_particles": False,
        "use_fusion": False,
        "use_incorporation": False,
    }

    # Типы морфем
    mt = lang.morphology.morpheme_types
    mt.has_suffixes = True
    mt.reduplication = "none"

    # Синтаксис
    lang.syntax = Syntax(
        basic_order="SOV",
        alignment="ergative-absolutive",
        head_direction="head-final",
        adj_position="before",
        gen_position="before",
        adposition_type="postposition",
    )

    # Парадигмы: Существительное (названия ЧР на русском и английском)
    noun_config = PartOfSpeechConfig(
        pos_id="noun",
        name_ru="Существительное",
        name_en="Noun",
        pos_class="content",
        category_order=["number", "case"],
    )

    number_cat = GrammaticalCategory(category_id="number", enabled=True)
    number_cat.rules = {
        "Singular": GrammarRule(value_id="Singular", enabled=True, affix_type="suffix", affix_pattern="-a", example_input="etxe"),
        "Plural": GrammarRule(value_id="Plural", enabled=True, affix_type="suffix", affix_pattern="-ak", example_input="etxe"),
    }
    noun_config.categories["number"] = number_cat

    case_cat = GrammaticalCategory(category_id="case", enabled=True)
    case_cat.rules = {
        "Absolutive": GrammarRule(value_id="Absolutive", enabled=True, affix_type="suffix", affix_pattern=""),
        "Ergative": GrammarRule(value_id="Ergative", enabled=True, affix_type="suffix", affix_pattern="-k", example_input="etxeak"),
        "Dative": GrammarRule(value_id="Dative", enabled=True, affix_type="suffix", affix_pattern="-ri", example_input="etxeari"),
        "Genitive": GrammarRule(value_id="Genitive", enabled=True, affix_type="suffix", affix_pattern="-ren", example_input="etxearen"),
        "Instrumental": GrammarRule(value_id="Instrumental", enabled=True, affix_type="suffix", affix_pattern="-z", example_input="etxeaz"),
        "Locative": GrammarRule(value_id="Locative", enabled=True, affix_type="suffix", affix_pattern="-n", example_input="etxean"),
        "Allative": GrammarRule(value_id="Allative", enabled=True, affix_type="suffix", affix_pattern="-ra", example_input="etxera"),
        "Ablative": GrammarRule(value_id="Ablative", enabled=True, affix_type="suffix", affix_pattern="-tik", example_input="etxetik"),
    }
    noun_config.categories["case"] = case_cat

    lang.pos_configs["noun"] = noun_config

    # Парадигмы: Глагол
    verb_config = PartOfSpeechConfig(
        pos_id="verb",
        name_ru="Глагол",
        name_en="Verb",
        pos_class="content",
        category_order=["tense", "subject_person", "object_person", "subject_number", "object_number"],
    )

    tense_cat = GrammaticalCategory(category_id="tense", enabled=True)
    tense_cat.rules = {
        "Present": GrammarRule(value_id="Present", enabled=True, affix_type="suffix", affix_pattern=""),
        "Past": GrammarRule(value_id="Past", enabled=True, affix_type="suffix", affix_pattern="-n", example_input="datorre"),
    }
    verb_config.categories["tense"] = tense_cat

    subj_person_cat = GrammaticalCategory(category_id="person", enabled=True)
    subj_person_cat.rules = {
        "1st": GrammarRule(value_id="1st", enabled=True, affix_type="prefix", affix_pattern="n-", example_input="ator"),
        "2nd": GrammarRule(value_id="2nd", enabled=True, affix_type="prefix", affix_pattern="h-", example_input="ator"),
        "3rd": GrammarRule(value_id="3rd", enabled=True, affix_type="prefix", affix_pattern="d-", example_input="ator"),
    }
    verb_config.categories["person"] = subj_person_cat

    obj_person_cat = GrammaticalCategory(category_id="object_person", enabled=True)
    obj_person_cat.rules = {
        "1st": GrammarRule(value_id="1st", enabled=True, affix_type="infix", affix_pattern="-n-", example_input="dator"),
        "2nd": GrammarRule(value_id="2nd", enabled=True, affix_type="infix", affix_pattern="-h-", example_input="dator"),
        "3rd": GrammarRule(value_id="3rd", enabled=True, affix_type="infix", affix_pattern="-∅-", example_input="dator"),
    }
    verb_config.categories["object_person"] = obj_person_cat

    lang.pos_configs["verb"] = verb_config

    # Прилагательное
    adj_config = PartOfSpeechConfig(
        pos_id="adjective",
        name_ru="Прилагательное",
        name_en="Adjective",
        pos_class="content",
        category_order=[],
    )
    lang.pos_configs["adjective"] = adj_config

    # Наречие
    adv_config = PartOfSpeechConfig(
        pos_id="adverb",
        name_ru="Наречие",
        name_en="Adverb",
        pos_class="content",
        category_order=[],
    )
    lang.pos_configs["adverb"] = adv_config

    # Местоимение
    pron_config = PartOfSpeechConfig(
        pos_id="pronoun",
        name_ru="Местоимение",
        name_en="Pronoun",
        pos_class="content",
        category_order=["person", "number", "case"],
    )
    lang.pos_configs["pronoun"] = pron_config

    # Служебные слова (послелоги)
    lang.function_words = [
        FunctionWord(name="Послелог '-rekin'", form="-rekin", function="comitative", applies_to_category="case", applies_to_value="Comitative", word_type="postposition", position="after"),
        FunctionWord(name="Послелог '-entzat'", form="-entzat", function="benefactive", applies_to_category="case", applies_to_value="Benefactive", word_type="postposition", position="after"),
        FunctionWord(name="Союз 'eta'", form="eta", function="conjunction", applies_to_category="", applies_to_value="", word_type="conjunction", position="before"),
        FunctionWord(name="Отрицание 'ez'", form="ez", function="negation", applies_to_category="polarity", applies_to_value="Negative", word_type="particle", position="before"),
    ]

    # Прагматика
    lang.pragmatics = Pragmatics(
        deixis_spatial="3 степени: близко / средне / далеко",
        deixis_temporal="ближайшее / отдалённое",
        deixis_personal="я, ты, он/она, мы, вы, они",
        topic_marking="Порядок слов (топик в начале), частица '-a'",
        focus_marking="Позиция перед глаголом",
        evidentiality="none",
        politeness_levels=2,
        registers=[
            Register(name="Нейтральный", description="Повседневное общение"),
            Register(name="Формальный", description="Официальное общение (zuka)"),
        ],
        discourse_markers=["ba", "beraz", "hortaz"],
    )

    # Письменность
    lang.writing = WritingSystem(
        script_type="alphabetic",
        direction="ltr",
        alphabet="a b d e f g h i j k l m n ñ o p r s t u x z",
        has_diacritics=True,
        diacritics_notes="ñ",
        numeral_system="arabic",
    )

    # Словарь (Лейпциг-Джакарта, баскские корни)
    lang.words = [
        Word(conword="esku", localword="рука", lemma="esku", pos_id="noun"),
        Word(conword="ezker", localword="левый", lemma="ezker", pos_id="adjective"),
        Word(conword="eskuin", localword="правый", lemma="eskuin", pos_id="adjective"),
        Word(conword="oin", localword="нога", lemma="oin", pos_id="noun"),
        Word(conword="belaun", localword="колено", lemma="belaun", pos_id="noun"),
        Word(conword="ibili", localword="идти", lemma="ibili", pos_id="verb"),
        Word(conword="bide", localword="дорога", lemma="bide", pos_id="noun"),
        Word(conword="etorri", localword="прийти", lemma="etorri", pos_id="verb"),
        Word(conword="etzan", localword="лежать", lemma="etzan", pos_id="verb"),
        Word(conword="eseri", localword="сидеть", lemma="eseri", pos_id="verb"),
        Word(conword="zutik", localword="стоять", lemma="zutik", pos_id="verb"),
        Word(conword="pertsona", localword="человек", lemma="pertsona", pos_id="noun"),
        Word(conword="gizon", localword="мужчина", lemma="gizon", pos_id="noun"),
        Word(conword="emakume", localword="женщина", lemma="emakume", pos_id="noun"),
        Word(conword="haur", localword="ребёнок", lemma="haur", pos_id="noun"),
        Word(conword="senar", localword="муж", lemma="senar", pos_id="noun"),
        Word(conword="emazte", localword="жена", lemma="emazte", pos_id="noun"),
        Word(conword="ama", localword="мать", lemma="ama", pos_id="noun"),
        Word(conword="aita", localword="отец", lemma="aita", pos_id="noun"),
        Word(conword="etxe", localword="дом", lemma="etxe", pos_id="noun"),
        Word(conword="sabel", localword="живот", lemma="sabel", pos_id="noun"),
        Word(conword="lepo", localword="шея", lemma="lepo", pos_id="noun"),
        Word(conword="bular", localword="грудь", lemma="bular", pos_id="noun"),
        Word(conword="bihotz", localword="сердце", lemma="bihotz", pos_id="noun"),
        Word(conword="gibel", localword="печень", lemma="gibel", pos_id="noun"),
        Word(conword="edan", localword="пить", lemma="edan", pos_id="verb"),
        Word(conword="jan", localword="есть", lemma="jan", pos_id="verb"),
        Word(conword="kosk", localword="кусать", lemma="kosk", pos_id="verb"),
        Word(conword="ikusi", localword="видеть", lemma="ikusi", pos_id="verb"),
        Word(conword="entzun", localword="слышать", lemma="entzun", pos_id="verb"),
        Word(conword="jakin", localword="знать", lemma="jakin", pos_id="verb"),
        Word(conword="lo", localword="спать", lemma="lo", pos_id="verb"),
        Word(conword="hil", localword="умирать", lemma="hil", pos_id="verb"),
        Word(conword="hilketa", localword="убивать", lemma="hilketa", pos_id="verb"),
        Word(conword="igeri", localword="плавать", lemma="igeri", pos_id="verb"),
        Word(conword="hegan", localword="летать", lemma="hegan", pos_id="verb"),
        Word(conword="eguzki", localword="солнце", lemma="eguzki", pos_id="noun"),
        Word(conword="ilargi", localword="луна", lemma="ilargi", pos_id="noun"),
        Word(conword="izar", localword="звезда", lemma="izar", pos_id="noun"),
        Word(conword="ur", localword="вода", lemma="ur", pos_id="noun"),
        Word(conword="euri", localword="дождь", lemma="euri", pos_id="noun"),
        Word(conword="harri", localword="камень", lemma="harri", pos_id="noun"),
        Word(conword="hondar", localword="песок", lemma="hondar", pos_id="noun"),
        Word(conword="lur", localword="земля", lemma="lur", pos_id="noun"),
        Word(conword="hodei", localword="облако", lemma="hodei", pos_id="noun"),
        Word(conword="ke", localword="дым", lemma="ke", pos_id="noun"),
        Word(conword="su", localword="огонь", lemma="su", pos_id="noun"),
        Word(conword="errauts", localword="пепел", lemma="errauts", pos_id="noun"),
        Word(conword="erre", localword="гореть", lemma="erre", pos_id="verb"),
        Word(conword="bidezidor", localword="тропа", lemma="bidezidor", pos_id="noun"),
        Word(conword="mendi", localword="гора", lemma="mendi", pos_id="noun"),
        Word(conword="gorri", localword="красный", lemma="gorri", pos_id="adjective"),
        Word(conword="berde", localword="зелёный", lemma="berde", pos_id="adjective"),
        Word(conword="hori", localword="жёлтый", lemma="hori", pos_id="adjective"),
        Word(conword="zuri", localword="белый", lemma="zuri", pos_id="adjective"),
        Word(conword="beltz", localword="чёрный", lemma="beltz", pos_id="adjective"),
        Word(conword="gau", localword="ночь", lemma="gau", pos_id="noun"),
        Word(conword="bero", localword="горячий", lemma="bero", pos_id="adjective"),
        Word(conword="hotz", localword="холодный", lemma="hotz", pos_id="adjective"),
        Word(conword="bete", localword="полный", lemma="bete", pos_id="adjective"),
        Word(conword="berri", localword="новый", lemma="berri", pos_id="adjective"),
        Word(conword="on", localword="хороший", lemma="on", pos_id="adjective"),
        Word(conword="biribil", localword="круглый", lemma="biribil", pos_id="adjective"),
        Word(conword="lehor", localword="сухой", lemma="lehor", pos_id="adjective"),
        Word(conword="izen", localword="имя", lemma="izen", pos_id="noun"),
        Word(conword="esan", localword="говорить", lemma="esan", pos_id="verb"),
        Word(conword="abestu", localword="петь", lemma="abestu", pos_id="verb"),
        Word(conword="jolastu", localword="играть", lemma="jolastu", pos_id="verb"),
        Word(conword="igeri_egin", localword="плавать", lemma="igeri_egin", pos_id="verb"),
        Word(conword="isuri", localword="течь", lemma="isuri", pos_id="verb"),
        Word(conword="izoztu", localword="замерзать", lemma="izoztu", pos_id="verb"),
        Word(conword="puztu", localword="набухать", lemma="puztu", pos_id="verb"),
        Word(conword="zuhaitz", localword="дерево", lemma="zuhaitz", pos_id="noun"),
        Word(conword="makila", localword="палка", lemma="makila", pos_id="noun"),
        Word(conword="fruitu", localword="фрукт", lemma="fruitu", pos_id="noun"),
        Word(conword="hazi", localword="семя", lemma="hazi", pos_id="noun"),
        Word(conword="hosto", localword="лист", lemma="hosto", pos_id="noun"),
        Word(conword="erro", localword="корень", lemma="erro", pos_id="noun"),
        Word(conword="azal", localword="кора", lemma="azal", pos_id="noun"),
        Word(conword="lore", localword="цветок", lemma="lore", pos_id="noun"),
        Word(conword="belar", localword="трава", lemma="belar", pos_id="noun"),
        Word(conword="soka", localword="верёвка", lemma="soka", pos_id="noun"),
        Word(conword="larru", localword="кожа", lemma="larru", pos_id="noun"),
        Word(conword="haragi", localword="мясо", lemma="haragi", pos_id="noun"),
        Word(conword="odol", localword="кровь", lemma="odol", pos_id="noun"),
        Word(conword="hezur", localword="кость", lemma="hezur", pos_id="noun"),
        Word(conword="gantz", localword="жир", lemma="gantz", pos_id="noun"),
        Word(conword="arrautza", localword="яйцо", lemma="arrautza", pos_id="noun"),
        Word(conword="adar", localword="рог", lemma="adar", pos_id="noun"),
        Word(conword="buztan", localword="хвост", lemma="buztan", pos_id="noun"),
        Word(conword="luma", localword="перо", lemma="luma", pos_id="noun"),
        Word(conword="ile", localword="волосы", lemma="ile", pos_id="noun"),
        Word(conword="buru", localword="голова", lemma="buru", pos_id="noun"),
        Word(conword="belarri", localword="ухо", lemma="belarri", pos_id="noun"),
        Word(conword="begi", localword="глаз", lemma="begi", pos_id="noun"),
        Word(conword="sudur", localword="нос", lemma="sudur", pos_id="noun"),
    ]

    for w in lang.words:
        w.pronunciation = lang.phonology.generate_pronunciation(w.conword)

    return lang

# ═══════════════════════════════════════════════════════════════════════════
# КОДИРОВАНИЕ / ДЕКОДИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

def encode_language(lang: Language) -> str:
    """Кодирует состояние языка в компактную строку (DNA)."""
    json_str = json.dumps(lang.to_dict(), ensure_ascii=False, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    compressed = gzip.compress(json_bytes, compresslevel=9)
    dna = base64.urlsafe_b64encode(compressed).decode('ascii').rstrip('=')
    return dna


def decode_language(dna: str) -> Optional[Language]:
    """Декодирует строку DNA обратно в объект Language."""
    try:
        padding = 4 - (len(dna) % 4)
        if padding != 4:
            dna += '=' * padding
        compressed = base64.urlsafe_b64decode(dna)
        json_bytes = gzip.decompress(compressed)
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
        return Language.from_dict(data)
    except Exception as e:
        print(f"[DNA] Ошибка декодирования: {e}")
        return None


def encode_language_readable(lang: Language) -> str:
    """Кодирует состояние языка в читаемую JSON-строку (без сжатия)."""
    return json.dumps(lang.to_dict(), ensure_ascii=False, indent=2)


def get_dna_info(dna: str) -> dict:
    """Возвращает информацию о DNA-строке."""
    try:
        padding = 4 - (len(dna) % 4)
        if padding != 4:
            dna_padded = dna + '=' * padding
        else:
            dna_padded = dna
        compressed = base64.urlsafe_b64decode(dna_padded)
        decompressed = gzip.decompress(compressed)
        return {
            "dna_length": len(dna),
            "compressed_bytes": len(compressed),
            "decompressed_bytes": len(decompressed),
            "compression_ratio": f"{(1 - len(compressed)/len(decompressed)) * 100:.1f}%",
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# ПРЕСЕТЫ (словарь с готовыми DNA)
# ═══════════════════════════════════════════════════════════════════════════

PRESETS = {
    "russian": {
        "name": "Русский",
        "description": "Флективный славянский язык с трёхродовой системой, шестью падежами, двумя спряжениями",
        "dna": None,
    },
    "english": {
        "name": "English",
        "description": "Analytic Germanic language with SVO order, remnants of case in pronouns",
        "dna": None,
    },
    "basque": {
        "name": "Euskara (Баскский)",
        "description": "Эргативный язык-изолят с полиперсональным согласованием, SOV порядок",
        "dna": None,
    },
}


def _init_presets():
    """Генерирует DNA для всех пресетов при первом импорте."""
    if PRESETS["russian"]["dna"] is None:
        PRESETS["russian"]["dna"] = encode_language(generate_russian_preset())
    if PRESETS["english"]["dna"] is None:
        PRESETS["english"]["dna"] = encode_language(generate_english_preset())
    if PRESETS["basque"]["dna"] is None:
        PRESETS["basque"]["dna"] = encode_language(generate_basque_preset())


_init_presets()
