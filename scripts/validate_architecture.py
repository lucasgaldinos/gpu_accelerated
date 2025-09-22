#!/usr/bin/env python3
"""
Architecture validation script for GPU TSP project.

Enforces:
- Hexagonal architecture compliance
- Protocol-based interfaces
- Clean separation of concerns
- Import dependency rules
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple, Set, Dict
import argparse


# Architecture rules
ARCHITECTURE_RULES = {
    'domain': {
        'allowed_imports': ['typing', 'abc', 'dataclasses', 'enum'],
        'forbidden_imports': ['numpy', 'cupy', 'numba', 'requests', 'flask'],
        'description': 'Domain layer should not depend on external frameworks'
    },
    'application': {
        'allowed_imports': ['typing', 'abc', 'logging'],
        'forbidden_imports': ['numpy', 'cupy', 'numba', 'requests', 'flask'],
        'description': 'Application layer should only depend on domain'
    },
    'infrastructure': {
        'allowed_imports': ['*'],  # Infrastructure can import anything
        'forbidden_imports': [],
        'description': 'Infrastructure layer implements external dependencies'
    }
}

# Required patterns for clean architecture
REQUIRED_PATTERNS = {
    'protocols': {
        'pattern': r'class \w+\(Protocol\):',
        'description': 'Use Protocol classes for interfaces'
    },
    'type_hints': {
        'pattern': r'def \w+\([^)]*\) -> ',
        'description': 'All functions should have return type hints'
    }
}


class ArchitectureAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze architecture compliance."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: Set[str] = set()
        self.classes: List[str] = []
        self.functions: List[Tuple[str, bool]] = []  # (name, has_return_type)
        self.protocols: List[str] = []
        self.violations: List[str] = []
    
    def visit_Import(self, node):
        """Visit import statements."""
        for name in node.names:
            self.imports.add(name.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from import statements."""
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append(node.name)
        
        # Check if it's a Protocol
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Protocol':
                self.protocols.append(node.name)
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        has_return_type = node.returns is not None
        self.functions.append((node.name, has_return_type))
        self.generic_visit(node)


def get_layer_from_path(file_path: Path) -> str:
    """Determine architecture layer from file path."""
    path_str = str(file_path).lower()
    
    if 'domain' in path_str or 'models' in path_str or 'entities' in path_str:
        return 'domain'
    elif 'application' in path_str or 'services' in path_str or 'use_cases' in path_str:
        return 'application'
    elif 'infrastructure' in path_str or 'adapters' in path_str or 'repositories' in path_str:
        return 'infrastructure'
    else:
        return 'unknown'


def validate_imports(analyzer: ArchitectureAnalyzer) -> List[str]:
    """Validate import dependencies based on layer."""
    violations = []
    layer = get_layer_from_path(analyzer.file_path)
    
    if layer in ARCHITECTURE_RULES:
        rules = ARCHITECTURE_RULES[layer]
        
        # Check forbidden imports
        for forbidden in rules['forbidden_imports']:
            if forbidden in analyzer.imports:
                violations.append(
                    f"Layer '{layer}' should not import '{forbidden}'. "
                    f"{rules['description']}"
                )
        
        # Check allowed imports (if not wildcard)
        if '*' not in rules['allowed_imports']:
            for import_name in analyzer.imports:
                if import_name not in rules['allowed_imports'] and import_name not in ['os', 'sys', 'pathlib']:
                    violations.append(
                        f"Layer '{layer}' should not import '{import_name}'. "
                        f"Allowed: {', '.join(rules['allowed_imports'])}"
                    )
    
    return violations


def validate_protocols(analyzer: ArchitectureAnalyzer) -> List[str]:
    """Validate Protocol usage."""
    violations = []
    
    # Check if interfaces use Protocol
    interface_indicators = ['interface', 'repository', 'service', 'provider']
    
    for class_name in analyzer.classes:
        class_lower = class_name.lower()
        is_interface = any(indicator in class_lower for indicator in interface_indicators)
        
        if is_interface and class_name not in analyzer.protocols:
            violations.append(
                f"Class '{class_name}' appears to be an interface but doesn't inherit from Protocol"
            )
    
    return violations


def validate_type_hints(analyzer: ArchitectureAnalyzer) -> List[str]:
    """Validate type hint usage."""
    violations = []
    
    # Check functions without return type hints
    for func_name, has_return_type in analyzer.functions:
        if not has_return_type and not func_name.startswith('_'):  # Skip private methods
            violations.append(
                f"Function '{func_name}' missing return type hint"
            )
    
    return violations


def validate_file(file_path: Path) -> List[Tuple[str, str]]:
    """Validate a single Python file."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        analyzer = ArchitectureAnalyzer(file_path)
        analyzer.visit(tree)
        
        # Run validations
        import_violations = validate_imports(analyzer)
        protocol_violations = validate_protocols(analyzer)
        type_violations = validate_type_hints(analyzer)
        
        all_violations = import_violations + protocol_violations + type_violations
        
        for violation in all_violations:
            violations.append((str(file_path), violation))
    
    except SyntaxError as e:
        violations.append((str(file_path), f"Syntax error: {str(e)}"))
    except Exception as e:
        violations.append((str(file_path), f"Error analyzing file: {str(e)}"))
    
    return violations


def generate_architecture_report(root_path: Path) -> str:
    """Generate architecture analysis report."""
    report = []
    report.append("🏗️  Architecture Analysis Report")
    report.append("=" * 40)
    report.append("")
    
    # Find Python files and categorize by layer
    layers: Dict[str, List[Path]] = {
        'domain': [],
        'application': [],
        'infrastructure': [],
        'unknown': []
    }
    
    for py_file in root_path.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            layer = get_layer_from_path(py_file)
            layers[layer].append(py_file)
    
    for layer, files in layers.items():
        if files:
            report.append(f"📁 {layer.upper()} Layer ({len(files)} files)")
            if layer in ARCHITECTURE_RULES:
                report.append(f"   Rule: {ARCHITECTURE_RULES[layer]['description']}")
            
            for file_path in sorted(files):
                rel_path = file_path.relative_to(root_path)
                report.append(f"   • {rel_path}")
            report.append("")
    
    return "\n".join(report)


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate hexagonal architecture')
    parser.add_argument('files', nargs='*', help='Python files to validate')
    parser.add_argument('--all', action='store_true', help='Check all Python files')
    parser.add_argument('--report', action='store_true', help='Generate architecture report')
    
    args = parser.parse_args()
    
    root_path = Path('.').resolve()
    violations = []
    
    if args.report:
        print(generate_architecture_report(root_path))
        return 0
    
    if args.all:
        # Find all Python files in code directory
        code_dir = root_path / 'code'
        if code_dir.exists():
            files_to_check = list(code_dir.rglob('*.py'))
        else:
            files_to_check = list(root_path.rglob('*.py'))
        
        # Filter out __pycache__ and test files
        files_to_check = [
            f for f in files_to_check 
            if '__pycache__' not in str(f) and f.name != '__init__.py'
        ]
    else:
        files_to_check = [Path(f) for f in args.files]
    
    # Validate each file
    for file_path in files_to_check:
        if file_path.exists() and file_path.suffix == '.py':
            file_violations = validate_file(file_path)
            violations.extend(file_violations)
    
    if violations:
        print("❌ Architecture violations found:")
        print()
        
        # Group violations by file
        file_violations: Dict[str, List[str]] = {}
        for file_path, issue in violations:
            if file_path not in file_violations:
                file_violations[file_path] = []
            file_violations[file_path].append(issue)
        
        for file_path, issues in file_violations.items():
            print(f"🐍 {file_path}")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        print(f"Total violations: {len(violations)} across {len(file_violations)} files")
        print()
        print("💡 Architecture Guidelines:")
        print("   • Domain layer: Pure business logic, no external dependencies")
        print("   • Application layer: Use cases and services, coordinates domain")
        print("   • Infrastructure layer: External integrations, databases, APIs")
        print("   • Use Protocol classes for interfaces")
        print("   • Add type hints to all public functions")
        
        return 1
    
    else:
        print("✅ All files follow hexagonal architecture principles!")
        return 0


if __name__ == '__main__':
    sys.exit(main())