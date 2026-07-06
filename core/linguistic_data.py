"""
Универсальная база лингвистических знаний.
Содержит полные списки грамматических категорий, их значений,
смысловые нагрузки служебных слов, словообразовательных аффиксов,
и универсальные иерархии (приоритеты) категорий.
Основано на WALS, Wikipedia, Bybee (1985), Greenberg (1963).
"""

# ═══════════════════════════════════════════════════════════════════════════
# 1. УНИВЕРСАЛЬНЫЕ ГРАММАТИЧЕСКИЕ КАТЕГОРИИ ДЛЯ КАЖДОЙ ЧАСТИ РЕЧИ
# ═══════════════════════════════════════════════════════════════════════════

UNIVERSAL_CATEGORIES = {
    # Именные части речи
    "noun": [
        "case",         # Падеж
        "number",       # Число
        "gender",       # Род / Именной класс
        "definiteness", # Определённость
        "animacy",      # Одушевлённость
        "possession",   # Посессивность (притяжательные формы)
        "derivation",   # Словообразование (деривация)
    ],

    "pronoun": [
        "case",         # Падеж
        "number",       # Число
        "gender",       # Род
        "person",       # Лицо
        "clusivity",    # Клюзивность (инклюзивное/эксклюзивное "мы")
        "definiteness", # Определённость
        "politeness",   # Вежливость (ты/Вы)
        "animacy",      # Одушевлённость
    ],

    "adjective": [
        "degree",       # Степень сравнения
        "case",         # Падеж (согласование)
        "number",       # Число (согласование)
        "gender",       # Род (согласование)
        "definiteness", # Определённость
        "derivation",   # Словообразование (деривация)
    ],

    "numeral": [
        "case",         # Падеж
        "number",       # Число
        "gender",       # Род
        "derivation",   # Словообразование (порядковые, собирательные)
    ],

    # Глагольные части речи
    "verb": [
        "tense",        # Время
        "aspect",       # Вид
        "mood",         # Наклонение
        "voice",        # Залог
        "person",       # Лицо (согласование с субъектом)
        "number",       # Число (согласование с субъектом)
        "gender",       # Род (согласование с субъектом)
        "evidentiality",# Эвиденциальность (источник информации)
        "polarity",     # Полярность (утверждение/отрицание)
        "transitivity", # Переходность
        "valency",      # Валентность (количество актантов)
        "causativity",  # Каузативность
        "reciprocity",  # Реципрок (взаимность)
        "reflexivity",  # Рефлексив (возвратность)
        "derivation",   # Словообразование (деривация)
    ],

    "participle": [
        "tense",        # Время
        "aspect",       # Вид
        "voice",        # Залог
        "case",         # Падеж
        "number",       # Число
        "gender",       # Род
    ],

    "gerund": [
        "case",         # Падеж
        "number",       # Число
    ],

    "gerundive": [
        "case",         # Падеж
        "number",       # Число
        "gender",       # Род
    ],

    # Наречия
    "adverb": [
        "degree",       # Степень сравнения
        "derivation",   # Словообразование (от прилагательных)
    ],

    # Служебные части речи
    "adposition": [
        "case",         # Падеж, которым управляет предлог/послелог
    ],

    "conjunction": [],
    "particle": [],
    "interjection": [],
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. УНИВЕРСАЛЬНЫЕ ИЕРАРХИИ (ПРИОРИТЕТЫ) КАТЕГОРИЙ
#    Основано на: Bybee (1985), Greenberg (1963)
#    Порядок: от ближнего к корню → к дальнему
# ═══════════════════════════════════════════════════════════════════════════

UNIVERSAL_CATEGORY_ORDER = {
    # Именная группа: корень → деривация → число → род → падеж → определённость
    "noun": [
        "derivation",      # Словообразование (уменьшительное, деятель)
        "number",          # Число
        "gender",          # Род / Именной класс
        "possession",      # Посессивность
        "case",            # Падеж
        "definiteness",    # Определённость
        "animacy",         # Одушевлённость
    ],

    "pronoun": [
        "person",          # Лицо
        "number",          # Число
        "gender",          # Род
        "clusivity",       # Клюзивность
        "case",            # Падеж
        "politeness",      # Вежливость
        "definiteness",    # Определённость
        "animacy",         # Одушевлённость
    ],

    "adjective": [
        "derivation",      # Словообразование
        "degree",          # Степень сравнения
        "number",          # Число
        "gender",          # Род
        "case",            # Падеж
        "definiteness",    # Определённость
    ],

    "numeral": [
        "derivation",      # Порядковые, собирательные
        "number",          # Число
        "gender",          # Род
        "case",            # Падеж
    ],

    # Глагольная группа: корень → валентность → залог → вид → время → наклонение → лицо/число
    "verb": [
        "derivation",      # Словообразование (отыменные глаголы)
        "valency",         # Валентность (переходность)
        "voice",           # Залог
        "causativity",     # Каузатив
        "reciprocity",     # Реципрок
        "reflexivity",     # Рефлексив
        "aspect",          # Вид
        "tense",           # Время
        "mood",            # Наклонение
        "evidentiality",   # Эвиденциальность
        "polarity",        # Полярность (отрицание)
        "person",          # Лицо
        "number",          # Число
        "gender",          # Род
    ],

    "participle": [
        "voice",           # Залог
        "aspect",          # Вид
        "tense",           # Время
        "number",          # Число
        "gender",          # Род
        "case",            # Падеж
    ],

    "adverb": [
        "derivation",      # Словообразование
        "degree",          # Степень сравнения
    ],
}

# Приоритеты по умолчанию (числовые значения, меньше = ближе к корню)
DEFAULT_CATEGORY_PRIORITIES = {
    # Именные
    "derivation": 1,
    "number": 2,
    "gender": 3,
    "possession": 4,
    "case": 5,
    "definiteness": 6,
    "animacy": 7,
    "person": 2,
    "clusivity": 4,
    "politeness": 6,

    # Глагольные
    "valency": 1,
    "voice": 2,
    "causativity": 3,
    "reciprocity": 4,
    "reflexivity": 5,
    "aspect": 6,
    "tense": 7,
    "mood": 8,
    "evidentiality": 9,
    "polarity": 10,

    # Общие
    "degree": 1,
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. ЧЕЛОВЕКОЧИТАЕМЫЕ НАЗВАНИЯ КАТЕГОРИЙ
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_NAMES_RU = {
    "case": "Падеж",
    "number": "Число",
    "gender": "Род / Класс",
    "definiteness": "Определённость",
    "animacy": "Одушевлённость",
    "possession": "Посессивность",
    "person": "Лицо",
    "clusivity": "Клюзивность",
    "politeness": "Вежливость",
    "degree": "Степень сравнения",
    "tense": "Время",
    "aspect": "Вид",
    "mood": "Наклонение",
    "voice": "Залог",
    "evidentiality": "Эвиденциальность",
    "polarity": "Полярность",
    "transitivity": "Переходность",
    "valency": "Валентность",
    "causativity": "Каузативность",
    "reciprocity": "Реципрок",
    "reflexivity": "Рефлексив",
    "derivation": "Словообразование",
}

CATEGORY_NAMES_EN = {
    "case": "Case",
    "number": "Number",
    "gender": "Gender / Class",
    "definiteness": "Definiteness",
    "animacy": "Animacy",
    "possession": "Possession",
    "person": "Person",
    "clusivity": "Clusivity",
    "politeness": "Politeness",
    "degree": "Degree of Comparison",
    "tense": "Tense",
    "aspect": "Aspect",
    "mood": "Mood",
    "voice": "Voice",
    "evidentiality": "Evidentiality",
    "polarity": "Polarity",
    "transitivity": "Transitivity",
    "valency": "Valency",
    "causativity": "Causativity",
    "reciprocity": "Reciprocity",
    "reflexivity": "Reflexivity",
    "derivation": "Derivation",
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. ЗНАЧЕНИЯ ДЛЯ КАЖДОЙ КАТЕГОРИИ
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_VALUES = {
    # Падежи
    "case": [
        ("Nominative", "Номинатив", "Именительный"),
        ("Accusative", "Аккузатив", "Винительный"),
        ("Genitive", "Генитив", "Родительный"),
        ("Dative", "Датив", "Дательный"),
        ("Instrumental", "Инструменталис", "Творительный"),
        ("Locative", "Локатив", "Местный"),
        ("Vocative", "Вокатив", "Звательный"),
        ("Ergative", "Эргатив", "Эргативный"),
        ("Absolutive", "Абсолютив", "Абсолютивный"),
        ("Ablative", "Аблатив", "Исходный"),
        ("Allative", "Аллатив", "Направительный"),
        ("Illative", "Иллатив", "Внутрь-направительный"),
        ("Inessive", "Инессив", "Внутри-местный"),
        ("Elative", "Элатив", "Изнутри-исходный"),
        ("Adessive", "Адессив", "На-местный"),
        ("Partitive", "Партитив", "Частичный"),
        ("Essive", "Эссив", "Пребывательный"),
        ("Translative", "Транслатив", "Превратительный"),
        ("Comitative", "Комитатив", "Совместный"),
        ("Abessive", "Абессив", "Лишительный"),
        ("Benefactive", "Бенефактив", "Бенефактивный"),
        ("Prolative", "Пролатив", "Продольный"),
    ],

    # Число
    "number": [
        ("Singular", "Сингуляр", "Единственное"),
        ("Plural", "Плюраль", "Множественное"),
        ("Dual", "Дуаль", "Двойственное"),
        ("Trial", "Триаль", "Тройственное"),
        ("Paucal", "Паукаль", "Паукальное"),
        ("Collective", "Коллектив", "Собирательное"),
    ],

    # Род / Именной класс
    "gender": [
        ("Masculine", "Маскулин", "Мужской"),
        ("Feminine", "Феминин", "Женский"),
        ("Neuter", "Нейтер", "Средний"),
        ("Common", "Коммон", "Общий"),
        ("Animate", "Анимейт", "Одушевлённый"),
        ("Inanimate", "Инанимейт", "Неодушевлённый"),
        ("Human", "Хьюман", "Человек"),
        ("Non-human", "Нон-хьюман", "Не-человек"),
    ],

    # Лицо
    "person": [
        ("1st", "1-е", "Первое"),
        ("2nd", "2-е", "Второе"),
        ("3rd", "3-е", "Третье"),
        ("4th", "4-е", "Четвёртое"),
    ],

    # Время
    "tense": [
        ("Present", "Презенс", "Настоящее"),
        ("Past", "Претерит", "Прошедшее"),
        ("Future", "Футур", "Будущее"),
        ("Hodiernal", "Ходиерналь", "Сегодняшнее"),
        ("Hesternal", "Хестерналь", "Вчерашнее"),
        ("Remote Past", "Ремоут паст", "Давнее прошедшее"),
        ("Remote Future", "Ремоут фьючер", "Отдалённое будущее"),
    ],

    # Вид
    "aspect": [
        ("Perfective", "Перфектив", "Совершенный"),
        ("Imperfective", "Имперфектив", "Несовершенный"),
        ("Perfect", "Перфект", "Перфект"),
        ("Progressive", "Прогрессив", "Продолженный"),
        ("Habitual", "Хабитуалис", "Обычный"),
        ("Iterative", "Итератив", "Повторяющийся"),
        ("Inchoative", "Инхоатив", "Начинательный"),
        ("Completive", "Комплетив", "Завершённый"),
    ],

    # Наклонение
    "mood": [
        ("Indicative", "Индикатив", "Изъявительное"),
        ("Imperative", "Императив", "Повелительное"),
        ("Subjunctive", "Субъюнктив", "Сослагательное"),
        ("Conditional", "Кондиционалис", "Условное"),
        ("Optative", "Оптатив", "Желательное"),
        ("Jussive", "Юссив", "Побудительное"),
        ("Potential", "Потенциалис", "Потенциальное"),
    ],

    # Залог
    "voice": [
        ("Active", "Актив", "Активный"),
        ("Passive", "Пассив", "Пассивный"),
        ("Middle", "Медиум", "Медиальный"),
        ("Antipassive", "Антипассив", "Антипассивный"),
        ("Causative", "Каузатив", "Каузативный"),
        ("Reciprocal", "Реципрок", "Взаимный"),
        ("Reflexive", "Рефлексив", "Возвратный"),
    ],

    # Степень сравнения
    "degree": [
        ("Positive", "Позитив", "Положительная"),
        ("Comparative", "Компаратив", "Сравнительная"),
        ("Superlative", "Суперлатив", "Превосходная"),
        ("Equative", "Экватив", "Уравнительная"),
    ],

    # Определённость
    "definiteness": [
        ("Definite", "Дефинит", "Определённый"),
        ("Indefinite", "Индефинит", "Неопределённый"),
        ("Specific", "Специфик", "Конкретный"),
    ],

    # Эвиденциальность
    "evidentiality": [
        ("Direct", "Директ", "Прямое"),
        ("Visual", "Вижуал", "Увиденное"),
        ("Non-visual", "Нон-вижуал", "Услышанное"),
        ("Inferred", "Инферд", "Выведенное"),
        ("Hearsay", "Хирсей", "Пересказ"),
    ],

    # Полярность
    "polarity": [
        ("Affirmative", "Аффирматив", "Утвердительное"),
        ("Negative", "Негатив", "Отрицательное"),
    ],

    # Одушевлённость
    "animacy": [
        ("Animate", "Анимейт", "Одушевлённое"),
        ("Inanimate", "Инанимейт", "Неодушевлённое"),
    ],

    # Посессивность
    "possession": [
        ("Possessed", "Посессед", "Обладаемое"),
        ("Possessor", "Посессор", "Обладатель"),
    ],

    # Клюзивность
    "clusivity": [
        ("Inclusive", "Инклюзив", "Инклюзивное"),
        ("Exclusive", "Эксклюзив", "Эксклюзивное"),
    ],

    # Вежливость
    "politeness": [
        ("Plain", "Плейн", "Простая"),
        ("Polite", "Полайт", "Вежливая"),
        ("Honorific", "Онорифик", "Почтительная"),
    ],

    # Переходность
    "transitivity": [
        ("Intransitive", "Интранзитив", "Непереходный"),
        ("Transitive", "Транзитив", "Переходный"),
        ("Ditransitive", "Ди-транзитив", "Двупереходный"),
    ],

    # Валентность
    "valency": [
        ("Avalent", "Авалент", "Безактантный"),
        ("Monovalent", "Моновалент", "Одноместный"),
        ("Divalent", "Дивалент", "Двухместный"),
        ("Trivalent", "Тривалент", "Трёхместный"),
    ],

    # Каузативность
    "causativity": [
        ("Non-causative", "Нон-каузатив", "Некаузативный"),
        ("Causative", "Каузатив", "Каузативный"),
    ],

    # Реципрок
    "reciprocity": [
        ("Non-reciprocal", "Нон-реципрок", "Не взаимный"),
        ("Reciprocal", "Реципрок", "Взаимный"),
    ],

    # Рефлексив
    "reflexivity": [
        ("Non-reflexive", "Нон-рефлексив", "Не возвратный"),
        ("Reflexive", "Рефлексив", "Возвратный"),
    ],

    # Словообразование (деривация)
    "derivation": [
        ("Diminutive", "Диминутив", "Уменьшительно-ласкательный"),
        ("Augmentative", "Аугментатив", "Увеличительный"),
        ("Agent", "Агентив", "Деятель (тот, кто делает)"),
        ("Instrument", "Инструментатив", "Инструмент (то, чем делают)"),
        ("Place", "Локатив", "Место (где делают)"),
        ("Abstract", "Абстрактив", "Абстрактное понятие"),
        ("Collective", "Коллектив", "Собирательное"),
        ("Feminine", "Феминитив", "Женский род (от мужского)"),
        ("Action", "Акцион", "Действие (процесс)"),
        ("Result", "Результатив", "Результат действия"),
        ("Quality", "Квалитатив", "Качество (свойство)"),
        ("Inhabitant", "Инхабитант", "Житель (места)"),
        ("Adjectivizer", "Адъективизатор", "Превращение в прилагательное"),
        ("Adverbializer", "Адвербиализатор", "Превращение в наречие"),
        ("Verbalizer", "Вербализатор", "Превращение в глагол"),
        ("Nominalizer", "Номинализатор", "Превращение в существительное"),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
# 5. СМЫСЛОВЫЕ НАГРУЗКИ СЛУЖЕБНЫХ СЛОВ И АФФИКСОВ
# ═══════════════════════════════════════════════════════════════════════════

FUNCTION_WORD_FUNCTIONS = {
    # Падежные и пространственные (служебные слова)
    "locative": {"category": "case", "description": "Местонахождение (где?)"},
    "ablative": {"category": "case", "description": "Исходная точка (откуда?)"},
    "allative": {"category": "case", "description": "Направление (куда?)"},
    "inessive": {"category": "case", "description": "Внутри (в чём?)"},
    "adessive": {"category": "case", "description": "На поверхности (на чём?)"},
    "elative": {"category": "case", "description": "Изнутри (из чего?)"},
    "illative": {"category": "case", "description": "Внутрь (во что?)"},
    "prolative": {"category": "case", "description": "По поверхности (по чему?)"},
    "instrumental": {"category": "case", "description": "Инструмент (чем?)"},
    "comitative": {"category": "case", "description": "Совместность (с кем?)"},
    "abessive": {"category": "case", "description": "Отсутствие (без чего?)"},
    "benefactive": {"category": "case", "description": "Для кого/чего (ради)?"},
    "ergative": {"category": "case", "description": "Субъект переходного глагола"},
    "accusative": {"category": "case", "description": "Прямой объект"},
    "genitive": {"category": "case", "description": "Принадлежность, часть"},
    "dative": {"category": "case", "description": "Косвенный объект, адресат"},
    "vocative": {"category": "case", "description": "Обращение"},

    # Временные
    "temporal_past": {"category": "tense", "description": "Прошедшее время"},
    "temporal_future": {"category": "tense", "description": "Будущее время"},
    "temporal_present": {"category": "tense", "description": "Настоящее время"},
    "temporal_remote_past": {"category": "tense", "description": "Давнее прошедшее"},
    "temporal_remote_future": {"category": "tense", "description": "Отдалённое будущее"},
    "temporal_hodiernal": {"category": "tense", "description": "Сегодняшнее время"},

    # Видовые
    "aspect_perfective": {"category": "aspect", "description": "Совершенный вид"},
    "aspect_imperfective": {"category": "aspect", "description": "Несовершенный вид"},
    "aspect_progressive": {"category": "aspect", "description": "Продолженное действие"},
    "aspect_habitual": {"category": "aspect", "description": "Обычное действие"},
    "aspect_completive": {"category": "aspect", "description": "Завершённое действие"},

    # Модальные и дискурсивные
    "negation": {"category": "polarity", "description": "Отрицание"},
    "question": {"category": "interrogative", "description": "Вопрос"},
    "emphasis": {"category": "focus", "description": "Эмфаза, выделение"},
    "topic": {"category": "topic", "description": "Маркер темы"},
    "focus": {"category": "focus", "description": "Маркер ремы/фокуса"},
    "evidential_direct": {"category": "evidentiality", "description": "Прямое свидетельство"},
    "evidential_hearsay": {"category": "evidentiality", "description": "Пересказ"},
    "evidential_inferred": {"category": "evidentiality", "description": "Вывод"},
    "conditional": {"category": "mood", "description": "Условное наклонение"},
    "causative": {"category": "causativity", "description": "Каузатив"},
    "passive": {"category": "voice", "description": "Пассивный залог"},

    # Определённость
    "definite": {"category": "definiteness", "description": "Определённый артикль"},
    "indefinite": {"category": "definiteness", "description": "Неопределённый артикль"},
    "partitive": {"category": "definiteness", "description": "Партитивный артикль"},

    # Степень сравнения
    "comparative": {"category": "degree", "description": "Сравнительная степень"},
    "superlative": {"category": "degree", "description": "Превосходная степень"},
    "equative": {"category": "degree", "description": "Уравнительная степень"},

    # Посессивность
    "possession": {"category": "possession", "description": "Принадлежность"},

    # Рефлексив / Реципрок
    "reflexive": {"category": "reflexivity", "description": "Возвратность"},
    "reciprocal": {"category": "reciprocity", "description": "Взаимность"},

    # Клюзивность
    "inclusive": {"category": "clusivity", "description": "Инклюзивное «мы»"},
    "exclusive": {"category": "clusivity", "description": "Эксклюзивное «мы»"},

    # Вежливость
    "polite": {"category": "politeness", "description": "Вежливая форма"},
    "honorific": {"category": "politeness", "description": "Почтительная форма"},
    "humble": {"category": "politeness", "description": "Скромная форма"},

    # ═══════════════════════════════════════════════════════════════════════
    # СЛОВООБРАЗОВАТЕЛЬНЫЕ ФУНКЦИИ (ДЕРИВАЦИЯ)
    # ═══════════════════════════════════════════════════════════════════════

    "deriv_diminutive": {"category": "derivation", "description": "Уменьшительно-ласкательный"},
    "deriv_augmentative": {"category": "derivation", "description": "Увеличительный"},
    "deriv_agent": {"category": "derivation", "description": "Деятель (тот, кто делает)"},
    "deriv_instrument": {"category": "derivation", "description": "Инструмент (то, чем делают)"},
    "deriv_place": {"category": "derivation", "description": "Место (где делают)"},
    "deriv_abstract": {"category": "derivation", "description": "Абстрактное понятие"},
    "deriv_collective": {"category": "derivation", "description": "Собирательное"},
    "deriv_feminine": {"category": "derivation", "description": "Женский род (от мужского)"},
    "deriv_action": {"category": "derivation", "description": "Действие (процесс)"},
    "deriv_result": {"category": "derivation", "description": "Результат действия"},
    "deriv_quality": {"category": "derivation", "description": "Качество (свойство)"},
    "deriv_inhabitant": {"category": "derivation", "description": "Житель (места)"},
    "deriv_adjectivizer": {"category": "derivation", "description": "Превращение в прилагательное"},
    "deriv_adverbializer": {"category": "derivation", "description": "Превращение в наречие"},
    "deriv_verbalizer": {"category": "derivation", "description": "Превращение в глагол"},
    "deriv_nominalizer": {"category": "derivation", "description": "Превращение в существительное"},
}

# ═══════════════════════════════════════════════════════════════════════════
# 6. ЧЕЛОВЕКОЧИТАЕМЫЕ НАЗВАНИЯ ФУНКЦИЙ
# ═══════════════════════════════════════════════════════════════════════════

FUNCTION_NAMES_RU = {
    # Пространственные и падежные
    "locative": "Локатив (где?)",
    "ablative": "Аблатив (откуда?)",
    "allative": "Аллатив (куда?)",
    "inessive": "Инессив (в чём?)",
    "adessive": "Адессив (на чём?)",
    "elative": "Элатив (из чего?)",
    "illative": "Иллатив (во что?)",
    "prolative": "Пролатив (по чему?)",
    "instrumental": "Инструменталис (чем?)",
    "comitative": "Комитатив (с кем?)",
    "abessive": "Абессив (без чего?)",
    "benefactive": "Бенефактив (для кого?)",
    "ergative": "Эргатив (субъект переходного)",
    "accusative": "Аккузатив (прямой объект)",
    "genitive": "Генитив (принадлежность)",
    "dative": "Датив (адресат)",
    "vocative": "Вокатив (обращение)",

    # Временные
    "temporal_past": "Прошедшее время",
    "temporal_future": "Будущее время",
    "temporal_present": "Настоящее время",
    "temporal_remote_past": "Давнее прошедшее",
    "temporal_remote_future": "Отдалённое будущее",
    "temporal_hodiernal": "Сегодняшнее время",

    # Видовые
    "aspect_perfective": "Совершенный вид",
    "aspect_imperfective": "Несовершенный вид",
    "aspect_progressive": "Прогрессив",
    "aspect_habitual": "Хабитуалис",
    "aspect_completive": "Комплетив",

    # Модальные и дискурсивные
    "negation": "Отрицание",
    "question": "Вопрос",
    "emphasis": "Эмфаза (выделение)",
    "topic": "Тема",
    "focus": "Фокус/Рема",
    "evidential_direct": "Эвиденц.: прямое",
    "evidential_hearsay": "Эвиденц.: пересказ",
    "evidential_inferred": "Эвиденц.: вывод",
    "conditional": "Условное наклонение",
    "causative": "Каузатив",
    "passive": "Пассив",

    # Определённость
    "definite": "Определённый артикль",
    "indefinite": "Неопределённый артикль",
    "partitive": "Партитивный артикль",

    # Степень сравнения
    "comparative": "Сравнительная степень",
    "superlative": "Превосходная степень",
    "equative": "Уравнительная степень",

    # Посессивность
    "possession": "Посессивность (чей?)",

    # Рефлексив / Реципрок
    "reflexive": "Рефлексив (-ся)",
    "reciprocal": "Реципрок (друг друга)",

    # Клюзивность
    "inclusive": "Инклюзив (мы с тобой)",
    "exclusive": "Эксклюзив (мы без тебя)",

    # Вежливость
    "polite": "Вежливая форма",
    "honorific": "Почтительная форма",
    "humble": "Скромная форма",

    # ═══════════════════════════════════════════════════════════════════════
    # СЛОВООБРАЗОВАТЕЛЬНЫЕ
    # ═══════════════════════════════════════════════════════════════════════
    "deriv_diminutive": "Уменьшительно-ласкательный",
    "deriv_augmentative": "Увеличительный",
    "deriv_agent": "Деятель (-тель, -ник)",
    "deriv_instrument": "Инструмент (-лка, -тор)",
    "deriv_place": "Место (-ня, -ище)",
    "deriv_abstract": "Абстракция (-ость, -ство)",
    "deriv_collective": "Собирательное (-ство, -ьё)",
    "deriv_feminine": "Феминитив (-ка, -ица)",
    "deriv_action": "Действие (-ние, -тие)",
    "deriv_result": "Результат (-ок, -ство)",
    "deriv_quality": "Качество (-ота, -изна)",
    "deriv_inhabitant": "Житель (-ец, -анин)",
    "deriv_adjectivizer": "Адъективация (-ный, -ский)",
    "deriv_adverbializer": "Адвербиализация (-о, -ски)",
    "deriv_verbalizer": "Вербализация (-овать, -еть)",
    "deriv_nominalizer": "Номинализация (-ние, -ость)",
}

FUNCTION_NAMES_EN = {
    # Spatial and case
    "locative": "Locative (where?)",
    "ablative": "Ablative (from where?)",
    "allative": "Allative (to where?)",
    "inessive": "Inessive (in what?)",
    "adessive": "Adessive (on what?)",
    "elative": "Elative (out of what?)",
    "illative": "Illative (into what?)",
    "prolative": "Prolative (along what?)",
    "instrumental": "Instrumental (with what?)",
    "comitative": "Comitative (with whom?)",
    "abessive": "Abessive (without what?)",
    "benefactive": "Benefactive (for whom?)",
    "ergative": "Ergative (transitive subject)",
    "accusative": "Accusative (direct object)",
    "genitive": "Genitive (possession)",
    "dative": "Dative (recipient)",
    "vocative": "Vocative (address)",

    # Temporal
    "temporal_past": "Past tense",
    "temporal_future": "Future tense",
    "temporal_present": "Present tense",
    "temporal_remote_past": "Remote past",
    "temporal_remote_future": "Remote future",
    "temporal_hodiernal": "Hodiernal (today)",

    # Aspect
    "aspect_perfective": "Perfective aspect",
    "aspect_imperfective": "Imperfective aspect",
    "aspect_progressive": "Progressive",
    "aspect_habitual": "Habitual",
    "aspect_completive": "Completive",

    # Modal and discourse
    "negation": "Negation",
    "question": "Question",
    "emphasis": "Emphasis",
    "topic": "Topic",
    "focus": "Focus/Rheme",
    "evidential_direct": "Evidential: direct",
    "evidential_hearsay": "Evidential: hearsay",
    "evidential_inferred": "Evidential: inferred",
    "conditional": "Conditional mood",
    "causative": "Causative",
    "passive": "Passive voice",

    # Definiteness
    "definite": "Definite article",
    "indefinite": "Indefinite article",
    "partitive": "Partitive article",

    # Degree
    "comparative": "Comparative degree",
    "superlative": "Superlative degree",
    "equative": "Equative degree",

    # Possession
    "possession": "Possession (whose?)",

    # Reflexive / Reciprocal
    "reflexive": "Reflexive (-self)",
    "reciprocal": "Reciprocal (each other)",

    # Clusivity
    "inclusive": "Inclusive (we with you)",
    "exclusive": "Exclusive (we without you)",

    # Politeness
    "polite": "Polite form",
    "honorific": "Honorific form",
    "humble": "Humble form",

    # ═══════════════════════════════════════════════════════════════════════
    # DERIVATION
    # ═══════════════════════════════════════════════════════════════════════
    "deriv_diminutive": "Diminutive",
    "deriv_augmentative": "Augmentative",
    "deriv_agent": "Agent (doer)",
    "deriv_instrument": "Instrument",
    "deriv_place": "Place",
    "deriv_abstract": "Abstract",
    "deriv_collective": "Collective",
    "deriv_feminine": "Feminine",
    "deriv_action": "Action (process)",
    "deriv_result": "Result",
    "deriv_quality": "Quality",
    "deriv_inhabitant": "Inhabitant",
    "deriv_adjectivizer": "Adjectivizer",
    "deriv_adverbializer": "Adverbializer",
    "deriv_verbalizer": "Verbalizer",
    "deriv_nominalizer": "Nominalizer",
}

# ═══════════════════════════════════════════════════════════════════════════
# 7. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════

def get_category_display(category_id: str, lang: str = "ru") -> str:
    """Возвращает человекочитаемое название категории."""
    if lang == "ru":
        return CATEGORY_NAMES_RU.get(category_id, category_id)
    return CATEGORY_NAMES_EN.get(category_id, category_id)


def get_value_display(value: tuple, lang: str = "ru") -> str:
    """
    Возвращает человекочитаемое название значения.
    value: кортеж (english, latin, native) или строка
    """
    if isinstance(value, tuple):
        if lang == "ru":
            return value[2] if len(value) > 2 else value[0]
        return value[0]
    return str(value)


def get_value_id(value: tuple) -> str:
    """Возвращает ID значения (английское название)."""
    if isinstance(value, tuple):
        return value[0]
    return str(value)


def get_all_values_for_category(category_id: str) -> list:
    """Возвращает список всех возможных значений для категории."""
    return CATEGORY_VALUES.get(category_id, [])


def get_categories_for_pos(pos_id: str) -> list:
    """Возвращает список категорий, доступных для данной части речи."""
    return UNIVERSAL_CATEGORIES.get(pos_id, [])


def get_function_display(function_id: str, lang: str = "ru") -> str:
    """Возвращает человекочитаемое название функции служебного слова или аффикса."""
    if lang == "ru":
        return FUNCTION_NAMES_RU.get(function_id, function_id)
    return FUNCTION_NAMES_EN.get(function_id, function_id)


def get_function_category(function_id: str) -> str:
    """Возвращает ID грамматической категории, к которой относится функция."""
    return FUNCTION_WORD_FUNCTIONS.get(function_id, {}).get("category", "")


def get_all_functions() -> list:
    """Возвращает список всех доступных функций (и грамматических, и словообразовательных)."""
    return list(FUNCTION_WORD_FUNCTIONS.keys())


def is_derivation_function(function_id: str) -> bool:
    """Проверяет, является ли функция словообразовательной."""
    cat = get_function_category(function_id)
    return cat == "derivation"


def is_grammatical_function(function_id: str) -> bool:
    """Проверяет, является ли функция грамматической (словоизменительной)."""
    cat = get_function_category(function_id)
    return cat != "derivation" and cat != ""


def get_default_category_order(pos_id: str) -> list[str]:
    """Возвращает порядок категорий по умолчанию для части речи."""
    return UNIVERSAL_CATEGORY_ORDER.get(pos_id, [])


def get_category_priority(category_id: str) -> int:
    """Возвращает числовой приоритет категории (меньше = ближе к корню)."""
    return DEFAULT_CATEGORY_PRIORITIES.get(category_id, 50)
