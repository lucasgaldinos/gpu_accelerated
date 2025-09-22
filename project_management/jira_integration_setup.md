---
title: "JIRA Integration Setup Guide for GPU-Accelerated TSP/VRP Project"
description: "Step-by-step guide for configuring JIRA with the task breakdown framework"
version: "1.0.0"
created: "2025-09-18"
updated: "2025-09-18"
status: "active"
methodology: ["JIRA-Configuration", "Project-Management-Setup"]
prerequisites: ["task-breakdown-framework", "atlassian-account"]
---

# JIRA Integration Setup Guide

## Overview

This guide provides the complete setup process for integrating JIRA with our GPU-Accelerated TSP/VRP optimization project using the task breakdown framework defined in our methodology.

## Prerequisites

1. **Atlassian Account**: Access to JIRA workspace
2. **MCP Integration**: Atlassian MCP tools configured in VS Code
3. **Project Framework**: Task breakdown framework documented
4. **Academic Requirements**: TCC standards and milestone alignment

## JIRA Project Configuration

### Step 1: Create Project

**Project Details**:

- **Project Name**: GPU-Accelerated TSP/VRP Optimization
- **Project Key**: TSPGPU
- **Project Type**: Software Development (Scrum/Kanban hybrid)
- **Description**: Academic research project implementing GPU-accelerated algorithms for TSP and VRP optimization with teaching-oriented methodology

### Step 2: Configure Issue Types

#### Primary Issue Types

1. **Epic** (`Epic`)
   - **Purpose**: Major deliverable or project phase (4-8 weeks)
   - **Icon**: 📋
   - **Color**: Blue (#0052CC)

2. **Story** (`Story`)
   - **Purpose**: Functional component within an epic (1-2 weeks)
   - **Icon**: 📖
   - **Color**: Green (#36B37E)

3. **Technical Story** (`Technical Story`)
   - **Purpose**: Non-functional work (infrastructure, refactoring)
   - **Icon**: ⚙️
   - **Color**: Orange (#FF8B00)

4. **Task** (`Task`)
   - **Purpose**: Concrete work item (2-16 hours)
   - **Icon**: ✅
   - **Color**: Purple (#6554C0)

5. **Subtask** (`Sub-task`)
   - **Purpose**: Implementation detail (0.5-4 hours)
   - **Icon**: 🔸
   - **Color**: Gray (#97A0AF)

6. **Spike** (`Spike`)
   - **Purpose**: Research/investigation (time-boxed)
   - **Icon**: 🔍
   - **Color**: Yellow (#FFAB00)

7. **Bug** (`Bug`)
   - **Purpose**: Defect or issue resolution
   - **Icon**: 🐛
   - **Color**: Red (#DE350B)

### Step 3: Custom Fields Configuration

#### Academic Integration Fields

1. **Academic Phase** (Single Select)
   - Options: Foundation, Architecture, Implementation, Validation, Documentation
   - Required for: Epic, Story
   - Description: "TCC project phase alignment"

2. **Learning Objective** (Text Field - Multi-line)
   - Required for: Epic, Story, Spike
   - Description: "Educational goals and knowledge outcomes"

3. **RACI Matrix** (Multi-Select)
   - Options: Responsible, Accountable, Consulted, Informed
   - Required for: All issue types
   - Description: "Responsibility assignment matrix"

4. **Validation Method** (Single Select)
   - Options: Unit Tests, Integration Tests, Performance Benchmarks, Peer Review, Academic Review
   - Required for: Story, Technical Story
   - Description: "How completion will be validated"

#### Project-Specific Fields

5. **Backend Type** (Multi-Select)
   - Options: NumPy (CPU), Numba (JIT), CuPy (GPU), All Backends
   - Required for: Stories involving computation
   - Description: "Computational backend implementation"

6. **Algorithm Category** (Single Select)
   - Options: TSP, VRP, Optimization, Infrastructure, Documentation
   - Required for: Epic, Story
   - Description: "Primary algorithm or system category"

7. **Performance Target** (Text Field - Single line)
   - Format: "Target: X ops/sec, Memory: Y MB"
   - Required for: Performance-related stories
   - Description: "Specific performance benchmarks"

### Step 4: Workflow Configuration

#### Epic Workflow: `Epic Lifecycle`

```text
States:
- To Do (Initial state)
- In Progress (Active development)
- Under Review (Academic/technical review)
- Validation (Performance/quality validation)
- Done (Complete)
- Blocked (Impediment)

Transitions:
- To Do → In Progress: "Start Epic"
- In Progress → Under Review: "Submit for Review"
- Under Review → In Progress: "Return for Changes"
- Under Review → Validation: "Approve for Validation"
- Validation → In Progress: "Validation Failed"
- Validation → Done: "Complete Epic"
- Any State → Blocked: "Block Epic"
- Blocked → Previous State: "Unblock Epic"
```

#### Story Workflow: `Story Development`

```text
States:
- Backlog (Not ready for development)
- Ready (Ready for sprint)
- In Progress (Active development)
- Code Review (Peer review phase)
- Testing (Quality validation)
- Done (Complete)
- Blocked (Impediment)

Transitions:
- Backlog → Ready: "Story Ready"
- Ready → In Progress: "Start Development"
- In Progress → Code Review: "Submit for Review"
- Code Review → In Progress: "Changes Requested"
- Code Review → Testing: "Code Approved"
- Testing → In Progress: "Tests Failed"
- Testing → Done: "Tests Passed"
- Any State → Blocked: "Block Story"
- Blocked → Previous State: "Unblock Story"
```

#### Task Workflow: `Simple Task Flow`

```text
States:
- To Do (Not started)
- In Progress (Active work)
- Review (Validation/check)
- Done (Complete)

Transitions:
- To Do → In Progress: "Start Task"
- In Progress → Review: "Ready for Review"
- Review → In Progress: "Needs Changes"
- Review → Done: "Task Complete"
```

### Step 5: Sprint and Board Configuration

#### Board Setup

**Board Name**: GPU TSP/VRP Development
**Board Type**: Scrum
**Columns**:

1. Backlog
2. Ready
3. In Progress
4. Review
5. Testing
6. Done

**Swimlanes**:

- Epic (Group by Epic)
- Priority (Group by Priority)
- Academic Phase (Group by Academic Phase)

#### Sprint Configuration

**Sprint Length**: 2 weeks
**Sprint Goal Format**: "Academic Milestone: [Learning Objective] + Technical Goal: [Implementation Target]"

### Step 6: Priority and Labeling System

#### Priority Levels

1. **Critical**: Academic deadline dependencies, blocking issues
2. **High**: Core functionality, major milestones
3. **Medium**: Feature enhancements, optimization
4. **Low**: Nice-to-have, documentation improvements

#### Label Categories

**Academic Labels**:

- `tcc-milestone`
- `literature-review`
- `methodology`
- `validation-required`

**Technical Labels**:

- `performance-critical`
- `gpu-acceleration`
- `algorithm-implementation`
- `testing`
- `documentation`

**Backend Labels**:

- `numpy-backend`
- `numba-backend`
- `cupy-backend`
- `multi-backend`

## Initial Project Structure in JIRA

### Theme/Initiative Level

**Initiative**: GPU Acceleration Research for TSP/VRP Optimization

### Epic Structure

#### Epic 1: Foundation and Environment

- **TSPGPU-E01**: Development Environment and Tooling Setup
- **TSPGPU-E02**: Project Architecture and Design Patterns
- **TSPGPU-E03**: Testing Framework and Quality Standards

#### Epic 2: Core Algorithm Implementation  

- **TSPGPU-E04**: TSP Algorithm Implementation (Multi-Backend)
- **TSPGPU-E05**: VRP Algorithm Implementation (Multi-Backend)
- **TSPGPU-E06**: Performance Optimization and GPU Acceleration

#### Epic 3: Validation and Research

- **TSPGPU-E07**: Performance Benchmarking and Analysis
- **TSPGPU-E08**: Academic Validation and Literature Integration
- **TSPGPU-E09**: Research Documentation and Publication

### Example Story Structure (Epic 1)

**TSPGPU-S001**: As a developer, I want a configured development environment so that I can begin implementation work

- **Academic Phase**: Foundation
- **Learning Objective**: Understand project tooling and development workflow
- **RACI**: R=Student, A=Supervisor, C=Technical Advisor, I=Academic Committee
- **Story Points**: 5

**TSPGPU-S002**: As a researcher, I want project architecture documentation so that I understand system design decisions

- **Academic Phase**: Foundation  
- **Learning Objective**: Learn hexagonal architecture and separation of concerns
- **RACI**: R=Student, A=Supervisor, C=Technical Advisor, I=Academic Committee
- **Story Points**: 8

## Implementation Timeline

### Phase 1: JIRA Setup (Week 1)

- [ ] Create JIRA project with configuration above
- [ ] Set up custom fields and workflows
- [ ] Configure boards and sprints
- [ ] Import initial epic structure

### Phase 2: Team Integration (Week 2)

- [ ] Train team on JIRA workflows
- [ ] Test issue creation and transitions
- [ ] Validate academic milestone alignment
- [ ] Refine processes based on feedback

### Phase 3: Full Implementation (Week 3+)

- [ ] Create detailed story breakdown
- [ ] Begin sprint planning and execution
- [ ] Monitor metrics and adjust processes
- [ ] Regular retrospectives and improvements

## Integration with Academic Calendar

### TCC Milestone Alignment

**Semester 1 Milestones**:

- Week 4: Literature Review Complete
- Week 8: Architecture and Design Approved
- Week 12: Core Implementation Complete
- Week 16: Initial Validation Results

**JIRA Integration**:

- Epic due dates aligned with academic milestones
- Automated reports for academic progress
- Integration with academic calendar events

### Reporting and Documentation

**Weekly Reports**:

- Sprint progress and velocity
- Academic objective completion
- Blocker identification and resolution

**Monthly Academic Reports**:

- Epic progress against milestones
- Learning objective achievement
- Research methodology compliance

## Quality Assurance

### Definition of Ready Checklist

For all stories entering a sprint:

- [ ] Acceptance criteria clearly defined
- [ ] Academic objectives specified
- [ ] Dependencies identified and resolved
- [ ] Story points estimated
- [ ] RACI assignments complete

### Definition of Done Checklist

For all completed work:

- [ ] Acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Academic standards satisfied
- [ ] Performance requirements met

## Monitoring and Metrics

### Key Performance Indicators

**Academic Metrics**:

- Learning objectives achieved per sprint
- Academic milestone adherence
- Research methodology compliance
- Literature integration progress

**Technical Metrics**:

- Velocity (story points per sprint)
- Cycle time (story start to completion)
- Quality metrics (defect rate, test coverage)
- Performance benchmarks achieved

**Process Metrics**:

- Sprint goal achievement rate
- Blocker resolution time
- Team satisfaction scores
- Retrospective action item completion

## Troubleshooting Common Issues

### MCP Integration Issues

**Problem**: Cannot access JIRA projects via MCP tools
**Solution**:

1. Verify Atlassian account permissions
2. Check cloud ID configuration in MCP tools
3. Ensure proper authentication tokens

**Problem**: Custom fields not appearing in MCP tools
**Solution**:

1. Fields may need time to propagate
2. Verify field context and scope settings
3. Check field visibility permissions

### Academic Integration Issues

**Problem**: Academic milestones not aligning with sprints
**Solution**:

1. Adjust sprint length to match academic calendar
2. Create buffer time for academic review processes
3. Use epic-level planning for major milestones

## Success Criteria

The JIRA integration is successful when:

- [ ] All project work is tracked in JIRA
- [ ] Academic milestones are clearly mapped
- [ ] Team productivity metrics improve
- [ ] Quality standards are consistently met
- [ ] Academic reporting is automated
- [ ] Research methodology is supported

---

*This setup guide should be updated as the JIRA configuration evolves and new requirements emerge.*
