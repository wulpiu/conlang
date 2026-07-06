"""
Универсальные грамматические отношения (Grammatical Relations).
Основано на лингвистической типологии и стандартных синтаксических функциях.
Используется для анализа предложений и правильного согласования.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# ТИПЫ ГРАММАТИЧЕСКИХ ОТНОШЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════

class RelationType(Enum):
    """Типы синтаксических отношений (грамматических функций)."""

    # Ядерные отношения (core arguments)
    SUBJECT = "subj"                    # Субъект (подлежащее)
    DIRECT_OBJECT = "obj"               # Прямой объект (дополнение)
    INDIRECT_OBJECT = "iobj"            # Косвенный объект (адресат)
    OBLIQUE = "obl"                     # Косвенное дополнение (предложное)

    # Предикативные отношения
    PREDICATE = "pred"                  # Предикат (сказуемое)
    COPULA = "cop"                      # Связка (быть, являться)
    PREDICATIVE = "predc"               # Именная часть сказуемого

    # Атрибутивные отношения
    ATTRIBUTE = "attr"                  # Определение (прилагательное)
    APPOSITION = "appos"                # Приложение
    DETERMINER = "det"                  # Детерминатив (артикль, указатель)
    POSSESSOR = "poss"                  # Посессор (владелец)

    # Адвербиальные отношения
    ADVERBIAL = "adv"                   # Обстоятельство
    TEMPORAL = "temp"                   # Временное обстоятельство
    LOCATIVE = "loc"                    # Пространственное обстоятельство
    MANNER = "man"                      # Образа действия
    CAUSE = "caus"                      # Причины
    PURPOSE = "purp"                    # Цели

    # Модификаторы
    MODIFIER = "mod"                    # Общий модификатор
    QUANTIFIER = "quant"                # Квантификатор (много, мало)
    NUMERAL = "num"                     # Числительное

    # Комплементы и клаузы
    COMPLEMENT = "comp"                 # Комплемент (дополнение клаузы)
    CLAUSAL_COMPLEMENT = "ccomp"        # Клаузальный комплемент
    RELATIVE_CLAUSE = "rel"             # Относительное придаточное
    ADVERBIAL_CLAUSE = "advcl"          # Обстоятельственное придаточное

    # Сочинительные отношения
    CONJUNCTION = "conj"                # Сочинительный союз
    COORDINATION = "coord"              # Сочинение

    # Вспомогательные
    AUXILIARY = "aux"                   # Вспомогательный глагол
    NEGATION = "neg"                    # Отрицание
    QUESTION = "q"                      # Вопросительная частица
    TOPIC = "top"                       # Тема (топик)
    FOCUS = "foc"                       # Фокус (рема)

    # Специальные
    VOCATIVE = "voc"                    # Обращение (звательный)
    DISCOURSE = "disc"                  # Дискурсивный маркер
    EXPLETIVE = "expl"                  # Эксплетив (формальное подлежащее)

    # Корень (для dependency grammars)
    ROOT = "root"                       # Корень предложения


# ═══════════════════════════════════════════════════════════════════════════
# ЧЕЛОВЕКОЧИТАЕМЫЕ НАЗВАНИЯ
# ═══════════════════════════════════════════════════════════════════════════

RELATION_NAMES_RU = {
    "subj": "Субъект",
    "obj": "Прямой объект",
    "iobj": "Косвенный объект",
    "obl": "Косвенное дополнение",
    "pred": "Предикат",
    "cop": "Связка",
    "predc": "Именная часть",
    "attr": "Определение",
    "appos": "Приложение",
    "det": "Детерминатив",
    "poss": "Посессор",
    "adv": "Обстоятельство",
    "temp": "Время",
    "loc": "Место",
    "man": "Образ действия",
    "caus": "Причина",
    "purp": "Цель",
    "mod": "Модификатор",
    "quant": "Квантификатор",
    "num": "Числительное",
    "comp": "Комплемент",
    "ccomp": "Клаузальный комплемент",
    "rel": "Относительное",
    "advcl": "Обст. придаточное",
    "conj": "Союз",
    "coord": "Сочинение",
    "aux": "Вспом. глагол",
    "neg": "Отрицание",
    "q": "Вопрос",
    "top": "Тема",
    "foc": "Фокус",
    "voc": "Обращение",
    "disc": "Дискурсив",
    "expl": "Формальное",
    "root": "Корень",
}

RELATION_NAMES_EN = {
    "subj": "Subject",
    "obj": "Direct Object",
    "iobj": "Indirect Object",
    "obl": "Oblique",
    "pred": "Predicate",
    "cop": "Copula",
    "predc": "Predicative",
    "attr": "Attribute",
    "appos": "Apposition",
    "det": "Determiner",
    "poss": "Possessor",
    "adv": "Adverbial",
    "temp": "Temporal",
    "loc": "Locative",
    "man": "Manner",
    "caus": "Cause",
    "purp": "Purpose",
    "mod": "Modifier",
    "quant": "Quantifier",
    "num": "Numeral",
    "comp": "Complement",
    "ccomp": "Clausal Complement",
    "rel": "Relative Clause",
    "advcl": "Adverbial Clause",
    "conj": "Conjunction",
    "coord": "Coordination",
    "aux": "Auxiliary",
    "neg": "Negation",
    "q": "Question",
    "top": "Topic",
    "foc": "Focus",
    "voc": "Vocative",
    "disc": "Discourse",
    "expl": "Expletive",
    "root": "Root",
}


# ═══════════════════════════════════════════════════════════════════════════
# СВЯЗЬ С ПАДЕЖАМИ (морфологическое выражение)
# ═══════════════════════════════════════════════════════════════════════════

# Как грамматические отношения выражаются падежами в разных строях
RELATION_TO_CASE = {
    "nominative-accusative": {
        "subj": "nominative",           # Субъект → Номинатив
        "obj": "accusative",            # Объект → Аккузатив
        "iobj": "dative",               # Косв. объект → Датив
        "poss": "genitive",             # Посессор → Генитив
    },
    "ergative-absolutive": {
        "subj": "ergative",             # Субъект переходного → Эргатив
        "subj_intrans": "absolutive",   # Субъект непереходного → Абсолютив
        "obj": "absolutive",            # Объект → Абсолютив
        "iobj": "dative",               # Косв. объект → Датив
        "poss": "genitive",             # Посессор → Генитив
    },
    "active-stative": {
        "subj_active": "agentive",      # Активный субъект → Агентив
        "subj_stative": "patientive",   # Статальный субъект → Пациентив
        "obj": "patientive",            # Объект → Пациентив
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# СВЯЗЬ С ПОЗИЦИЕЙ В ПРЕДЛОЖЕНИИ (конфигурационное выражение)
# ═══════════════════════════════════════════════════════════════════════════

# Позиция отношений в зависимости от базового порядка слов
RELATION_POSITION = {
    "SOV": {
        "subj": 0,      # Субъект первый
        "obj": 1,       # Объект второй
        "pred": 2,      # Глагол последний
        "iobj": 1.5,    # Косв. объект между прямым и глаголом
    },
    "SVO": {
        "subj": 0,      # Субъект первый
        "pred": 1,      # Глагол второй
        "obj": 2,       # Объект третий
        "iobj": 2.5,    # Косв. объект после прямого
    },
    "VSO": {
        "pred": 0,      # Глагол первый
        "subj": 1,      # Субъект второй
        "obj": 2,       # Объект третий
    },
    "VOS": {
        "pred": 0,      # Глагол первый
        "obj": 1,       # Объект второй
        "subj": 2,      # Субъект третий
    },
    "OVS": {
        "obj": 0,       # Объект первый
        "pred": 1,      # Глагол второй
        "subj": 2,      # Субъект третий
    },
    "OSV": {
        "obj": 0,       # Объект первый
        "subj": 1,      # Субъект второй
        "pred": 2,      # Глагол третий
    },
}

# Позиция атрибутов
ATTRIBUTE_POSITION = {
    "adj": {
        "before": "attr",   # Прилагательное перед существительным
        "after": "attr",    # Прилагательное после существительного
    },
    "gen": {
        "before": "poss",   # Генитив перед существительным
        "after": "poss",    # Генитив после существительного
    },
    "det": {
        "before": "det",    # Детерминатив перед существительным
        "after": "det",     # Детерминатив после существительного
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# СВЯЗЬ С СОГЛАСОВАНИЕМ
# ═══════════════════════════════════════════════════════════════════════════

# Какие отношения требуют согласования
AGREEMENT_RULES = [
    {
        "controller": "subj",           # Кто управляет
        "target": "pred",               # Кто согласуется
        "features": ["person", "number", "gender"],  # По каким признакам
    },
    {
        "controller": "subj",
        "target": "aux",
        "features": ["person", "number"],
    },
    {
        "controller": "obj",
        "target": "pred",               # Полиперсональное согласование
        "features": ["person", "number"],
    },
    {
        "controller": "noun",           # Существительное (любое)
        "target": "attr",               # Прилагательное
        "features": ["case", "number", "gender"],
    },
    {
        "controller": "noun",
        "target": "det",                # Артикль/детерминатив
        "features": ["case", "number", "gender"],
    },
    {
        "controller": "antecedent",     # Антецедент
        "target": "rel",                # Относительное местоимение
        "features": ["number", "gender"],
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# КЛАСС ДЛЯ ХРАНЕНИЯ ОТНОШЕНИЙ В ПРЕДЛОЖЕНИИ
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GrammaticalRelation:
    """
    Одно грамматическое отношение в предложении.
    Связывает два слова (или слово и группу).
    """
    relation_type: str = ""         # Тип отношения (subj, obj, attr, etc.)
    head_index: int = -1            # Индекс главного слова (к которому относится)
    dependent_index: int = -1       # Индекс зависимого слова
    features: Dict[str, str] = field(default_factory=dict)  # Доп. признаки

    def get_relation_display(self, lang: str = "ru") -> str:
        """Возвращает человекочитаемое название отношения."""
        if lang == "ru":
            return RELATION_NAMES_RU.get(self.relation_type, self.relation_type)
        return RELATION_NAMES_EN.get(self.relation_type, self.relation_type)


@dataclass
class SentenceAnalysis:
    """
    Результат анализа предложения — список токенов и отношения между ними.
    """
    tokens: List[Any] = field(default_factory=list)           # Список токенов (из text_analyzer)
    relations: List[GrammaticalRelation] = field(default_factory=list)  # Отношения
    root_index: int = -1                                       # Индекс корневого слова

    def get_subject(self) -> Optional[Any]:
        """Возвращает токен субъекта."""
        for rel in self.relations:
            if rel.relation_type == "subj":
                return self.tokens[rel.dependent_index] if rel.dependent_index < len(self.tokens) else None
        return None

    def get_predicate(self) -> Optional[Any]:
        """Возвращает токен предиката (глагола)."""
        for rel in self.relations:
            if rel.relation_type == "pred":
                return self.tokens[rel.dependent_index] if rel.dependent_index < len(self.tokens) else None
        return None

    def get_object(self) -> Optional[Any]:
        """Возвращает токен прямого объекта."""
        for rel in self.relations:
            if rel.relation_type == "obj":
                return self.tokens[rel.dependent_index] if rel.dependent_index < len(self.tokens) else None
        return None

    def get_indirect_object(self) -> Optional[Any]:
        """Возвращает токен косвенного объекта."""
        for rel in self.relations:
            if rel.relation_type == "iobj":
                return self.tokens[rel.dependent_index] if rel.dependent_index < len(self.tokens) else None
        return None

    def get_attributes(self, head_index: int) -> List[Any]:
        """Возвращает все атрибуты для указанного главного слова."""
        attrs = []
        for rel in self.relations:
            if rel.relation_type in ("attr", "det", "poss", "num", "quant") and rel.head_index == head_index:
                attrs.append(self.tokens[rel.dependent_index])
        return attrs

    def get_adverbials(self, head_index: int) -> List[Any]:
        """Возвращает все обстоятельства для указанного главного слова."""
        advs = []
        for rel in self.relations:
            if rel.relation_type in ("adv", "temp", "loc", "man") and rel.head_index == head_index:
                advs.append(self.tokens[rel.dependent_index])
        return advs


# ═══════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════

def get_relation_display(relation_type: str, lang: str = "ru") -> str:
    """Возвращает человекочитаемое название типа отношения."""
    if lang == "ru":
        return RELATION_NAMES_RU.get(relation_type, relation_type)
    return RELATION_NAMES_EN.get(relation_type, relation_type)


def get_case_for_relation(relation_type: str, alignment: str, is_transitive: bool = True) -> str:
    """
    Возвращает падеж, соответствующий грамматическому отношению
    в зависимости от синтаксического строя.
    """
    mapping = RELATION_TO_CASE.get(alignment, RELATION_TO_CASE["nominative-accusative"])

    if alignment == "ergative-absolutive":
        if relation_type == "subj" and is_transitive:
            return mapping.get("subj", "ergative")
        elif relation_type == "subj" and not is_transitive:
            return mapping.get("subj_intrans", "absolutive")

    return mapping.get(relation_type, "")


def get_default_position(relation_type: str, word_order: str) -> float:
    """
    Возвращает позицию отношения в предложении (0 = первое, 1 = второе и т.д.)
    для заданного базового порядка слов.
    """
    positions = RELATION_POSITION.get(word_order, RELATION_POSITION["SVO"])
    return positions.get(relation_type, 99)  # 99 = в конец


def get_agreement_features(controller_type: str, target_type: str) -> List[str]:
    """
    Возвращает список признаков, по которым target согласуется с controller.
    """
    for rule in AGREEMENT_RULES:
        if rule["controller"] == controller_type and rule["target"] == target_type:
            return rule["features"]
    return []


def is_core_relation(relation_type: str) -> bool:
    """Проверяет, является ли отношение ядерным (субъект, объект, предикат)."""
    return relation_type in ("subj", "obj", "iobj", "pred")


def is_modifier_relation(relation_type: str) -> bool:
    """Проверяет, является ли отношение модификатором (атрибут, обстоятельство)."""
    return relation_type in ("attr", "det", "poss", "adv", "temp", "loc", "man", "mod")
