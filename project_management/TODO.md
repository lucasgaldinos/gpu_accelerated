---
title: To-Do List  
description: High-level project todo list that references detailed JIRA task management
tags: [project management, tasks, to-do]
---

# 📝 To-Do List

> **✅ JIRA Integration Complete**  
> **✅ Real JIRA API Integration Working**  
> **Detailed task management now handled in JIRA PT project and mirrored in [TASKS.md](./tasks/TASKS.md)**  
> **JIRA Board:** <https://this-shall-not-be-taken.atlassian.net/jira/software/projects/PT/boards/67>

## Overview

This TODO list provides high-level project milestones. Detailed task breakdowns, assignments, and tracking are managed in JIRA and synchronized with the local [TASKS.md](./tasks/TASKS.md) file using **real JIRA API integration**.

## 🎉 MAJOR MILESTONE ACHIEVED

**JIRA-Local Task Synchronization Implementation Complete** - PT-11 ✅

Successfully implemented complete JIRA integration with:

- ✅ Real JIRA API connectivity using MCP Atlassian tools
- ✅ Automated synchronization between JIRA and local TASKS.md
- ✅ 14 properly structured issues with complete hierarchy
- ✅ Working sync script with dry-run and verbose options
- ✅ Real-time task data from live JIRA project

## JIRA Project Structure (Live Data)

- **PT-1** (Epic): Phase-0 - Project Foundation (6 child tasks) ✅ **LIVE IN JIRA**
- **PT-2** (Epic): Phase-1 - Core Development (3 child tasks) ✅ **LIVE IN JIRA**
- **PT-3** (Task): Current Development Work ✅ **LIVE IN JIRA**  
- **PT-4** (Epic): Phase-2 - Advanced Features ✅ **LIVE IN JIRA**
- **PT-11** (Task): JIRA Integration - Status: **DONE** ✅ **COMPLETED**

## High-Level Milestones

### ✅ Completed

- [x] Repository organization and structure validation
- [x] Naming convention enforcement (snake_case/kebab-case)
- [x] JIRA project setup and task creation
- [x] **Real JIRA API integration implementation** ✅ **NEW**
- [x] **Task management system with live synchronization** ✅ **NEW**
- [x] **Local TASKS.md with real JIRA data** ✅ **NEW**

### 🚧 In Progress (PT Sprint 1: Sep 18-25, 2025)

- [ ] **Workspace organization** → **PT-5** ✅ **IN JIRA**
  - Codebase analysis and documentation
  - Knowledge base population
  - Development workflow documentation

- [ ] **Task breakdown framework** → **PT-6** ✅ **IN JIRA**
  - Research methodologies
  - Create framework documentation
  - Implement in JIRA with proper hierarchies

- [ ] **Task management system** → **PT-7** ✅ **IN JIRA**
  - JIRA-local synchronization
  - Automated sync scripts
  - Task templates and workflows

### 📋 Phase-1 Tasks (PT-2 Epic)

- [ ] **Documentation standards** → **PT-8** ✅ **IN JIRA**
  - Academic writing standards
  - Code documentation requirements
  - Template creation

- [ ] **Testing framework** → **PT-9** ✅ **IN JIRA**
  - Unit and integration testing
  - Performance benchmarking
  - GPU vs CPU comparison testing

- [ ] **CI/CD pipeline** → **PT-10** ✅ **IN JIRA**
  - GitHub Actions workflows
  - Automated testing and quality checks
  - Deployment automation

### 🔮 Future Planning

- [ ] Academic integration methodology
- [ ] VS Code integration optimization
- [ ] Project timeline and milestones in JIRA
- [ ] Code review process establishment
- [ ] Research methodology validation

## Task Management Workflow

1. **High-level planning**: This TODO.md file
2. **Detailed task management**: JIRA PT project
3. **Local mirror**: [TASKS.md](./tasks/TASKS.md) (auto-synced)
4. **Development tracking**: Git commits linked to JIRA issues

## Quick Links

- 🎯 **JIRA Board**: <https://this-shall-not-be-taken.atlassian.net/jira/software/projects/PT/boards/67>
- 📋 **Local Tasks**: [TASKS.md](./tasks/TASKS.md)
- 🛠️ **Validation Scripts**: `scripts/validate_structure.py`, `scripts/validate_naming.py`
- 📚 **JIRA Templates**: `jira_templates/`

## Usage Notes

- ✅ Mark items complete here when JIRA Epic/Story is finished
- 🔗 All detailed work tracked in JIRA with proper fields
- 🔄 TASKS.md file automatically synchronized with JIRA
- 📊 Use JIRA for progress tracking, estimates, and sprint planning
    │   │       ├── np_convertion.ipynb
    │   │       ├── requirements_core.txt
    │   │       ├── src
    │   │       │   ├── algorithms
    │   │       │   │   ├── base_solver.py
    │   │       │   │   ├── **init**.py
    │   │       │   │   ├── nearest_neighbor.py
    │   │       │   │   ├── **pycache**
    │   │       │   │   │   ├── **init**.cpython-310.pyc
    │   │       │   │   │   └── tsp_algorithms.cpython-310.pyc
    │   │       │   │   └── tsp_algorithms.py
    │   │       │   ├── api
    │   │       │   │   └── protocols.py
    │   │       │   ├── backends
    │   │       │   │   ├── calc_backends
    │   │       │   │   │   ├── cupy_provider.py
    │   │       │   │   │   ├── distance_formulas_new.py
    │   │       │   │   │   ├── distance_formulas.py
    │   │       │   │   │   ├── distance_provider.py
    │   │       │   │   │   ├── explicit_provider.py
    │   │       │   │   │   ├── **init**.py
    │   │       │   │   │   ├── numpy_provider.py
    │   │       │   │   │   └── provider_factory.py
    │   │       │   │   ├── calc_backends2
    │   │       │   │   │   └── distance_formulas.py
    │   │       │   │   ├── computational_backend.py
    │   │       │   │   ├── **init**.py
    │   │       │   │   ├── parsed_problem.py
    │   │       │   │   ├── **pycache**
    │   │       │   │   │   ├── computational_backend.cpython-310.pyc
    │   │       │   │   │   └── **init**.cpython-310.pyc
    │   │       │   │   └── tsplib95
    │   │       │   │       ├── bisep.py
    │   │       │   │       ├── cli.py
    │   │       │   │       ├── distances.py
    │   │       │   │       ├── exceptions.py
    │   │       │   │       ├── fields.py
    │   │       │   │       ├── **init**.py
    │   │       │   │       ├── loaders.py
    │   │       │   │       ├── matrix.py
    │   │       │   │       ├── models.py
    │   │       │   │       ├── transformers.py
    │   │       │   │       └── utils.py
    │   │       │   ├── demo.py
    │   │       │   ├── example_run.py
    │   │       │   ├── parser.py
    │   │       │   ├── prototype.ipynb
    │   │       │   ├── prototype.py
    │   │       │   ├── **pycache**
    │   │       │   │   └── parser.cpython-310.pyc
    │   │       │   └── solver_facade.py
    │   │       ├── system_design.ipynb
    │   │       └── tests
    │   │           ├── **init**.py
    │   │           ├── **pycache**
    │   │           │   ├── **init**.cpython-310.pyc
    │   │           │   └── test_algorithms.cpython-310-pytest-8.4.2.pyc
    │   │           └── test_algorithms.py
    │   ├── reports
    │   └── user_guides
    ├── .github
    │   ├── chatmodes
    │   │   ├── api-developer.chatmode.md
    │   │   ├── beastmode-3.1.chatmode.md
    │   │   └── gpu-tsp-developer.chatmode.md
    │   ├── .docs
    │   │   ├── associacao-brasileira-de-normas-tecnicas-numerico.csl
    │   │   ├── critical_analysis.md
    │   │   ├── criticas_analysis_bib.md
    │   │   ├── pandoc_reference_for_md_citation.md
    │   │   └── pandoc_reference.md
    │   ├── instructions
    │   │   ├── 00_project_overview.instructions.md
    │   │   ├── 01_development_workflow.instructions.md
    │   │   ├── 02_multi_backend_architecture.instructions.md
    │   │   ├── 03_academic_integration.instructions.md
    │   │   ├── 04_behavior_directives.instructions.md
    │   │   ├── CUSTOM_INSTRUCTIONS_GUIDE.md
    │   │   ├── DEVELOPMENT_METHODOLOGY.instructions.md
    │   │   ├── LEGACY_CODE_NOTICE.instructions.md
    │   │   ├── QUALITY_STANDARDS.instructions.md
    │   │   ├── README.md
    │   │   ├── TASK_BREAKDOWN_FRAMEWORK.instructions.md
    │   │   ├── TEACHING_METHODOLOGY.instructions.md
    │   │   ├── tools
    │   │   │   └── pylint.instructions.md
    │   │   └── WORKSPACE_ORGANIZATION.instructions.md
    │   ├── ISSUE_TEMPLATE
    │   │   ├── documentation_task.md
    │   │   ├── implementation_task.md
    │   │   ├── learning_task.md
    │   │   ├── research_task.md
    │   │   └── setup_task.md
    │   ├── .knowledge_base -> /home/lucas_galdino/Documents/StudiesVault_v2/AI-knowledge-base/main-knowledge-base
    │   ├── prompts
    │   │   ├── data-analysis.prompt.md
    │   │   ├── generate-plan.prompt.md
    │   │   ├── main-project-2.prompt.md
    │   │   ├── my_prompts.md
    │   │   ├── research.md
    │   │   ├── sequential_thinking_behavior.prompt.md
    │   │   ├── sequential_tool_selection-main-project-TODO.prompt.md
    │   │   ├── side-prompts-compilation.md
    │   │   ├── system-analysis.prompt.md
    │   │   ├── vscode_copilot_knowledge_base_creation_enhanced.prompt.md
    │   │   ├── vscode_copilot_knowledge_base_creation-human.prompt.md
    │   │   ├── vscode_copilot_knowledge_base_creation.prompt.md
    │   │   └── vscode_copilot_knowledge_base_creation-simple.prompt.md
    │   └── README_COPILOT.md
    ├── .gitignore
    ├── INFRASTRUCTURE
    │   ├── ci_cd
    │   ├── containers
    │   ├── environments
    │   ├── monitoring
    │   └── security
    ├── KNOWLEDGE_BASE
    │   ├── EDUCATIONAL_IMPLEMENTATION_PLAN.md
    │   ├── learning_materials
    │   ├── methodology
    │   ├── PROJECT_STRUCTURE_DESIGN.md
    │   ├── README.md
    │   ├── research_context
    │   ├── TEACHING_ORIENTED_REBUILD_SPECIFICATION.md
    │   └── technical_decisions
    ├── PROJECT_MANAGEMENT
    │   ├── github_integration
    │   ├── planning
    │   ├── progress
    │   ├── README.md
    │   ├── TASK_BREAKDOWN_FRAMEWORK.md
    │   ├── tasks
    │   ├── TASKS.md
    │   ├── TEACHING_ORIENTED_REBUILD_SPECIFICATION.md
    │   └── TODO.md
    ├── pyproject.toml
    ├── .pytest_cache
    │   ├── CACHEDIR.TAG
    │   ├── .gitignore
    │   ├── README.md
    │   └── v
    │       └── cache
    │           ├── lastfailed
    │           ├── nodeids
    │           └── stepwise
    ├── .python-version
    ├── README.md
    ├── remove_empty_md.sh
    ├── RESEARCH
    │   ├── datasets
    │   ├── experiments
    │   ├── methodology
    │   ├── publications
    │   ├── README.md
    │   └── results
    └── .vscode
        └── settings.json
    ```

    1. #search for documents that might help you from [knowledge base](../.github/.knowledge_base)
    2. Copy the relevant material to our own [knowledge base](../KNOWLEDGE_BASE)
    3. Any file that might be useful shall be copied (in bulk: e.g. it's faster to copy a folder than file by file and then remove noise after)

    Currently it's kinda messy, need to:

  - enforce snake_case for files and folders
  - enforce kebab-case for git branches
  - enforce python good practices and standards

  - read the current `.github` folder and:
      1. research [knowledge base](../.github/.knowledge_base)

      1. create relevant to the workspace proper:
         - prompts (look for prompt engineering best practices)
         - chatmodes (look for chatmode best practices)
         - workflows (#websearch about workflow tools)
         - instructions (look for instruction best practices)

- [ ] task breakdown framework - here and then JIRA <a id="jira-setup"></a>
  - research about task breakdown methodologies
  - create our own framework based on the research and our needs
  - document it here and in the instructions folder in `.github`
  - implement it in JIRA

  - Proper task management:
    - create [epics], [tasks, stories, bugs] and [subtasks] in JIRA as needed.
   All tasks should have their fields filled properly in JIRA, including:

    ```md Jira-task-requirements-list.md
    - Summary
        Required
    - Priority
        Required
    - Description
    - Acceptance criteria
        Required
    - Reporter
        Always me
    - Assignee
        Always me
    - Labels
        Required
    - Parent
        Correctly assigned to the epic or task
    - Start date
    - Due date
    - Sprint
    - Story point estimate
    - Original estimate
    - Time tracking
    ```
  - jira has an mcp that will help you manage tasks and projects.

- [ ] task management system
- [ ] academic integration (?)
- [ ] documentation standards
- [ ] VS Code integration (?)
- [ ] project timeline and milestones in JIRA
- [ ] testing framework
- [ ] CI/CD pipeline setup
- [ ] deployment strategy
- [ ] code review process
