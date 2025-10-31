import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Dict
from ..config import settings


class LocalVectorStore:
    def __init__(self, chroma_dir: str, embed_model: str, api_key: str):
        self.client = chromadb.PersistentClient(
            path=chroma_dir, settings=ChromaSettings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(name="kb_main")

        if settings.embeddings_backend == "local":
            # Zero-cost local embeddings
            self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        else:
            self.embed_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key, model_name=embed_model
            )

    def add_texts(self, texts: List[str], metadatas: List[Dict], ids: List[str]):
        embeddings = self.embed_fn(texts)
        self.collection.add(
            documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids
        )

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        # Return metadatas + documents
        res = self.collection.query(
            query_texts=[query], n_results=k, include=["documents", "metadatas"]
        )
        docs = []
        for doc, meta in zip(
            res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]
        ):
            docs.append({"text": doc, **(meta or {})})
        return docs
