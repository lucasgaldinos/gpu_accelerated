#!/usr/bin/env python3
"""
Script to examine PDF structure and identify chapter boundaries.

LEARNING OBJECTIVE: Understand PDF document structure and TOC analysis
This script analyzes the Simchi-Levi PDF to understand its organization.

Educational Notes:
- PDF Table of Contents (TOC) provides hierarchical structure
- Bookmarks can indicate chapter boundaries
- Text pattern analysis helps identify chapters when TOC is absent
- Understanding PDF structure is crucial for automated document processing
"""

import sys
from pathlib import Path
import re

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def examine_pdf_structure(pdf_path):
    """
    Examine PDF structure to identify chapter organization.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Analysis results including TOC, metadata, and chapter patterns
    """
    try:
        # Try importing PyMuPDF first
        import pymupdf
        
        print(f"Opening PDF: {pdf_path}")
        doc = pymupdf.open(pdf_path)
        
        results = {
            "total_pages": len(doc),
            "metadata": doc.metadata,
            "has_toc": False,
            "toc_entries": [],
            "potential_chapters": []
        }
        
        print(f"Total pages: {results['total_pages']}")
        print(f"Metadata: {results['metadata']}")
        
        # Check for Table of Contents
        toc = doc.get_toc()
        if toc:
            results["has_toc"] = True
            results["toc_entries"] = toc
            print(f"\n✅ Found Table of Contents with {len(toc)} entries:")
            for i, entry in enumerate(toc):
                level, title, page = entry[:3]
                print(f"  {i+1:2d}. Level {level}: '{title}' (Page {page})")
                
                # Identify chapter-level entries (usually level 1)
                if level == 1:
                    results["potential_chapters"].append({
                        "title": title,
                        "page": page,
                        "type": "toc_chapter"
                    })
        else:
            print("\n❌ No Table of Contents found")
        
        # If no TOC, analyze text patterns for chapter detection
        if not toc:
            print("\n🔍 Analyzing text patterns for chapter detection...")
            chapter_patterns = [
                r"^Chapter\s+\d+",
                r"^CHAPTER\s+\d+",
                r"^\d+\.\s+[A-Z][A-Za-z\s]+",
                r"^Part\s+[IVX\d]+",
                r"^PART\s+[IVX\d]+"
            ]
            
            for page_num in range(min(20, len(doc))):  # Check first 20 pages
                page = doc.load_page(page_num)
                text = page.get_text()
                lines = text.split('\n')
                
                for line_num, line in enumerate(lines[:50]):  # Check first 50 lines per page
                    line = line.strip()
                    if not line:
                        continue
                        
                    for pattern in chapter_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            results["potential_chapters"].append({
                                "title": line,
                                "page": page_num + 1,
                                "type": "text_pattern",
                                "pattern": pattern
                            })
                            print(f"  Found potential chapter on page {page_num + 1}: '{line}'")
                            break
        
        # Analyze first few pages for document structure
        print(f"\n📄 First 3 pages content preview:")
        for page_num in range(min(3, len(doc))):
            page = doc.load_page(page_num)
            text = page.get_text()
            lines = text.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            print(f"\nPage {page_num + 1} (showing first 10 non-empty lines):")
            for i, line in enumerate(non_empty_lines[:10]):
                print(f"  {i+1:2d}: {line}")
            if len(non_empty_lines) > 10:
                print(f"  ... and {len(non_empty_lines) - 10} more lines")
        
        doc.close()
        return results
        
    except ImportError:
        print("❌ PyMuPDF not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pymupdf"], check=True)
        print("✅ PyMuPDF installed. Please run the script again.")
        return None
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return None

def main():
    """Main function to examine the PDF structure."""
    # Path to the Simchi-Levi PDF
    pdf_path = Path(__file__).parent.parent / "knowledge_base" / "tcc_context" / "referencias_professr" / "simchi-levi2014-logic-of-logistics-454.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🔍 PDF Structure Analysis")
    print("=" * 50)
    
    results = examine_pdf_structure(str(pdf_path))
    
    if results:
        print(f"\n📊 Analysis Summary:")
        print(f"  Total pages: {results['total_pages']}")
        print(f"  Has TOC: {results['has_toc']}")
        print(f"  Potential chapters found: {len(results['potential_chapters'])}")
        
        if results['potential_chapters']:
            print(f"\n📋 Chapter Summary:")
            for i, chapter in enumerate(results['potential_chapters']):
                print(f"  {i+1:2d}. {chapter['title']} (Page {chapter['page']}) - {chapter['type']}")

if __name__ == "__main__":
    main()