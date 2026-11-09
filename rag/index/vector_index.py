"""
RAG Vector Index and BM25 Inverted Index.
Supports:
- Dense embedding cosine similarity
- BM25 sparse keyword matching
- Reciprocal Rank Fusion (RRF) for hybrid retrieval
- Re-ranking scores
"""
import math
import re
from collections import Counter
from typing import Any, Optional

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class PureTfidfVectorizer:
    def __init__(self, max_features: int = 4000):
        self.max_features = max_features
        self.vocab: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.num_docs = 0

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())

    def fit_transform(self, texts: list[str]) -> list[dict[int, float]]:
        self.num_docs = len(texts)
        df = Counter()
        doc_tokens = []
        for t in texts:
            tokens = self._tokenize(t)
            doc_tokens.append(tokens)
            for w in set(tokens):
                df[w] += 1
        
        most_common = [w for w, _ in df.most_common(self.max_features)]
        self.vocab = {w: i for i, w in enumerate(most_common)}
        
        for w in self.vocab:
            self.idf[w] = math.log((self.num_docs + 1) / (df[w] + 1)) + 1.0

        return [self._vectorize(tokens) for tokens in doc_tokens]

    def transform(self, texts: list[str]) -> list[dict[int, float]]:
        return [self._vectorize(self._tokenize(t)) for t in texts]

    def _vectorize(self, tokens: list[str]) -> dict[int, float]:
        tf = Counter(tokens)
        vec = {}
        norm_sq = 0.0
        for w, count in tf.items():
            if w in self.vocab:
                idx = self.vocab[w]
                val = count * self.idf[w]
                vec[idx] = val
                norm_sq += val * val
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {idx: val / norm for idx, val in vec.items()}

def pure_cosine_similarity(vec_q: dict[int, float], doc_vectors: list[dict[int, float]]) -> list[float]:
    sims = []
    for d_vec in doc_vectors:
        dot = sum(vec_q[i] * d_vec[i] for i in vec_q if i in d_vec)
        sims.append(dot)
    return sims

class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: list[list[str]] = []
        self.doc_lengths: list[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: dict[str, int] = Counter()
        self.num_docs: int = 0

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())

    def fit(self, texts: list[str]):
        self.corpus = [self._tokenize(t) for t in texts]
        self.num_docs = len(self.corpus)
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avg_doc_len = sum(self.doc_lengths) / max(1, self.num_docs)
        
        self.doc_freqs = Counter()
        for doc in self.corpus:
            unique_words = set(doc)
            for w in unique_words:
                self.doc_freqs[w] += 1

    def search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        q_tokens = self._tokenize(query)
        scores = []
        for doc_idx, doc in enumerate(self.corpus):
            doc_len = self.doc_lengths[doc_idx]
            term_freqs = Counter(doc)
            score = 0.0
            for q in q_tokens:
                if q not in term_freqs:
                    continue
                tf = term_freqs[q]
                df = self.doc_freqs.get(q, 0)
                idf = math.log(1 + (self.num_docs - df + 0.5) / (df + 0.5))
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(1, self.avg_doc_len)))
                score += idf * (numerator / denominator)
            scores.append((doc_idx, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class PortfolioIndex:
    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks
        self.texts = [c["text"] for c in chunks]
        
        # Dense representation
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(max_features=4000, ngram_range=(1, 2), stop_words="english")
            self.tfidf_matrix = self.vectorizer.fit_transform(self.texts) if self.texts else None
        else:
            self.vectorizer = PureTfidfVectorizer(max_features=4000)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.texts) if self.texts else []

        # Sparse BM25 representation
        self.bm25 = BM25Index()
        if self.texts:
            self.bm25.fit(self.texts)

    def dense_search(self, query: str, top_k: int = 10) -> list[tuple[dict[str, Any], float]]:
        if not self.texts or self.tfidf_matrix is None:
            return []
        
        if HAS_SKLEARN:
            q_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
            ranked_indices = np.argsort(sims)[::-1][:top_k]
            return [(self.chunks[i], float(sims[i])) for i in ranked_indices]
        else:
            q_vec = self.vectorizer.transform([query])[0]
            sims = pure_cosine_similarity(q_vec, self.tfidf_matrix)
            scored = list(enumerate(sims))
            scored.sort(key=lambda x: x[1], reverse=True)
            return [(self.chunks[i], float(s)) for i, s in scored[:top_k]]

    def bm25_search(self, query: str, top_k: int = 10) -> list[tuple[dict[str, Any], float]]:
        results = self.bm25.search(query, top_k=top_k)
        return [(self.chunks[idx], score) for idx, score in results]

    def hybrid_search_rrf(self, query: str, top_k: int = 5, rrf_k: int = 60) -> list[tuple[dict[str, Any], float]]:
        """Reciprocal Rank Fusion of BM25 and Dense Cosine ranks."""
        dense_results = self.dense_search(query, top_k=top_k * 3)
        bm25_results = self.bm25_search(query, top_k=top_k * 3)

        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, dict[str, Any]] = {}

        # Dense rank scoring
        for rank, (chunk, _) in enumerate(dense_results):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        # BM25 rank scoring
        for rank, (chunk, _) in enumerate(bm25_results):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        return [(chunk_map[cid], rrf_scores[cid]) for cid in sorted_cids[:top_k]]

