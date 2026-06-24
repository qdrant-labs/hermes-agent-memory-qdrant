from __future__ import annotations

import threading
from typing import Any, Dict, List

DEFAULT_DENSE_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_SPARSE_MODEL = "Qdrant/bm25"


class FastEmbedEmbedder:
    def __init__(
        self,
        model_name: str = DEFAULT_DENSE_MODEL,
        *,
        sparse_model_name: str = DEFAULT_SPARSE_MODEL,
        **_: Any,
    ) -> None:
        self.model_name = model_name or DEFAULT_DENSE_MODEL
        self.sparse_model_name = sparse_model_name or DEFAULT_SPARSE_MODEL
        self._dense = None
        self._sparse = None
        self._dim: int | None = None
        self._lock = threading.Lock()

    def _get_dense(self):
        if self._dense is None:
            with self._lock:
                if self._dense is None:
                    from fastembed import TextEmbedding

                    self._dense = TextEmbedding(self.model_name)
        return self._dense

    def _get_sparse(self):
        if self._sparse is None:
            with self._lock:
                if self._sparse is None:
                    from fastembed import SparseTextEmbedding

                    self._sparse = SparseTextEmbedding(self.sparse_model_name)
        return self._sparse

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed_one("dim probe"))
        return self._dim

    def warm(self) -> int:
        return self.dim

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        clean = [t if t else " " for t in texts]
        return [v.tolist() for v in self._get_dense().embed(clean)]

    def embed_sparse(self, text: str) -> tuple[list[int], list[float]]:
        return self.embed_sparse_batch([text])[0]

    def embed_sparse_batch(self, texts: list[str]) -> list[tuple[list[int], list[float]]]:
        if not texts:
            return []
        clean = [t if t else " " for t in texts]
        out = []
        for result in self._get_sparse().embed(clean):
            if not result.indices.size:
                out.append(([0], [0.0]))
            else:
                out.append((result.indices.tolist(), result.values.tolist()))
        return out


def embedder_from_config(embedding_cfg: Dict[str, Any] | None) -> FastEmbedEmbedder:
    cfg = embedding_cfg or {}
    return FastEmbedEmbedder(
        cfg.get("model", DEFAULT_DENSE_MODEL),
        sparse_model_name=cfg.get("sparse_model", DEFAULT_SPARSE_MODEL),
    )
