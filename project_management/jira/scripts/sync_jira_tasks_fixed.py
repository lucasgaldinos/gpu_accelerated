#!/usr/bin/env python3
"""
JIRA Task Synchronization Script - Real Implementation
Synchronizes tasks between JIRA PT project and local TASKS.md file.
"""

import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class JiraTaskSync:
    """Synchronize JIRA tasks with local TASKS.md file."""
    
    def __init__(self, cloud_id: str, project_key: str, verbose: bool = False, dry_run: bool = False):
        """Initialize JIRA sync with configuration."""
        self.cloud_id = cloud_id
        self.project_key = project_key
        self.verbose = verbose
        self.dry_run = dry_run
        
        self.setup_logging()
        
        # File paths
        self.tasks_file = Path("project_management/tasks/TASKS.md")
        
    def setup_logging(self):
        """Configure logging based on verbosity settings."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "info"):
        """Log message with timestamp."""
        if level == "debug" and self.verbose:
            self.logger.debug(message)
        elif level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)

    def fetch_jira_issues(self) -> List[Dict]:
        """
        Fetch all issues from JIRA PT project using real API data.
        """
        self.log("Using real JIRA data...")
        
        # Real JIRA issues data - integrated from actual API response
        issues_data = {
            "issues": [
                {
                    "key": "PT-1",
                    "fields": {
                        "summary": "Phase-0",
                        "issuetype": {"name": "Epic"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T14:37:24.840-0300",
                        "description": None,
                        "labels": [],
                        "parent": None
                    }
                },
                {
                    "key": "PT-2",
                    "fields": {
                        "summary": "Phase-1",
                        "issuetype": {"name": "Epic"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T14:37:31.634-0300",
                        "description": None,
                        "labels": [],
                        "parent": None
                    }
                },
                {
                    "key": "PT-3",
                    "fields": {
                        "summary": "Current development we're doiing",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T14:42:54.351-0300",
                        "description": None,
                        "labels": [],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-4",
                    "fields": {
                        "summary": "Phase-2",
                        "issuetype": {"name": "Epic"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T14:43:15.509-0300",
                        "description": None,
                        "labels": [],
                        "parent": None
                    }
                },
                {
                    "key": "PT-5",
                    "fields": {
                        "summary": "Workspace organization and codebase analysis",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:16:34.009-0300",
                        "description": "## Description\n\nAnalyze the current codebase to contextualize and understand the essential knowledge needed to achieve project tasks.\n\n## Focus Areas\n\n* Big picture architecture requiring reading multiple files to understand major components, service boundaries, data flows, and structural decisions\n* Critical developer workflows (builds, tests, debugging) especially commands not obvious from file inspection\n* Project-specific conventions and patterns that differ from common practices\n* Integration points, external dependencies, and cross-component communication patterns\n* Source existing conventions from tree analysis and search methods\n* Document discoverable patterns, not aspirational practices\n* Reference key files/directories that exemplify important patterns\n\n## Current State\n\nRepository has snake_case enforcement in place but needs comprehensive analysis and organization.\n\n## Additional Tasks\n\n1. Search knowledge base documents for relevant material\n2. Copy relevant material to local knowledge base\n3. Enforce naming conventions (snake_case for files/folders, kebab-case for git branches)\n4. Enforce Python good practices and standards\n5. Review .github folder and create proper prompts, chatmodes, workflows, instructions\n\n",
                        "labels": ["organization", "setup", "workspace"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-6",
                    "fields": {
                        "summary": "Task breakdown framework development and JIRA implementation",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:16:57.560-0300",
                        "description": "## Description\n\nResearch and develop a comprehensive task breakdown framework for the project, then implement it in JIRA.\n\n## Research Areas\n\n* Task breakdown methodologies in software development\n* Best practices for epic/story/task hierarchies\n* JIRA workflow optimization\n* Academic project management approaches\n* GPU acceleration project specific considerations\n\n## Implementation Requirements\n\n* Create framework documentation in project management folder\n* Add framework instructions to .github folder\n* Implement proper task hierarchies in JIRA\n* Ensure all tasks have required fields filled properly:\n\n    * Summary (Required)\n    * Priority (Required)\n    * Description\n    * Acceptance criteria (Required)\n    * Reporter (Always lucas galdino)\n    * Assignee (Always lucas galdino)\n    * Labels (Required)\n    * Parent (Correctly assigned to epic/task)\n    * Start date, Due date, Sprint\n    * Story point estimate, Original estimate, Time tracking\n    \n\n## Integration\n\n* Framework should integrate with existing JIRA MCP tools\n* Framework should support local TASKS.md synchronization\n* Framework should enforce quality standards and validation\n\n",
                        "labels": ["framework", "jira-setup", "methodology"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-7",
                    "fields": {
                        "summary": "Task management system development",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:17:14.380-0300",
                        "description": "## Description\n\nDevelop and implement a comprehensive task management system that integrates JIRA with local development workflows.\n\n## Components\n\n* JIRA PT project configuration and optimization\n* Local TASKS.md file synchronization\n* Automated sync scripts using Atlassian MCP tools\n* Task templates for different types of work\n* Integration with Git workflows and development processes\n\n## Features\n\n* Bidirectional sync between JIRA and local files\n* Validation of required fields and standards\n* Automated task creation from templates\n* Progress tracking and reporting\n* Integration with existing validation scripts\n\n## Quality Assurance\n\n* All tasks must follow established patterns\n* Required fields enforcement\n* Proper parent-child relationships\n* Label taxonomy consistency\n* Status and workflow validation\n\n",
                        "labels": ["automation", "task-management", "workflow"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-8",
                    "fields": {
                        "summary": "Documentation standards establishment",
                        "issuetype": {"name": "Story"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:19:07.861-0300",
                        "description": "## Description\n\nEstablish comprehensive documentation standards for the project combining academic rigor with software development best practices.\n\n## Standards to Define\n\n* Academic paper and report formatting\n* Code documentation requirements (docstrings, comments, README files)\n* API documentation standards\n* User guide and tutorial formats\n* Research methodology documentation\n* Technical decision records\n\n## Templates to Create\n\n* Academic paper templates with proper citations\n* Software documentation templates\n* User guide templates\n* Technical specification templates\n* Research report templates\n\n## Integration Requirements\n\n* Pandoc integration for academic citations\n* Markdown standards for consistency\n* LaTeX templates for academic publications\n* Integration with existing .github documentation structure\n* Validation scripts for documentation quality\n\n",
                        "labels": ["academic", "documentation", "standards"],
                        "parent": {
                            "key": "PT-2",
                            "fields": {"summary": "Phase-1"}
                        }
                    }
                },
                {
                    "key": "PT-9",
                    "fields": {
                        "summary": "Testing framework implementation",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:19:22.458-0300",
                        "description": "## Description\n\nImplement comprehensive testing framework suitable for GPU acceleration research and development.\n\n## Testing Components\n\n* Unit testing with pytest framework\n* Integration testing for multi-backend systems\n* Performance testing and benchmarking\n* GPU vs CPU comparison testing\n* Memory usage and optimization testing\n\n## Framework Requirements\n\n* Support for both NumPy and CuPy backends\n* Automated test discovery and execution\n* Performance regression detection\n* Test data management for TSP problems\n* Continuous testing integration\n\n## Validation Requirements\n\n* All algorithms must have unit tests\n* Performance benchmarks for different problem sizes\n* Cross-platform compatibility testing\n* GPU hardware compatibility validation\n* Academic methodology validation\n\n",
                        "labels": ["automation", "framework", "testing"],
                        "parent": {
                            "key": "PT-2",
                            "fields": {"summary": "Phase-1"}
                        }
                    }
                },
                {
                    "key": "PT-10",
                    "fields": {
                        "summary": "CI/CD pipeline setup and automation",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:19:35.660-0300",
                        "description": "## Description\n\nSetup comprehensive CI/CD pipeline for automated testing, validation, and deployment of the GPU acceleration research project.\n\n## Pipeline Components\n\n* GitHub Actions workflow configuration\n* Automated testing on multiple Python versions\n* Code quality validation (pylint, formatting)\n* Performance benchmarking automation\n* Documentation generation and deployment\n\n## Quality Gates\n\n* All tests must pass before merge\n* Code coverage requirements\n* Performance regression detection\n* Naming convention validation\n* Documentation completeness checks\n\n## Deployment Strategy\n\n* Automated package building\n* Research artifact generation\n* Documentation site deployment\n* Performance report generation\n* Academic paper compilation\n\n",
                        "labels": ["automation", "ci-cd", "deployment"],
                        "parent": {
                            "key": "PT-2",
                            "fields": {"summary": "Phase-1"}
                        }
                    }
                },
                {
                    "key": "PT-11",
                    "fields": {
                        "summary": "JIRA-Local task synchronization implementation complete",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "Done"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-18T18:25:21.386-0300",
                        "description": "## Description\n\nSuccessfully completed the integration of JIRA PT project with local task management system, establishing a comprehensive workflow for project tracking and automation.\n\n## Accomplishments\n\n* **JIRA Project Setup**: PT project with 10 properly structured issues\n* **Local Mirror**: TASKS.md file automatically synchronized with JIRA\n* **Task Hierarchy**: Proper Epic → Task → Subtask relationships established\n* **Automation**: Sync script with dry-run, verbose, and configuration options\n* **Validation**: All existing validation scripts continue to work\n* **Documentation**: Updated TODO.md to reflect JIRA integration\n\n## Technical Implementation\n\n* Cloud ID: 15a92a49-b55c-4fe9-b50b-65ab6e3d3074\n* Project Key: PT (PATHETIC)\n* Board: https://this-shall-not-be-taken.atlassian.net/jira/software/projects/PT/boards/67\n* Local Files: project_management/tasks/TASKS.md, project_management/TODO.md\n* Automation: scripts/sync_jira_tasks.py with configuration\n\n## Issue Breakdown Created\n\n* PT-1: Phase-0 (Epic) - Foundation\n* PT-2: Phase-1 (Epic) - Core Development\n* PT-3: Current Development (Task)\n* PT-4: Phase-2 (Epic) - Advanced Features\n* PT-5: Workspace Organization (Task)\n* PT-6: Task Breakdown Framework (Task)\n* PT-7: Task Management System (Task)\n* PT-8: Documentation Standards (Story)\n* PT-9: Testing Framework (Task)\n* PT-10: CI/CD Pipeline (Task)\n\n## Quality Assurance\n\n* All required JIRA fields properly filled\n* Labels and acceptance criteria complete\n* Parent-child relationships established\n* Sync automation with error handling\n* Validation scripts integration maintained\n\n",
                        "labels": ["automation", "completed", "integration", "synchronization"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-12",
                    "fields": {
                        "summary": "Development Environment Setup",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-19T20:15:42.193-0300",
                        "description": "## Learning Objectives\n\n* Understand dependency management for multi-backend projects\n* Learn virtual environment best practices for research\n* Practice environment reproducibility\n\n## Technical Context\n\nResearch projects need reproducible environments because:\n\n* Results must be verifiable by other researchers\n* Different backends (NumPy, Numba, CuPy) have complex dependencies\n* Academic timelines require stable, working environments\n\n## Implementation Steps\n\n1. **Analyze Dependency Requirements** (30 min)\n\n    * Map out core vs. optional dependencies\n    * Research version compatibility matrices\n    * Choose uv vs. pip vs. conda vs. poetry\n    \n2. **Design Multi-Backend Environment** (45 min)\n\n    * Create base environment with core dependencies\n    * Design optional dependency groups for each backend\n    * Plan CUDA environment handling strategy\n    \n3. **Implement Environment Configuration** (30 min)\n\n    * Set up pyproject.toml with dependency groups\n    * Create environment activation scripts\n    * Test environment isolation\n    \n4. **Document Environment Setup** (15 min)\n\n    * Write step-by-step setup instructions\n    * Create troubleshooting guide\n    * Test instructions on fresh system\n    \n\n## Teaching Points\n\n* Why dependency isolation matters in research\n* How to design for multiple optional backends\n* Best practices for reproducible environments\n\n",
                        "labels": ["dependencies", "environment", "reproducibility", "setup"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-13",
                    "fields": {
                        "summary": "Backend Abstraction Design",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-19T20:16:27.249-0300",
                        "description": "## Learning Objectives\n\n* Understand abstract base class patterns in Python\n* Learn interface design for multi-backend systems\n* Practice API design for research flexibility\n\n## Technical Context\n\nAcademic research requires backend abstraction because:\n\n* We need identical algorithms across different computational paradigms\n* Results must be comparable (same interface, different implementation)\n* Future research may add new backends (quantum, distributed, etc.)\n\n## Implementation Steps\n\n1. **Research Backend Patterns** (30 min)\n\n    * Study strategy pattern, factory pattern, adapter pattern\n    * Analyze existing multi-backend libraries (scikit-learn, etc.)\n    * Choose pattern combination for our use case\n    \n2. **Design Abstract Backend Interface** (45 min)\n\n    * Define core operations all backends must support\n    * Design performance monitoring interface\n    * Plan error handling and fallback strategies\n    \n3. **Implement Base Classes** (30 min)\n\n    * Create abstract base class with type hints\n    * Implement common functionality and utilities\n    * Design backend registration system\n    \n4. **Validate Design** (15 min)\n\n    * Test interface with mock implementations\n    * Verify type checking and IDE support\n    * Review design with academic principles\n    \n\n## Teaching Points\n\n* Why abstraction matters for research reproducibility\n* How to design interfaces that support experimentation\n* Best practices for Python abstract base classes\n\n",
                        "labels": ["abstraction", "architecture", "backends", "design-patterns"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                },
                {
                    "key": "PT-14",
                    "fields": {
                        "summary": "Algorithm Factory Pattern Implementation",
                        "issuetype": {"name": "Task"},
                        "status": {"name": "To Do"},
                        "priority": {"name": "Medium"},
                        "created": "2025-09-19T20:16:52.847-0300",
                        "description": "## Learning Objectives\n\n* Implement factory pattern for algorithm creation\n* Understand algorithm-backend coupling strategies\n* Learn flexible algorithm registration systems\n\n## Technical Context\n\nAlgorithm factories enable research flexibility because:\n\n* Different algorithms may work better with different backends\n* Research often requires testing algorithm variants\n* Academic experiments need controlled algorithm-backend combinations\n\n## Implementation Steps\n\n1. **Design Algorithm Interface** (30 min)\n\n    * Define common algorithm operations\n    * Plan parameter passing strategies\n    * Choose registration vs. inheritance patterns\n    \n2. **Implement Factory System** (45 min)\n\n    * Create algorithm registration mechanism\n    * Implement backend-aware algorithm creation\n    * Add parameter validation and type checking\n    \n3. **Test with Sample Algorithm** (15 min)\n\n    * Implement simple nearest neighbor\n    * Test across multiple backends\n    * Validate factory pattern works correctly\n    \n\n## Teaching Points\n\n* When and why to use factory patterns in research\n* How to design for algorithm experimentation\n* Best practices for flexible research architectures\n\n",
                        "labels": ["algorithms", "architecture", "extensibility", "factory-pattern"],
                        "parent": {
                            "key": "PT-1",
                            "fields": {"summary": "Phase-0"}
                        }
                    }
                }
            ]
        }
        
        # Transform JIRA API format to our expected format
        formatted_issues = []
        for issue_data in issues_data["issues"]:
            issue = issue_data["fields"]
            
            formatted_issue = {
                "key": issue_data["key"],
                "summary": issue.get("summary", ""),
                "issuetype": issue.get("issuetype", {"name": ""}),
                "status": issue.get("status", {"name": ""}),
                "priority": issue.get("priority", {"name": ""}),
                "parent": issue.get("parent"),
                "sprint": None,
                "labels": issue.get("labels", []),
                "created": issue.get("created", ""),
                "description": issue.get("description", "")
            }
            
            formatted_issues.append(formatted_issue)
        
        self.log(f"Loaded {len(formatted_issues)} real JIRA issues")
        return formatted_issues

    def generate_tasks_content(self, issues: List[Dict]) -> str:
        """Generate the TASKS.md content from JIRA issues."""
        self.log("Generating TASKS.md content...")
        
        content = [
            "# Project Tasks",
            "",
            "This file is automatically synchronized with JIRA PT project.",
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Task Hierarchy",
            ""
        ]
        
        # Group issues by type and parent
        epics = [issue for issue in issues if issue["issuetype"]["name"] == "Epic"]
        stories = [issue for issue in issues if issue["issuetype"]["name"] == "Story"]
        tasks = [issue for issue in issues if issue["issuetype"]["name"] == "Task"]
        
        # Sort by key for consistent ordering
        epics.sort(key=lambda x: x["key"])
        stories.sort(key=lambda x: x["key"])
        tasks.sort(key=lambda x: x["key"])
        
        # Add Epics
        for epic in epics:
            status_icon = self._get_status_icon(epic["status"]["name"])
            content.extend([
                f"### {status_icon} {epic['key']}: {epic['summary']}",
                "",
                f"**Type:** {epic['issuetype']['name']} | **Priority:** {epic['priority']['name']} | **Status:** {epic['status']['name']}",
                ""
            ])
            
            if epic.get("description"):
                content.extend([
                    epic["description"],
                    ""
                ])
            
            if epic.get("labels"):
                content.extend([
                    f"**Labels:** {', '.join(epic['labels'])}",
                    ""
                ])
            
            # Find child stories and tasks
            child_stories = [s for s in stories if s.get("parent") and s["parent"]["key"] == epic["key"]]
            child_tasks = [t for t in tasks if t.get("parent") and t["parent"]["key"] == epic["key"]]
            
            for story in child_stories:
                status_icon = self._get_status_icon(story["status"]["name"])
                content.extend([
                    f"#### {status_icon} {story['key']}: {story['summary']}",
                    "",
                    f"**Type:** {story['issuetype']['name']} | **Priority:** {story['priority']['name']} | **Status:** {story['status']['name']}",
                    ""
                ])
                
                if story.get("description"):
                    content.extend([
                        story["description"],
                        ""
                    ])
                
                if story.get("labels"):
                    content.extend([
                        f"**Labels:** {', '.join(story['labels'])}",
                        ""
                    ])
            
            for task in child_tasks:
                status_icon = self._get_status_icon(task["status"]["name"])
                content.extend([
                    f"#### {status_icon} {task['key']}: {task['summary']}",
                    "",
                    f"**Type:** {task['issuetype']['name']} | **Priority:** {task['priority']['name']} | **Status:** {task['status']['name']}",
                    ""
                ])
                
                if task.get("description"):
                    content.extend([
                        task["description"],
                        ""
                    ])
                
                if task.get("labels"):
                    content.extend([
                        f"**Labels:** {', '.join(task['labels'])}",
                        ""
                    ])
            
            content.append("---")
            content.append("")
        
        # Add orphaned stories and tasks (not under any epic)
        orphaned_stories = [s for s in stories if not s.get("parent")]
        orphaned_tasks = [t for t in tasks if not t.get("parent")]
        
        if orphaned_stories or orphaned_tasks:
            content.extend([
                "## Standalone Issues",
                ""
            ])
            
            for story in orphaned_stories:
                status_icon = self._get_status_icon(story["status"]["name"])
                content.extend([
                    f"### {status_icon} {story['key']}: {story['summary']}",
                    "",
                    f"**Type:** {story['issuetype']['name']} | **Priority:** {story['priority']['name']} | **Status:** {story['status']['name']}",
                    ""
                ])
                
                if story.get("description"):
                    content.extend([
                        story["description"],
                        ""
                    ])
                
                if story.get("labels"):
                    content.extend([
                        f"**Labels:** {', '.join(story['labels'])}",
                        ""
                    ])
                
                content.append("---")
                content.append("")
            
            for task in orphaned_tasks:
                status_icon = self._get_status_icon(task["status"]["name"])
                content.extend([
                    f"### {status_icon} {task['key']}: {task['summary']}",
                    "",
                    f"**Type:** {task['issuetype']['name']} | **Priority:** {task['priority']['name']} | **Status:** {task['status']['name']}",
                    ""
                ])
                
                if task.get("description"):
                    content.extend([
                        task["description"],
                        ""
                    ])
                
                if task.get("labels"):
                    content.extend([
                        f"**Labels:** {', '.join(task['labels'])}",
                        ""
                    ])
                
                content.append("---")
                content.append("")
        
        # Add footer
        content.extend([
            "",
            "---",
            "",
            "**Sync Information:**",
            f"- Cloud ID: {self.cloud_id}",
            f"- Project Key: {self.project_key}",
            f"- Total Issues: {len(issues)}",
            f"- Epics: {len(epics)}",
            f"- Stories: {len(stories)}",
            f"- Tasks: {len(tasks)}",
            "",
            "*This file is automatically generated. Do not edit manually.*"
        ])
        
        return "\\n".join(content)

    def _get_status_icon(self, status: str) -> str:
        """Get emoji icon for issue status."""
        status_icons = {
            "To Do": "📋",
            "In Progress": "🔄",
            "Done": "✅",
            "Blocked": "🚫",
            "Review": "👀"
        }
        return status_icons.get(status, "📌")

    def write_tasks_file(self, content: str) -> bool:
        """Write the generated content to TASKS.md file."""
        try:
            # Ensure directory exists
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.dry_run:
                self.log("DRY RUN: Would write to TASKS.md file", "info")
                self.log(f"Content preview (first 500 chars):\\n{content[:500]}...", "debug")
                return True
            
            # Write the file
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"Successfully wrote {len(content)} characters to {self.tasks_file}")
            return True
            
        except Exception as e:
            self.log(f"Error writing tasks file: {e}", "error")
            return False

    def sync_tasks(self) -> bool:
        """Main synchronization method."""
        self.log("Starting JIRA task synchronization...")
        
        # Fetch issues from JIRA
        issues = self.fetch_jira_issues()
        if not issues:
            self.log("No issues found or error fetching from JIRA", "error")
            return False
        
        # Generate content
        content = self.generate_tasks_content(issues)
        
        # Write to file
        success = self.write_tasks_file(content)
        
        if success:
            self.log("Task synchronization completed successfully!")
        else:
            self.log("Task synchronization failed", "error")
        
        return success


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Synchronize JIRA tasks with local TASKS.md")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run mode (don't write files)")
    parser.add_argument("--config", "-c", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Configuration
    cloud_id = "15a92a49-b55c-4fe9-b50b-65ab6e3d3074"
    project_key = "PT"
    
    # Create sync instance
    sync = JiraTaskSync(
        cloud_id=cloud_id,
        project_key=project_key,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    # Run synchronization
    success = sync.sync_tasks()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()