"""
Тесты «круговой» сериализации: Language -> dict -> Language -> dict.

Идея: если словарь ДО и словарь ПОСЛЕ (после сохранения и повторной
загрузки) совпадают полностью — значит, ни один кусочек данных
не потерялся. Если где-то что-то не совпало — тест покажет ровно
в каком месте (какое поле).
"""
from core.model import (
    Consonant,
    FunctionWord,
    GrammarRule,
    GrammaticalCategory,
    Language,
    PartOfSpeechConfig,
    Register,
    Vowel,
    Word,
)


def test_empty_language_roundtrip():
    """Пустой (только что созданный) язык должен переживать save/load без изменений."""
    lang = Language()
    d1 = lang.to_dict()
    lang2 = Language.from_dict(d1)
    d2 = lang2.to_dict()
    assert d1 == d2


def test_language_with_data_roundtrip():
    """То же самое, но с реально заполненными данными в разных разделах."""
    lang = Language(name="Тестовый", author="Андрей", version="0.1")

    lang.phonology.vowels.append(Vowel(symbol="a", height="low", backness="front"))
    lang.phonology.consonants.append(Consonant(symbol="k", place="velar", manner="stop"))

    lang.words.append(Word(conword="mira", localword="звезда", pos_id="noun"))

    lang.pragmatics.registers.append(Register(name="формальный", description="офиц. документы"))
    lang.pragmatics.discourse_markers = ["итак", "однако"]

    # Новая (актуальная) система парадигм
    cfg = PartOfSpeechConfig(pos_id="noun", name_ru="Существительное", name_en="Noun")
    cat = GrammaticalCategory(category_id="case", enabled=True)
    cat.rules["nominative"] = GrammarRule(value_id="nominative", enabled=True, affix_pattern="-a")
    cfg.categories["case"] = cat
    lang.pos_configs["noun"] = cfg

    lang.function_words.append(FunctionWord(name="ли", function="question marker"))

    d1 = lang.to_dict()
    lang2 = Language.from_dict(d1)
    d2 = lang2.to_dict()

    assert d1 == d2


def test_missing_keys_get_sane_defaults():
    """
    Имитация СТАРОГО файла: словарь без части ключей
    (как будто файл сохранён более ранней версией программы).
    from_dict не должен падать с ошибкой.
    """
    old_data = {"name": "Старый язык", "version": "0.1"}
    lang = Language.from_dict(old_data)
    assert lang.name == "Старый язык"
    assert lang.words == []
    assert lang.pos_configs  # дефолтные части речи должны подставиться


def test_unknown_extra_keys_are_ignored_not_crash():
    """
    Имитация файла из БУДУЩЕЙ версии программы (лишние поля).
    Сейчас _dc() их просто игнорирует — фиксируем это поведение явно,
    чтобы, если оно случайно изменится, тест сразу упал.
    """
    lang = Language()
    d = lang.to_dict()
    d["words"] = [{"conword": "test", "localword": "тест", "pos_id": "noun",
                   "FUTURE_FIELD_THAT_DOESNT_EXIST_YET": 123}]
    lang2 = Language.from_dict(d)  # не должно упасть
    assert lang2.words[0].conword == "test"


def test_word_lemma_autofill():
    """
    В from_dict есть отдельная логика: если lemma не задана,
    она заполняется из localword.lower(). Проверяем, что она реально работает.
    """
    d = Language().to_dict()
    d["words"] = [{"conword": "mira", "localword": "Звезда", "pos_id": "noun", "lemma": ""}]
    lang = Language.from_dict(d)
    assert lang.words[0].lemma == "звезда"
