"""
Model manager - Download and cache models
"""

import logging
import os
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class ModelManager:
    """Manage model downloads and caching"""
    
    def __init__(self, config):
        """Initialize model manager"""
        self.config = config
        self.model_dir = Path(config.model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def ensure_model_available(
        self,
        model_type: str,
        model_url: str,
        model_path: str
    ) -> str:
        """
        Ensure model is available locally, download if necessary
        
        Args:
            model_type: Type of model ('qwen', 'embedding', etc.)
            model_url: URL to download from
            model_path: Local path to save/check
        
        Returns:
            Path to model
        """
        model_path = Path(model_path)
        
        # Check if model already exists
        if model_path.exists():
            logger.info(f"Model found at {model_path}")
            return str(model_path)
        
        # Download model
        logger.info(f"Downloading {model_type} model...")
        logger.info(f"URL: {model_url}")
        logger.info(f"This may take a few minutes depending on internet speed")
        
        try:
            self._download_model(model_url, str(model_path))
            logger.info(f"✓ Model downloaded to {model_path}")
            return str(model_path)
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    def _download_model(self, url: str, output_path: str):
        """
        Download model from URL
        
        Args:
            url: Download URL
            output_path: Where to save
        """
        try:
            import urllib.request
            import shutil
            
            # Create temporary file
            temp_path = output_path + '.tmp'
            
            # Download with progress
            def download_with_progress(url, filepath):
                """Download with progress indicator"""
                try:
                    with urllib.request.urlopen(url, timeout=300) as response:
                        total_size = int(response.headers.get('Content-Length', 0))
                        downloaded = 0
                        chunk_size = 8192
                        
                        with open(filepath, 'wb') as f:
                            while True:
                                chunk = response.read(chunk_size)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    mb_downloaded = downloaded / (1024 * 1024)
                                    mb_total = total_size / (1024 * 1024)
                                    logger.info(f"  Downloaded: {mb_downloaded:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)")
                except Exception as e:
                    raise RuntimeError(f"Download failed: {e}")
            
            download_with_progress(url, temp_path)
            
            # Move to final location
            shutil.move(temp_path, output_path)
            
        except ImportError:
            # Fallback using requests if available
            try:
                import requests
                
                response = requests.get(url, stream=True, timeout=300)
                response.raise_for_status()
                
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_downloaded = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                logger.info(f"  Downloaded: {mb_downloaded:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)")
            
            except ImportError:
                raise ImportError(
                    "Neither urllib nor requests available. "
                    "Install requests with: pip install requests"
                )
            except Exception as e:
                raise RuntimeError(f"Download failed: {e}")
