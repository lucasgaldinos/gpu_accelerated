---
title: "Automated Quality Enforcement Configuration"
applyTo: "**"
enforced: true
validation: "pre-commit,ci-cd,real-time"
---

# Automated Quality Enforcement Configuration

## PRE-COMMIT HOOKS (MANDATORY)

### Installation and Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Configuration File (.pre-commit-config.yaml)

```yaml
repos:
  - repo: local
    hooks:
      # Repository structure validation
      - id: validate-structure
        name: Validate repository structure
        entry: python scripts/validate_structure.py
        language: system
        pass_filenames: false
        
      # File naming validation
      - id: validate-naming
        name: Validate file naming conventions
        entry: python scripts/validate_naming.py
        language: system
        pass_filenames: false
        
      # JIRA integration validation
      - id: validate-jira-integration
        name: Validate JIRA branch/commit conventions
        entry: python scripts/validate_jira_integration.py
        language: system
        stages: [commit-msg, pre-push]
        
  # Code quality tools
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        
  # Documentation and markdown
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.35.0
    hooks:
      - id: markdownlint
        args: ["--fix"]
```

## VALIDATION SCRIPTS (ENFORCED)

### Structure Validation (scripts/validate_structure.py)

```python
#!/usr/bin/env python3
"""Repository structure validation script."""

import os
import sys
from pathlib import Path

REQUIRED_DIRECTORIES = {
    "code": {
        "required": True,
        "subdirs": ["src", "tests", "examples"]
    },
    "data": {"required": True},
    "documentation": {"required": True},
    "infrastructure": {"required": True},
    "knowledge_base": {"required": True},
    "project_management": {
        "required": True,
        "subdirs": ["jira_templates", "tasks", "planning"]
    },
    "research": {"required": True}
}

def validate_structure():
    """Validate repository directory structure."""
    errors = []
    root = Path(".")
    
    for dirname, config in REQUIRED_DIRECTORIES.items():
        dir_path = root / dirname
        if not dir_path.exists():
            errors.append(f"❌ Missing required directory: {dirname}")
            continue
            
        if "subdirs" in config:
            for subdir in config["subdirs"]:
                subdir_path = dir_path / subdir
                if not subdir_path.exists():
                    errors.append(f"❌ Missing subdirectory: {dirname}/{subdir}")
    
    return errors

if __name__ == "__main__":
    errors = validate_structure()
    if errors:
        print("Repository structure validation failed:")
        for error in errors:
            print(error)
        sys.exit(1)
    print("✅ Repository structure validation passed")
```

### Naming Validation (scripts/validate_naming.py)

```python
#!/usr/bin/env python3
"""File and directory naming validation script."""

import re
import sys
from pathlib import Path

NAMING_RULES = {
    "directories": r"^[a-z][a-z0-9_]*$",  # snake_case
    "python_files": r"^[a-z][a-z0-9_]*\.py$",  # snake_case.py
    "test_files": r"^(test_|_test\.py$|tests\.py$)",  # test_*.py or *_test.py
    "config_files": r"^[a-z][a-z0-9-]*\.(yml|yaml|json|toml)$",  # kebab-case
    "markdown_files": r"^([A-Z][A-Z0-9_]*\.md|[a-z][a-z0-9_]*\.md)$"  # UPPER or snake_case
}

def validate_naming():
    """Validate file and directory naming conventions."""
    errors = []
    
    # Check directories
    for path in Path(".").rglob("*"):
        if path.is_dir() and not path.name.startswith("."):
            if not re.match(NAMING_RULES["directories"], path.name):
                errors.append(f"❌ Invalid directory name: {path}")
                
        elif path.is_file():
            # Check Python files
            if path.suffix == ".py":
                if path.name.startswith("test_") or path.name.endswith("_test.py"):
                    if not re.search(NAMING_RULES["test_files"], path.name):
                        errors.append(f"❌ Invalid test file name: {path}")
                else:
                    if not re.match(NAMING_RULES["python_files"], path.name):
                        errors.append(f"❌ Invalid Python file name: {path}")
                        
            # Check configuration files
            elif path.suffix in [".yml", ".yaml", ".json", ".toml"]:
                if not re.match(NAMING_RULES["config_files"], path.name):
                    errors.append(f"❌ Invalid config file name: {path}")
                    
            # Check markdown files
            elif path.suffix == ".md":
                if not re.match(NAMING_RULES["markdown_files"], path.name):
                    errors.append(f"❌ Invalid markdown file name: {path}")
    
    return errors

if __name__ == "__main__":
    errors = validate_naming()
    if errors:
        print("File naming validation failed:")
        for error in errors[:10]:  # Show first 10 errors
            print(error)
        if len(errors) > 10:
            print(f"... and {len(errors) - 10} more errors")
        sys.exit(1)
    print("✅ File naming validation passed")
```

### JIRA Integration Validation (scripts/validate_jira_integration.py)

```python
#!/usr/bin/env python3
"""JIRA integration validation script."""

import os
import re
import sys
import subprocess

PROJECT_KEY = "PT"
BRANCH_PATTERN = rf"^(feature|bugfix|research|docs)/{PROJECT_KEY}-\d+-.*$"
COMMIT_PATTERN = rf"^{PROJECT_KEY}-\d+:.*$"

def get_current_branch():
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_commit_message():
    """Get current commit message."""
    commit_msg_file = sys.argv[1] if len(sys.argv) > 1 else ".git/COMMIT_EDITMSG"
    try:
        with open(commit_msg_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def validate_jira_integration():
    """Validate JIRA integration requirements."""
    errors = []
    
    # Validate branch name
    branch = get_current_branch()
    if branch and branch not in ["main", "master", "develop"]:
        if not re.match(BRANCH_PATTERN, branch):
            errors.append(
                f"❌ Invalid branch name: {branch}\n"
                f"   Must follow pattern: {{type}}/{PROJECT_KEY}-{{number}}-{{description}}\n"
                f"   Example: feature/{PROJECT_KEY}-123-implement-nearest-neighbor"
            )
    
    # Validate commit message
    commit_msg = get_commit_message()
    if commit_msg:
        if not re.match(COMMIT_PATTERN, commit_msg.split('\n')[0]):
            errors.append(
                f"❌ Invalid commit message: {commit_msg.split(chr(10))[0]}\n"
                f"   Must start with: {PROJECT_KEY}-{{number}}:\n"
                f"   Example: {PROJECT_KEY}-123: Implement CuPy backend for distance provider"
            )
    
    return errors

if __name__ == "__main__":
    errors = validate_jira_integration()
    if errors:
        print("JIRA integration validation failed:")
        for error in errors:
            print(error)
        sys.exit(1)
    print("✅ JIRA integration validation passed")
```

## CI/CD PIPELINE CONFIGURATION

### GitHub Actions Workflow (.github/workflows/quality-validation.yml)

```yaml
name: Quality Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pre-commit pytest black isort flake8 mypy
          
      - name: Validate repository structure
        run: python scripts/validate_structure.py
        
      - name: Validate naming conventions
        run: python scripts/validate_naming.py
        
      - name: Run pre-commit hooks
        run: pre-commit run --all-files
        
      - name: Run tests
        run: pytest code/tests/ -v --cov=code/src/ --cov-report=xml
        
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## VS CODE INTEGRATION

### Settings Configuration (.vscode/settings.json)

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.sortImports.args": ["--profile", "black"],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "files.associations": {
    "*.md": "markdown"
  },
  "markdownlint.config": {
    "MD013": false,
    "MD033": false
  }
}
```

### Tasks Configuration (.vscode/tasks.json)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate Repository",
      "type": "shell",
      "command": "python",
      "args": ["scripts/validate_all.py"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest",
      "args": ["code/tests/", "-v", "--cov=code/src/"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    }
  ]
}
```

## ENFORCEMENT MECHANISMS

### Real-time Validation (File Watchers)

```python
#!/usr/bin/env python3
"""Real-time file validation using watchdog."""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ValidationHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.validate_file(Path(event.src_path))
    
    def validate_file(self, file_path):
        """Validate individual file."""
        # Run relevant validations based on file type
        pass

# Start file watcher
observer = Observer()
observer.schedule(ValidationHandler(), ".", recursive=True)
observer.start()
```

### Git Hooks Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running pre-commit validation..."
python scripts/validate_structure.py || exit 1
python scripts/validate_naming.py || exit 1
python scripts/validate_jira_integration.py || exit 1

echo "🧹 Running code formatting..."
black code/ || exit 1
isort code/ || exit 1

echo "🔍 Running linting..."
flake8 code/ || exit 1
mypy code/src/ || exit 1

echo "🧪 Running tests..."
pytest code/tests/ --cov=code/src/ --cov-fail-under=80 || exit 1

echo "✅ All validations passed!"
```

## QUALITY METRICS TRACKING

### Code Quality Dashboard

```python
#!/usr/bin/env python3
"""Generate quality metrics dashboard."""

import json
from pathlib import Path

def generate_quality_report():
    """Generate comprehensive quality report."""
    metrics = {
        "structure_compliance": validate_structure_score(),
        "naming_compliance": validate_naming_score(),
        "code_coverage": get_test_coverage(),
        "type_hint_coverage": get_type_hint_coverage(),
        "documentation_coverage": get_documentation_coverage(),
        "jira_integration_score": validate_jira_score()
    }
    
    with open("quality_report.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics
```

---

**These quality enforcement mechanisms are MANDATORY and automatically applied to all code and documentation changes.**
