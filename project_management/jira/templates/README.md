# JIRA PT Project Quick Start Guide

## 🚀 Getting Started with Your JIRA Project

### Project Information

- **URL**: <https://this-shall-not-be-taken.atlassian.net/jira/software/projects/PT/boards/67>
- **Project Key**: PT
- **Board ID**: 67
- **Type**: TCC Academic Research Project

### 📋 Immediate Actions Required

1. **Run Configuration Script**:
   ```bash
   cd project_management/jira_templates/
   ./configure_pt_project.sh
   ```

2. **Set Up Custom Fields** (Admin Required):
   - Academic Phase (Select: Literature Review, Implementation, etc.)
   - Learning Objective (Text)
   - Algorithm Type (Select: Classical TSP, GPU Optimization, etc.)
   - Performance Target (Text)
   - RACI Role (Select: Responsible, Accountable, etc.)
   - Complexity Level (Select: Basic, Intermediate, Advanced, Research)
   - Testing Requirement (Multi-select: Unit Tests, Benchmarks, etc.)

3. **Configure Workflows**:
   - Use the Academic Development Workflow
   - Set up transitions: Literature Review → Design → Implementation → Testing → Analysis → Documentation → Review → Complete

4. **Create Initial Issues**:
   - Start with Theme: "GPU Optimization Research Theme"
   - Add Epic: "Classical TSP Algorithm Implementation"
   - Break down into Stories using the templates

### 🎯 Sample Issue Hierarchy

```
Theme: GPU Optimization Research Theme (PT-1)
├── Epic: Classical TSP Algorithm Implementation (PT-2)
│   ├── Story: Implement GPU-Accelerated Nearest Neighbor TSP (PT-3)
│   │   ├── Task: Design DistanceProvider Protocol Interface (PT-4)
│   │   │   └── Sub-task: Implement CuPy Backend for DistanceProvider (PT-5)
│   │   ├── Task: Implement Nearest Neighbor Core Algorithm (PT-6)
│   │   └── Task: Create Performance Benchmarking Suite (PT-7)
│   └── Story: Implement GPU-Accelerated 2-opt Optimization (PT-8)
└── Epic: VRP Algorithm Research and Implementation (PT-9)
```

### 📊 Key JQL Queries for PT Project

#### Academic Progress Tracking

```jql
project = PT AND "Academic Phase" in ("Implementation", "Testing") ORDER BY priority DESC
```

#### Performance-Critical Tasks

```jql
project = PT AND "Performance Target" is not EMPTY AND status != Done
```

#### My Current Work

```jql
project = PT AND assignee = currentUser() AND status in ("In Progress", "Design", "Implementation")
```

#### High-Priority Research Tasks

```jql
project = PT AND "Complexity Level" = "Research" AND priority = High
```

### 🎨 Board Configuration

Configure your Kanban board columns to match the academic workflow:

1. **Backlog** (Literature Review)
2. **Design** (Design)
3. **In Development** (Implementation)
4. **Testing** (Testing)
5. **Analysis** (Analysis)
6. **Documentation** (Documentation)
7. **Review** (Review)
8. **Done** (Complete)

### 📝 Issue Creation Workflow

1. **Create Theme** for major research areas
2. **Break into Epics** for academic milestones
3. **Define Stories** with clear acceptance criteria
4. **Add Tasks** for specific development work
5. **Create Sub-tasks** for atomic work units

### 🔧 Integration with Development

- Link JIRA issues to Git branches: `PT-123-implement-nearest-neighbor`
- Include issue keys in commit messages: `git commit -m "PT-123: Add CuPy distance provider implementation"`
- Use issue keys in pull request titles: `[PT-123] Implement GPU-accelerated Nearest Neighbor algorithm`

### 📚 Academic Compliance

Every issue should include:

- **Learning Objective**: What knowledge is gained
- **Academic Phase**: Current research phase
- **Testing Requirements**: How validation is performed
- **Literature Context**: Related research references

### 🎯 Success Metrics

- Issues properly categorized by Academic Phase
- Performance targets defined and tracked
- All implementations have proper testing requirements
- Academic documentation standards maintained
- Regular progress reviews and milestone tracking

### 📞 Support Resources

- **JIRA Documentation**: <https://support.atlassian.com/jira/>
- **API Reference**: <https://developer.atlassian.com/cloud/jira/platform/rest/>
- **Project Templates**: Available in `jira_templates/` directory
- **Configuration Scripts**: Use `configure_pt_project.sh` for setup automation

---

**Ready to start your academic research with proper project management!** 🎓
