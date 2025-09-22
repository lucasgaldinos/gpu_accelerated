#!/usr/bin/env python3
"""
Project structure validation script for GPU TSP project.

Enforces:
- Proper file organization according to documented structure
- Required directories exist
- Files are in correct locations
- No scattered files outside designated areas
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Define the expected project structure
EXPECTED_STRUCTURE = {
    'artifacts': {
        'description': 'Build artifacts, distributions, releases',
        'allowed_files': {'builds/', 'checksums/', 'distributions/', 'releases/'},
        'file_patterns': ['*.tar.gz', '*.whl', '*.zip', '*.sha256']
    },
    'code': {
        'description': 'Source code and implementation',
        'allowed_files': {'src/', 'tests/', 'examples/', '__init__.py'},
        'file_patterns': ['*.py', 'requirements*.txt', 'setup.py', 'pyproject.toml']
    },
    'data': {
        'description': 'Data files and datasets',
        'allowed_files': {'metadata/', 'processed/', 'raw/', 'synthetic/'},
        'file_patterns': ['*.csv', '*.json', '*.npy', '*.npz', '*.pkl']
    },
    'documentation': {
        'description': 'User and developer documentation',
        'allowed_files': {'api/', 'developer_guides/', 'user_guides/', 'reports/', 'academic/'},
        'file_patterns': ['*.md', '*.rst', '*.html', '*.pdf']
    },
    'infrastructure': {
        'description': 'DevOps and infrastructure configuration',
        'allowed_files': {'ci_cd/', 'containers/', 'environments/', 'monitoring/', 'security/'},
        'file_patterns': ['*.yaml', '*.yml', 'Dockerfile*', '*.tf', '*.sh']
    },
    'knowledge_base': {
        'description': 'Academic and technical knowledge',
        'allowed_files': {'learning_materials/', 'methodology/', 'research_context/', 'technical_decisions/'},
        'file_patterns': ['*.md', '*.bib', '*.tex', '*.pdf']
    },
    'project_management': {
        'description': 'Project planning and management',
        'allowed_files': {'github_integration/', 'planning/', 'progress/', 'tasks/', 'jira/'},
        'file_patterns': ['*.md', '*.yaml', '*.json']
    },
    'research': {
        'description': 'Research materials and results',
        'allowed_files': {'datasets/', 'experiments/', 'methodology/', 'publications/', 'results/'},
        'file_patterns': ['*.md', '*.tex', '*.bib', '*.pdf', '*.ipynb', '*.py']
    }
}

# Files allowed in root directory
ALLOWED_ROOT_FILES = {
    'README.md',
    'pyproject.toml',
    'uv.lock',
    'requirements.txt',
    'requirements-dev.txt',
    '.gitignore',
    '.python-version',
    'LICENSE',
    'CHANGELOG.md',
    'WORKSPACE_ORGANIZATION_COMPLETE.md',
    'remove_empty_md.sh'
}

# Directories allowed in root
ALLOWED_ROOT_DIRS = set(EXPECTED_STRUCTURE.keys()) | {'.git', '.github', '.vscode', '.venv', 'scripts'}


def check_required_directories(root_path: Path) -> List[str]:
    """Check if all required directories exist."""
    missing = []
    
    for dir_name in EXPECTED_STRUCTURE.keys():
        dir_path = root_path / dir_name
        if not dir_path.exists():
            missing.append(f"Required directory missing: {dir_name}/")
    
    return missing


def check_file_organization(root_path: Path) -> List[Tuple[str, str]]:
    """Check if files are properly organized."""
    violations = []
    
    # Check root directory for scattered files
    for item in root_path.iterdir():
        if item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append((
                    item.name,
                    f"File '{item.name}' should not be in root directory. "
                    f"Move to appropriate subdirectory."
                ))
        elif item.is_dir():
            if item.name not in ALLOWED_ROOT_DIRS:
                violations.append((
                    f"{item.name}/",
                    f"Unexpected directory '{item.name}' in root. "
                    f"Expected: {', '.join(sorted(ALLOWED_ROOT_DIRS))}"
                ))
    
    return violations


def check_directory_contents(root_path: Path) -> List[Tuple[str, str]]:
    """Check if directory contents match expected structure."""
    violations = []
    
    for dir_name, config in EXPECTED_STRUCTURE.items():
        dir_path = root_path / dir_name
        if not dir_path.exists():
            continue
            
        # Get allowed subdirectories
        allowed_subdirs = {name.rstrip('/') for name in config['allowed_files'] if name.endswith('/')}
        
        # Check subdirectories
        for item in dir_path.iterdir():
            if item.is_dir():
                if item.name not in allowed_subdirs:
                    violations.append((
                        f"{dir_name}/{item.name}/",
                        f"Unexpected subdirectory in {dir_name}/. "
                        f"Expected: {', '.join(sorted(allowed_subdirs))}"
                    ))
    
    return violations


def suggest_file_location(file_path: Path, root_path: Path) -> str:
    """Suggest where a misplaced file should go."""
    file_name = file_path.name
    file_ext = file_path.suffix.lower()
    
    # Simple heuristics for common file types
    suggestions = []
    
    for dir_name, config in EXPECTED_STRUCTURE.items():
        for pattern in config['file_patterns']:
            if pattern.startswith('*.') and file_ext == pattern[1:]:
                suggestions.append(f"{dir_name}/ ({config['description']})")
    
    if not suggestions:
        # Fallback suggestions based on file name patterns
        if 'test' in file_name.lower():
            suggestions.append("code/tests/ (test files)")
        elif file_ext == '.py':
            suggestions.append("code/src/ (source code)")
        elif file_ext == '.md':
            suggestions.append("documentation/ (documentation)")
        elif 'data' in file_name.lower():
            suggestions.append("data/ (datasets)")
    
    return suggestions[0] if suggestions else "unknown (manual review needed)"


def generate_structure_report(root_path: Path) -> str:
    """Generate a report of current vs expected structure."""
    report = []
    report.append("📁 Current Project Structure Analysis")
    report.append("=" * 50)
    report.append("")
    
    for dir_name, config in EXPECTED_STRUCTURE.items():
        dir_path = root_path / dir_name
        status = "✅" if dir_path.exists() else "❌"
        
        report.append(f"{status} {dir_name}/")
        report.append(f"   Purpose: {config['description']}")
        
        if dir_path.exists():
            subdirs = [item.name for item in dir_path.iterdir() if item.is_dir()]
            files = [item.name for item in dir_path.iterdir() if item.is_file()]
            
            if subdirs:
                report.append(f"   Subdirectories: {', '.join(sorted(subdirs))}")
            if files:
                report.append(f"   Files: {len(files)} files")
        else:
            report.append("   Status: MISSING")
        
        report.append("")
    
    return "\n".join(report)


def main():
    """Main validation function."""
    root_path = Path('.').resolve()
    violations = []
    
    print("🔍 Validating project structure...")
    print()
    
    # Check required directories
    missing_dirs = check_required_directories(root_path)
    if missing_dirs:
        violations.extend([(item, "Missing required directory") for item in missing_dirs])
    
    # Check file organization
    org_violations = check_file_organization(root_path)
    violations.extend(org_violations)
    
    # Check directory contents
    content_violations = check_directory_contents(root_path)
    violations.extend(content_violations)
    
    if violations:
        print("❌ Project structure violations found:")
        print()
        
        for item, message in violations:
            print(f"  • {item}")
            print(f"    {message}")
            
            # Suggest location for misplaced files
            if "should not be in root" in message:
                suggestion = suggest_file_location(Path(item), root_path)
                print(f"    Suggested location: {suggestion}")
            
            print()
        
        print(f"Total violations: {len(violations)}")
        print()
        
        # Generate structure report
        print(generate_structure_report(root_path))
        
        return 1
    
    else:
        print("✅ Project structure is properly organized!")
        print()
        print(generate_structure_report(root_path))
        return 0


if __name__ == '__main__':
    sys.exit(main())