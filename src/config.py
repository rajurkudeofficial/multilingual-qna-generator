"""
Configuration management
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    """Pipeline configuration"""
    
    # Files
    input_file: str
    output_file: str = "output/QnA.xlsx"
    
    # Q&A generation
    num_questions: int = 10
    top_k: int = 3
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 128
    
    # Model and device
    device: str = 'auto'  # auto, cpu, cuda, mps
    model_type: str = 'q5_k_m'  # q5_k_m, q4_k_m
    
    # Model paths
    model_dir: str = 'models'
    
    # Model names
    qwen_model_name: str = 'Qwen3-4B'
    embedding_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    indicative_model_name: str = 'ai4bharat/IndicTrans2'
    
    # Temperature for generation
    temperature: float = 0.7
    
    # Similarity threshold for deduplication
    similarity_threshold: float = 0.85
    
    # Min answer length (characters)
    min_answer_length: int = 20
    
    # Max retries for LLM calls
    max_retries: int = 2
    
    def __post_init__(self):
        """Validate and resolve paths"""
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
    
    @property
    def qwen_model_path(self) -> str:
        """Get Qwen model path"""
        return os.path.join(
            self.model_dir,
            f'{self.qwen_model_name}-{self.model_type.upper()}.gguf'
        )
    
    @property
    def qwen_model_url(self) -> str:
        """Get Qwen model download URL from Hugging Face"""
        if self.model_type == 'q5_k_m':
            return 'https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q5_K_M.gguf'
        else:  # q4_k_m
            return 'https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf'
