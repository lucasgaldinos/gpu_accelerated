#!/usr/bin/env python3
"""
PDF to Markdown Converter
========================

A comprehensive script to convert PDF files to clean, well-formatted markdown.
Specially designed for academic documents with mathematical formulas, tables, and figures.

Features:
- High-quality markdown conversion with formula preservation
- Image extraction and embedding options
- Post-processing to remove artifacts and improve readability
- Batch processing for multiple files
- Configurable output options for different use cases

Usage:
    python convert_pdf_to_markdown.py input.pdf
    python convert_pdf_to_markdown.py --input-dir extracted_chapters/ --output-dir markdown_chapters/
    python convert_pdf_to_markdown.py input.pdf --embed-images --clean-output
"""

import argparse
import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import pymupdf4llm
    import pymupdf
except ImportError as e:
    print("Error: Required packages not installed.")
    print("Please install with: uv add pymupdf4llm")
    raise e


class PDFToMarkdownConverter:
    """Advanced PDF to Markdown converter with academic document optimization."""
    
    def __init__(self, 
                 embed_images: bool = False,
                 write_images: bool = True,
                 clean_output: bool = True,
                 preserve_formulas: bool = True,
                 extract_tables: bool = True,
                 dpi: int = 150,
                 image_format: str = "png"):
        """
        Initialize the converter with configuration options.
        
        Args:
            embed_images: Embed images as base64 in markdown (increases file size)
            write_images: Extract images to separate files
            clean_output: Apply post-processing to clean the markdown
            preserve_formulas: Attempt to preserve mathematical formulas
            extract_tables: Extract and format tables
            dpi: Image resolution for extracted images
            image_format: Format for extracted images (png, jpg, etc.)
        """
        self.embed_images = embed_images
        self.write_images = write_images and not embed_images  # Don't write if embedding
        self.clean_output = clean_output
        self.preserve_formulas = preserve_formulas
        self.extract_tables = extract_tables
        self.dpi = dpi
        self.image_format = image_format
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def convert_file(self, 
                    input_path: Path, 
                    output_path: Optional[Path] = None,
                    image_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Convert a single PDF file to markdown.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for output markdown file (auto-generated if None)
            image_dir: Directory for extracted images (auto-generated if None)
            
        Returns:
            Dictionary with conversion results and metadata
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output paths if not provided
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}.md"
        
        if image_dir is None and self.write_images:
            image_dir = input_path.parent / f"{input_path.stem}_images"
            image_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Converting {input_path.name} to markdown...")
        
        try:
            # Configure conversion parameters
            conversion_params = {
                'embed_images': self.embed_images,
                'write_images': self.write_images,
                'dpi': self.dpi,
                'image_format': self.image_format,
                'force_text': True,  # Extract text even when overlapping with images
                'ignore_graphics': False,  # Keep graphics for better layout understanding
                'ignore_images': False,  # Keep images for completeness
                'table_strategy': 'lines_strict' if self.extract_tables else None,
                'page_separators': False,  # Clean output without page markers
                'show_progress': True,  # Show conversion progress
                'fontsize_limit': 3,  # Ignore very small text (likely artifacts)
                'image_size_limit': 0.02,  # Ignore very small images (likely decorations)
            }
            
            # Add image path if writing images
            if self.write_images and image_dir:
                conversion_params['image_path'] = str(image_dir)
            
            # Convert PDF to markdown
            markdown_text = pymupdf4llm.to_markdown(str(input_path), **conversion_params)
            
            # Apply post-processing if enabled
            if self.clean_output:
                markdown_text = self._clean_markdown(markdown_text)
            
            # Write the markdown file
            output_path.write_text(markdown_text, encoding='utf-8')
            
            # Generate metadata
            doc = pymupdf.open(str(input_path))
            metadata = {
                'input_file': str(input_path),
                'output_file': str(output_path),
                'image_dir': str(image_dir) if image_dir else None,
                'page_count': doc.page_count,
                'file_size_mb': input_path.stat().st_size / (1024 * 1024),
                'conversion_params': conversion_params,
                'success': True
            }
            doc.close()
            
            self.logger.info(f"✅ Successfully converted {input_path.name}")
            self.logger.info(f"📄 Output: {output_path}")
            if image_dir and image_dir.exists():
                image_count = len(list(image_dir.glob(f"*.{self.image_format}")))
                self.logger.info(f"🖼️  Extracted {image_count} images to: {image_dir}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert {input_path.name}: {str(e)}")
            return {
                'input_file': str(input_path),
                'error': str(e),
                'success': False
            }
    
    def _clean_markdown(self, text: str) -> str:
        """
        Apply post-processing to clean up the markdown output.
        
        Args:
            text: Raw markdown text from conversion
            
        Returns:
            Cleaned markdown text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up header formatting
        text = re.sub(r'#{7,}', '######', text)  # Limit to h6 maximum
        
        # Fix common OCR artifacts in academic papers
        if self.preserve_formulas:
            # Preserve common mathematical notation
            text = re.sub(r'\b([A-Za-z])\s+([0-9]+)\b', r'\1_\2', text)  # Fix subscripts
            text = re.sub(r'\b([A-Za-z])\s*\^\s*([0-9]+)\b', r'\1^\2', text)  # Fix superscripts
        
        # Clean up table formatting
        text = re.sub(r'\|\s*\|\s*\|', '|', text)  # Remove empty table cells
        
        # Remove page artifacts commonly found in academic PDFs
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Remove page numbers
        text = re.sub(r'\n\s*(Chapter|Section)\s+\d+.*\n', '\n', text)  # Remove chapter headers in content
        
        # Fix bullet points and lists
        text = re.sub(r'•\s*', '- ', text)  # Convert bullet points to markdown lists
        text = re.sub(r'◦\s*', '  - ', text)  # Convert sub-bullets to indented lists
        
        # Clean up excessive punctuation
        text = re.sub(r'\.{4,}', '...', text)  # Fix excessive dots
        text = re.sub(r'-{3,}', '---', text)  # Fix excessive dashes
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def convert_batch(self, 
                     input_dir: Path, 
                     output_dir: Path,
                     pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Convert multiple PDF files in a directory.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output markdown files
            pattern: File pattern to match (default: "*.pdf")
            
        Returns:
            List of conversion results for each file
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(input_dir.glob(pattern))
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {input_dir}")
            return []
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to convert")
        results = []
        
        for pdf_file in sorted(pdf_files):
            output_file = output_dir / f"{pdf_file.stem}.md"
            image_dir = output_dir / f"{pdf_file.stem}_images" if self.write_images else None
            
            result = self.convert_file(pdf_file, output_file, image_dir)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        self.logger.info(f"📊 Conversion complete: {successful}/{len(results)} files successful")
        
        return results


def main():
    """Command-line interface for the PDF to Markdown converter."""
    parser = argparse.ArgumentParser(
        description="Convert PDF files to clean, well-formatted markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --output-file clean_document.md
  %(prog)s --input-dir pdfs/ --output-dir markdown/
  %(prog)s document.pdf --embed-images --no-clean
        """
    )
    
    # Input/Output options
    parser.add_argument(
        'input_file', 
        nargs='?',
        type=Path,
        help='Input PDF file to convert'
    )
    parser.add_argument(
        '--input-dir', 
        type=Path,
        help='Directory containing PDF files for batch conversion'
    )
    parser.add_argument(
        '--output-file', 
        type=Path,
        help='Output markdown file (for single file conversion)'
    )
    parser.add_argument(
        '--output-dir', 
        type=Path,
        help='Output directory for converted files'
    )
    
    # Image handling options
    parser.add_argument(
        '--embed-images',
        action='store_true',
        help='Embed images as base64 in markdown (increases file size)'
    )
    parser.add_argument(
        '--no-write-images',
        action='store_true',
        help='Do not extract images to separate files'
    )
    parser.add_argument(
        '--image-format',
        default='png',
        choices=['png', 'jpg', 'jpeg', 'webp'],
        help='Format for extracted images (default: png)'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='Image resolution in DPI (default: 150)'
    )
    
    # Processing options
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip post-processing cleanup'
    )
    parser.add_argument(
        '--no-tables',
        action='store_true',
        help='Skip table extraction'
    )
    parser.add_argument(
        '--pattern',
        default='*.pdf',
        help='File pattern for batch conversion (default: *.pdf)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.input_file and not args.input_dir:
        parser.error("Must specify either input_file or --input-dir")
    
    if args.input_file and args.input_dir:
        parser.error("Cannot specify both input_file and --input-dir")
    
    # Initialize converter
    converter = PDFToMarkdownConverter(
        embed_images=args.embed_images,
        write_images=not args.no_write_images,
        clean_output=not args.no_clean,
        extract_tables=not args.no_tables,
        dpi=args.dpi,
        image_format=args.image_format
    )
    
    try:
        if args.input_file:
            # Single file conversion
            result = converter.convert_file(
                args.input_file,
                args.output_file
            )
            
            if result.get('success'):
                print(f"✅ Successfully converted: {result['output_file']}")
            else:
                print(f"❌ Conversion failed: {result.get('error', 'Unknown error')}")
                return 1
                
        else:
            # Batch conversion
            output_dir = args.output_dir or args.input_dir / 'markdown_output'
            results = converter.convert_batch(
                args.input_dir,
                output_dir,
                args.pattern
            )
            
            successful = sum(1 for r in results if r.get('success', False))
            if successful == 0:
                print("❌ No files converted successfully")
                return 1
            elif successful < len(results):
                print(f"⚠️  Partial success: {successful}/{len(results)} files converted")
                return 1
            else:
                print(f"✅ All {len(results)} files converted successfully")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())