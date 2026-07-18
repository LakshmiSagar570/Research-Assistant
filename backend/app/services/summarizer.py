"""
FR2: Extractive summarization of paper abstracts.

Approach: frequency-weighted sentence scoring (a classic, explainable
extractive method - Luhn's algorithm lineage). No external ML model or
paid API is required, matching the SRS's "rule-based + extractive
summarization" architecture decision.

Why extractive and not abstractive here:
  - Zero cost, zero external API dependency, deterministic output.
  - Defensible in a viva: every sentence in the summary is a real
    sentence from the source, so there is no hallucination risk.
  - Abstractive (LLM-based) summarization is explicitly scoped as a
    future phase in the SRS (AI Layer: "future Ollama integration").
"""
import re
from collections import Counter

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "for", "to", "with",
    "is", "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "we", "our", "it", "its", "as", "by", "at", "from", "which", "such",
    "can", "also", "into", "than", "then", "using", "used", "use", "based",
    "not", "no", "have", "has", "had", "will", "would", "may", "might", "their",
    "these", "results", "paper", "study",
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
_WORD_RE = re.compile(r"[A-Za-z]+")


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]


def _word_frequencies(sentences: list[str]) -> Counter:
    freq = Counter()
    for sentence in sentences:
        words = _WORD_RE.findall(sentence.lower())
        for w in words:
            if w not in _STOPWORDS and len(w) > 2:
                freq[w] += 1
    return freq


def extractive_summary(text: str, sentence_count: int = 4) -> str:
    """
    Scores each sentence by the sum of its (normalized) word
    frequencies, then returns the top-N highest scoring sentences in
    their ORIGINAL order (so the summary still reads coherently).
    """
    sentences = _split_sentences(text)
    if len(sentences) <= sentence_count:
        return " ".join(sentences)

    freq = _word_frequencies(sentences)
    if not freq:
        return " ".join(sentences[:sentence_count])

    max_freq = max(freq.values())
    normalized = {w: c / max_freq for w, c in freq.items()}

    scores = []
    for idx, sentence in enumerate(sentences):
        words = _WORD_RE.findall(sentence.lower())
        if not words:
            scores.append((idx, 0.0))
            continue
        # Slight position bias: earlier sentences in an abstract tend to
        # state the core contribution (standard abstract convention).
        position_bias = 1.0 if idx == 0 else 0.9
        raw = sum(normalized.get(w, 0.0) for w in words) / len(words)
        scores.append((idx, raw * position_bias))

    top_indices = sorted(
        sorted(scores, key=lambda x: x[1], reverse=True)[:sentence_count],
        key=lambda x: x[0],  # restore original order
    )
    return " ".join(sentences[i] for i, _ in top_indices)
