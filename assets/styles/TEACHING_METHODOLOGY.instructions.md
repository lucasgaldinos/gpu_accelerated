---
applyTo: "**/*.md,**/KNOWLEDGE_BASE/**"
description: "Educational methodology commands for teaching-oriented development"
---
## Purpose

These instructions enforce the educational methodology for the GPU-accelerated TSP/VRP optimization project. Every development activity must prioritize learning and understanding while maintaining production quality.

# Teaching Methodology Commands

## Core Educational Principles

## LEARNING-FIRST COMMANDS

### 🎓 Learning-First Development

### Before Writing Any Code

1. **Understand completely**: Research all concepts first1. **Understand Before Implementing**: Research concepts thoroughly before writing code

2. **Define learning goals**: What will this teach?2. **Explain Every Decision**: Document technical choices and trade-offs

3. **Plan teaching sequence**: Simple to complex progression3. **Progressive Complexity**: Build from simple to advanced incrementally

4. **Identify misconceptions**: What might confuse learners?4. **Validate Understanding**: Test knowledge through implementation

5. **Prepare examples**: Multiple scenarios and use cases5. **Reflect and Improve**: Regular review and refinement of approach

### While Documenting### 📚 Knowledge Construction

1. **Explain WHY not HOW**: Focus on reasoning and decisions

2. **Use multiple examples**: Show different use cases1. **Multiple Perspectives**: Compare different approaches and solutions

3. **Include failed attempts**: Show what doesn't work and why2. **Hands-On Validation**: Test everything to build confidence

4. **Connect to theory**: Link practice to academic concepts3. **Conceptual Connections**: Link new learning to existing knowledge

5. **Progressive disclosure**: Reveal complexity gradually4. **Meta-Cognitive Awareness**: Think about thinking and learning processes

5. **Documentation as Learning**: Write to deepen understanding

## EDUCATIONAL STRUCTURE COMMANDS

## Task Execution Methodology

### Phase-Based Learning

- **Phase 1**: GPU Fundamentals (foundation building)### Phase Structure

- **Phase 2**: Architecture Design (pattern recognition)

- **Phase 3**: Algorithm Implementation (problem solving)All development follows the 5-phase educational progression:

- **Phase 4**: Database Integration (system thinking)

- **Phase 5**: Performance Analysis (research skills)1. **Phase 1**: Foundation and Environment (GPU fundamentals)

2. **Phase 2**: Core Architecture (Design patterns and abstractions)

### Content Organization3. **Phase 3**: Algorithm Implementation (Progressive algorithm complexity)

1. **Learning objectives first**: Clear goals for each section4. **Phase 4**: Database Integration (Data management and persistence)

2. **Prerequisites stated**: What needs to be known before5. **Phase 5**: Performance Analysis (Academic validation and research)

3. **Examples before theory**: Show then explain

4. **Practice opportunities**: Hands-on exercises included### Task Learning Sequence

5. **Assessment criteria**: How to measure understanding

Every TSP-GPU-XXX task must follow this learning sequence:

## DOCUMENTATION COMMANDS

#### 1. Conceptual Foundation (30-45 min)

### Educational Content Requirements

- **Context setting**: Why is this important?```yaml

- **Multiple perspectives**: Different ways to approach problemsActivities:

- **Hands-on validation**: Working examples that can be tested- Read background materials and documentation

- **Reflection prompts**: Questions to deepen understanding- Understand theoretical foundations

- **Connection building**: Links to related concepts- Identify key concepts and terminology

- Map connections to previous learning

### Teaching Material Standards

1. **Clarity**: Use simple, clear languageDeliverables:

2. **Completeness**: Cover all important aspects- Notes on key concepts in KNOWLEDGE_BASE/learning_materials/

3. **Accuracy**: Technical information must be correct- Questions and areas needing clarification

4. **Engagement**: Make content interesting and relevant- Connections to existing knowledge documented

5. **Accessibility**: Suitable for target learning level```

## KNOWLEDGE VALIDATION COMMANDS#### 2. Design and Planning (30-45 min)

### Understanding Checks```yaml

- [ ] Can explain concept to someone elseActivities:

- [ ] Can implement from scratch without copy-paste- Analyze requirements and constraints

- [ ] Can identify when to use vs when not to use- Compare alternative approaches

- [ ] Can troubleshoot common problems- Make architectural decisions with rationale

- [ ] Can connect to broader patterns- Plan implementation strategy

### Teaching Quality GatesDeliverables

- [ ] Learning objectives clearly stated- Technical Decision Record (ADR) in KNOWLEDGE_BASE/technical_decisions/

- [ ] Examples work and demonstrate concepts- Implementation plan with clear steps

- [ ] Progressive complexity maintained- Test strategy and validation criteria

- [ ] Common misconceptions addressed- Learning objectives for implementation phase

- [ ] Assessment criteria provided```

#### 3. Implementation (60-90 min)

```yaml
Activities:
- Implement solution following clean architecture
- Write comprehensive tests
- Document code with educational comments
- Validate against requirements

Deliverables:
- Working implementation in IMPLEMENTATION/src/
- Comprehensive test suite in IMPLEMENTATION/tests/
- Code documentation explaining approach
- Performance and correctness validation
```

#### 4. Validation and Reflection (15-30 min)

```yaml
Activities:
- Test implementation thoroughly
- Analyze performance characteristics
- Reflect on learning outcomes
- Document lessons learned

Deliverables:
- Validation report confirming success criteria
- Performance analysis and benchmarks
- Reflection notes on what was learned
- Improvements for future tasks
```

## Code Quality Standards

### Educational Code Requirements

1. **Self-Documenting**: Code tells a story that teaches concepts
2. **Multiple Examples**: Show different approaches and their trade-offs
3. **Progressive Complexity**: Build from simple examples to full implementation
4. **Error Scenarios**: Include handling of edge cases and failures
5. **Performance Awareness**: Understand and document performance implications

### Documentation Standards

#### Code Comments

```python
# LEARNING OBJECTIVE: Understand GPU memory coalescing
# WHY THIS APPROACH: Coalesced access improves bandwidth utilization
# TRADE-OFFS: More complex indexing vs significant performance gain

def coalesced_distance_matrix(points_gpu):
    """
    Compute distance matrix with coalesced memory access pattern.
    
    Educational Notes:
    - This implementation prioritizes memory bandwidth efficiency
    - Alternative: Simple nested loops (easier to understand, slower)
    - Key concept: Memory coalescing in CUDA programming
    
    Performance Characteristics:
    - Memory bandwidth: ~80% of theoretical peak
    - Scales well with problem size up to GPU memory limits
    - 3-5x speedup vs non-coalesced implementation
    """
    # Implementation with educational comments throughout
```

#### Function Documentation

```python
def algorithm_factory(algorithm_name: str, backend: str) -> BaseAlgorithm:
    """
    Factory method for creating optimization algorithms.
    
    Teaching Objectives:
    - Understand Factory pattern and its benefits
    - Learn about dependency injection and testability
    - Practice interface design and abstraction
    
    Technical Decisions:
    - Factory pattern: Enables runtime algorithm selection
    - Backend abstraction: Supports multiple compute platforms
    - Interface design: Ensures consistent API across algorithms
    
    Args:
        algorithm_name: Name of optimization algorithm (e.g., 'nearest_neighbor')
        backend: Computational backend ('numpy', 'numba', 'cupy')
        
    Returns:
        Algorithm instance implementing BaseAlgorithm interface
        
    Example:
        >>> tsp_solver = algorithm_factory('nearest_neighbor', 'cupy')
        >>> solution = tsp_solver.solve(distance_matrix)
    """
```

### Test Documentation

Every test must include educational context:

```python
class TestDistanceMatrixGPU:
    """
    Educational test suite for GPU distance matrix computation.
    
    Learning Objectives:
    - Validate GPU implementation correctness
    - Understand floating-point precision in GPU computing
    - Practice performance testing methodologies
    """
    
    def test_accuracy_vs_cpu_implementation(self):
        """
        LEARNING: GPU implementations must maintain numerical accuracy.
        
        This test validates that GPU computation produces results
        within acceptable tolerance of CPU reference implementation.
        
        Educational Notes:
        - Floating-point arithmetic differences between CPU/GPU
        - Importance of choosing appropriate tolerances
        - Validation strategies for parallel algorithms
        """
        # Test implementation with educational comments
```

## Research Integration Requirements

### Academic Standards

1. **Literature Review**: Reference relevant academic sources
2. **Methodology Documentation**: Clear experimental design
3. **Statistical Validation**: Appropriate statistical tests
4. **Reproducibility**: Complete reproduction instructions
5. **Citation Standards**: Proper academic citations

### Experimental Design

Every performance evaluation must include:

```yaml
Experimental Design:
  Objective: Clear statement of what is being measured
  Hypothesis: Predicted outcomes and rationale
  Variables:
    Independent: What we control (problem size, algorithm, backend)
    Dependent: What we measure (runtime, memory usage, solution quality)
    Controlled: What we keep constant (hardware, software versions)
  Methodology: Step-by-step experimental procedure
  Analysis: Statistical methods for result interpretation

Documentation Location: RESEARCH/experiments/phase_X_experiment_name/
```

### Result Documentation

All experimental results must include:

1. **Raw Data**: Complete experimental outputs
2. **Statistical Analysis**: Appropriate statistical tests and confidence intervals
3. **Visualization**: Clear plots and charts showing results
4. **Interpretation**: Academic-quality analysis of findings
5. **Limitations**: Honest assessment of constraints and threats to validity

## Quality Assurance Process

### Learning Validation

Before marking any task complete, validate:

- [ ] **Conceptual Understanding**: Can explain concepts to others
- [ ] **Implementation Quality**: Code meets educational and technical standards
- [ ] **Documentation Completeness**: All decisions and trade-offs documented
- [ ] **Test Coverage**: Comprehensive testing with educational value
- [ ] **Performance Validation**: Meets or exceeds baseline requirements

### Academic Review

All deliverables must pass academic quality review:

- [ ] **Technical Accuracy**: Implementations are correct and well-designed
- [ ] **Educational Value**: Clear learning objectives achieved
- [ ] **Documentation Quality**: Academic writing standards met
- [ ] **Reproducibility**: Others can follow and reproduce work
- [ ] **Citation Compliance**: Proper attribution of sources and methods

## Common Teaching Anti-Patterns to Avoid

### ❌ Implementation Without Understanding

```python
# BAD: Copy-paste without explanation
def some_algorithm(data):
    # Complex implementation with no comments
    return magic_result
```

### ✅ Understanding-Driven Implementation

```python
# GOOD: Clear educational progression
def nearest_neighbor_tsp(distance_matrix):
    """
    LEARNING OBJECTIVE: Understand greedy algorithm construction.
    
    This implements the nearest neighbor heuristic for TSP:
    1. Start at arbitrary city
    2. Always move to nearest unvisited city
    3. Return to start when all cities visited
    
    WHY THIS ALGORITHM:
    - Simple to understand and implement
    - Good introduction to constructive heuristics
    - Baseline for comparing more sophisticated methods
    
    LIMITATIONS:
    - Often produces poor solutions (can be 2x optimal)
    - No guarantee of solution quality
    - Greedy choice may lead to poor later decisions
    """
    # Step-by-step implementation with educational comments
```

### ❌ Premature Optimization

```python
# BAD: Complex optimization without understanding basics
def hyper_optimized_function(data):
    # Unreadable optimized code
    pass
```

### ✅ Progressive Optimization

```python
# GOOD: Start simple, optimize incrementally
def distance_computation_v1_simple(points):
    """Version 1: Clear, simple implementation for learning."""
    
def distance_computation_v2_vectorized(points):
    """Version 2: NumPy vectorization for performance."""
    
def distance_computation_v3_gpu(points):
    """Version 3: GPU acceleration for scale."""
```

## Success Metrics

### Learning Outcomes

- **Conceptual Mastery**: Deep understanding of GPU computing and optimization
- **Technical Skills**: Ability to implement and optimize algorithms
- **Research Capability**: Skills in experimental design and validation
- **Academic Writing**: Quality documentation and analysis

### Implementation Quality

- **Code Quality**: Clean, well-documented, testable code
- **Performance**: Meets or exceeds academic benchmarks
- **Reproducibility**: Complete reproduction by others
- **Innovation**: Novel insights or improvements documented

---

**Remember**: The goal is not just working code, but deep understanding and academic-quality research. Every line of code should teach something valuable.
