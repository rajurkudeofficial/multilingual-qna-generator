"""
Embeddings - Generate and store embeddings
"""

import logging
import numpy as np
from typing import List, Tuple
import os

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for chunks using local models"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', device: str = 'auto'):
        """
        Initialize embedding model
        
        Args:
            model_name: Model identifier
            device: Device to use ('cpu', 'cuda', 'auto')
        """
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.model = None
        self.embedder = None
        self._load_model()
    
    def _resolve_device(self, device: str) -> str:
        """Resolve device to use"""
        if device == 'auto':
            try:
                import torch
                return 'cuda' if torch.cuda.is_available() else 'cpu'
            except:
                return 'cpu'
        return device
    
    def _load_model(self):
        """Load embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedder = SentenceTransformer(self.model_name)
            self.embedder.to(self.device)
            logger.info(f"Embedding model loaded on {self.device}")
        except ImportError:
            raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    def generate(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
        
        Returns:
            numpy array of embeddings (n_samples, embedding_dim)
        """
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        try:
            embeddings = self.embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {e}")


class VectorStore:
    """Local vector store using FAISS"""
    
    def __init__(self, embeddings: np.ndarray, chunks: List[Tuple[str, int]]):
        """
        Initialize vector store
        
        Args:
            embeddings: numpy array of embeddings
            chunks: List of (text, index) tuples
        """
        self.embeddings = embeddings
        self.chunks = chunks
        self.index = None
        self._build_index()
    
    def _build_index(self):
        """Build FAISS index"""
        try:
            import faiss
            
            embedding_dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(embedding_dim)
            
            # Ensure embeddings are float32
            embeddings_float32 = self.embeddings.astype(np.float32)
            self.index.add(embeddings_float32)
            
            logger.info(f"Built FAISS index with {len(self.chunks)} chunks")
        except ImportError:
            raise ImportError("faiss-cpu not installed. Install with: pip install faiss-cpu")
        except Exception as e:
            raise RuntimeError(f"Failed to build FAISS index: {e}")
    
    def retrieve(self, query_embedding: np.ndarray, k: int = 3) -> List[Tuple[str, float, int]]:
        """
        Retrieve top-k similar chunks
        
        Args:
            query_embedding: Query embedding
            k: Number of results to return
        
        Returns:
            List of (chunk_text, similarity_score, chunk_index) tuples
        """
        if self.index is None:
            raise RuntimeError("Index not built")
        
        # Ensure query is float32
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding, min(k, len(self.chunks)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                chunk_text, chunk_idx = self.chunks[idx]
                # Convert L2 distance to similarity (lower distance = higher similarity)
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((chunk_text, similarity, chunk_idx))
        
        return results
