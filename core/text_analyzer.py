"""
Анализатор текста для русского, английского и баскского языков.
Определяет части речи, леммы и грамматические признаки.
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Русский
try:
    from pymorphy3 import MorphAnalyzer
    PYMORPHY_AVAILABLE = True
except ImportError:
    PYMORPHY_AVAILABLE = False

# Английский
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Баскский (через stanza)
try:
    import stanza
    STANZA_AVAILABLE = True
except ImportError:
    STANZA_AVAILABLE = False


# Маппинг частей речи
RU_POS_MAP = {
    'NOUN': 'noun', 'ADJF': 'adjective', 'ADJS': 'adjective',
    'VERB': 'verb', 'INFN': 'verb', 'ADVB': 'adverb',
    'NPRO': 'pronoun', 'PREP': 'preposition', 'CONJ': 'conjunction',
    'PRCL': 'particle', 'INTJ': 'interjection', 'NUMR': 'numeral',
}

EN_POS_MAP = {
    'NOUN': 'noun', 'PROPN': 'noun', 'ADJ': 'adjective',
    'VERB': 'verb', 'AUX': 'verb', 'ADV': 'adverb',
    'PRON': 'pronoun', 'DET': 'determiner', 'ADP': 'preposition',
    'CCONJ': 'conjunction', 'SCONJ': 'conjunction', 'PART': 'particle',
    'INTJ': 'interjection', 'NUM': 'numeral',
}

# Баскский (stanza использует Universal Dependencies)
EU_POS_MAP = {
    'NOUN': 'noun', 'PROPN': 'noun', 'ADJ': 'adjective',
    'VERB': 'verb', 'AUX': 'verb', 'ADV': 'adverb',
    'PRON': 'pronoun', 'DET': 'determiner', 'ADP': 'adposition',
    'CCONJ': 'conjunction', 'SCONJ': 'conjunction', 'PART': 'particle',
    'INTJ': 'interjection', 'NUM': 'numeral',
}


@dataclass
class Token:
    word: str
    lemma: str
    pos: str
    features: Dict[str, str] = field(default_factory=dict)
    is_punctuation: bool = False

    def has_feature(self, key: str, value: str = None) -> bool:
        if value is None:
            return key in self.features
        return self.features.get(key) == value


class RussianAnalyzer:
    def __init__(self):
        if not PYMORPHY_AVAILABLE:
            raise RuntimeError("pymorphy3 not installed")
        self._morph = MorphAnalyzer()

    def analyze(self, text: str) -> List[Token]:
        tokens = []
        words = re.findall(r'\w+|[^\w\s]', text)

        for word in words:
            if re.match(r'^[^\w\s]+$', word):
                tokens.append(Token(word=word, lemma=word, pos='punctuation', is_punctuation=True))
                continue

            parsed = self._morph.parse(word)
            if not parsed:
                tokens.append(Token(word=word, lemma=word, pos='other'))
                continue

            p = parsed[0]
            tag = p.tag

            pos = RU_POS_MAP.get(tag.POS, 'other')
            features = {}
            if tag.gender:
                features['gender'] = tag.gender
            if tag.number:
                features['number'] = tag.number
            if tag.case:
                features['case'] = tag.case
            if tag.person:
                features['person'] = tag.person
            if tag.tense:
                features['tense'] = tag.tense
            if tag.aspect:
                features['aspect'] = tag.aspect

            tokens.append(Token(word=word, lemma=p.normal_form, pos=pos, features=features))

        return tokens


class EnglishAnalyzer:
    def __init__(self):
        if not SPACY_AVAILABLE:
            raise RuntimeError("spaCy not installed")
        self._nlp = spacy.load("en_core_web_sm")

    def analyze(self, text: str) -> List[Token]:
        doc = self._nlp(text)
        tokens = []

        for token in doc:
            if token.is_punct:
                tokens.append(Token(word=token.text, lemma=token.text, pos='punctuation', is_punctuation=True))
                continue

            if token.is_space:
                continue

            pos = EN_POS_MAP.get(token.pos_, 'other')
            features = {}
            if token.morph.get('Number'):
                features['number'] = token.morph.get('Number')[0].lower()
            if token.morph.get('Person'):
                features['person'] = token.morph.get('Person')[0]
            if token.morph.get('Tense'):
                features['tense'] = token.morph.get('Tense')[0].lower()

            tokens.append(Token(word=token.text, lemma=token.lemma_, pos=pos, features=features))

        return tokens


class BasqueAnalyzer:
    """Анализатор для баскского языка через stanza."""

    def __init__(self):
        if not STANZA_AVAILABLE:
            raise RuntimeError("stanza not installed")
        # Скачиваем модель если её нет
        try:
            self._nlp = stanza.Pipeline('eu', processors='tokenize,mwt,pos,lemma,depparse')
        except Exception:
            stanza.download('eu')
            self._nlp = stanza.Pipeline('eu', processors='tokenize,mwt,pos,lemma,depparse')

    def analyze(self, text: str) -> List[Token]:
        doc = self._nlp(text)
        tokens = []

        for sent in doc.sentences:
            for word in sent.words:
                # Пропускаем пунктуацию
                if word.upos == 'PUNCT':
                    tokens.append(Token(word=word.text, lemma=word.text, pos='punctuation', is_punctuation=True))
                    continue

                pos = EU_POS_MAP.get(word.upos, 'other')
                features = {}

                # Извлекаем признаки из feats если есть
                if word.feats:
                    for feat in word.feats.split('|'):
                        if '=' in feat:
                            key, value = feat.split('=')
                            features[key.lower()] = value.lower()

                tokens.append(Token(
                    word=word.text,
                    lemma=word.lemma if word.lemma else word.text,
                    pos=pos,
                    features=features
                ))

        return tokens


class TextAnalyzer:
    def __init__(self, lang: Optional[str] = None):
        self.lang = lang
        self._ru_analyzer = None
        self._en_analyzer = None
        self._eu_analyzer = None

    def _detect_language(self, text: str) -> str:
        # Кириллица -> русский
        if re.search(r'[а-яА-ЯёЁ]', text):
            return 'ru'
        # Баскский — много букв k, z, tz, tx (эвристика)
        if re.search(r'\b(euskara|etxe|gizon|emakume|haur|egun|bai|ez)\b', text, re.IGNORECASE):
            return 'eu'
        # По умолчанию английский
        return 'en'

    def analyze(self, text: str) -> List[Token]:
        if not text.strip():
            return []

        lang = self.lang or self._detect_language(text)

        if lang == 'ru':
            if not self._ru_analyzer:
                self._ru_analyzer = RussianAnalyzer()
            return self._ru_analyzer.analyze(text)
        elif lang == 'eu':
            if not self._eu_analyzer:
                self._eu_analyzer = BasqueAnalyzer()
            return self._eu_analyzer.analyze(text)
        else:
            if not self._en_analyzer:
                self._en_analyzer = EnglishAnalyzer()
            return self._en_analyzer.analyze(text)

    def get_words(self, tokens: List[Token]) -> List[Token]:
        return [t for t in tokens if not t.is_punctuation]
