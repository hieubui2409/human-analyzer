"""BM25-based text search over CSV data for framework scripts."""
import csv
import math
import re
from pathlib import Path


def load_csv(path: str | Path, encoding: str = "utf-8") -> list[dict[str, str]]:
    """Load CSV file with encoding detection fallback."""
    path = Path(path)
    for enc in (encoding, "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise UnicodeDecodeError(f"Cannot decode {path} with any known encoding")


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenization with basic normalization."""
    return re.findall(r"[a-zA-ZÀ-ỹ0-9]+", text.lower())


def search(
    query: str,
    rows: list[dict[str, str]],
    text_fields: list[str] | None = None,
    top_k: int = 10,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[tuple[int, float, dict[str, str]]]:
    """BM25 search over rows. Returns [(row_index, score, row), ...] sorted by score desc."""
    if not rows:
        return []

    if text_fields is None:
        text_fields = list(rows[0].keys())

    def row_text(row: dict[str, str]) -> str:
        return " ".join(row.get(f, "") or "" for f in text_fields)

    docs = [_tokenize(row_text(r)) for r in rows]
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    n = len(docs)
    avgdl = sum(len(d) for d in docs) / max(n, 1)

    df: dict[str, int] = {}
    for doc in docs:
        seen: set[str] = set()
        for token in doc:
            if token not in seen:
                df[token] = df.get(token, 0) + 1
                seen.add(token)

    scores: list[float] = [0.0] * n
    for qt in query_tokens:
        if qt not in df:
            continue
        idf = math.log((n - df[qt] + 0.5) / (df[qt] + 0.5) + 1.0)
        for i, doc in enumerate(docs):
            tf = doc.count(qt)
            if tf == 0:
                continue
            dl = len(doc)
            num = tf * (k1 + 1)
            denom = tf + k1 * (1 - b + b * dl / avgdl)
            scores[i] += idf * num / denom

    ranked = sorted(
        ((i, s, rows[i]) for i, s in enumerate(scores) if s > 0),
        key=lambda x: x[1],
        reverse=True,
    )
    return ranked[:top_k]
