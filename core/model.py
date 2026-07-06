"""
Модель данных ConLang Studio.
Каждый раздел чеклиста — отдельный датакласс.
Всё сериализуется в/из dict для JSON.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


def _dc(d: dict, cls):
    """Создать датакласс из словаря, игнорируя лишние ключи."""
    known = {k for k in cls.__dataclass_fields__}
    return cls(**{k: v for k, v in d.items() if k in known})


# ═══════════════════════════════════════════════════════════════════════════
# ФОНЕТИКА И ФОНОЛОГИЯ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Vowel:
    symbol: str = ""
    height: str = ""
    backness: str = ""
    rounded: bool = False
    nasal: bool = False
    long: bool = False
    notes: str = ""


@dataclass
class Consonant:
    symbol: str = ""
    place: str = ""
    manner: str = ""
    voiced: bool = True
    aspirated: bool = False
    palatalized: bool = False
    labialized: bool = False
    ejective: bool = False
    notes: str = ""


@dataclass
class Prosody:
    stress_type: str = ""
    stress_position: str = ""
    tone_count: int = 0
    tone_names: list = field(default_factory=list)
    length_phonemic: bool = False
    notes: str = ""


@dataclass
class Phonotactics:
    syllable_templates: list = field(default_factory=lambda: ["CV"])
    max_onset: int = 1
    max_coda: int = 1
    vowel_harmony: bool = False
    harmony_type: str = ""
    forbidden_clusters: list = field(default_factory=list)
    notes: str = ""

    @property
    def syllable_template(self) -> str:
        """Для обратной совместимости."""
        return self.syllable_templates[0] if self.syllable_templates else "CV"


@dataclass
class PhonemeRule:
    chars: str = ""
    pronun: str = ""
    priority: int = 0


@dataclass
class Phonology:
    vowels: list[Vowel] = field(default_factory=list)
    consonants: list[Consonant] = field(default_factory=list)
    prosody: Prosody = field(default_factory=Prosody)
    phonotactics: Phonotactics = field(default_factory=Phonotactics)
    phoneme_rules: list[PhonemeRule] = field(default_factory=list)

    def generate_pronunciation(self, word: str) -> str:
        result = word
        for r in sorted(self.phoneme_rules, key=lambda x: -x.priority):
            result = result.replace(r.chars, r.pronun)
        return result


# ═══════════════════════════════════════════════════════════════════════════
# МОРФОЛОГИЯ (старая, deprecated)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LangType:
    primary: str = ""
    notes: str = ""


@dataclass
class MorphemeTypes:
    has_prefixes: bool = False
    has_suffixes: bool = False
    has_postfixes: bool = False
    has_infixes: bool = False
    has_circumfixes: bool = False
    has_interfixes: bool = False
    has_transfixes: bool = False
    has_duplifixes: bool = False
    has_simulfixes: bool = False
    has_disfixes: bool = False
    has_suprafixes: bool = False
    has_clitics: bool = False
    reduplication: str = ""
    notes: str = ""


@dataclass
class MorphProcess:
    name: str = ""
    process_type: str = ""
    description: str = ""


@dataclass
class GramCategory:
    name: str = ""
    abbr: str = ""
    notes: str = ""


@dataclass
class GramCategoryGroup:
    name: str = ""
    cat_type: str = ""
    values: list[GramCategory] = field(default_factory=list)
    notes: str = ""


@dataclass
class PartOfSpeech:
    id: str = ""
    name_ru: str = ""
    name_en: str = ""
    pos_class: str = ""
    notes: str = ""

    def display(self, lang: str) -> str:
        return self.name_ru if lang == "ru" else self.name_en


@dataclass
class Morphology:
    lang_type: LangType = field(default_factory=LangType)
    morpheme_types: MorphemeTypes = field(default_factory=MorphemeTypes)
    morph_processes: list[MorphProcess] = field(default_factory=list)
    parts_of_speech: list[PartOfSpeech] = field(default_factory=list)
    gram_categories: list[GramCategoryGroup] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# СТАРАЯ ПАРАДИГМА (deprecated)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AffixRule:
    form_name: str = ""
    affix_type: str = "suffix"
    affix_pattern: str = ""
    example_input: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return _dc(d, cls)


@dataclass
class Paradigm:
    pos_id: str = ""
    rules: list[AffixRule] = field(default_factory=list)

    def to_dict(self):
        return {"pos_id": self.pos_id, "rules": [r.to_dict() for r in self.rules]}

    @classmethod
    def from_dict(cls, d):
        p = cls(pos_id=d.get("pos_id", ""))
        p.rules = [AffixRule.from_dict(r) for r in d.get("rules", [])]
        return p


# ═══════════════════════════════════════════════════════════════════════════
# ЛЕКСИКОН
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Word:
    conword: str = ""
    localword: str = ""
    lemma: str = ""
    pos_id: str = ""
    definition: str = ""
    pronunciation: str = ""
    override_pronun: bool = False
    gram_values: dict = field(default_factory=dict)
    etymology: str = ""
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# СЛОВООБРАЗОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CompoundRule:
    pattern: str = ""
    description: str = ""
    example: str = ""


@dataclass
class WordFormation:
    compound_rules: list[CompoundRule] = field(default_factory=list)
    conversion_notes: str = ""
    abbreviation_notes: str = ""
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# СИНТАКСИС
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Syntax:
    basic_order: str = ""
    alignment: str = ""
    split_ergativity: str = ""
    head_direction: str = ""
    adj_position: str = ""
    gen_position: str = ""
    adposition_type: str = ""
    question_formation: str = ""
    negation_type: str = ""
    relative_clause: str = ""
    agreement_notes: str = ""
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# ПРАГМАТИКА И ДИСКУРС
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Register:
    name: str = ""
    description: str = ""


@dataclass
class Pragmatics:
    deixis_spatial: str = ""
    deixis_temporal: str = ""
    deixis_personal: str = ""
    topic_marking: str = ""
    focus_marking: str = ""
    evidentiality: str = ""
    politeness_levels: int = 0
    registers: list[Register] = field(default_factory=list)
    discourse_markers: list[str] = field(default_factory=list)
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# ПИСЬМЕННОСТЬ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class WritingSystem:
    script_type: str = ""
    direction: str = ""
    alphabet: str = ""
    has_diacritics: bool = False
    diacritics_notes: str = ""
    punctuation_notes: str = ""
    numeral_system: str = ""
    orthography_notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# НОВАЯ МОДЕЛЬ: УНИФИЦИРОВАННЫЕ ПАРАДИГМЫ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GrammarRule:
    """Одно правило для одного значения грамматической категории."""
    value_id: str = ""
    enabled: bool = False
    affix_type: str = "suffix"
    affix_pattern: str = ""
    example_input: str = ""
    example_output: str = ""
    # Флексия
    fusion_category: str = ""
    fusion_value: str = ""
    fusion_pattern: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "GrammarRule":
        return _dc(d, cls)


@dataclass
class GrammaticalCategory:
    """Настроенная грамматическая категория для части речи."""
    category_id: str = ""
    enabled: bool = False
    rules: dict[str, GrammarRule] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "category_id": self.category_id,
            "enabled": self.enabled,
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GrammaticalCategory":
        cat = cls(
            category_id=d.get("category_id", ""),
            enabled=d.get("enabled", False),
        )
        for value_id, rule_dict in d.get("rules", {}).items():
            cat.rules[value_id] = GrammarRule.from_dict(rule_dict)
        return cat


@dataclass
class PartOfSpeechConfig:
    """Полная конфигурация части речи."""
    pos_id: str = ""
    name_ru: str = ""
    name_en: str = ""
    pos_class: str = "content"
    notes: str = ""
    categories: dict[str, GrammaticalCategory] = field(default_factory=dict)
    # Приоритеты категорий
    category_order: list[str] = field(default_factory=list)
    # Инкорпорация
    incorporation_enabled: bool = False
    incorporation_position: str = "before"
    incorporation_pattern: str = "{object}-{verb}"
    incorporation_notes: str = ""

    def display(self, lang: str) -> str:
        return self.name_ru if lang == "ru" else self.name_en

    def to_dict(self) -> dict:
        return {
            "pos_id": self.pos_id,
            "name_ru": self.name_ru,
            "name_en": self.name_en,
            "pos_class": self.pos_class,
            "notes": self.notes,
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "category_order": self.category_order,
            "incorporation_enabled": self.incorporation_enabled,
            "incorporation_position": self.incorporation_position,
            "incorporation_pattern": self.incorporation_pattern,
            "incorporation_notes": self.incorporation_notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PartOfSpeechConfig":
        config = cls(
            pos_id=d.get("pos_id", ""),
            name_ru=d.get("name_ru", ""),
            name_en=d.get("name_en", ""),
            pos_class=d.get("pos_class", "content"),
            notes=d.get("notes", ""),
            category_order=d.get("category_order", []),
            incorporation_enabled=d.get("incorporation_enabled", False),
            incorporation_position=d.get("incorporation_position", "before"),
            incorporation_pattern=d.get("incorporation_pattern", "{object}-{verb}"),
            incorporation_notes=d.get("incorporation_notes", ""),
        )
        for cat_id, cat_dict in d.get("categories", {}).items():
            config.categories[cat_id] = GrammaticalCategory.from_dict(cat_dict)
        return config


# ═══════════════════════════════════════════════════════════════════════════
# СЛУЖЕБНЫЕ СЛОВА
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FunctionWord:
    """Служебное слово для аналитических языков."""
    name: str = ""
    form: str = ""
    function: str = ""
    applies_to_category: str = ""
    applies_to_value: str = ""
    word_type: str = ""
    position: str = "before"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FunctionWord":
        if "word_type" not in d:
            d["word_type"] = ""
        return _dc(d, cls)


# ═══════════════════════════════════════════════════════════════════════════
# СИНТАКСИЧЕСКИЙ АНАЛИЗ (для конструктора предложений)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GrammaticalRelation:
    """Одно грамматическое отношение в предложении."""
    relation_type: str = ""
    head_index: int = -1
    dependent_index: int = -1


@dataclass
class SentenceAnalysis:
    """Результат синтаксического анализа предложения."""
    tokens: list = field(default_factory=list)
    relations: list[GrammaticalRelation] = field(default_factory=list)
    root_index: int = -1

    def has_object(self) -> bool:
        """Проверяет, есть ли в предложении прямой объект."""
        for rel in self.relations:
            if rel.relation_type == "obj":
                return True
        return False

    def get_subject(self) -> Optional[Any]:
        """Возвращает токен субъекта."""
        for rel in self.relations:
            if rel.relation_type == "subj" and rel.dependent_index < len(self.tokens):
                return self.tokens[rel.dependent_index]
        return None

    def get_predicate(self) -> Optional[Any]:
        """Возвращает токен предиката."""
        for rel in self.relations:
            if rel.relation_type == "pred" and rel.dependent_index < len(self.tokens):
                return self.tokens[rel.dependent_index]
        return None

    def get_object(self) -> Optional[Any]:
        """Возвращает токен прямого объекта."""
        for rel in self.relations:
            if rel.relation_type == "obj" and rel.dependent_index < len(self.tokens):
                return self.tokens[rel.dependent_index]
        return None


# ═══════════════════════════════════════════════════════════════════════════
# СТАНДАРТНЫЕ ЧАСТИ РЕЧИ
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_POS_CONFIGS = [
    ("noun", "Существительное", "Noun", "content"),
    ("pronoun", "Местоимение", "Pronoun", "content"),
    ("verb", "Глагол", "Verb", "content"),
    ("adjective", "Прилагательное", "Adjective", "content"),
    ("numeral", "Числительное", "Numeral", "content"),
    ("adverb", "Наречие", "Adverb", "content"),
    ("participle", "Причастие", "Participle", "content"),
    ("gerund", "Герундий", "Gerund", "content"),
    ("gerundive", "Деепричастие", "Gerundive", "content"),
    ("adposition", "Адпозиция", "Adposition", "function"),
    ("conjunction", "Союз", "Conjunction", "function"),
    ("particle", "Частица", "Particle", "function"),
    ("interjection", "Междометие", "Interjection", "function"),
]


# ═══════════════════════════════════════════════════════════════════════════
# КОРНЕВОЙ ОБЪЕКТ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Language:
    name: str = "Новый язык"
    local_language: str = "Русский"
    author: str = ""
    description: str = ""
    version: str = "1.0"

    phonology: Phonology = field(default_factory=Phonology)
    morphology: Morphology = field(default_factory=Morphology)
    words: list[Word] = field(default_factory=list)
    word_formation: WordFormation = field(default_factory=WordFormation)
    syntax: Syntax = field(default_factory=Syntax)
    pragmatics: Pragmatics = field(default_factory=Pragmatics)
    writing: WritingSystem = field(default_factory=WritingSystem)

    word_unique: bool = True
    pos_mandatory: bool = True
    def_mandatory: bool = False
    extra: dict = field(default_factory=dict)

    paradigms: list[Paradigm] = field(default_factory=list)
    pos_configs: dict[str, PartOfSpeechConfig] = field(default_factory=dict)
    function_words: list[FunctionWord] = field(default_factory=list)

    def __post_init__(self):
        # Раньше дефолтные части речи подставлялись только при загрузке
        # файла (from_dict), поэтому свежесозданный Language() отличался
        # от того же языка после одного цикла save/load. Теперь дефолты
        # есть сразу, в момент создания объекта.
        if not self.pos_configs:
            self._init_default_pos_configs()

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pos_configs"] = {k: v.to_dict() for k, v in self.pos_configs.items()}
        data["function_words"] = [fw.to_dict() for fw in self.function_words]
        for w in data["words"]:
            if not w["lemma"]:
                w["lemma"] = w["localword"].lower()
        return data

    @classmethod
    def from_dict(cls, d: dict) -> "Language":
        lang = cls(
            name=d.get("name", "Новый язык"),
            local_language=d.get("local_language", "Русский"),
            author=d.get("author", ""),
            description=d.get("description", ""),
            version=d.get("version", "1.0"),
            word_unique=d.get("word_unique", True),
            pos_mandatory=d.get("pos_mandatory", True),
            def_mandatory=d.get("def_mandatory", False),
        )
        lang.extra = d.get("extra", {})
        lang.paradigms = [Paradigm.from_dict(p) for p in d.get("paradigms", [])]

        ph = d.get("phonology", {})
        lang.phonology = Phonology(
            vowels=[_dc(v, Vowel) for v in ph.get("vowels", [])],
            consonants=[_dc(c, Consonant) for c in ph.get("consonants", [])],
            prosody=_dc(ph.get("prosody", {}), Prosody),
            phonotactics=_dc(ph.get("phonotactics", {}), Phonotactics),
            phoneme_rules=[_dc(r, PhonemeRule) for r in ph.get("phoneme_rules", [])],
        )

        mo = d.get("morphology", {})
        morph = Morphology(
            lang_type=_dc(mo.get("lang_type", {}), LangType),
            morpheme_types=_dc(mo.get("morpheme_types", {}), MorphemeTypes),
            morph_processes=[_dc(p, MorphProcess) for p in mo.get("morph_processes", [])],
        )
        for p in mo.get("parts_of_speech", []):
            morph.parts_of_speech.append(_dc(p, PartOfSpeech))
        for g in mo.get("gram_categories", []):
            grp = _dc(g, GramCategoryGroup)
            grp.values = [_dc(v, GramCategory) for v in g.get("values", [])]
            morph.gram_categories.append(grp)
        lang.morphology = morph

        lang.words = [_dc(w, Word) for w in d.get("words", [])]
        for w in lang.words:
            if not w.lemma:
                w.lemma = w.localword.lower()

        wf = d.get("word_formation", {})
        lang.word_formation = WordFormation(
            compound_rules=[_dc(r, CompoundRule) for r in wf.get("compound_rules", [])],
            conversion_notes=wf.get("conversion_notes", ""),
            abbreviation_notes=wf.get("abbreviation_notes", ""),
            notes=wf.get("notes", ""),
        )

        lang.syntax = _dc(d.get("syntax", {}), Syntax)

        pr = d.get("pragmatics", {})
        prag = _dc(pr, Pragmatics)
        prag.registers = [_dc(r, Register) for r in pr.get("registers", [])]
        prag.discourse_markers = pr.get("discourse_markers", [])
        lang.pragmatics = prag

        lang.writing = _dc(d.get("writing", {}), WritingSystem)

        pos_configs_dict = d.get("pos_configs", {})
        for pos_id, config_dict in pos_configs_dict.items():
            lang.pos_configs[pos_id] = PartOfSpeechConfig.from_dict(config_dict)

        lang.function_words = [FunctionWord.from_dict(fw) for fw in d.get("function_words", [])]

        if not lang.pos_configs:
            lang._init_default_pos_configs()

        return lang

    def _init_default_pos_configs(self):
        from core.linguistic_data import UNIVERSAL_CATEGORIES, get_default_category_order
        for pos_id, name_ru, name_en, pos_class in DEFAULT_POS_CONFIGS:
            config = PartOfSpeechConfig(
                pos_id=pos_id,
                name_ru=name_ru,
                name_en=name_en,
                pos_class=pos_class,
                category_order=get_default_category_order(pos_id),
            )
            for cat_id in UNIVERSAL_CATEGORIES.get(pos_id, []):
                config.categories[cat_id] = GrammaticalCategory(category_id=cat_id, enabled=False)
            self.pos_configs[pos_id] = config
