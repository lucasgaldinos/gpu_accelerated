#!/usr/bin/env python3
"""
PDF Chapter Separator Script

LEARNING OBJECTIVE: Understand document processing automation and TOC-based splitting
This script automatically separates a PDF into individual chapters based on its Table of Contents.

Educational Notes:
- Table of Contents (TOC) provides hierarchical document structure
- Chapter identification using TOC level analysis
- PDF manipulation using PyMuPDF for professional-grade document processing
- Automated file organization following academic naming conventions

Performance Characteristics:
- Processes large PDFs (400+ pages) efficiently
- Memory-efficient page-by-page processing
- Preserves original PDF quality and formatting

Technical Decisions:
- PyMuPDF chosen for robust PDF handling and TOC support
- Configurable chapter detection based on TOC hierarchy levels
- Output organization follows academic document structure
- Supports both numbered chapters and named parts/sections
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse
import logging

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_chapter_splitter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFChapterSplitter:
    """
    Professional PDF chapter splitting utility.
    
    This class implements academic-grade PDF processing for separating
    large documents into individual chapters based on Table of Contents.
    """
    
    def __init__(self, pdf_path: str, output_dir: str = None):
        """
        Initialize the PDF chapter splitter.
        
        Args:
            pdf_path (str): Path to the input PDF file
            output_dir (str): Output directory for chapter files
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent / f"{self.pdf_path.stem}_chapters"
        self.doc = None
        self.toc = []
        self.chapters = []
        
        # Import PyMuPDF
        try:
            import pymupdf
            self.pymupdf = pymupdf
        except ImportError:
            logger.error("PyMuPDF not installed. Please install with: pip install pymupdf")
            raise ImportError("PyMuPDF is required for PDF processing")
    
    def __enter__(self):
        """Context manager entry."""
        self.open_document()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_document()
    
    def open_document(self):
        """Open the PDF document and extract TOC."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        logger.info(f"Opening PDF: {self.pdf_path}")
        self.doc = self.pymupdf.open(str(self.pdf_path))
        logger.info(f"Document opened successfully - {len(self.doc)} pages")
        
        # Extract Table of Contents
        self.toc = self.doc.get_toc()
        if not self.toc:
            logger.warning("No Table of Contents found - will use basic page splitting")
        else:
            logger.info(f"Found TOC with {len(self.toc)} entries")
    
    def close_document(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            logger.info("Document closed")
    
    def sanitize_filename(self, text: str) -> str:
        """
        Sanitize text for use as filename.
        
        Args:
            text (str): Raw text to sanitize
            
        Returns:
            str: Sanitized filename
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', text)
        sanitized = re.sub(r'[\\s]+', '_', sanitized)
        sanitized = re.sub(r'[._-]+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized
    
    def identify_chapters(self, chapter_levels: List[int] = [1], 
                         chapters_only: bool = True) -> List[Dict[str, Any]]:
        """
        Identify chapter boundaries from TOC.
        
        Args:
            chapter_levels (List[int]): TOC levels to consider as chapters
            chapters_only (bool): If True, filter out parts and front/back matter
            
        Returns:
            List[Dict]: List of chapter information
        """
        if not self.toc:
            logger.warning("No TOC available - creating single file output")
            return [{
                'title': self.pdf_path.stem,
                'start_page': 1,
                'end_page': len(self.doc),
                'level': 0,
                'type': 'complete_document'
            }]
        
        chapters = []
        
        # Find all entries at specified levels
        all_entries = [entry for entry in self.toc if entry[0] in chapter_levels]
        
        # If chapters_only is True, filter intelligently
        if chapters_only:
            chapter_entries = []
            for entry in all_entries:
                level, title, page = entry[:3]
                title_lower = title.lower()
                
                # Skip part divisions and front/back matter
                if (title_lower.startswith('part ') or 
                    title_lower in ['preface', 'acknowledgments', 'contents', 
                                  'list of tables', 'list of figures', 'references', 'index']):
                    logger.debug(f"Skipping part/front matter: {title}")
                    continue
                
                # Include numbered chapters and introduction
                if (re.match(r'^\d+', title) or 
                    title_lower.startswith('introduction') or
                    'introduction' in title_lower):
                    chapter_entries.append(entry)
                else:
                    logger.debug(f"Filtering out non-chapter entry: {title}")
        else:
            chapter_entries = all_entries
        
        # If we filtered out too much, fall back to level 2
        if chapters_only and len(chapter_entries) < 5:
            logger.info("Few chapters found at level 1, trying level 2 for numbered chapters")
            level_2_entries = [entry for entry in self.toc if entry[0] == 2]
            numbered_chapters = [entry for entry in level_2_entries 
                               if re.match(r'^\d+', entry[1])]
            if len(numbered_chapters) > len(chapter_entries):
                chapter_entries = numbered_chapters
                logger.info(f"Using {len(numbered_chapters)} numbered chapters from level 2")
        
        logger.info(f"Found {len(chapter_entries)} chapter-level entries")
        
        for i, entry in enumerate(chapter_entries):
            level, title, page = entry[:3]
            
            # Determine end page
            if i + 1 < len(chapter_entries):
                end_page = chapter_entries[i + 1][2] - 1
            else:
                end_page = len(self.doc)
            
            # Skip empty chapters
            if page >= end_page:
                logger.warning(f"Skipping empty chapter: {title}")
                continue
            
            chapter_info = {
                'title': title,
                'start_page': page,
                'end_page': end_page,
                'level': level,
                'type': 'chapter',
                'filename': self.sanitize_filename(f"{page:03d}_{title}")
            }
            
            chapters.append(chapter_info)
            logger.debug(f"Chapter: {title} (Pages {page}-{end_page})")
        
        self.chapters = chapters
        return chapters
    
    def extract_chapter(self, chapter: Dict[str, Any], output_path: Path) -> bool:
        """
        Extract a single chapter to a separate PDF file.
        
        Args:
            chapter (Dict): Chapter information
            output_path (Path): Output file path
            
        Returns:
            bool: Success status
        """
        try:
            # Create new PDF document
            new_doc = self.pymupdf.open()
            
            # Insert pages (PyMuPDF uses 0-based indexing, but TOC uses 1-based)
            start_page = chapter['start_page'] - 1
            end_page = chapter['end_page'] - 1
            
            new_doc.insert_pdf(self.doc, from_page=start_page, to_page=end_page)
            
            # Set metadata
            metadata = {
                'title': chapter['title'],
                'subject': f"Chapter extracted from {self.pdf_path.name}",
                'creator': 'PDF Chapter Splitter',
                'producer': 'PyMuPDF',
                'keywords': 'chapter, logistics, academic'
            }
            new_doc.set_metadata(metadata)
            
            # Save the chapter
            new_doc.save(str(output_path))
            new_doc.close()
            
            logger.info(f"Extracted: {chapter['title']} → {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract chapter {chapter['title']}: {e}")
            return False
    
    def split_chapters(self, chapter_levels: List[int] = [1], 
                      include_parts: bool = False,
                      chapters_only: bool = True) -> Dict[str, Any]:
        """
        Split the PDF into chapters based on TOC.
        
        Args:
            chapter_levels (List[int]): TOC levels to consider as chapters
            include_parts (bool): Whether to include part-level divisions
            chapters_only (bool): Whether to filter out parts and front/back matter
            
        Returns:
            Dict: Results summary
        """
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
        
        # If include_parts is True, also split by major parts
        levels_to_split = chapter_levels.copy()
        if include_parts:
            # Look for part-level entries (typically containing "Part")
            part_entries = [entry for entry in self.toc 
                          if entry[0] == 1 and 'part' in entry[1].lower()]
            if part_entries:
                logger.info(f"Found {len(part_entries)} part-level divisions")
        
        # Identify chapters
        chapters = self.identify_chapters(chapter_levels, chapters_only)
        
        results = {
            'total_chapters': len(chapters),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'output_directory': str(self.output_dir),
            'chapter_files': []
        }
        
        # Extract each chapter
        for chapter in chapters:
            output_filename = f"{chapter['filename']}.pdf"
            output_path = self.output_dir / output_filename
            
            if self.extract_chapter(chapter, output_path):
                results['successful_extractions'] += 1
                results['chapter_files'].append({
                    'title': chapter['title'],
                    'filename': output_filename,
                    'pages': f"{chapter['start_page']}-{chapter['end_page']}",
                    'page_count': chapter['end_page'] - chapter['start_page'] + 1
                })
            else:
                results['failed_extractions'] += 1
        
        # Generate summary report
        self.generate_summary_report(results)
        
        return results
    
    def generate_summary_report(self, results: Dict[str, Any]):
        """
        Generate a summary report of the splitting operation.
        
        Args:
            results (Dict): Results from the splitting operation
        """
        report_path = self.output_dir / "chapter_extraction_summary.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter Extraction Summary\\n\\n")
            f.write(f"**Source Document:** {self.pdf_path.name}\\n")
            f.write(f"**Total Pages:** {len(self.doc)}\\n")
            f.write(f"**Extraction Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            f.write(f"## Results\\n\\n")
            f.write(f"- **Total Chapters:** {results['total_chapters']}\\n")
            f.write(f"- **Successful Extractions:** {results['successful_extractions']}\\n")
            f.write(f"- **Failed Extractions:** {results['failed_extractions']}\\n")
            f.write(f"- **Output Directory:** `{results['output_directory']}`\\n\\n")
            
            if results['chapter_files']:
                f.write(f"## Extracted Chapters\\n\\n")
                f.write(f"| # | Chapter Title | Filename | Pages | Page Count |\\n")
                f.write(f"|---|---------------|----------|-------|------------|\\n")
                
                for i, chapter in enumerate(results['chapter_files'], 1):
                    f.write(f"| {i} | {chapter['title']} | `{chapter['filename']}` | {chapter['pages']} | {chapter['page_count']} |\\n")
            
            f.write(f"\\n## Usage Notes\\n\\n")
            f.write(f"- All extracted chapters maintain original PDF quality and formatting\\n")
            f.write(f"- Chapter boundaries determined from document Table of Contents\\n")
            f.write(f"- Files are named with page numbers for easy reference\\n")
            f.write(f"- Each chapter includes proper metadata for academic use\\n")
        
        logger.info(f"Summary report saved: {report_path}")

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Split a PDF into chapters based on Table of Contents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split into numbered chapters only (default behavior)
  python split_pdf_chapters.py document.pdf
  
  # Split into chapters and sections (levels 1 and 2)
  python split_pdf_chapters.py document.pdf --levels 1 2
  
  # Include part-level divisions and front/back matter
  python split_pdf_chapters.py document.pdf --include-parts
  
  # Extract all level 1 entries without filtering
  python split_pdf_chapters.py document.pdf --all-levels
  
  # Specify custom output directory
  python split_pdf_chapters.py document.pdf --output /path/to/output
        """
    )
    
    parser.add_argument('pdf_path', help='Path to the PDF file to split')
    parser.add_argument('--output', '-o', help='Output directory for chapter files')
    parser.add_argument('--levels', '-l', nargs='+', type=int, default=[1],
                       help='TOC levels to consider as chapters (default: 1)')
    parser.add_argument('--include-parts', action='store_true',
                       help='Include part-level divisions (by default, extracts numbered chapters only)')
    parser.add_argument('--all-levels', action='store_true',
                       help='Extract all entries at specified levels without filtering')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Process the PDF
    try:
        with PDFChapterSplitter(args.pdf_path, args.output) as splitter:
            results = splitter.split_chapters(
                chapter_levels=args.levels,
                include_parts=args.include_parts,
                chapters_only=not (args.include_parts or args.all_levels)
            )
        
        # Display results
        print(f"\\n✅ Chapter extraction completed!")
        print(f"📁 Output directory: {results['output_directory']}")
        print(f"📄 Chapters extracted: {results['successful_extractions']}/{results['total_chapters']}")
        
        if results['failed_extractions'] > 0:
            print(f"⚠️  Failed extractions: {results['failed_extractions']}")
        
        print(f"\\n📋 Extracted chapters:")
        for i, chapter in enumerate(results['chapter_files'], 1):
            print(f"  {i:2d}. {chapter['title']} ({chapter['page_count']} pages)")
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()