# JIRA Integration API Documentation

> **Complete API Reference for JIRA Tools and Scripts**
>
> Technical documentation for developers working with the JIRA integration system, including sync tools, validation scripts, and automation components.

## Table of Contents

1. [API Overview](#api-overview)
2. [Core Modules](#core-modules)
3. [Sync Engine API](#sync-engine-api)
4. [Validation System API](#validation-system-api)
5. [Configuration Management](#configuration-management)
6. [Error Handling](#error-handling)
7. [Extension Framework](#extension-framework)
8. [Testing APIs](#testing-apis)

---

## API Overview

The JIRA integration system provides a comprehensive Python API for synchronizing, validating, and managing JIRA tasks within the academic research environment.

### Architecture Overview

```mermaid
C4Component
    title JIRA Integration System Components
    
    Container_Boundary(sync_engine, "Sync Engine") {
        Component(task_sync, "Task Synchronizer", "Core sync logic")
        Component(data_manager, "Data Manager", "JIRA data operations")
        Component(diagram_gen, "Diagram Generator", "Mermaid visualization")
    }
    
    Container_Boundary(validation_system, "Validation System") {
        Component(structure_validator, "Structure Validator", "Repository structure")
        Component(naming_validator, "Naming Validator", "Naming conventions")
        Component(academic_validator, "Academic Validator", "TCC standards")
        Component(jira_validator, "JIRA Validator", "Integration compliance")
    }
    
    Container_Boundary(config_system, "Configuration") {
        Component(config_manager, "Config Manager", "Settings management")
        Component(template_engine, "Template Engine", "Issue templates")
    }
    
    System_Ext(jira_api, "JIRA REST API", "External JIRA system")
    System_Ext(git_hooks, "Git Hooks", "Pre-commit integration")
    
    Rel(task_sync, data_manager, "Uses")
    Rel(task_sync, diagram_gen, "Generates")
    Rel(data_manager, jira_api, "Queries")
    Rel(validation_system, git_hooks, "Integrates with")
    Rel(config_manager, template_engine, "Configures")
```

### Core Dependencies

```python
# Required packages
import requests          # HTTP client for JIRA API
import yaml             # Configuration file parsing
import json             # Data serialization
import datetime         # Timestamp management
import typing           # Type annotations
import pathlib          # File system operations
import re               # Regular expressions
import logging          # Logging framework
```

## Core Modules

### JIRATaskSynchronizer

The main synchronization engine for JIRA tasks.

#### Class Definition

```python
class JIRATaskSynchronizer:
    """
    Advanced JIRA task synchronization with validation and reporting.
    
    Provides comprehensive task management including:
    - Bulk task operations
    - Validation and quality checks
    - Automated diagram generation
    - Progress tracking and reporting
    """
    
    def __init__(self, 
                 config_file: str = "jira_sync_config.ini",
                 mock_mode: bool = True,
                 validation_enabled: bool = True):
        """
        Initialize the JIRA synchronizer.
        
        Args:
            config_file: Path to configuration file
            mock_mode: Use mock data instead of live JIRA
            validation_enabled: Enable quality validation
        """
```

#### Core Methods

##### sync_tasks()

```python
def sync_tasks(self, 
               project_key: str = "PT",
               output_format: str = "json",
               include_diagrams: bool = True) -> Dict[str, Any]:
    """
    Synchronize JIRA tasks with local storage.
    
    Args:
        project_key: JIRA project identifier
        output_format: Output format (json, yaml, markdown)
        include_diagrams: Generate Mermaid diagrams
        
    Returns:
        Sync results with task data and metadata
        
    Raises:
        JIRAConnectionError: When JIRA API is unreachable
        ValidationError: When task validation fails
        ConfigurationError: When configuration is invalid
    """
```

##### get_tasks_by_status()

```python
def get_tasks_by_status(self, 
                       status: str,
                       assignee: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve tasks filtered by status and optional assignee.
    
    Args:
        status: Task status (e.g., "To Do", "In Progress", "Done")
        assignee: Optional assignee filter
        
    Returns:
        List of matching task dictionaries
    """
```

##### validate_task_quality()

```python
def validate_task_quality(self, issues: List[Dict]) -> List[str]:
    """
    Validate task quality against academic standards.
    
    Args:
        issues: List of JIRA issue dictionaries
        
    Returns:
        List of validation violations
    """
```

##### generate_progress_report()

```python
def generate_progress_report(self, 
                           format_type: str = "markdown") -> str:
    """
    Generate comprehensive progress report.
    
    Args:
        format_type: Report format (markdown, html, json)
        
    Returns:
        Formatted progress report
    """
```

#### Usage Examples

##### Basic Task Synchronization

```python
from jira.scripts.sync_jira_tasks_fixed import JIRATaskSynchronizer

# Initialize synchronizer
sync = JIRATaskSynchronizer(
    config_file="jira_sync_config.ini",
    mock_mode=True,
    validation_enabled=True
)

# Sync all tasks
results = sync.sync_tasks(
    project_key="PT",
    output_format="json",
    include_diagrams=True
)

print(f"Synced {len(results['tasks'])} tasks")
print(f"Validation violations: {len(results['violations'])}")
```

##### Filtered Task Retrieval

```python
# Get in-progress tasks
in_progress = sync.get_tasks_by_status("In Progress")
print(f"Tasks in progress: {len(in_progress)}")

# Get tasks assigned to specific user
user_tasks = sync.get_tasks_by_status("To Do", assignee="lucas.galdino")
print(f"User tasks: {len(user_tasks)}")
```

##### Quality Validation

```python
# Validate specific tasks
issues = sync.get_all_issues()
violations = sync.validate_task_quality(issues)

if violations:
    print("Quality violations found:")
    for violation in violations:
        print(f"  - {violation}")
else:
    print("All tasks meet quality standards")
```

### DataManager

Handles JIRA data operations and caching.

#### Class Definition

```python
class DataManager:
    """
    Manages JIRA data operations including caching and persistence.
    """
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize data manager.
        
        Args:
            cache_dir: Directory for caching data
            ttl_hours: Cache time-to-live in hours
        """
```

#### Key Methods

##### fetch_issues()

```python
def fetch_issues(self, 
                project_key: str,
                use_cache: bool = True,
                force_refresh: bool = False) -> List[Dict]:
    """
    Fetch issues from JIRA with intelligent caching.
    
    Args:
        project_key: JIRA project key
        use_cache: Use cached data if available
        force_refresh: Force fresh data from JIRA
        
    Returns:
        List of issue dictionaries
    """
```

##### cache_data()

```python
def cache_data(self, 
              key: str, 
              data: Any, 
              ttl_hours: Optional[int] = None) -> None:
    """
    Cache data with automatic expiration.
    
    Args:
        key: Cache key identifier
        data: Data to cache
        ttl_hours: Override default TTL
    """
```

## Sync Engine API

### Configuration Structure

```python
@dataclasses.dataclass
class SyncConfig:
    """Configuration for JIRA synchronization."""
    
    project_key: str = "PT"
    base_url: str = "https://company.atlassian.net"
    username: str = ""
    api_token: str = ""
    mock_mode: bool = True
    validation_enabled: bool = True
    output_directory: str = "output"
    diagram_generation: bool = True
    cache_ttl_hours: int = 24
    
    @classmethod
    def from_file(cls, config_path: str) -> 'SyncConfig':
        """Load configuration from INI file."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
```

### Task Data Model

```python
@dataclasses.dataclass
class TaskData:
    """Structured representation of a JIRA task."""
    
    key: str
    summary: str
    description: str
    status: str
    priority: str
    assignee: Optional[str]
    labels: List[str]
    parent: Optional[str]
    story_points: Optional[int]
    created: datetime.datetime
    updated: datetime.datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        
    def validate(self) -> List[str]:
        """Validate task data quality."""
```

### Sync Results

```python
@dataclasses.dataclass
class SyncResults:
    """Results from synchronization operation."""
    
    timestamp: datetime.datetime
    project_key: str
    total_tasks: int
    synced_tasks: int
    failed_tasks: int
    validation_violations: List[str]
    generated_files: List[str]
    execution_time: float
    
    def generate_summary(self) -> str:
        """Generate human-readable summary."""
```

## Validation System API

### Structure Validator

Validates repository structure compliance.

```python
class StructureValidator:
    """Validates repository directory structure."""
    
    REQUIRED_DIRECTORIES = {
        "code": {"required": True, "subdirs": ["src", "tests", "examples"]},
        "data": {"required": True},
        "documentation": {"required": True},
        "infrastructure": {"required": True},
        "knowledge_base": {"required": True},
        "project_management": {"required": True},
        "research": {"required": True}
    }
    
    def validate(self, root_path: str = ".") -> List[str]:
        """
        Validate directory structure.
        
        Args:
            root_path: Repository root path
            
        Returns:
            List of validation errors
        """
        
    def generate_structure_report(self) -> Dict[str, Any]:
        """Generate detailed structure report."""
```

### Naming Validator

Validates file and directory naming conventions.

```python
class NamingValidator:
    """Validates naming conventions across the repository."""
    
    NAMING_RULES = {
        "directories": r"^[a-z][a-z0-9_]*$",
        "python_files": r"^[a-z][a-z0-9_]*\.py$",
        "test_files": r"^(test_|_test\.py$|tests\.py$)",
        "config_files": r"^[a-z][a-z0-9-]*\.(yml|yaml|json|toml)$",
        "markdown_files": r"^([A-Z][A-Z0-9_]*\.md|[a-z][a-z0-9_]*\.md)$"
    }
    
    def validate_file(self, file_path: str) -> List[str]:
        """Validate single file naming."""
        
    def validate_directory(self, dir_path: str) -> List[str]:
        """Validate directory naming recursively."""
        
    def validate_all(self, root_path: str = ".") -> Dict[str, List[str]]:
        """Validate all files and directories."""
```

### Academic Standards Validator

Ensures compliance with TCC academic requirements.

```python
class AcademicValidator:
    """Validates academic standards compliance."""
    
    def validate_task_description(self, description: str) -> List[str]:
        """
        Validate task description against academic standards.
        
        Args:
            description: Task description text
            
        Returns:
            List of validation violations
        """
        
    def check_research_methodology(self, task_data: Dict) -> List[str]:
        """Validate research methodology documentation."""
        
    def validate_citation_format(self, text: str) -> List[str]:
        """Validate academic citation formats."""
        
    def generate_compliance_report(self, tasks: List[Dict]) -> Dict:
        """Generate comprehensive compliance report."""
```

### JIRA Integration Validator

Validates JIRA-specific integration requirements.

```python
class JIRAIntegrationValidator:
    """Validates JIRA integration compliance."""
    
    PROJECT_KEY = "PT"
    BRANCH_PATTERN = rf"^(feature|bugfix|research|docs)/{PROJECT_KEY}-\d+-.*$"
    COMMIT_PATTERN = rf"^{PROJECT_KEY}-\d+:.*$"
    
    def validate_branch_name(self, branch_name: str) -> List[str]:
        """Validate Git branch naming."""
        
    def validate_commit_message(self, commit_msg: str) -> List[str]:
        """Validate commit message format."""
        
    def validate_issue_links(self, issue_data: Dict) -> List[str]:
        """Validate issue parent-child relationships."""
```

## Configuration Management

### Configuration File Format

```ini
# jira_sync_config.ini

[JIRA]
base_url = https://company.atlassian.net
username = your_email@company.com
api_token = your_api_token
project_key = PT

[SYNC]
mock_mode = true
validation_enabled = true
output_directory = output
cache_ttl_hours = 24

[QUALITY]
min_description_length = 50
required_labels = true
enforce_parent_links = true
academic_standards = true

[OUTPUT]
format = json
include_diagrams = true
diagram_format = mermaid
generate_reports = true
```

### Configuration Loading

```python
class ConfigManager:
    """Manages configuration loading and validation."""
    
    def load_config(self, config_path: str) -> SyncConfig:
        """Load and validate configuration file."""
        
    def validate_config(self, config: SyncConfig) -> List[str]:
        """Validate configuration completeness."""
        
    def get_default_config(self) -> SyncConfig:
        """Get default configuration values."""
        
    def save_config(self, config: SyncConfig, path: str) -> None:
        """Save configuration to file."""
```

## Error Handling

### Exception Hierarchy

```python
class JIRAIntegrationError(Exception):
    """Base exception for JIRA integration errors."""
    pass

class JIRAConnectionError(JIRAIntegrationError):
    """JIRA API connection errors."""
    pass

class ValidationError(JIRAIntegrationError):
    """Task validation errors."""
    pass

class ConfigurationError(JIRAIntegrationError):
    """Configuration-related errors."""
    pass

class DataFormatError(JIRAIntegrationError):
    """Data format and parsing errors."""
    pass
```

### Error Context

```python
@dataclasses.dataclass
class ErrorContext:
    """Provides context for error handling."""
    
    operation: str
    timestamp: datetime.datetime
    task_key: Optional[str]
    details: Dict[str, Any]
    stack_trace: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
```

## Extension Framework

### Plugin Interface

```python
class JIRAPlugin:
    """Base class for JIRA integration plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        
    def before_sync(self, tasks: List[Dict]) -> List[Dict]:
        """Hook called before synchronization."""
        return tasks
        
    def after_sync(self, results: SyncResults) -> SyncResults:
        """Hook called after synchronization."""
        return results
        
    def validate_task(self, task: Dict) -> List[str]:
        """Custom task validation logic."""
        return []
```

### Built-in Plugins

#### Diagram Generator Plugin

```python
class DiagramGeneratorPlugin(JIRAPlugin):
    """Generates Mermaid diagrams from task data."""
    
    def generate_gantt_chart(self, tasks: List[Dict]) -> str:
        """Generate Gantt chart from task timeline."""
        
    def generate_dependency_graph(self, tasks: List[Dict]) -> str:
        """Generate task dependency flowchart."""
        
    def generate_progress_timeline(self, tasks: List[Dict]) -> str:
        """Generate progress timeline diagram."""
```

#### Academic Standards Plugin

```python
class AcademicStandardsPlugin(JIRAPlugin):
    """Enforces TCC academic standards."""
    
    def validate_research_methodology(self, task: Dict) -> List[str]:
        """Validate research methodology documentation."""
        
    def check_citation_requirements(self, description: str) -> List[str]:
        """Check academic citation requirements."""
        
    def generate_literature_map(self, tasks: List[Dict]) -> str:
        """Generate literature reference map."""
```

## Testing APIs

### Test Utilities

```python
class JIRATestHelper:
    """Utilities for testing JIRA integration."""
    
    @staticmethod
    def create_mock_issue(key: str, **kwargs) -> Dict[str, Any]:
        """Create mock JIRA issue for testing."""
        
    @staticmethod
    def create_test_config() -> SyncConfig:
        """Create test configuration."""
        
    @staticmethod
    def assert_validation_passes(violations: List[str]) -> None:
        """Assert that validation passes."""
        
    @staticmethod
    def assert_task_structure(task: Dict, required_fields: List[str]) -> None:
        """Assert task has required structure."""
```

### Mock Data Factory

```python
class MockDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_epic(phase: int) -> Dict[str, Any]:
        """Create mock epic for specified phase."""
        
    @staticmethod
    def create_story(epic_key: str, story_type: str) -> Dict[str, Any]:
        """Create mock story under epic."""
        
    @staticmethod
    def create_task(parent_key: str, task_type: str) -> Dict[str, Any]:
        """Create mock task under story."""
        
    @staticmethod
    def create_project_dataset(num_phases: int = 3) -> List[Dict[str, Any]]:
        """Create complete project dataset."""
```

### Integration Tests

```python
class IntegrationTestSuite:
    """Integration tests for JIRA synchronization."""
    
    def test_full_sync_cycle(self):
        """Test complete synchronization cycle."""
        
    def test_validation_pipeline(self):
        """Test validation pipeline."""
        
    def test_error_handling(self):
        """Test error handling scenarios."""
        
    def test_plugin_integration(self):
        """Test plugin system integration."""
```

---

## API Usage Examples

### Complete Workflow Example

```python
from jira.scripts.sync_jira_tasks_fixed import JIRATaskSynchronizer
from jira.scripts.validation import ValidationSuite

# Initialize components
sync = JIRATaskSynchronizer(mock_mode=True)
validator = ValidationSuite()

# Perform sync with validation
results = sync.sync_tasks(
    project_key="PT",
    output_format="json",
    include_diagrams=True
)

# Run quality validation
violations = validator.validate_all()

# Generate reports
if not violations:
    report = sync.generate_progress_report("markdown")
    print("Sync completed successfully")
    print(report)
else:
    print("Quality issues found:")
    for violation in violations:
        print(f"  - {violation}")
```

### Custom Plugin Development

```python
class CustomReportPlugin(JIRAPlugin):
    """Custom reporting plugin example."""
    
    def after_sync(self, results: SyncResults) -> SyncResults:
        """Generate custom reports after sync."""
        
        # Create custom visualization
        chart = self.create_burndown_chart(results.tasks)
        
        # Save to custom location
        output_path = f"reports/burndown_{results.timestamp}.svg"
        with open(output_path, "w") as f:
            f.write(chart)
            
        # Add to results
        results.generated_files.append(output_path)
        
        return results
    
    def create_burndown_chart(self, tasks: List[Dict]) -> str:
        """Create burndown chart in SVG format."""
        # Implementation here
        pass
```

---

*This API documentation is automatically generated and validated. For the latest updates, refer to the source code and integration tests.*
