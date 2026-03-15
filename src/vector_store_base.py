"""
Base Vector Store Interface
Abstract class defining the interface for vector database implementations
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations"""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize vector store
        
        Args:
            dimension: Embedding vector dimension
        """
        self.dimension = dimension
        self.total_vectors = 0
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the vector store (create index, connect to server, etc.)"""
        pass
    
    @abstractmethod
    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """
        Add embeddings with metadata to the vector store
        
        Args:
            embeddings: NumPy array of shape (n_vectors, dimension)
            metadata: List of metadata dictionaries for each vector
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector of shape (dimension,) or (1, dimension)
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing indices, distances, and metadata
        """
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Persist the vector store to disk/database"""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """Load the vector store from disk/database"""
        pass
    
    @abstractmethod
    def delete_all(self) -> None:
        """Delete all vectors from the store"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_vectors': self.total_vectors,
            'dimension': self.dimension,
            'type': self.__class__.__name__
        }
