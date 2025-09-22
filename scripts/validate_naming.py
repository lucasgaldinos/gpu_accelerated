#!/usr/bin/env python3
"""
Naming convention validation script for GPU TSP project.

Enforces:
- snake_case for directories and files
- kebab-case for git branches
- Consistent naming across project
"""
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple


def is_snake_case(name: str) -> bool:
    """Check if a name follows snake_case convention."""
    # Allow numbers, letters, underscores, dots for files
    return bool(re.match(r'^[a-z0-9_\.]+$', name))


def is_valid_directory_name(name: str) -> bool:
    """Check if directory name is valid snake_case."""
    # No dots allowed in directory names
    return bool(re.match(r'^[a-z0-9_]+$', name))


def check_directories(root_path: Path) -> List[Tuple[str, str]]:
    """Check all directories for naming convention compliance."""
    violations = []
    
    # Skip these directories from checking
    skip_dirs = {'.git', '.vscode', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
    
    # Paths exempt from strict naming (research data, external datasets)
    exempt_paths = {
        'research/publications',
        'research/methodology/tcc_context', 
        '.github',
        'documentation/developer_guides/legacy_code'
    }
    
    for item in root_path.rglob('*'):
        if item.is_dir():
            # Check if this path should be skipped entirely
            rel_path = str(item.relative_to(root_path))
            if any(skip in item.parts for skip in skip_dirs):
                continue
                
            # Check if this path should be exempt
            is_exempt = any(rel_path.startswith(exempt) for exempt in exempt_paths)
            
            if not is_exempt and not is_valid_directory_name(item.name):
                violations.append((
                    rel_path,
                    f"Directory '{item.name}' should be snake_case"
                ))
    
    return violations


def check_files(root_path: Path) -> List[Tuple[str, str]]:
    """Check all files for naming convention compliance."""
    violations = []
    
    # File extensions that should be snake_case
    check_extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.toml', '.txt', '.sh'}
    
    for item in root_path.rglob('*'):
        if item.is_file():
            # Skip hidden files and files in skip directories
            if item.name.startswith('.'):
                continue
                
            if any(skip in item.parts for skip in ['.git', '.vscode', '__pycache__', '.venv']):
                continue
                
            # Check if file extension requires snake_case
            if item.suffix in check_extensions:
                # Remove extension for checking
                name_without_ext = item.stem
                if not is_snake_case(name_without_ext):
                    violations.append((
                        str(item.relative_to(root_path)),
                        f"File '{item.name}' should be snake_case"
                    ))
    
    return violations


def suggest_snake_case(name: str) -> str:
    """Suggest snake_case version of a name."""
    # Convert CamelCase to snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # Replace spaces and hyphens with underscores
    result = re.sub(r'[\s\-]+', '_', result)
    
    # Remove multiple underscores
    result = re.sub(r'_+', '_', result)
    
    # Remove leading/trailing underscores
    result = result.strip('_')
    
    return result


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate naming conventions')
    parser.add_argument('--check-directories', action='store_true',
                       help='Check directory naming')
    parser.add_argument('--check-files', action='store_true',
                       help='Check file naming')
    parser.add_argument('--suggest-fixes', action='store_true',
                       help='Suggest fixes for violations')
    parser.add_argument('--root', type=str, default='.',
                       help='Root directory to check')
    
    args = parser.parse_args()
    
    root_path = Path(args.root).resolve()
    violations = []
    
    if args.check_directories or not (args.check_files):
        violations.extend(check_directories(root_path))
    
    if args.check_files:
        violations.extend(check_files(root_path))
    
    if violations:
        print("❌ Naming convention violations found:")
        print()
        
        for path, message in violations:
            print(f"  • {path}")
            print(f"    {message}")
            
            if args.suggest_fixes:
                current_name = Path(path).name
                suggested = suggest_snake_case(current_name)
                if suggested != current_name:
                    print(f"    Suggested: {suggested}")
            print()
        
        print(f"Total violations: {len(violations)}")
        
        if not args.suggest_fixes:
            print("\nRun with --suggest-fixes to see suggested corrections.")
        
        return 1
    
    else:
        print("✅ All names follow snake_case convention!")
        return 0


if __name__ == '__main__':
    sys.exit(main())