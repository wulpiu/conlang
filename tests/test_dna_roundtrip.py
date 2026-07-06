"""
Тесты для DNA-строки (base64(gzip(json))) — механизма экспорта/импорта
всего языка одной строкой, включая три встроенных пресета.
"""
from core.dna_language import (
    decode_language,
    encode_language,
    generate_basque_preset,
    generate_english_preset,
    generate_russian_preset,
    get_dna_info,
)
from core.model import Language, Word


def test_encode_decode_empty_language():
    lang = Language(name="Пустышка")
    dna = encode_language(lang)
    lang2 = decode_language(dna)
    assert lang2 is not None
    assert lang2.name == "Пустышка"
    assert lang.to_dict() == lang2.to_dict()


def test_encode_decode_language_with_words():
    lang = Language(name="Ковыльное")
    lang.words.append(Word(conword="ora", localword="степь", pos_id="noun"))
    dna = encode_language(lang)
    lang2 = decode_language(dna)
    assert lang2.to_dict() == lang.to_dict()


def test_decode_garbage_returns_none_not_crash():
    """Битая/чужая строка не должна ронять программу — только вернуть None."""
    assert decode_language("это не dna, а случайный текст") is None
    assert decode_language("") is None


def test_get_dna_info_matches_encode():
    lang = Language(name="Инфо-тест")
    dna = encode_language(lang)
    info = get_dna_info(dna)
    assert "error" not in info
    assert info["dna_length"] == len(dna)


def test_preset_russian_roundtrip():
    lang = generate_russian_preset()
    dna = encode_language(lang)
    lang2 = decode_language(dna)
    assert lang2 is not None
    assert lang2.to_dict() == lang.to_dict()


def test_preset_english_roundtrip():
    lang = generate_english_preset()
    dna = encode_language(lang)
    lang2 = decode_language(dna)
    assert lang2 is not None
    assert lang2.to_dict() == lang.to_dict()


def test_preset_basque_roundtrip():
    lang = generate_basque_preset()
    dna = encode_language(lang)
    lang2 = decode_language(dna)
    assert lang2 is not None
    assert lang2.to_dict() == lang.to_dict()
