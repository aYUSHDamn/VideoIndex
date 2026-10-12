from collections import Counter
from collections.abc import Sequence
import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


EXTRA_STOP_WORDS = {
    "actually", "also", "back", "come", "coming", "episode", "game",
    "get", "going", "got", "guys", "hey", "just", "know", "let", "like",
    "little", "look", "looks", "make", "maybe", "new", "okay", "one",
    "play", "playing", "really", "right", "saw", "saying", "show", "start",
    "subscribe", "talk", "take", "tell", "thank", "thanks", "thing", "think",
    "thought", "today", "try", "use", "video", "want", "way", "well", "yeah",
    "youre", "youve", "gonna", "wanna", "ive", "im", "ill", "id", "dont",
    "didnt", "doesnt", "thats", "theres", "theyre", "weve", "weare", "lets",
    "ll", "ve", "re", "don", "guess", "kind", "copies", "official", "psa",
}
STOP_WORDS = sorted(set(ENGLISH_STOP_WORDS) | EXTRA_STOP_WORDS)
PHRASE_CONNECTORS = {"of", "the", "and", "in", "at", "to", "for"}
PROPER_NAME_PATTERN = re.compile(
    r"\b[A-Z][a-zA-Z0-9]+(?:\s+(?:(?i:of|the|and|in|at|to|for)\s+)?"
    r"[A-Z][a-zA-Z0-9]+){1,4}\b"
)


def extract_tags(transcripts: str | Sequence[str], top_n: int = 5) -> list[list[str]]:
    """Extract transcript keywords, preferring repeated multiword name phrases."""
    if top_n < 1:
        raise ValueError("top_n must be at least 1")
    documents = [transcripts] if isinstance(transcripts, str) else list(transcripts)
    if not documents:
        return []
    if any(not isinstance(text, str) for text in documents):
        raise TypeError("transcripts must contain only strings")
    if all(not text.strip() for text in documents):
        return [[] for _ in documents]

    vectorizer = TfidfVectorizer(
        stop_words=STOP_WORDS,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9]{2,}\b",
    )
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError as exc:
        if "empty vocabulary" in str(exc).lower():
            return [[] for _ in documents]
        raise

    vocabulary = vectorizer.get_feature_names_out()
    results = []
    for index, row in enumerate(matrix):
        phrases = Counter()
        for phrase in PROPER_NAME_PATTERN.findall(documents[index]):
            normalized = " ".join(phrase.lower().split())
            content_words = [
                word for word in normalized.split()
                if word not in PHRASE_CONNECTORS
            ]
            if len(content_words) >= 2:
                phrases[normalized] += 1

        ranked_phrases = [
            phrase for phrase, count in phrases.most_common()
            if count >= 2 or (
                len([word for word in phrase.split() if word not in PHRASE_CONNECTORS]) >= 3
                and len(documents[index]) > 300
            )
        ]
        scores = row.toarray().ravel()
        word_order = scores.argsort()[::-1]
        phrase_words = {word for phrase in ranked_phrases for word in phrase.split()}
        ranked_words = [
            vocabulary[word_index]
            for word_index in word_order
            if scores[word_index] > 0 and vocabulary[word_index] not in phrase_words
        ]
        results.append(list(dict.fromkeys(ranked_phrases + ranked_words))[:top_n])
    return results
