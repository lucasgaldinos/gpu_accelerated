#!/usr/bin/env python3
"""
PDF Subchapter Extractor Script

LEARNING OBJECTIVE: Extract specific subchapters (sections) from PDF documents
This script extracts individual subchapters (like 1.1, 1.2, 4.2, etc.) from the Simchi-Levi PDF
based on the Table of Contents hierarchy.

Educational Notes:
- TOC levels determine hierarchy: Level 3 = subchapters (1.1, 4.2), Level 4 = sub-subchapters
- Automated extraction maintains academic document structure
- Page range calculation from TOC entries
- Output organization for research reference

Features:
- Extract specific subchapters by number/title
- Batch extraction of multiple subchapters
- Convert extracted sections to markdown
- Maintain proper academic naming conventions
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
        logging.FileHandler('subchapter_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SubchapterExtractor:
    """
    Extract specific subchapters from PDF documents using TOC analysis.
    """
    
    def __init__(self, pdf_path: str, output_dir: str = None):
        """
        Initialize the subchapter extractor.
        
        Args:
            pdf_path (str): Path to the input PDF file
            output_dir (str): Output directory for extracted subchapters
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent / f"{self.pdf_path.stem}_subchapters"
        self.doc = None
        self.toc = []
        self.subchapters = []
        
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
            raise ValueError("No Table of Contents found - cannot extract subchapters")
        
        logger.info(f"Found {len(self.toc)} TOC entries")
        self._analyze_subchapters()
    
    def close_document(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None
    
    def _analyze_subchapters(self):
        """Analyze TOC to identify subchapters (level 3) and their page ranges."""
        self.subchapters = []
        
        for i, entry in enumerate(self.toc):
            level, title, page = entry[:3]
            
            # We're interested in level 3 (subchapters like 4.1, 4.2) and level 4 (sub-subchapters like 4.2.1)
            if level in [3, 4]:
                # Find the end page by looking at the next entry at the same or higher level
                end_page = None
                for j in range(i + 1, len(self.toc)):
                    next_level, next_title, next_page = self.toc[j][:3]
                    if next_level <= level:  # Same or higher level (end of current section)
                        end_page = next_page - 1
                        break
                
                # If no next section found, use document end
                if end_page is None:
                    end_page = len(self.doc)
                
                subchapter_info = {
                    'level': level,
                    'title': title,
                    'start_page': page,
                    'end_page': end_page,
                    'page_count': end_page - page + 1,
                    'toc_index': i
                }
                
                self.subchapters.append(subchapter_info)
        
        logger.info(f"Found {len(self.subchapters)} subchapters")
    
    def list_subchapters(self, filter_pattern: str = None) -> List[Dict]:
        """
        List available subchapters with optional filtering.
        
        Args:
            filter_pattern (str): Regex pattern to filter subchapter titles
            
        Returns:
            List[Dict]: List of subchapter information
        """
        if filter_pattern:
            pattern = re.compile(filter_pattern, re.IGNORECASE)
            filtered = [sc for sc in self.subchapters if pattern.search(sc['title'])]
        else:
            filtered = self.subchapters
        
        return filtered
    
    def extract_subchapter(self, subchapter_info: Dict, output_format: str = 'pdf') -> Path:
        """
        Extract a specific subchapter to a file.
        
        Args:
            subchapter_info (Dict): Subchapter information from list_subchapters()
            output_format (str): Output format ('pdf' or 'markdown')
            
        Returns:
            Path: Path to the extracted file
        """
        title = subchapter_info['title']
        start_page = subchapter_info['start_page'] - 1  # PyMuPDF uses 0-based indexing
        end_page = subchapter_info['end_page'] - 1
        
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', '_', clean_title.strip())
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_format.lower() == 'pdf':
            output_file = self.output_dir / f"{clean_title}.pdf"
            
            # Create new PDF with selected pages
            new_doc = self.pymupdf.open()
            new_doc.insert_pdf(self.doc, from_page=start_page, to_page=end_page)
            new_doc.save(str(output_file))
            new_doc.close()
            
            logger.info(f"Extracted PDF: {output_file}")
            
        elif output_format.lower() == 'markdown':
            output_file = self.output_dir / f"{clean_title}.md"
            
            # Extract text and convert to markdown
            markdown_content = []
            markdown_content.append(f"# {title}")
            markdown_content.append("")
            
            for page_num in range(start_page, end_page + 1):
                page = self.doc.load_page(page_num)
                text = page.get_text()
                
                # Basic markdown formatting
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Simple heuristics for markdown formatting
                        if re.match(r'^\d+\.\d+', line):  # Section numbers
                            markdown_content.append(f"## {line}")
                        elif line.isupper() and len(line) < 100:  # Likely headers
                            markdown_content.append(f"### {line}")
                        else:
                            markdown_content.append(line)
                    markdown_content.append("")
            
            # Write markdown file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(markdown_content))
            
            logger.info(f"Extracted Markdown: {output_file}")
        
        return output_file
    
    def extract_multiple_subchapters(self, 
                                   patterns: List[str], 
                                   output_format: str = 'pdf') -> List[Path]:
        """
        Extract multiple subchapters matching the given patterns.
        
        Args:
            patterns (List[str]): List of regex patterns to match subchapter titles
            output_format (str): Output format ('pdf' or 'markdown')
            
        Returns:
            List[Path]: List of paths to extracted files
        """
        extracted_files = []
        
        for pattern in patterns:
            matching_subchapters = self.list_subchapters(pattern)
            logger.info(f"Pattern '{pattern}' matched {len(matching_subchapters)} subchapters")
            
            for subchapter in matching_subchapters:
                try:
                    output_file = self.extract_subchapter(subchapter, output_format)
                    extracted_files.append(output_file)
                except Exception as e:
                    logger.error(f"Failed to extract {subchapter['title']}: {e}")
        
        return extracted_files

def main():
    """Main function to handle command line arguments and execute extraction."""
    parser = argparse.ArgumentParser(description="Extract subchapters from PDF documents")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", "-o", help="Output directory for extracted files")
    parser.add_argument("--format", "-f", choices=['pdf', 'markdown'], default='pdf',
                       help="Output format (default: pdf)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List available subchapters")
    parser.add_argument("--patterns", "-p", nargs="+",
                       help="Regex patterns to match subchapter titles")
    parser.add_argument("--filter", help="Filter subchapters by regex pattern")
    
    args = parser.parse_args()
    
    try:
        with SubchapterExtractor(args.pdf_path, args.output_dir) as extractor:
            
            if args.list:
                subchapters = extractor.list_subchapters(args.filter)
                print(f"\n📋 Available Subchapters ({len(subchapters)}):")
                print("=" * 80)
                for i, sc in enumerate(subchapters, 1):
                    print(f"{i:3d}. Level {sc['level']}: {sc['title']}")
                    print(f"     Pages {sc['start_page']}-{sc['end_page']} ({sc['page_count']} pages)")
                return
            
            if args.patterns:
                extracted_files = extractor.extract_multiple_subchapters(args.patterns, args.format)
                print(f"\n✅ Extracted {len(extracted_files)} subchapters:")
                for file_path in extracted_files:
                    print(f"   - {file_path}")
            else:
                print("No extraction patterns specified. Use --patterns or --list to see available subchapters.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()