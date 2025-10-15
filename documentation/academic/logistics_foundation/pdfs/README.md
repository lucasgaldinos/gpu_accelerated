# PDF Files Directory

This directory contains PDF files with exercises from "The Logic of Logistics" and related materials.

## Current Files

### Expected File
- `085_4_Worst_Case_Analysis.pdf` - Chapter 4: Worst-Case Analysis exercises

## Instructions

1. **Place PDF file here**: Copy the PDF file containing exercises to this directory

2. **File naming**: Use descriptive names like:
   - `{page_number}_{chapter_number}_{chapter_title}.pdf`
   - Example: `085_4_Worst_Case_Analysis.pdf`

3. **Run extraction**: Use the solution generator to extract exercises:
   ```bash
   python scripts/generate_exercise_solutions.py \
     --pdf-path documentation/academic/logistics_foundation/pdfs/085_4_Worst_Case_Analysis.pdf \
     --output-dir documentation/academic/logistics_foundation/solutions \
     --extract-only
   ```

4. **Complete solutions**: Edit the generated templates with full solutions

## Git LFS (Optional)

PDFs are currently excluded from git (see `.gitignore`). If you want to version control PDFs:

1. Install Git LFS:
   ```bash
   git lfs install
   ```

2. Track PDF files:
   ```bash
   git lfs track "*.pdf"
   ```

3. Add and commit:
   ```bash
   git add .gitattributes
   git add *.pdf
   git commit -m "Add PDF files with Git LFS"
   ```

## Note

Due to copyright considerations, PDF files from textbooks should not be committed to public repositories without proper permissions. Use this directory for local processing only.

---

*Place your PDF file here and follow the processing guide to generate solutions.*
