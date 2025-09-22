#!/usr/bin/env python3
"""
Demo script showing different PDF chapter extraction modes.

This script demonstrates the various ways to extract content from the Simchi-Levi PDF.
"""

import subprocess
import sys
from pathlib import Path

def run_extraction_demo():
    """Demonstrate different extraction modes."""
    pdf_path = "knowledge_base/tcc_context/referencias_professr/simchi-levi2014-logic-of-logistics-454.pdf"
    base_script = "python scripts/split_pdf_chapters.py"
    
    print("🔍 PDF Chapter Extraction Demo")
    print("=" * 50)
    
    demos = [
        {
            "name": "Individual Chapters (Default)",
            "description": "Extracts numbered chapters automatically",
            "command": f'{base_script} "{pdf_path}" --output "demo_chapters"',
            "expected": "Chapters 2-21 individually"
        },
        {
            "name": "Parts Only", 
            "description": "Extracts major part divisions",
            "command": f'{base_script} "{pdf_path}" --output "demo_parts" --include-parts',
            "expected": "Parts I-V plus front/back matter"
        },
        {
            "name": "All Level 1 Entries",
            "description": "Extracts everything at TOC level 1",
            "command": f'{base_script} "{pdf_path}" --output "demo_all" --all-levels',
            "expected": "All 13 level-1 TOC entries"
        }
    ]
    
    for demo in demos:
        print(f"\n📋 {demo['name']}")
        print(f"   Description: {demo['description']}")
        print(f"   Expected: {demo['expected']}")
        print(f"   Command: {demo['command']}")
        
        user_input = input("   Run this demo? (y/n/q): ").strip().lower()
        if user_input == 'q':
            break
        elif user_input == 'y':
            print("   Running...")
            try:
                result = subprocess.run(demo['command'].split(), 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("   ✅ Success!")
                    # Extract chapter count from output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Chapters extracted:" in line:
                            print(f"   📊 {line.strip()}")
                            break
                else:
                    print(f"   ❌ Failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("   ⏰ Timeout (operation taking too long)")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Demo completed!")
    print(f"\nUsage Summary:")
    print(f"• Default: Extract numbered chapters automatically")
    print(f"• --include-parts: Extract parts and front/back matter") 
    print(f"• --all-levels: Extract everything at specified level")
    print(f"• --levels 1 2: Extract from multiple TOC levels")

if __name__ == "__main__":
    run_extraction_demo()