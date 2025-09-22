#!/usr/bin/env python3
"""
Enhanced PDF to Markdown Batch Processor
=======================================

Optimized batch processing script for converting academic PDF chapters to markdown.
Includes special handling for different PDF types and enhanced post-processing.

Usage:
    python batch_convert_chapters.py --input-dir extracted_chapters/ --output-dir markdown_chapters/
    python batch_convert_chapters.py --embed-text-only --enhance-academic
"""

import argparse
import logging
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import pymupdf4llm
    import pymupdf
except ImportError as e:
    print("Error: Required packages not installed.")
    print("Please install with: uv add pymupdf4llm")
    raise e


class EnhancedChapterConverter:
    """Enhanced converter optimized for academic chapter processing."""
    
    def __init__(self, 
                 text_priority: bool = True,
                 enhance_academic: bool = True,
                 preserve_structure: bool = True,
                 extract_metadata: bool = True):
        """
        Initialize the enhanced converter.
        
        Args:
            text_priority: Prioritize text extraction over images for text-based PDFs
            enhance_academic: Apply academic-specific enhancements
            preserve_structure: Maintain document structure and formatting
            extract_metadata: Extract and include document metadata
        """
        self.text_priority = text_priority
        self.enhance_academic = enhance_academic
        self.preserve_structure = preserve_structure
        self.extract_metadata = extract_metadata
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_pdf_type(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Analyze PDF to determine the best conversion strategy.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF characteristics and recommended settings
        """
        doc = pymupdf.open(str(pdf_path))
        
        # Sample first few pages to analyze content
        text_pages = 0
        total_text_length = 0
        total_images = 0
        
        sample_pages = min(3, doc.page_count)
        
        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()
            images = page.get_images()
            
            if len(text.strip()) > 100:  # Significant text content
                text_pages += 1
                total_text_length += len(text)
            
            total_images += len(images)
        
        doc.close()
        
        # Determine PDF characteristics
        avg_text_per_page = total_text_length / sample_pages if sample_pages > 0 else 0
        is_text_based = text_pages >= sample_pages * 0.7 and avg_text_per_page > 200
        is_image_heavy = total_images > sample_pages * 2
        is_scanned = not is_text_based and total_images > 0
        
        return {
            'is_text_based': is_text_based,
            'is_image_heavy': is_image_heavy,
            'is_scanned': is_scanned,
            'avg_text_per_page': avg_text_per_page,
            'total_images': total_images,
            'sample_pages': sample_pages,
            'recommended_strategy': self._get_conversion_strategy(is_text_based, is_image_heavy, is_scanned)
        }
    
    def _get_conversion_strategy(self, is_text_based: bool, is_image_heavy: bool, is_scanned: bool) -> str:
        """Determine the best conversion strategy based on PDF characteristics."""
        if is_scanned:
            return 'image_focused'
        elif is_text_based and not is_image_heavy:
            return 'text_focused'
        elif is_text_based and is_image_heavy:
            return 'hybrid'
        else:
            return 'balanced'
    
    def convert_chapter(self, 
                       pdf_path: Path, 
                       output_path: Path,
                       strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert a single chapter with optimized settings.
        
        Args:
            pdf_path: Path to the chapter PDF
            output_path: Path for the output markdown
            strategy: Override automatic strategy detection
            
        Returns:
            Conversion results and metadata
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Chapter file not found: {pdf_path}")
        
        # Analyze PDF if strategy not provided
        if strategy is None:
            analysis = self.detect_pdf_type(pdf_path)
            strategy = analysis['recommended_strategy']
        else:
            analysis = {}
        
        self.logger.info(f"Converting {pdf_path.name} using {strategy} strategy...")
        
        # Configure conversion parameters based on strategy
        params = self._get_conversion_params(strategy)
        
        try:
            # Convert to markdown
            markdown_text = pymupdf4llm.to_markdown(str(pdf_path), **params)
            
            # Apply enhancements
            if self.enhance_academic:
                markdown_text = self._enhance_academic_content(markdown_text)
            
            if self.preserve_structure:
                markdown_text = self._preserve_document_structure(markdown_text)
            
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write markdown file
            output_path.write_text(markdown_text, encoding='utf-8')
            
            # Extract metadata if enabled
            metadata = {}
            if self.extract_metadata:
                metadata = self._extract_chapter_metadata(pdf_path, markdown_text)
            
            result = {
                'input_file': str(pdf_path),
                'output_file': str(output_path),
                'strategy': strategy,
                'analysis': analysis,
                'metadata': metadata,
                'success': True,
                'char_count': len(markdown_text),
                'line_count': len(markdown_text.split('\n'))
            }
            
            self.logger.info(f"✅ Successfully converted {pdf_path.name}")
            self.logger.info(f"📄 Output: {output_path}")
            self.logger.info(f"📊 {result['char_count']} characters, {result['line_count']} lines")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert {pdf_path.name}: {str(e)}")
            return {
                'input_file': str(pdf_path),
                'error': str(e),
                'success': False
            }
    
    def _get_conversion_params(self, strategy: str) -> Dict[str, Any]:
        """Get conversion parameters optimized for the given strategy."""
        base_params = {
            'show_progress': True,
            'fontsize_limit': 3,
            'force_text': True,
        }
        
        if strategy == 'text_focused':
            return {
                **base_params,
                'write_images': False,
                'embed_images': False,
                'ignore_graphics': True,
                'ignore_images': False,
                'table_strategy': 'lines_strict',
                'extract_words': False,
            }
        
        elif strategy == 'image_focused':
            return {
                **base_params,
                'write_images': True,
                'embed_images': False,
                'ignore_graphics': False,
                'ignore_images': False,
                'table_strategy': None,
                'dpi': 200,
                'image_format': 'png',
            }
        
        elif strategy == 'hybrid':
            return {
                **base_params,
                'write_images': True,
                'embed_images': False,
                'ignore_graphics': False,
                'ignore_images': False,
                'table_strategy': 'lines_strict',
                'dpi': 150,
                'image_format': 'png',
                'image_size_limit': 0.03,
            }
        
        else:  # balanced
            return {
                **base_params,
                'write_images': True,
                'embed_images': False,
                'ignore_graphics': False,
                'ignore_images': False,
                'table_strategy': 'lines',
                'dpi': 150,
                'image_format': 'png',
            }
    
    def _enhance_academic_content(self, text: str) -> str:
        """Apply academic-specific enhancements to the markdown."""
        # Fix common academic formatting issues
        text = re.sub(r'\n\s*([A-Z][a-z]+\.?)\s*\n', r'\n\n**\1**\n\n', text)  # Bold standalone words (likely definitions)
        
        # Improve equation formatting
        text = re.sub(r'(\$[^$]+\$)', r'\n\1\n', text)  # Isolate inline math
        text = re.sub(r'(\$\$[^$]+\$\$)', r'\n\1\n', text)  # Isolate display math
        
        # Fix reference formatting
        text = re.sub(r'\[(\d+)\]', r'[\1]', text)  # Clean reference numbers
        text = re.sub(r'([A-Za-z])\s+et\s+al\.?\s+(\d{4})', r'\1 et al. (\2)', text)  # Fix citations
        
        # Improve list formatting
        text = re.sub(r'^\s*(\d+)\.\s+', r'\1. ', text, flags=re.MULTILINE)  # Clean numbered lists
        text = re.sub(r'^\s*[•▪▫]\s+', r'- ', text, flags=re.MULTILINE)  # Convert bullets to markdown
        
        # Fix algorithm and theorem formatting
        text = re.sub(r'\n\s*(Algorithm|Theorem|Lemma|Definition|Proof|Example)\s*(\d+)?\.?\s*:?\s*\n', 
                     r'\n\n**\1 \2**\n\n', text)
        
        return text
    
    def _preserve_document_structure(self, text: str) -> str:
        """Preserve and enhance document structure."""
        lines = text.split('\n')
        processed_lines = []
        
        for i, line in enumerate(lines):
            # Identify and enhance chapter/section titles
            if re.match(r'^[A-Z][A-Z\s]{10,}$', line.strip()):  # All caps lines (likely titles)
                processed_lines.append(f'\n# {line.strip().title()}\n')
            elif re.match(r'^\d+\.?\s+[A-Z]', line.strip()):  # Numbered sections
                processed_lines.append(f'\n## {line.strip()}\n')
            elif re.match(r'^\d+\.\d+\.?\s+[A-Z]', line.strip()):  # Subsections
                processed_lines.append(f'\n### {line.strip()}\n')
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _extract_chapter_metadata(self, pdf_path: Path, markdown_text: str) -> Dict[str, Any]:
        """Extract metadata from the chapter."""
        doc = pymupdf.open(str(pdf_path))
        
        # Basic PDF metadata
        metadata = {
            'filename': pdf_path.name,
            'page_count': doc.page_count,
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'subject': doc.metadata.get('subject', ''),
            'creator': doc.metadata.get('creator', ''),
        }
        
        # Extract chapter-specific information
        first_page_text = doc[0].get_text() if doc.page_count > 0 else ""
        
        # Try to extract chapter title from first page
        lines = first_page_text.split('\n')[:10]  # First 10 lines
        for line in lines:
            line = line.strip()
            if len(line) > 5 and any(word in line.lower() for word in ['chapter', 'section']):
                metadata['extracted_title'] = line
                break
        
        # Count tables, figures, equations
        metadata['table_count'] = len(re.findall(r'\|.*\|', markdown_text))
        metadata['figure_count'] = len(re.findall(r'!\[.*\]\(.*\)', markdown_text))
        metadata['equation_count'] = len(re.findall(r'\$.*\$', markdown_text))
        
        doc.close()
        return metadata
    
    def convert_batch(self, 
                     input_dir: Path, 
                     output_dir: Path,
                     pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Convert multiple chapter files with optimized settings for each.
        
        Args:
            input_dir: Directory containing chapter PDFs
            output_dir: Directory for output markdown files
            pattern: File pattern to match
            
        Returns:
            List of conversion results
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
            result = self.convert_chapter(pdf_file, output_file)
            results.append(result)
        
        # Generate summary report
        self._generate_conversion_report(results, output_dir)
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        self.logger.info(f"📊 Batch conversion complete: {successful}/{len(results)} files successful")
        
        return results
    
    def _generate_conversion_report(self, results: List[Dict[str, Any]], output_dir: Path):
        """Generate a detailed conversion report."""
        report_path = output_dir / "conversion_report.json"
        
        summary = {
            'total_files': len(results),
            'successful_conversions': sum(1 for r in results if r.get('success', False)),
            'failed_conversions': sum(1 for r in results if not r.get('success', False)),
            'strategies_used': {},
            'total_pages': 0,
            'total_characters': 0,
            'details': results
        }
        
        for result in results:
            if result.get('success'):
                strategy = result.get('strategy', 'unknown')
                summary['strategies_used'][strategy] = summary['strategies_used'].get(strategy, 0) + 1
                
                analysis = result.get('analysis', {})
                summary['total_pages'] += analysis.get('sample_pages', 0)
                summary['total_characters'] += result.get('char_count', 0)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📋 Conversion report saved: {report_path}")


def main():
    """Command-line interface for the enhanced chapter converter."""
    parser = argparse.ArgumentParser(
        description="Convert PDF chapters to markdown with enhanced academic processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input-dir extracted_chapters/ --output-dir markdown_chapters/
  %(prog)s chapter.pdf --output-file chapter.md --text-priority
  %(prog)s --input-dir vrp_chapters/ --enhance-academic --preserve-structure
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
        help='Directory containing PDF chapter files'
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
    
    # Processing options
    parser.add_argument(
        '--text-priority',
        action='store_true',
        help='Prioritize text extraction over images (better for text-based PDFs)'
    )
    parser.add_argument(
        '--enhance-academic',
        action='store_true',
        default=True,
        help='Apply academic-specific enhancements (default: True)'
    )
    parser.add_argument(
        '--preserve-structure',
        action='store_true',
        default=True,
        help='Preserve and enhance document structure (default: True)'
    )
    parser.add_argument(
        '--extract-metadata',
        action='store_true',
        default=True,
        help='Extract and include document metadata (default: True)'
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
    converter = EnhancedChapterConverter(
        text_priority=args.text_priority,
        enhance_academic=args.enhance_academic,
        preserve_structure=args.preserve_structure,
        extract_metadata=args.extract_metadata
    )
    
    try:
        if args.input_file:
            # Single file conversion
            output_file = args.output_file or args.input_file.with_suffix('.md')
            result = converter.convert_chapter(args.input_file, output_file)
            
            if result.get('success'):
                print(f"✅ Successfully converted: {result['output_file']}")
            else:
                print(f"❌ Conversion failed: {result.get('error', 'Unknown error')}")
                return 1
                
        else:
            # Batch conversion
            output_dir = args.output_dir or args.input_dir / 'markdown_chapters'
            results = converter.convert_batch(args.input_dir, output_dir, args.pattern)
            
            successful = sum(1 for r in results if r.get('success', False))
            if successful == 0:
                print("❌ No files converted successfully")
                return 1
            elif successful < len(results):
                print(f"⚠️  Partial success: {successful}/{len(results)} files converted")
            else:
                print(f"✅ All {len(results)} files converted successfully")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())