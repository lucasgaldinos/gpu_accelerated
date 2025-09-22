# GPU-Accelerated TSP/VRP Optimization - Clean Implementation

This project implements GPU-accelerated algorithms for the Traveling Salesman Problem (TSP) and Vehicle Routing Problem (VRP) using a teaching-oriented approach that prioritizes learning and understanding.

## Project Structure

```
gpu_accelerated/
├── 📋 project_management/     # Task tracking and project coordination
│   └── jira/                  # JIRA integration for task management
├── 🧠 knowledge_base/         # Learning materials and documentation  
├── 🏗️ code/                   # Source code and development
│   ├── src/                   # Source code packages (algorithms, backends, protocols, utils)
│   ├── tests/                 # Test suite (unit, integration, benchmarks)
│   └── examples/              # Usage examples and demos
├── 🧪 research/               # Academic research and validation
├── 📊 data/                   # Datasets and experimental data
├── 📝 documentation/          # Generated docs and reports
│   ├── api/                   # API documentation
│   ├── user_guides/           # User guides
│   ├── developer_guides/      # Developer guides
│   ├── academic/              # Academic documentation
│   └── reports/               # Project reports
├── 🔧 infrastructure/         # DevOps and configuration
├── 📦 artifacts/              # Build outputs and distributions
└── 🛠️ scripts/               # Validation and utility scripts
```

## Getting Started

1. **Review Project Management**: Start with `project_management/TODO.md` for current priorities
2. **Understanding the Design**: Read `knowledge_base/PROJECT_STRUCTURE_DESIGN.md`
3. **Educational Plan**: Follow `knowledge_base/EDUCATIONAL_IMPLEMENTATION_PLAN.md`
4. **Implementation**: Begin with tasks in `project_management/tasks/TASKS.md`
5. **JIRA Integration**: Use `project_management/jira/` for advanced task management

## Key Features

- **Teaching-Oriented Development**: Each task includes learning objectives and technical decision explanations
- **Multi-Backend Support**: NumPy (CPU), Numba (JIT), and CuPy (GPU) implementations
- **Academic Integration**: Aligned with Brazilian TCC standards and research methodology
- **Clean Architecture**: Hexagonal architecture with clear separation of concerns
- **Comprehensive Testing**: Unit, integration, and performance benchmarks

## Development Philosophy

This project emphasizes:

- **Learning over speed**: Understanding concepts deeply before implementation
- **Quality over quantity**: Well-tested, documented, and maintainable code
- **Academic rigor**: Research-grade validation and reproducibility
- **Progressive complexity**: Building from simple to advanced concepts

## Technology Stack

- **Python 3.10+** with uv for dependency management
- **CUDA** for GPU acceleration
- **CuPy** for GPU array operations
- **Numba** for JIT compilation
- **pytest** for comprehensive testing

## Workspace Organization

This workspace follows enforced repository standards with:

- **snake_case naming**: All directories and files use consistent naming conventions
- **Structured organization**: Clear separation of concerns across directories
- **Academic compliance**: Aligned with TCC requirements and research standards
- **Automated validation**: Scripts to ensure quality and naming compliance

See `documentation/reports/WORKSPACE_REORGANIZATION_COMPLETE.md` for detailed reorganization information.

## Academic Context

This implementation serves as both a learning exercise and a production-quality system for solving TSP/VRP optimization problems. It follows Brazilian TCC (Trabalho de Conclusão de Curso) standards and incorporates research methodology appropriate for academic validation.

## Next Steps

Begin with Task TSP-GPU-001 (Development Environment Setup) following the educational implementation plan for a structured learning experience.

---

*This is a clean restart from the original messy implementation, focusing on education, understanding, and academic quality.*
