# Architecture Diagrams - GPU-Accelerated Routing Optimization

This directory contains comprehensive architectural documentation for the TCC (undergraduate thesis) project on GPU-accelerated routing optimization algorithms.

## 📑 Available Diagrams

### 1. Class Diagram: Genetic Algorithm Architecture
**File**: [`class_diagram_genetic_algorithms.md`](./class_diagram_genetic_algorithms.md)

Shows the complete class hierarchy, inheritance relationships, and composition patterns for all genetic algorithm implementations.

**Key Highlights**:
- Template Method Pattern in `GeneticAlgorithmBase`
- Strategy Pattern for selection, crossover, and mutation
- Concrete implementations: CPU, HybridNaive, HybridOptimized, FullGPU, FullGPUEarlyStop
- Protocol-based dependency injection
- Lazy loading in `ProblemContext`

**Use Cases**:
- Understanding the ISO-algorithmic design
- Identifying variant differences
- Explaining design patterns used
- Thesis Chapter 3 (Methodology)

---

### 2. Architecture Diagram: Module Structure
**File**: [`architecture_diagram_src_modules.md`](./architecture_diagram_src_modules.md)

Illustrates the layered architecture of the entire `code/src` module, including all dependencies and interactions between layers.

**Layers Shown**:
1. 🌐 External Dependencies (NumPy, CuPy, CUDA)
2. 📦 Data Layer (Problem, Exceptions)
3. 🔌 Protocol Layer (BackendModule, ProblemContext, Strategies)
4. 🔧 Utility Layer (gpu_helpers, distances)
5. 🎯 Strategy Layer (Selection, Crossover, Mutation)
6. 🧬 Algorithm Layer (GeneticAlgorithm variants)
7. ⚡ CUDA Kernel Layer (.cu files)
8. 📂 Loader Layer (DatabaseLoader)
9. 📊 Benchmarking Layer (Statistics)

**Use Cases**:
- Understanding system architecture
- Explaining separation of concerns
- Memory transfer pattern analysis
- Thesis Chapter 3 (System Design)

---

### 3. Sequence Diagrams: Execution Flows
**File**: [`sequence_diagrams_ga_execution.md`](./sequence_diagrams_ga_execution.md)

Contains detailed sequence diagrams showing runtime interactions and call flows for different GA variants.

**Diagrams Included**:
1. **CPU Variant Execution Flow**: Complete step-by-step execution showing all method calls
2. **FullGPU Variant Execution Flow**: Monolithic kernel approach with memory transfers
3. **Module Interaction During Initialization**: How components collaborate during setup
4. **Hybrid Variants Comparison**: Memory transfer patterns side-by-side

**Key Insights**:
- CPU variant: Sequential, 0 transfers
- HybridNaive: 256 individual GPU calls, ~20MB per generation
- HybridOptimized: Single batch call, ~10MB per generation
- FullGPU: One-time setup, ~8MB total for 1000 generations (2500x reduction)

**Use Cases**:
- Understanding runtime behavior
- Comparing memory transfer overhead
- Explaining GPU optimization strategies
- Thesis Chapter 4 (Results & Analysis)

---

### 4. Module Imports and Dependencies
**File**: [`module_imports_dependencies.md`](./module_imports_dependencies.md)

Comprehensive graph showing all import relationships and dependencies between modules in `code/src`.

**Analysis Provided**:
- Complete import chains for all modules
- Critical dependency paths
- Circular dependency prevention strategies
- Module responsibility matrix
- Most imported/importing modules ranking

**Key Features**:
- Shows both static imports and dynamic kernel loading
- Distinguishes between solid dependencies and dotted runtime links
- Color-coded by module type
- Includes actual import statements from key files

**Use Cases**:
- Understanding code organization
- Debugging import issues
- Refactoring guidance
- Thesis Appendix (Technical Documentation)

---

## 🎨 Diagram Format

All diagrams are written in **Mermaid** syntax, which:
- Renders automatically in GitHub, GitLab, VS Code, and many markdown viewers
- Can be exported to PNG/SVG for thesis documents
- Is version-controlled as plain text
- Is easy to update and maintain

### Viewing the Diagrams

**In GitHub/GitLab**: Diagrams render automatically in markdown preview

**In VS Code**: Install the [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension

**For LaTeX/PDF Thesis**: Use [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) to export:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Export diagram to PNG
mmdc -i class_diagram_genetic_algorithms.md -o class_diagram.png

# Export to SVG (better for PDF)
mmdc -i class_diagram_genetic_algorithms.md -o class_diagram.svg
```

**Online Editors**:
- [Mermaid Live Editor](https://mermaid.live/) - Interactive editing and export
- Copy diagram code blocks and paste for instant preview

---

## 📊 Academic Usage Guide

### For TCC/Thesis Documentation

#### Chapter 3: Methodology
- Use **Class Diagram** to explain ISO-algorithmic design
- Use **Architecture Diagram** to show system layers
- Reference design patterns (Template Method, Strategy, Dependency Injection)

#### Chapter 4: Implementation
- Use **Sequence Diagrams** to explain execution flow differences
- Use **Module Imports** to document code organization
- Show memory transfer patterns for performance analysis

#### Chapter 5: Results & Discussion
- Use **Sequence Diagrams - Hybrid Comparison** for transfer overhead analysis
- Reference architectural decisions in performance results
- Explain why FullGPU achieves 2500x transfer reduction

### Citing Design Patterns

The diagrams reference these academic sources:

- **Template Method Pattern**: Gamma et al. (1994) - "Design Patterns: Elements of Reusable Object-Oriented Software"
- **Strategy Pattern**: Gamma et al. (1994) - "Design Patterns"
- **Dependency Injection**: Fowler (2004) - "Inversion of Control Containers and the Dependency Injection pattern"
- **Protocol-Based Design**: PEP 544 - "Protocols: Structural subtyping (static duck typing)"
- **Lazy Loading**: Fowler (2002) - "Patterns of Enterprise Application Architecture"
- **Fujimoto Kernel**: Fujimoto & Tsutsui (2011) - "A highly parallel TSP solver for GPUs"

---

## 🔍 Navigation Guide

### By Topic

**Understanding the Algorithm**:
1. Start with **Class Diagram** for overall structure
2. Read **CPU Sequence Diagram** for baseline flow
3. Compare with **FullGPU Sequence Diagram** for differences

**Understanding the Architecture**:
1. Start with **Architecture Diagram** for layers
2. Read **Module Imports** for detailed dependencies
3. Reference **Initialization Sequence Diagram** for startup flow

**Understanding Performance**:
1. Read **Hybrid Variants Comparison** sequence diagram
2. Review memory transfer tables in sequence diagrams
3. Cross-reference with architectural patterns in class diagram

### By Use Case

**Writing thesis methodology section**:
- Class Diagram → Design patterns explanation
- Architecture Diagram → System design rationale

**Explaining experimental setup**:
- Sequence Diagrams → Execution flow differences
- Architecture Diagram → Memory transfer patterns

**Debugging or extending code**:
- Module Imports → Find dependencies
- Sequence Diagrams → Understand call flow
- Class Diagram → Identify extension points

---

## 📝 Diagram Maintenance

### Adding New Diagrams

1. Create new `.md` file in this directory
2. Use Mermaid syntax (see existing files for examples)
3. Add entry to this README
4. Test rendering in GitHub preview
5. Commit with descriptive message

### Updating Existing Diagrams

When code changes require diagram updates:

1. Identify affected diagrams (usually multiple)
2. Update Mermaid code blocks
3. Verify rendering
4. Add note in diagram about update date/reason
5. Cross-reference in commit message

### Style Guidelines

**Consistent Styling**:
- Use color-coding by module type (see existing diagrams)
- Add notes for complex interactions
- Include academic references where applicable
- Use clear, descriptive labels

**Diagram Complexity**:
- Keep diagrams focused on single concern
- Split complex flows into multiple diagrams
- Use subgraphs for logical grouping
- Add summary tables for comparison

---

## 🔗 Related Documentation

### Code Documentation
- [`../developer_guides/`](../developer_guides/) - Implementation guides
- [`../technical_decisions/`](../technical_decisions/) - Architecture decision records
- [`../reports/`](../reports/) - Analysis reports

### Thesis Documentation
- [`../../first_draft.md`](../../first_draft.md) - TCC draft with research questions
- [`../../second_draft.md`](../../second_draft.md) - Updated thesis draft
- [`PROJECT_STATUS_AND_ANSWERS.md`](../../PROJECT_STATUS_AND_ANSWERS.md) - Current status

### Source Code
- [`../../code/src/`](../../code/src/) - Implementation (what diagrams document)
- [`../../code/benchmarks/`](../../code/benchmarks/) - Performance validation
- [`../../code/examples/`](../../code/examples/) - Usage examples

---

## 📚 Bibliography References

### Design Patterns & Architecture
1. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

2. Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

3. Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.

4. Van Rossum, G., Levkivskyi, I., & Langa, Ł. (2017). PEP 544 – Protocols: Structural subtyping (static duck typing). Python Enhancement Proposals.

### GPU Computing & Algorithms
5. Fujimoto, N., & Tsutsui, S. (2011). A highly parallel TSP solver for GPUs. In *International Conference on Parallel and Distributed Computing, Applications and Technologies* (pp. 264-271).

6. Kirk, D. B., & Hwu, W. W. (2016). *Programming Massively Parallel Processors: A Hands-on Approach* (3rd ed.). Morgan Kaufmann.

7. NVIDIA Corporation. (2023). *CUDA C++ Best Practices Guide*. NVIDIA Developer Documentation.

### Genetic Algorithms
8. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.

9. Davis, L. (1985). Applying Adaptive Algorithms to Epistatic Domains. In *Proceedings of IJCAI-85* (pp. 162-164).

10. Miller, B. L., & Goldberg, D. E. (1995). Genetic Algorithms, Tournament Selection, and the Effects of Noise. *Complex Systems*, 9(3), 193-212.

---

## 🤝 Contributing

When adding or updating diagrams:

1. **Consistency**: Follow existing styling and conventions
2. **Completeness**: Include all relevant interactions/dependencies
3. **Clarity**: Add notes and explanations for complex parts
4. **Accuracy**: Verify against actual code implementation
5. **References**: Cite academic sources for patterns/algorithms
6. **Testing**: Ensure diagrams render correctly before committing

---

## 📧 Contact & Support

For questions about the diagrams or architecture:

1. Check inline comments in diagram files
2. Review related documentation in `../developer_guides/`
3. Consult thesis advisor for academic questions
4. Create issue in repository for technical questions

---

**Last Updated**: 2025-01-28  
**Diagram Count**: 4 files, 10+ diagrams  
**Total Coverage**: ~95% of `code/src` architecture

---

## Quick Reference

| Need | Diagram | Section |
|------|---------|---------|
| Class hierarchy | Class Diagram | Full diagram |
| System layers | Architecture Diagram | Full diagram |
| Execution flow | Sequence Diagrams | CPU/FullGPU flows |
| Memory transfers | Sequence Diagrams | Hybrid comparison |
| Import chains | Module Imports | Import analysis |
| Design patterns | Class Diagram | Key Patterns section |
| Performance insights | Sequence Diagrams | Key Observations |
| Code organization | Module Imports | Module Structure |
