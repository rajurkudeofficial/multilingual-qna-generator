#!/usr/bin/env python3
"""
Multilingual Q&A Generation System
Main CLI entry point
"""

import argparse
import sys
import logging
from pathlib import Path

from src.pipeline import QAGenerationPipeline
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Multilingual Q&A Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input input/IKS.pdf
  python main.py --input input/document.docx --output results/QnA.xlsx
  python main.py --input input/text.txt --num-questions 15 --device cuda
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input document (PDF, DOCX, or TXT)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/QnA.xlsx',
        help='Path to output Excel file (default: output/QnA.xlsx)'
    )
    parser.add_argument(
        '--num-questions',
        type=int,
        default=10,
        help='Number of Q&A pairs to generate (default: 10)'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=3,
        help='Number of chunks to retrieve for context (default: 3)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Size of text chunks (default: 512)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=128,
        help='Overlap between chunks (default: 128)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cpu', 'cuda', 'mps'],
        help='Compute device (default: auto)'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        default='q5_k_m',
        choices=['q5_k_m', 'q4_k_m'],
        help='Model quantization type (default: q5_k_m)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)
    
    supported_formats = {'.pdf', '.docx', '.txt'}
    if input_path.suffix.lower() not in supported_formats:
        logger.error(f"Unsupported file format: {input_path.suffix}. Supported: {supported_formats}")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Configure pipeline
        config = Config(
            input_file=str(input_path),
            output_file=str(output_path),
            num_questions=args.num_questions,
            top_k=args.top_k,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            device=args.device,
            model_type=args.model_type
        )
        
        # Run pipeline
        logger.info("Starting Q&A generation pipeline...")
        pipeline = QAGenerationPipeline(config)
        pipeline.run()
        
        logger.info(f"✓ Q&A generation complete!")
        logger.info(f"✓ Output saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    main()
