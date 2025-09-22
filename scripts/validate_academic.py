#!/usr/bin/env python3
"""
Academic standards validation script for GPU TSP project.

Enforces:
- TCC (Brazilian thesis) compliance
- Proper academic documentation structure
- Citation and reference standards
- Research methodology compliance
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


# Academic standards and requirements
ACADEMIC_STANDARDS = {
    'documentation_headers': {
        'required_fields': ['title', 'description', 'version', 'created', 'status'],
        'optional_fields': ['updated', 'author', 'reviewer', 'tags']
    },
    'research_papers': {
        'required_sections': ['Abstract', 'Introduction', 'Methodology', 'Results', 'Conclusion'],
        'citation_format': r'\[@[\w\d\-_]+\d{4}[\w\d\-_]*\]'
    },
    'technical_decisions': {
        'required_fields': ['Decision', 'Status', 'Context', 'Consequences'],
        'adr_format': True
    }
}

# File type mappings for academic content
ACADEMIC_FILE_TYPES = {
    '.md': 'markdown',
    '.tex': 'latex',
    '.bib': 'bibtex'
}


def validate_yaml_frontmatter(content: str) -> Tuple[bool, List[str]]:
    """Validate YAML frontmatter in markdown files."""
    violations = []
    
    # Check if file has frontmatter
    if not content.startswith('---\n'):
        violations.append("Missing YAML frontmatter. Academic documents require metadata headers.")
        return False, violations
    
    # Extract frontmatter
    try:
        end_marker = content.find('\n---\n', 4)
        if end_marker == -1:
            violations.append("Invalid YAML frontmatter format. Missing closing '---'.")
            return False, violations
        
        frontmatter = content[4:end_marker]
        
        # Check required fields
        required = ACADEMIC_STANDARDS['documentation_headers']['required_fields']
        for field in required:
            if f'{field}:' not in frontmatter:
                violations.append(f"Missing required field in frontmatter: '{field}'")
        
        # Check for proper format
        lines = frontmatter.strip().split('\n')
        for line in lines:
            if ':' not in line:
                violations.append(f"Invalid frontmatter line format: '{line.strip()}'")
    
    except Exception as e:
        violations.append(f"Error parsing YAML frontmatter: {str(e)}")
    
    return len(violations) == 0, violations


def validate_research_structure(content: str, file_path: Path) -> Tuple[bool, List[str]]:
    """Validate research document structure."""
    violations = []
    
    # Check if it's a research document
    if 'research' not in str(file_path).lower() and 'methodology' not in str(file_path).lower():
        return True, []  # Not a research document
    
    required_sections = ACADEMIC_STANDARDS['research_papers']['required_sections']
    
    # Look for section headers
    found_sections = []
    for section in required_sections:
        patterns = [
            f'# {section}',
            f'## {section}',
            f'### {section}'
        ]
        
        for pattern in patterns:
            if pattern in content:
                found_sections.append(section)
                break
    
    # Check for missing sections
    missing_sections = set(required_sections) - set(found_sections)
    if missing_sections:
        violations.append(f"Missing required research sections: {', '.join(missing_sections)}")
    
    return len(violations) == 0, violations


def validate_citations(content: str) -> Tuple[bool, List[str]]:
    """Validate citation format and presence."""
    violations = []
    
    # Check for citation format
    citation_pattern = ACADEMIC_STANDARDS['research_papers']['citation_format']
    citations = re.findall(citation_pattern, content)
    
    # Look for academic claims without citations
    claim_indicators = [
        'research shows', 'studies indicate', 'according to',
        'has been proven', 'it is known that', 'literature suggests'
    ]
    
    for indicator in claim_indicators:
        if indicator.lower() in content.lower():
            # Check if there's a citation nearby (within 100 characters)
            pos = content.lower().find(indicator.lower())
            context = content[pos:pos+100]
            if not re.search(citation_pattern, context):
                violations.append(f"Academic claim '{indicator}' found without proper citation")
    
    # Check bibliography section
    if citations and 'references' not in content.lower() and 'bibliography' not in content.lower():
        violations.append("Citations found but no References/Bibliography section")
    
    return len(violations) == 0, violations


def validate_adr_format(content: str, file_path: Path) -> Tuple[bool, List[str]]:
    """Validate Architectural Decision Record format."""
    violations = []
    
    # Check if it's an ADR file
    if 'technical_decisions' not in str(file_path):
        return True, []
    
    required_fields = ACADEMIC_STANDARDS['technical_decisions']['required_fields']
    
    for field in required_fields:
        patterns = [
            f'## {field}',
            f'### {field}',
            f'**{field}**:'
        ]
        
        found = any(pattern in content for pattern in patterns)
        if not found:
            violations.append(f"Missing ADR section: '{field}'")
    
    return len(violations) == 0, violations


def validate_academic_language(content: str) -> Tuple[bool, List[str]]:
    """Validate academic writing standards."""
    violations = []
    
    # Check for informal language
    informal_terms = [
        "don't", "can't", "won't", "isn't", "aren't",
        "it's", "that's", "here's", "what's"
    ]
    
    for term in informal_terms:
        if term in content.lower():
            violations.append(f"Avoid contractions in academic writing: '{term}'")
    
    # Check for first person usage (academic style preference)
    first_person = ['i think', 'i believe', 'in my opinion', 'i feel']
    for phrase in first_person:
        if phrase in content.lower():
            violations.append(f"Avoid first-person language in academic writing: '{phrase}'")
    
    # Check for proper terminology
    tech_terms = {
        'gpu': 'GPU',
        'cpu': 'CPU',
        'api': 'API',
        'tsp': 'TSP',
        'vrp': 'VRP'
    }
    
    for incorrect, correct in tech_terms.items():
        # Only flag if not already correct
        if f' {incorrect} ' in content and f' {correct} ' not in content:
            violations.append(f"Technical acronym should be capitalized: '{incorrect}' → '{correct}'")
    
    return len(violations) == 0, violations


def validate_file(file_path: Path) -> List[Tuple[str, str]]:
    """Validate a single academic file."""
    violations = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return [(str(file_path), f"Error reading file: {str(e)}")]
    
    file_type = file_path.suffix.lower()
    
    # Validate based on file type
    if file_type == '.md':
        # YAML frontmatter validation
        is_valid, issues = validate_yaml_frontmatter(content)
        if not is_valid:
            violations.extend([(str(file_path), issue) for issue in issues])
        
        # Research structure validation
        is_valid, issues = validate_research_structure(content, file_path)
        if not is_valid:
            violations.extend([(str(file_path), issue) for issue in issues])
        
        # Citation validation
        is_valid, issues = validate_citations(content)
        if not is_valid:
            violations.extend([(str(file_path), issue) for issue in issues])
        
        # ADR format validation
        is_valid, issues = validate_adr_format(content, file_path)
        if not is_valid:
            violations.extend([(str(file_path), issue) for issue in issues])
        
        # Academic language validation
        is_valid, issues = validate_academic_language(content)
        if not is_valid:
            violations.extend([(str(file_path), issue) for issue in issues])
    
    return violations


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate academic standards')
    parser.add_argument('files', nargs='*', help='Files to validate')
    parser.add_argument('--all', action='store_true', help='Check all academic files')
    
    args = parser.parse_args()
    
    violations = []
    
    if args.all:
        # Find all academic files
        root = Path('.')
        academic_dirs = ['documentation', 'research', 'knowledge_base']
        files_to_check = []
        
        for dir_name in academic_dirs:
            dir_path = root / dir_name
            if dir_path.exists():
                files_to_check.extend(dir_path.rglob('*.md'))
                files_to_check.extend(dir_path.rglob('*.tex'))
    else:
        files_to_check = [Path(f) for f in args.files]
    
    # Validate each file
    for file_path in files_to_check:
        if file_path.exists() and file_path.suffix.lower() in ACADEMIC_FILE_TYPES:
            file_violations = validate_file(file_path)
            violations.extend(file_violations)
    
    if violations:
        print("❌ Academic standards violations found:")
        print()
        
        # Group violations by file
        file_violations: Dict[str, List[str]] = {}
        for file_path, issue in violations:
            if file_path not in file_violations:
                file_violations[file_path] = []
            file_violations[file_path].append(issue)
        
        for file_path, issues in file_violations.items():
            print(f"📄 {file_path}")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        print(f"Total violations: {len(violations)} across {len(file_violations)} files")
        return 1
    
    else:
        print("✅ All files meet academic standards!")
        return 0


if __name__ == '__main__':
    sys.exit(main())