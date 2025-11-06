# GPU-Accelerated Heuristic Framework for Routing Problems

**Trabalho de Conclusão de Curso - UFSC**

> **Document Status (Pre-Implementation)**:
>
> - ✅ Benchmark selection complete (30 instances documented)
> - ✅ Memory analysis complete (65% VRAM limit justified)
> - ⏳ ALL Research questions MUST be defined with academic citations
> - ⏳ Pseudocode in Appendices B (templates ready, awaiting implementation validation)
> - ⏳ Literature review ongoing (key papers cited, comprehensive review in progress)
> - ⏳ Experimental results (Chapter 4) - awaiting implementation
> - 📊 Target length: 50-60 pages

---

## RESUMO / ABSTRACT

[To be written after implementation]

**Palavras-chave:** GPU acceleration, TSP, VRP, metaheuristics, local search, CuPy

---

## SUMÁRIO

- [GPU-Accelerated Heuristic Framework for Routing Problems](#gpu-accelerated-heuristic-framework-for-routing-problems)
  - [RESUMO / ABSTRACT](#resumo--abstract)
  - [SUMÁRIO](#sumário)
  - [LISTA DE SÍMBOLOS](#lista-de-símbolos)
  - [LISTA DE ABREVIATURAS E SIGLAS](#lista-de-abreviaturas-e-siglas)
  - [LISTA DE TABELAS](#lista-de-tabelas)
  - [LISTA DE FIGURAS](#lista-de-figuras)
  - [1. INTRODUÇÃO](#1-introdução)
    - [1.1 Justificativa](#11-justificativa)
      - [1.1.1 Historical context and Key Motivations (Don't know if this should be here.)](#111-historical-context-and-key-motivations-dont-know-if-this-should-be-here)
    - [1.2 Objetivos](#12-objetivos)
      - [1.2.1 Objetivo Geral](#121-objetivo-geral)
      - [1.2.2 Objetivos Específicos](#122-objetivos-específicos)
    - [1.3 Limitações do Trabalho](#13-limitações-do-trabalho)
  - [2. REVISÃO BIBLIOGRÁFICA](#2-revisão-bibliográfica)
    - [2.1 Combinatorial Optimization Problems](#21-combinatorial-optimization-problems)
    - [2.2 Heuristic Approaches](#22-heuristic-approaches)
      - [2.2.1 Construction Heuristics](#221-construction-heuristics)
      - [2.2.2 Improvement Heuristics](#222-improvement-heuristics)
    - [2.3 Metaheuristic Strategies](#23-metaheuristic-strategies)
      - [2.3.1 Genetic Algorithms (Reference Only)](#231-genetic-algorithms-reference-only)
      - [2.3.2 Simulated Annealing](#232-simulated-annealing)
      - [2.3.3 Tabu Search (Reference Only)](#233-tabu-search-reference-only)
    - [2.4 Hybrid Approaches](#24-hybrid-approaches)
    - [2.5 GPU Computing for Optimization](#25-gpu-computing-for-optimization)
  - [3. MATERIAIS E MÉTODOS](#3-materiais-e-métodos)
    - [3.1 System Specifications](#31-system-specifications)
    - [3.2 Backend Architecture](#32-backend-architecture)
      - [3.2.1 Module Pattern vs. OOP Inheritance](#321-module-pattern-vs-oop-inheritance)
      - [3.2.2 Protocol-Based Type Safety (PEP 544)](#322-protocol-based-type-safety-pep-544)
      - [3.2.3 Preliminary Validation](#323-preliminary-validation)
    - [3.3 Algorithm Implementation](#33-algorithm-implementation)
      - [3.3.1 Construction Heuristic (Initial Solution)](#331-construction-heuristic-initial-solution)
        - [TSP Construction heuristics](#tsp-construction-heuristics)
      - [3.3.2 Improvement Heuristic (Local Search)](#332-improvement-heuristic-local-search)
      - [3.3.3 Metaheuristic Strategy](#333-metaheuristic-strategy)
      - [3.3.4 Hybrid Approach](#334-hybrid-approach)
      - [3.3.5 Implementation Strategy: Vectorization and Backend Integration](#335-implementation-strategy-vectorization-and-backend-integration)
    - [3.4 Benchmark Problem Selection](#34-benchmark-problem-selection)
      - [3.4.1 Research Questions Driving Selection](#341-research-questions-driving-selection)
      - [3.4.2 MVP Benchmark Selection (3 Instances)](#342-mvp-benchmark-selection-3-instances)
      - [3.4.3 Complete Benchmark Instance Tables (30 Instances)](#343-complete-benchmark-instance-tables-30-instances)
        - [TSP Instances (18 total - 60%)](#tsp-instances-18-total---60)
        - [ATSP Instances (6 total - 20%)](#atsp-instances-6-total---20)
        - [CVRP Instances (6 total - 20%)](#cvrp-instances-6-total---20)
        - [Size Distribution Summary](#size-distribution-summary)
      - [3.4.4 Memory Footprint Analysis](#344-memory-footprint-analysis)
      - [3.4.4 Expected Experimental Results](#344-expected-experimental-results)
      - [3.4.5 Data Format Specification](#345-data-format-specification)
    - [3.5 Experimental Design](#35-experimental-design)
      - [3.5.1 Comparison 1: Deterministic Local Search (2-opt)](#351-comparison-1-deterministic-local-search-2-opt)
      - [3.5.2 Comparison 2: Stochastic Metaheuristics (SA vs. GA)](#352-comparison-2-stochastic-metaheuristics-sa-vs-ga)
      - [3.5.3 Statistical Methodology](#353-statistical-methodology)
  - [4. RESULTADOS](#4-resultados)
    - [4.1 Statistical Test Validation](#41-statistical-test-validation)
    - [4.2 Analysis 1: 2-opt (Deterministic) Performance](#42-analysis-1-2-opt-deterministic-performance)
    - [4.3 Analysis 2: Metaheuristic Quality (Fixed-Time Budget)](#43-analysis-2-metaheuristic-quality-fixed-time-budget)
    - [4.4 Analysis 3: Convergence Speed and Statistical Ranking](#44-analysis-3-convergence-speed-and-statistical-ranking)
  - [5. DISCUSSÃO E CONSIDERAÇÕES](#5-discussão-e-considerações)
    - [5.1 Performance Analysis](#51-performance-analysis)
    - [5.2 Algorithm Comparison](#52-algorithm-comparison)
    - [5.3 Scalability Observations](#53-scalability-observations)
    - [5.4 Limitations and Constraints](#54-limitations-and-constraints)
  - [6. CONCLUSÃO](#6-conclusão)
    - [6.1 Recomendações para Trabalhos Futuros](#61-recomendações-para-trabalhos-futuros)
  - [REFERÊNCIAS](#referências)
  - [GLOSSÁRIO](#glossário)
  - [RESEARCH QUESTIONS TO ANSWER](#research-questions-to-answer)
  - [REFERÊNCIAS](#referências-1)
  - [APÊNDICE A - DETALHES DE IMPLEMENTAÇÃO](#apêndice-a---detalhes-de-implementação)
    - [A.1 Esquema do Banco de Dados](#a1-esquema-do-banco-de-dados)
    - [A.2 Interface `Problem` - Especificação Completa](#a2-interface-problem---especificação-completa)
    - [A.3 Consulta de Carregamento SQL](#a3-consulta-de-carregamento-sql)
    - [A.4 Backend Abstraction: Implementação Completa](#a4-backend-abstraction-implementação-completa)
    - [A.5 Padrões de Vetorização](#a5-padrões-de-vetorização)
    - [A.6 Implementação Multi-Start](#a6-implementação-multi-start)
    - [A.7 Especificações de Hardware e Software](#a7-especificações-de-hardware-e-software)
    - [A.8 Protocolos de Medição de Desempenho](#a8-protocolos-de-medição-de-desempenho)
  - [APÊNDICE B - PSEUDOCÓDIGO DOS ALGORITMOS](#apêndice-b---pseudocódigo-dos-algoritmos)
    - [B.1 Nearest Neighbor Construction](#b1-nearest-neighbor-construction)
    - [B.2 2-opt Improvement](#b2-2-opt-improvement)
    - [B.3 Simulated Annealing with 2-opt](#b3-simulated-annealing-with-2-opt)
  - [Academic References](#academic-references)
    - [Benchmark Instance Sources](#benchmark-instance-sources)
    - [GPU Computing for Optimization](#gpu-computing-for-optimization)
    - [Experimental Design and Statistical Methods](#experimental-design-and-statistical-methods)

[To be generated automatically by LaTeX/document processor]

---

## LISTA DE SÍMBOLOS

| Símbolo      | Descrição                                  |
| ------------ | ------------------------------------------ |
| $n$          | Número de nós/cidades no problema          |
| $i, j, k$    | Índices de nós                             |
| $x_i, y_i$   | Coordenadas do nó $i$                      |
| $d_{ij}$     | Distância entre nós $i$ e $j$              |
| $D$          | Matriz de distâncias $n \times n$          |
| $\pi$        | Tour/rota (permutação de nós)              |
| $c(\pi)$     | Custo total do tour $\pi$                  |
| $Q$          | Capacidade do veículo (CVRP)               |
| $q_i$        | Demanda do nó $i$ (CVRP)                   |
| $K$          | Número de veículos (CVRP)                  |
| $T$          | Temperatura (Simulated Annealing)          |
| $\alpha$     | Taxa de resfriamento (Simulated Annealing) |
| $GPU_{time}$ | Tempo de execução em GPU                   |
| $CPU_{time}$ | Tempo de execução em CPU                   |
| $speedup$    | Aceleração = $CPU_{time} / GPU_{time}$     |

---

## LISTA DE ABREVIATURAS E SIGLAS

| Sigla   | Significado                                                  |
| ------- | ------------------------------------------------------------ |
| TSP     | Traveling Salesman Problem (Problema do Caixeiro Viajante)   |
| ATSP    | Asymmetric TSP (TSP Assimétrico)                             |
| VRP     | Vehicle Routing Problem (Problema de Roteamento de Veículos) |
| CVRP    | Capacitated VRP (VRP Capacitado)                             |
| MDVRP   | Multi-Depot VRP (VRP com Múltiplos Depósitos)                |
| VRPPD   | VRP with Pickup and Delivery (VRP com Coleta e Entrega)      |
| GPU     | Graphics Processing Unit (Unidade de Processamento Gráfico)  |
| CPU     | Central Processing Unit (Unidade Central de Processamento)   |
| CUDA    | Compute Unified Device Architecture                          |
| VRAM    | Video Random Access Memory (Memória de Vídeo)                |
| SA      | Simulated Annealing (Recozimento Simulado)                   |
| GA      | Genetic Algorithm (Algoritmo Genético)                       |
| TS      | Tabu Search (Busca Tabu)                                     |
| 2-opt   | Operador de melhoria que troca 2 arestas                     |
| 3-opt   | Operador de melhoria que troca 3 arestas                     |
| Or-opt  | Operador de realocação de sequências                         |
| NN      | Nearest Neighbor (Vizinho Mais Próximo)                      |
| TSPLIB  | Biblioteca padrão de instâncias TSP                          |
| CVRPLIB | Biblioteca padrão de instâncias CVRP                         |

---

## LISTA DE TABELAS

[To be generated automatically - will include:]

- Tabela 3.1: 30 Instâncias de Benchmark Selecionadas
- Tabela 3.2: Distribuição por Tamanho e Tipo de Problema
- Tabela 3.3: Análise de Memória (Maiores Instâncias)
- Tabela 3.4: Predições de Speedup por Tamanho de Problema
- Tabela 3.5: Metas de Qualidade de Solução

---

## LISTA DE FIGURAS

[To be generated automatically - will include:]

- Figura 3.1: Distribuição de Tamanho das Instâncias
- Figura 3.2: Análise de Memória VRAM
- Figura 4.1: Curva de Speedup GPU vs Tamanho do Problema
- Figura 4.2: Comparação de Qualidade: NN vs 2-opt vs SA+2-opt

---

## 1. INTRODUÇÃO

### 1.1 Justificativa

This project addresses the computational challenge of solving combinatorial routing problems (TSP/VRP) which are NP-hard in nature. While exact methods guarantee optimal solutions, they become computationally infeasible for large instances. Heuristic and metaheuristic approaches provide high-quality solutions in reasonable time, but their computational intensity makes them ideal candidates for GPU acceleration.

> **VRP Types for this TCC:**
>
> - **CVRP (Capacitated VRP):** Base variant with vehicle capacity constraints - CORE FOCUS
> - **TSP:** Special case of VRP (single vehicle, no capacity) - ESSENTIAL for baseline
> - **Future consideration (optional):** MDVRP (Multi-Depot), VRPPD (Pickup-Delivery) - only if time permits after core implementation

Modern GPUs offer massive parallel processing capabilities that can dramatically accelerate neighborhood evaluation in local search algorithms. By implementing a modular heuristic framework with both NumPy (CPU) and CuPy (GPU) backends, we can scientifically measure the performance impact of GPU acceleration on solution quality within fixed time budgets.

#### 1.1.1 Historical context and Key Motivations (Don't know if this should be here.)

> To write. Use specially Cook's book: **"In Pursuit of the Traveling Salesman"**

### 1.2 Objetivos

#### 1.2.1 Objetivo Geral

Design, implement, and benchmark a modular framework for solving routing problems (TSP/CVRP), comparing the performance and solution quality of various improvement and metaheuristic strategies on both CPU and GPU backends.

#### 1.2.2 Objetivos Específicos

1. Implement modular improvement heuristics (2-opt, 3-opt, Or-opt) with vectorized operations.
    > - why these? Aren't there others in my references?
    > - which others could I use? (focusing on my current bibliographic reference?)
    > - Are they easier to implement?
2. Develop metaheuristic strategies (GA, SA, TS) that can utilize different operators
    > - How many hybrid strategies should I analyze?
3. Create hybrid methods combining global search strategies with local search operators
4. Compare CPU (NumPy) vs GPU (CuPy) performance using identical algorithmic logic
5. Analyze solution quality vs runtime trade-offs across different algorithm combinations
6. Validate implementations against standard benchmark instances from TSPLIB and CVRPLIB

> - must take care to not overload the project scope
> - both the modular design and the GPU acceleration are key contributions, should I focus only on one? Which would be a better option for a close schedule?
> - Should I do both for the main TCC or focus on only the gpu acceleration part and the modular approach as an appendix or something else?

### 1.3 Limitações do Trabalho

- Focus on heuristic/metaheuristic approaches (no exact methods like branch-and-bound)
- Limited to symmetric TSP, asymmetric TSP (ATSP), and capacitated VRP (CVRP) - no time windows or other advanced VRP constraints
    > maybe `MDVRP`
- Comparison limited to internal CPU vs GPU benchmarking (not against external state-of-the-art published results)
    > [!note] did not understand
    > What do you mean by this?
- Selected subset of **30 benchmark instances** (18 TSP, 6 ATSP, 6 CVRP) from TSPLIB and CVRPLIB, not entire problem libraries
- Hardware-specific results (GTX 1050 Mobile with 4GB VRAM) - findings may not generalize to other GPU architectures
    > Results demonstrate GPU acceleration on mid-range mobile hardware. Higher-end GPUs (e.g., RTX 4090 with 24GB VRAM) would likely show greater speedups and support larger problem instances. A brief comparison on high-end hardware may be included if access is available, but is not required for experimental validity.

---

## 2. REVISÃO BIBLIOGRÁFICA

[To be expanded based on literature review - see Literature Review Plan section below]

> **Bibliography Structure Notes:**
>
> Use refs.bib entries to support:
>
> 1. **Section 2.1:** TSP/VRP complexity theory (cite foundational papers)
> 2. **Section 2.2:** Heuristic algorithm papers (original algorithm publications)
> 3. **Section 2.3:** Metaheuristic survey papers (SA parameter tuning guidelines)
> 4. **Section 2.5:** GPU computing papers (fujimoto2011highly for distance matrix, general GPU optimization surveys)
>
> **See LITERATURE_REVIEW_PLAN.md for detailed reading list and citation strategy**

### 2.1 Combinatorial Optimization Problems

- TSP fundamentals: problem definition, optimal tour properties, complexity analysis
- VRP variants and constraints: capacitated (CVRP), multi-depot (MDVRP), pickup-delivery (VRPPD)
- NP-hardness implications: why heuristics are necessary, approximation guarantees

> **VRP Variants to Cover (based on CVRPLIB dataset):**
>
> **Primary focus:** Capacitated VRP (CVRP)
>
> - Most common variant in literature
> - All CVRPLIB instances are CVRP-based
> - Single depot, homogeneous fleet, capacity constraints only
>
> **Mention briefly (literature context only):**
>
> - MDVRP (Multi-Depot): Multiple depots, route assignment complexity
> - VRPPD (Pickup-Delivery): Precedence constraints, paired locations
> - VRPTW (Time Windows): Time-based constraints, affects local search feasibility
>
> **Skip entirely:** VRPB (Backhauls), SDVRP (Split Delivery), PVRP (Periodic)
>
> - Not present in selected benchmark instances
> - Add implementation complexity without GPU acceleration insights
>
> **Rationale:** CVRP demonstrates all core concepts for GPU acceleration. Other variants differ in CONSTRAINT HANDLING (route validity checks), not DISTANCE CALCULATIONS (where GPU helps).

### 2.2 Heuristic Approaches

Construction heuristics generate initial feasible solutions, while improvement heuristics refine existing solutions through local search. This work focuses on simple, GPU-parallelizable operators suitable for demonstrating hardware acceleration benefits.

#### 2.2.1 Construction Heuristics

**Nearest Neighbor** heuristic provides fast initial solution construction through greedy nearest-city selection [cite: foundational TSP papers]. While simple, it demonstrates O(n²) complexity patterns relevant to GPU optimization analysis.

> **Other construction methods (literature context only, not implemented):**
>
> - Clarke-Wright Savings: Route merging for CVRP [cite]
> - Christofides: 1.5-approximation via MST + matching [cite] - O(n³) complexity makes it impractical for TCC scope
> - Insertion heuristics: Incremental tour building variants [cite]

#### 2.2.2 Improvement Heuristics

**2-opt local search** removes edge crossings through systematic edge pair exchanges [cite: 2-opt original paper]. Its O(n²) neighborhood size and independent move evaluation make it ideal for GPU vectorization.

> **Implementation focus:**
>
> - 2-opt provides clear demonstration of GPU parallelization benefits
> - Vectorized implementation evaluates all n(n-1)/2 moves simultaneously on GPU
> - Primary comparison point for CPU vs GPU performance analysis
>
> **Additional operators considered but not implemented:**
>
> - **Or-opt:** Sequence relocation (1-3 nodes) - similar parallelization pattern to 2-opt, could add in Week 2-3 if time permits
> - **3-opt:** Triple edge exchange - 7 reconnection cases, O(n³) complexity, vectorization significantly more complex
> - **Cross-exchange:** VRP-specific inter-route swaps - requires route management logic
> - **Lin-Kernighan:** Variable-depth search - sequential decision-making incompatible with GPU parallelization approach
>
> **Rationale for scope limitation:**
> Each additional operator requires 3-5 days (algorithm logic + GPU vectorization + validation). 2-opt alone sufficient to demonstrate GPU acceleration concepts for TCC timeframe.

### 2.3 Metaheuristic Strategies

Metaheuristics guide the search process to escape local optima through acceptance criteria, memory structures, or population-based evolution. This work implements Simulated Annealing as a representative trajectory-based metaheuristic suitable for GPU-accelerated local search integration.

#### 2.3.1 Genetic Algorithms (Reference Only)

Population-based evolutionary search using crossover, mutation, and selection operators [cite: GA surveys, routing-specific implementations]. While highly parallelizable, implementation complexity exceeds TCC scope.

> **GA parallelization potential (future work):**
>
> - Population evaluation: Highly parallel (evaluate N individuals simultaneously)
> - Crossover operations: Can parallelize across population pairs
> - Fitness calculation: Embarrassingly parallel (each individual independent)

#### 2.3.2 Simulated Annealing

Probabilistic acceptance of worse solutions enables escape from local optima through temperature-controlled exploration [cite: Kirkpatrick et al. 1983]. Acceptance probability follows $P(\Delta E, T) = e^{-\Delta E / T}$ with geometric or adaptive cooling schedules [cite: SA parameter tuning surveys].

> **SA parameter tuning guidelines from literature:**
>
> - Initial temperature selection: Accept ~80-90% of random moves initially [cite]
> - Cooling schedule: Geometric (T ← αT, α ∈ [0.8, 0.99]) most common [cite]
> - Stopping criteria: Fixed iterations, temperature threshold, or convergence detection [cite]
>
> **SA Implementation Focus (Week 2 implementation note):**
>
> - Core of hybrid approach (SA + 2-opt)
> - GPU accelerates MOVE EVALUATION (2-opt neighborhood), not SA logic
> - Temperature schedule runs on CPU, move acceptance on CPU, only move costs on GPU
> - SA provides global search diversification, 2-opt provides local intensification

#### 2.3.3 Tabu Search (Reference Only)

Memory-based search preventing cycling through short-term tabu lists and aspiration criteria [cite: Glover, TS for routing]. Complex memory management adds implementation overhead with marginal GPU benefit for TCC scope.

> **TS described for completeness in literature review, not implemented in TCC.**

### 2.4 Hybrid Approaches

- **Memetic algorithms:** Combination of GA population search + local search intensification
- **Benefits of hybridization:** Global exploration + local exploitation synergy
- **Literature examples:** GA+2-opt, SA+3-opt, TS+Or-opt combinations
- Performance comparison studies: hybrid vs pure metaheuristics

> **Hybrid Focus:**
> Primary implementation: SA + 2-opt (trajectory-based + local search)
> Literature coverage: Include Memetic (GA+LS) examples for context

### 2.5 GPU Computing for Optimization

- **CUDA architecture basics:** Thread hierarchy, memory model, kernel execution
- **CuPy framework:** NumPy-compatible GPU arrays, automatic memory management
- **Vectorization strategies:** Loop elimination, array broadcasting, reduction operations
- **Memory management:** Host-device transfer costs, memory pool optimization
- **Performance characteristics:** When GPU provides benefit (problem size, parallelism degree)
- **Routing-specific GPU applications:** Distance matrix calculations, neighborhood evaluation

> **GPU Literature Coverage:**
>
> - **Primary:** fujimoto2011highly (GPU distance matrix computation)
> - **Supporting:** General GPU optimization surveys
> - **Application focus:** Local search neighborhood evaluation parallelization

---

## 3. MATERIAIS E MÉTODOS

### 3.1 System Specifications

- **CPU:** Intel Core i7-7700HQ @ 2.80GHz (8 cores)
- **RAM:** 16 GB
- **GPU:** NVIDIA GeForce GTX 1050 Mobile (4 GB VRAM, Pascal architecture)
- **Software:** Python 3.x, NumPy, CuPy 13.4.1, CUDA 12.8

### 3.2 Backend Architecture

**Design Philosophy: Drop-In Replacement Pattern**

The backend architecture uses a simple module aliasing pattern enabling CPU/GPU agnostic algorithms: `xp = cupy if use_gpu else numpy`. This design directly implements the philosophy established by **Okuta et al. (2017)** in their CuPy library specification: "CuPy is designed as a drop-in replacement for NumPy, providing a GPU-accelerated array library with an API identical to NumPy's core functionality." [^okuta2017cupy] By aliasing the array module at runtime, algorithms written for NumPy can be executed on GPU without code modification.

[^okuta2017cupy]: Okuta, R., Unno, Y., Nishino, D., Hido, S., & Loomis, C. (2017). CuPy: A NumPy-Compatible Library for NVIDIA GPU Calculations. _Proceedings of Workshop on Machine Learning Systems (LearningSys) in The Thirty-first Annual Conference on Neural Information Processing Systems (NIPS)_. <https://learningsys.org/nips17/assets/papers/paper_16.pdf>

#### 3.2.1 Module Pattern vs. OOP Inheritance

This implementation uses **module aliasing** rather than object-oriented abstraction (`CPUBackend`, `GPUBackend` classes). This choice prioritizes simplicity and zero-cost abstraction:

- **No runtime overhead**: Direct module function calls without method dispatch or virtual function indirection
- **Minimal code**: One-line backend selection vs. multiple class definitions and factory patterns
- **Alignment with CuPy's design**: Okuta et al. explicitly designed CuPy for drop-in replacement usage, not OOP wrapping

**Trade-off**: Requires backend parameter propagation discipline across function call chains (see Appendix A for implementation examples).

#### 3.2.2 Protocol-Based Type Safety (PEP 544)

Type checking uses **structural subtyping** (protocols) rather than nominal inheritance. Both NumPy and CuPy satisfy a minimal `BackendModule` protocol **implicitly** - no explicit inheritance required. This follows **PEP 544** (Protocols: Structural subtyping), enabling type-safe duck typing validated by MyPy. [^pep544]

[^pep544]: PEP 544 – Protocols: Structural subtyping (static duck typing). Python Enhancement Proposals. <https://peps.python.org/pep-0544/>

**Benefits**: Type hints document required backend functionality without coupling to specific implementations. Future array libraries (JAX, PyTorch tensors) can integrate by satisfying the protocol.

**Implementation**: Every algorithm accepts an optional `backend` parameter (defaults to NumPy), aliased to `xp` internally. Nested function calls propagate this parameter to ensure consistent backend usage across the call chain. See Appendix A.2 for MST and Christofides examples demonstrating backend parameter patterns.

#### 3.2.3 Preliminary Validation

Preliminary testing on berlin52 (52 nodes), lin318 (318 nodes), and d2103 (2,103 nodes) confirmed backend abstraction correctness (identical tour outputs for NumPy and CuPy backends) and revealed GPU overhead for construction heuristics due to sequential dependencies.

> [!important] **Validation Methodology Requirements**
>
> Complete academic validation requires:
>
> - **Statistical Analysis**: Multi-run experiments (n≥30) with confidence intervals and hypothesis testing
> - **Correctness Thresholds**: Define acceptable tolerance for floating-point differences between backends (e.g., $\epsilon < 10^{-6}$ for tour costs)
> - **Expanded Test Suite**: Validate on full benchmark set (30 instances spanning 7-15,112 nodes, not just 3 preliminary instances)
> - **Performance Analysis**: GPU overhead breakeven point analysis addressing Research Question Q1 (Section 3.4.1)
> - **Hypothesis Testing**: Statistical validation of claims regarding GPU suitability for sequential vs. parallel algorithms
>
> **Status**: Preliminary validation complete (correctness confirmed on 3 instances). Comprehensive statistical analysis is a separate task (See project_status.md TODO list).

### 3.3 Algorithm Implementation

> [!note] We'll focus
>
> - Why? this heuristic was chosen, importance, etc.
> - How? was this heuristic built
> - Citing the proper references from [`refs.bib`](./documentation/refs.bib)
> - Choose only 2 for construction heuristic: less important for the project
> - Implement the 4 bin packing algorithms:
>   - BFD and FFD
>   - One exact method for bin packing
> - The split protocol:
>   - split and split

#### 3.3.1 Construction Heuristic (Initial Solution)

##### TSP Construction heuristics

**Implemented: Nearest Neighbor**

- Simple greedy tour construction: always move to nearest unvisited city
- $O(n^2)$ complexity, runs on CPU
- Provides consistent starting point for improvement phase comparison
- Implementation: ~1 day (MVP Day 1)

> **Other TSP construction methods considered:**
>
> - Clark-wright savings
> - Christofides (TSP approximation): 1.5-approximation guarantee, but $O(n^3)$ complexity + matching algorithm = 5+ days
> - MST-based heuristics: Prim's algorithm for initial tour. Similar complexity to Nearest Neighbor.
> - **Decision:** Nearest Neighbor sufficient for demonstrating improvement heuristic performance. Construction quality not the focus of GPU comparison.

#### 3.3.2 Improvement Heuristic (Local Search)

**Implemented: 2-opt**

- Edge pair exchange to remove tour crossings
- O(n²) neighborhood size enables clear GPU parallelization demonstration
- Deterministic: same initial tour → same final result (validates GPU correctness)
- Implementation: ~2 days (MVP Day 3-4: CPU version Day 3, GPU vectorization Day 4)

> **Other operators considered:**
>
> - **Or-opt:** Relocate sequences of 1-3 cities. Similar vectorization pattern to 2-opt. Could add Week 2-3 if time permits to show operator modularity.
> - **3-opt:** 7 reconnection cases, O(n³) complexity. Vectorization significantly more complex, diminishing returns for GPU demonstration.
> - **Cross-exchange (VRP):** Inter-route swaps for CVRP. Requires route management logic, adds 3-4 days.
> - **Lin-Kernighan:** Variable-depth adaptive search. Sequential decision-making incompatible with full GPU parallelization.
>
> **Implementation time estimates:**
>
> - Each additional operator: 3-5 days (algorithm logic + GPU vectorization + testing)
> - TCC scope: 2-opt alone demonstrates core GPU acceleration concept

#### 3.3.3 Metaheuristic Strategy

**Implemented: Simulated Annealing (SA)**

- Probabilistic acceptance enables escape from local optima
- Temperature schedule controls exploration/exploitation balance
- Integrates with 2-opt for hybrid SA+2-opt approach
- Implementation: ~2-3 days (Week 2)

> **Other metaheuristics considered:**
>
> - **Genetic Algorithm (GA):** Population-based, highly parallelizable fitness evaluation. But adds complexity:
>
>   - Crossover operators for routing (PMX, OX, CX): 2-3 days
>   - Population management and selection: 1-2 days
>   - Integration with 2-opt for Memetic Algorithm: 1-2 days
>   - **Total:** 4-7 additional days beyond SA
>
> - **Tabu Search (TS):** Memory-based search with tabu lists and aspiration criteria. Memory management adds complexity with marginal GPU benefit (GPU accelerates move evaluation, not memory logic).
>
> - **Iterated Local Search (ILS):** Restart-based with perturbations. Similar complexity to SA, not worth implementing both.
>
> **Decision:** SA sufficient to demonstrate hybrid metaheuristic + local search + GPU acceleration. GA/TS mentioned in literature review for completeness.

#### 3.3.4 Hybrid Approach

**Implemented: SA + 2-opt**

- SA provides global search diversification (escape local optima)
- 2-opt provides local search intensification (refinement)
- GPU accelerates 2-opt neighborhood evaluation within SA framework
- Implementation: Integrated with SA implementation (Week 2)

> **Implementation note:**
>
> - SA logic (temperature, acceptance) runs on CPU
> - 2-opt move evaluation runs on GPU (vectorized distance calculations)
> - Demonstrates how GPU acceleration applies to metaheuristic frameworks

#### 3.3.5 Implementation Strategy: Vectorization and Backend Integration

**Core Approach: Vectorization-First Design**

All algorithms implement vectorization as the primary parallelization strategy, avoiding explicit loops where possible. This aligns with NumPy/CuPy's design philosophy and enables efficient GPU utilization through batch operations on array data.

**Backend Parameter Propagation:**

Every algorithm function signature includes an optional `backend` parameter (defaults to NumPy for CPU-only environments). Internal operations use the aliased module (`xp = backend if backend is not None else np`), and nested function calls explicitly propagate the backend parameter to ensure consistency across the entire call chain. This discipline prevents accidental mixing of NumPy and CuPy operations, which would cause performance degradation and potential errors.

**Type Hints for Academic Rigor:**

All functions are annotated with input/output types following Python's type hinting conventions. Protocol-based backend typing (Section 3.2.2) enables MyPy static analysis, catching backend mismatches and type errors during development rather than at runtime.

> [!note] **Kernel Launch Optimization**
>
> Construction heuristics required careful optimization to reduce GPU kernel launches:
>
> - **Original Implementation**: 4 CuPy operations per iteration → $4n$ kernel launches for $n$-node problem
> - **Optimized Implementation**: 3 operations per iteration → $3n$ kernel launches (25% reduction)
> - **Optimization Strategy**: Combine operations where possible (e.g., fuse masking with distance calculation)
>
> Despite optimization, construction heuristics remain $O(n)$ in kernel launches due to inherent sequential dependencies. Each iteration's result determines the next iteration's computation, preventing full parallelization. This finding validates the focus on improvement heuristics (2-opt, Or-opt), where parallelism occurs across independent move evaluations rather than sequential construction steps.

**Vectorization Results:**

Implemented and validated for construction heuristics on preliminary test instances (berlin52, lin318, d2103):

- **Nearest Neighbor**: Vectorized with identical results across NumPy and CuPy backends
- **MST-based (Prim's)**: Vectorized distance matrix operations, consistent tour construction
- **Christofides**: Partial implementation (matching and tour construction vectorized)

**Implementation Timeline:**

- Week 1: Nearest Neighbor vectorization (3 days) + backend testing (1 day)
- Week 2: MST vectorization (2 days) + Christofides completion (3 days)
- Week 3: 2-opt vectorization (4 days)
- Week 4: Simulated Annealing integration (3 days)

### 3.4 Benchmark Problem Selection

**Selection Strategy**: 30 routing problems (18 TSP, 6 ATSP, 6 CVRP) spanning 7 → 15,112 nodes, selected to address five core research questions while respecting the 4GB VRAM constraint.

**Hardware Constraint**: GTX 1050 Mobile 4GB VRAM  
**Maximum Feasible Instance**: d15112 (15,112 nodes, 1.70GB distance matrix = 42.5% VRAM)

---

#### 3.4.1 Research Questions Driving Selection

**Q1: GPU Overhead Threshold** - At what problem size does GPU become beneficial compared to CPU?

- **Hypothesis**: GPU incurs overhead (memory transfer, kernel launch) making it slower for small instances[^gpu_overhead]
- **Test Instances**: 5 tiny instances <50 nodes (burma14, berlin52, br17, eil7, ftv47)
- **Expected Breakeven**: ~100 nodes for TSP/ATSP, higher for CVRP (route logic overhead)
- **TCC Contribution**: Establishes lower bound for GPU efficiency, demonstrates overhead phenomenon

[^gpu_overhead]: GPU parallelization incurs overhead from memory transfer time (host ↔ device) and kernel launch latency. For parallel algorithms to be beneficial, the computational speedup must exceed this overhead cost. Schulz et al. (2013) provide a comprehensive survey of GPU computing applied to routing problems, discussing overhead considerations and breakeven points for different problem sizes [@schulz2013gpu]

**Q2: Scaling Behavior** - How does GPU speedup scale with problem size?

- **Hypothesis**: Superlinear speedup growth as parallelism degree increases, plateauing at memory limits[^gpu_scaling]
- **Test Instances**: 18 size points spanning 7 → 15,112 nodes (full spectrum coverage)
- **Expected Pattern**: Exponential growth (0.5x at n=14 → 70x at n=6000) with plateau at n=15,000
- **TCC Contribution**: Speedup curve analysis (Chapter 4), demonstrates GPU sweet spot (n > 500)

[^gpu_scaling]: GPU-accelerated TSP local search algorithms demonstrate significant speedup for large problem instances. Fujimoto & Tsutsui (2011) implemented parallel 2-opt local search on CUDA, achieving substantial performance improvements over CPU implementations for problems with thousands of cities [@fujimoto2011highly]. Rocki & Suda (2013) present high-performance GPU-accelerated local optimization techniques for TSP, demonstrating the effectiveness of parallel neighborhood evaluation [@tsp_gpu].

**Q3: Memory Bottlenecks** - When does 4GB VRAM limit performance?

- **Hypothesis**: Performance degrades when distance matrix + algorithmic overhead exceeds VRAM capacity[^vram_bottleneck]
- **Test Instances**: 5 largest (fl1577, d2103, pcb3038, rl5934, d15112)
- **Critical Validation**: d15112 (1.70GB = 42.5% VRAM) as maximum feasible within hardware constraint
- **TCC Contribution**: Memory management validation, hardware scalability limits discussion

[^vram_bottleneck]: GPU memory constraints significantly impact algorithm performance when problem size approaches device memory capacity. Memory bandwidth saturation and reduced cache efficiency cause performance degradation. Abdelatti & Sodhi (2020) discuss GPU memory management strategies for routing problems, emphasizing the importance of memory-aware algorithm design [@abdelatti2020improvedgpuheuristic].

**Q4: Problem Structure Impact** - Do different geometric patterns affect GPU performance?

- **Hypothesis**: Structure affects solution quality but not GPU parallelization efficiency (distance computation is structure-agnostic)[^structure_agnostic]
- **Test Instances**: Random (rat783), clustered (ch130, d1291), geometric (kroA100), circuit board (pcb3038)
- **Expected Result**: Similar GPU speedups across structures (variance <15%)
- **TCC Contribution**: Generalizability analysis, demonstrates GPU benefit independent of problem geometry

[^structure_agnostic]: GPU parallelization of distance matrix computation and local search move evaluation operates on coordinates/distances, independent of problem structure. The computational pattern remains identical regardless of whether cities are randomly distributed, clustered, or follow geometric patterns, as parallel evaluation processes all pairwise distances or 2-opt moves uniformly. This structure-independence is inherent to data-parallel SIMT (Single Instruction, Multiple Threads) execution model [@rocki2013tsp].

**Q5: Problem Type Comparison** - Do TSP, ATSP, and CVRP benefit differently from GPU acceleration?

- **Hypothesis**: GPU accelerates distance calculations (common to all), but constraint handling (route validation) adds CPU overhead[^problem_type_comparison]
- **Test Instances**: 18 TSP (symmetric), 6 ATSP (asymmetric matrices), 6 CVRP (capacity constraints)
- **Expected Results**: TSP ≈ ATSP speedup > CVRP speedup (route logic reduces GPU advantage by 20-30%)
- **TCC Contribution**: Comparative analysis across problem types, distinguishes GPU benefit from problem-specific logic

[^problem_type_comparison]: While TSP algorithms can be directly adapted to ATSP (using asymmetric distance matrices), CVRP requires additional constraint handling that introduces computational overhead. CVRP typically requires capacity validation and multi-route optimization, which reduce GPU's purely computational advantage. GPU implementations for heterogeneous vehicle routing problems must balance parallel computation with constraint checking [@benaini2015gpu; @benaini2018genetic].

**Statistical Validation Methodology**:

To rigorously test these hypotheses, the following statistical approach will be employed:

1. **Number of Experimental Runs**:

    - **Deterministic algorithms** (Nearest Neighbor, 2-opt): 1 run per instance, as results are reproducible
    - **Stochastic algorithms** (Simulated Annealing): 30 runs per instance to establish statistical significance

2. **Statistical Tests**:

    - **Hypothesis Q1 (Overhead Threshold)**: Descriptive statistics (mean execution time) to identify break-even problem size where $GPU_{time} < CPU_{time}$
    - **Hypothesis Q2 (Scaling Behavior)**: Regression analysis to model speedup as a function of problem size $(speedup = f(n))$, reporting $R^2$ and regression coefficients
    - **Solution Quality Comparison**: Paired t-test to compare CPU vs GPU solution quality (gap to optimal)
    - **Hypothesis Q5 (Problem Type Comparison)**: One-way ANOVA to test if mean speedups differ significantly across TSP, ATSP, and CVRP categories

3. **Confidence Intervals**: 95% confidence intervals will be reported for all stochastic algorithm results (SA)

4. **Correctness Validation**: For deterministic algorithms (2-opt), CPU and GPU implementations must produce **identical** final tours to validate implementation correctness

---

#### 3.4.2 MVP Benchmark Selection (3 Instances)

For rapid prototyping and initial validation of GPU acceleration capabilities, **three representative TSP instances** from the TSPLIB benchmark library[^reinelt1991] were selected. These instances systematically cover the GPU performance spectrum from overhead-dominated small problems to peak-performance large-scale problems:

**MVP Benchmark Set**

| Instance                   | Nodes | Edge Type | Memory  | Purpose                 | Expected Speedup          | Research Questions          |
| -------------------------- | ----- | --------- | ------- | ----------------------- | ------------------------- | --------------------------- |
| **berlin52**[^reinelt1991] | 52    | EUC_2D    | <0.01GB | Overhead demonstration  | 0.7-1.2x (near breakeven) | Q1 (GPU overhead threshold) |
| **lin318**[^reinelt1991]   | 318   | EUC_2D    | <0.01GB | GPU advantage showcase  | 15-20x (sweet spot)       | Q2 (scaling behavior)       |
| **d2103**[^reinelt1991]    | 2,103 | EUC_2D    | 0.03GB  | Large-scale performance | 45-55x (peak performance) | Q2, Q3 (scaling & memory)   |

**Rationale for MVP Selection**:

1. **berlin52** (52 cities): Classic TSPLIB benchmark widely cited in TSP literature[^reinelt1991]. Demonstrates GPU overhead on small instances where memory transfer costs dominate computational benefits. Expected near-breakeven performance (0.7-1.2x) validates overhead hypothesis (Q1).

2. **lin318** (318 cities): Medium-sized instance representing the GPU "sweet spot" where parallelism benefits clearly outweigh overhead. Expected 15-20x speedup demonstrates clear GPU advantage and validates scaling hypothesis (Q2). Instance size ensures comfortable memory usage (<0.01GB = <0.25% VRAM).

3. **d2103** (2,103 cities): Large-scale instance testing peak GPU performance and memory efficiency. Distance matrix footprint of 0.03GB (0.8% VRAM) ensures safe execution while demonstrating scalability to large problems. Expected 45-55x speedup validates GPU scaling at high parallelism degrees (Q2) and tests memory management strategies (Q3).

**Size Coverage**: MVP spans **40x node range** (52 → 2,103), covering three critical performance zones:

- **Overhead zone** (n < 100): berlin52 demonstrates GPU overhead where CPU may be faster
- **Advantage zone** (100 ≤ n < 1000): lin318 shows clear GPU benefit (15-20x)
- **Peak zone** (n ≥ 1000): d2103 demonstrates maximum GPU speedup (45-55x)

This three-instance subset enables rapid validation of core hypotheses before expanding to the full 30-instance benchmark suite.

**Speedup Prediction Methodology**: Expected speedup ranges shown in tables are derived from three sources:

1. **GPU TSP Literature**: Fujimoto & Tsutsui (2011) reported 20-50x speedup on TSPLIB instances (n=1,000-3,000) using CUDA-based 2-opt local search on NVIDIA GPUs[^fujimoto2011]. Their results demonstrate that GPU acceleration becomes significant for medium-to-large instances.

2. **Theoretical Hardware Analysis**: GTX 1050 Mobile specifications provide theoretical parallelism: 384 CUDA cores vs 4 CPU threads = 96x theoretical peak throughput. However, this peak is never achieved due to memory bandwidth limitations and algorithmic overhead.

3. **Overhead Adjustment for Problem Size**:
    - **Small instances** (n < 100): Memory transfer overhead dominates computation time, resulting in 0.5-1.5x speedup (CPU may be faster)
    - **Medium instances** (100 ≤ n < 1000): Computational benefits exceed memory transfer costs, yielding 5-25x speedup
    - **Large instances** (n ≥ 1000): Peak GPU performance, but limited by memory bandwidth saturation, plateauing at 50-80x

Actual measured speedups will be reported in Chapter 4 and compared to these predictions to validate the GPU overhead threshold hypothesis (Q1) and scaling behavior hypothesis (Q2).

**Solution Quality Validation**: Known optimal tour lengths for all TSPLIB instances are documented in Reinelt (1991) and maintained at the TSPLIB repository (<http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/>). These optimal values will be used to calculate solution quality gaps (percentage above optimal) when evaluating algorithm performance in Chapter 4. CVRP optimal solutions are similarly documented in CVRPLIB[^christofides1969].

---

#### 3.4.3 Complete Benchmark Instance Tables (30 Instances)

The full experimental validation employs **30 routing problem instances** spanning three problem types (TSP, ATSP, CVRP) and six size tiers (Tiny to Extreme). All instances have been validated for database availability and hardware memory constraints (GTX 1050 Mobile 4GB VRAM).

> **Note on Table Usage**: These comprehensive tables serve dual purposes: (1) academic documentation of experimental design, and (2) implementation reference for loading instances from the database. Key instances for understanding research design are highlighted in **bold** (MVP instances and maximum feasible instance d15112).

##### TSP Instances (18 total - 60%)

All TSP instances use symmetric distance matrices with various edge weight types (EUC_2D, GEO, ATT).

| #   | Instance     | Nodes  | Edge Type | Tier       | Memory (GB) | % VRAM    | Expected Speedup | Research Questions |
| --- | ------------ | ------ | --------- | ---------- | ----------- | --------- | ---------------- | ------------------ |
| 1   | **berlin52** | 52     | EUC_2D    | Tiny       | <0.01       | <0.1%     | 0.7-1.2x         | Q1, Q4             |
| 2   | kroA100      | 100    | EUC_2D    | Small      | <0.01       | <0.1%     | 1.5-3x           | Q1, Q2             |
| 3   | pr152        | 152    | EUC_2D    | Small      | <0.01       | <0.1%     | 3-5x             | Q2                 |
| 4   | gr202        | 202    | GEO       | Medium     | <0.01       | <0.1%     | 5-8x             | Q2, Q4             |
| 5   | **lin318**   | 318    | EUC_2D    | Medium     | <0.01       | <0.1%     | 15-20x           | Q2, Q4             |
| 6   | rd400        | 400    | EUC_2D    | Medium     | <0.01       | <0.1%     | 18-25x           | Q2                 |
| 7   | pcb442       | 442    | EUC_2D    | Medium     | <0.01       | <0.1%     | 20-28x           | Q2, Q4             |
| 8   | d493         | 493    | EUC_2D    | Medium     | <0.01       | <0.1%     | 22-30x           | Q2                 |
| 9   | att532       | 532    | ATT       | Large      | <0.01       | 0.1%      | 25-35x           | Q2, Q4             |
| 10  | d657         | 657    | EUC_2D    | Large      | <0.01       | 0.1%      | 28-38x           | Q2                 |
| 11  | rat783       | 783    | EUC_2D    | Large      | 0.00        | 0.1%      | 30-40x           | Q2, Q4             |
| 12  | pr1002       | 1,002  | EUC_2D    | Large      | 0.01        | 0.2%      | 35-45x           | Q2                 |
| 13  | d1291        | 1,291  | EUC_2D    | Large      | 0.01        | 0.3%      | 40-50x           | Q2, Q4             |
| 14  | fl1577       | 1,577  | EUC_2D    | Very Large | 0.02        | 0.5%      | 42-52x           | Q2, Q3             |
| 15  | rl1889       | 1,889  | EUC_2D    | Very Large | 0.03        | 0.7%      | 45-55x           | Q2, Q3             |
| 16  | **d2103**    | 2,103  | EUC_2D    | Very Large | 0.03        | 0.8%      | 45-55x           | Q2, Q3             |
| 17  | pcb3038      | 3,038  | EUC_2D    | Very Large | 0.07        | 1.7%      | 50-60x           | Q2, Q3, Q4         |
| 18  | **d15112**   | 15,112 | EUC_2D    | Extreme    | **1.70**    | **42.5%** | **50-80x**       | Q2, Q3             |

**Edge Weight Types**: EUC_2D (Euclidean 2D, 16 instances), GEO (Geographical haversine, 1 instance), ATT (Pseudo-Euclidean, 1 instance)

##### ATSP Instances (6 total - 20%)

All ATSP instances use **EXPLICIT** edge weights (precomputed asymmetric distance matrices). These instances have **NULL coordinates** in the database and require loading distance matrices directly from the edge_weights table.

| #   | Instance | Nodes | Edge Type | Tier   | Memory (GB) | % VRAM | Expected Speedup      | Research Questions |
| --- | -------- | ----- | --------- | ------ | ----------- | ------ | --------------------- | ------------------ |
| 19  | br17     | 17    | EXPLICIT  | Tiny   | <0.01       | <0.1%  | 0.3-0.7x (CPU faster) | Q1, Q5             |
| 20  | ry48p    | 48    | EXPLICIT  | Tiny   | <0.01       | <0.1%  | 0.7-1.2x              | Q1, Q5             |
| 21  | ft53     | 53    | EXPLICIT  | Small  | <0.01       | <0.1%  | 1-2x                  | Q2, Q5             |
| 22  | ft70     | 70    | EXPLICIT  | Small  | <0.01       | <0.1%  | 1-2x                  | Q2, Q5             |
| 23  | ftv170   | 171   | EXPLICIT  | Small  | <0.01       | <0.1%  | 5-10x                 | Q2, Q5             |
| 24  | rbg403   | 403   | EXPLICIT  | Medium | <0.01       | <0.1%  | 20-30x                | Q2, Q5             |

> **⚠️ ATSP Implementation Note**: All ATSP instances have NULL coordinates (x=NULL, y=NULL) because they use precomputed asymmetric distance matrices. Distance matrices must be loaded from `edge_weights` table, not computed from coordinates.

##### CVRP Instances (6 total - 20%)

Capacitated Vehicle Routing Problem instances with depot and customer demands. These instances test GPU acceleration in the presence of route validation constraints.

| #   | Instance                     | Nodes | Edge Type | Capacity | Tier   | Memory (GB) | % VRAM | Expected Speedup | Research Questions |
| --- | ---------------------------- | ----- | --------- | -------- | ------ | ----------- | ------ | ---------------- | ------------------ |
| 25  | eil22                        | 22    | EUC_2D    | 6000     | Tiny   | <0.01       | <0.1%  | 0.5-1x           | Q1, Q5             |
| 26  | eil31                        | 31    | EXPLICIT  | 140      | Tiny   | <0.01       | <0.1%  | 0.7-1.2x         | Q1, Q5             |
| 27  | eilA76                       | 76    | EUC_2D    | 140      | Small  | <0.01       | <0.1%  | 1-2x             | Q2, Q5             |
| 28  | eilA101                      | 101   | EUC_2D    | 200      | Small  | <0.01       | <0.1%  | 2-4x             | Q2, Q5             |
| 29  | gil262                       | 262   | EUC_2D    | 500      | Medium | <0.01       | <0.1%  | 10-15x           | Q2, Q5             |
| 30  | **Li_25**[^christofides1969] | 761   | EUC_2D    | 900      | Large  | <0.01       | 0.1%   | 25-35x           | Q2, Q3, Q5         |

> **⚠️ CVRP Scaling Limitation**: Only 6 CVRP instances meet the 4GB VRAM constraint. Larger instances like Flanders1 (20,001 nodes, 2.98GB) and Flanders2 (30,001 nodes, 6.71GB) were excluded due to memory violations, limiting CVRP scaling analysis to $n \leq 761$ compared to TSP ($n \leq 15,112$).

##### Size Distribution Summary

The 30-instance selection provides comprehensive coverage across six size tiers:

| Tier           | Node Range | Count | % Total | Primary Research Questions        | Representative Instances                                     |
| -------------- | ---------- | ----- | ------- | --------------------------------- | ------------------------------------------------------------ |
| **Tiny**       | n < 50     | 4     | 13.3%   | Q1 (GPU overhead)                 | br17, eil22, eil31, ry48p                                    |
| **Small**      | 50-200     | 8     | 26.7%   | Q1, Q2 (breakeven, early scaling) | berlin52, kroA100, pr152, gr202, ft53, ft70, ftv170, eilA101 |
| **Medium**     | 200-500    | 7     | 23.3%   | Q2, Q4 (GPU advantage, structure) | lin318, rd400, pcb442, d493, att532, rbg403, gil262          |
| **Large**      | 500-1500   | 6     | 20.0%   | Q2 (GPU sweet spot)               | d657, rat783, Li_25, pr1002, d1291, fl1577                   |
| **Very Large** | 1500-5000  | 4     | 13.3%   | Q2, Q3 (peak performance, memory) | rl1889, d2103, pcb3038                                       |
| **Extreme**    | n > 5000   | 1     | 3.3%    | Q3 (memory limits)                | d15112                                                       |

**Experimental Design Rationale**:

The 30-instance distribution was deliberately chosen to systematically test the five research hypotheses:

- **Size distribution**: Heavy emphasis on small-medium instances (50% with $n < 500$) precisely identifies GPU breakeven point (Q1) and captures early scaling behavior (Q2). Sufficient large instances (20% with $n > 500$) demonstrate GPU sweet spot where parallelism benefits are maximized.

- **Type distribution**: 60% TSP (most extensively benchmarked problem type in GPU literature), 20% ATSP (tests asymmetric distance matrices), 20% CVRP (tests GPU acceleration with route validation constraints) enables comparative analysis across problem types (Q5).

- **Structure diversity**: Random (rat783), clustered (d1291), geometric (kroA100), circuit board (pcb442, pcb3038), and geographical (gr202) patterns test generalizability hypothesis (Q4) that GPU speedup is structure-agnostic.

- **Classic benchmarks included**: berlin52, kroA100, att532, pr1002, d15112 are widely cited in TSP/ATSP literature, ensuring comparability with published GPU acceleration research[^fujimoto2011][^tsp_gpu].

**Statistical Validation Methodology**:

- **Deterministic algorithms** (Nearest Neighbor, 2-opt): Single run per instance, as results are reproducible. CPU and GPU implementations must produce **identical** final tours to validate correctness.

    > [!note] Questions, not to answer on TCC.
    >
    > - Doesn't the parallelization affect on this? Yes, parallelization can lead to different execution paths and timing, but the final solution must remain consistent across runs.

- **Stochastic algorithms** (Simulated Annealing): **30 independent runs** per instance to establish statistical significance. Sample size of 30 enables calculation of 95% confidence intervals and provides statistical power to detect speedup differences of 10% or greater (assuming coefficient of variation ≤ 15%, typical for SA runtime)[^statistical_power]. Results will report mean execution time, standard deviation, and 95% confidence intervals.
    > [!note] Questions, not to answer on TCC.
    >
    > - Which implementations could I make to take even more advantage of parallelization? Consider using more aggressive partitioning strategies, optimizing memory access patterns, and leveraging shared memory on the GPU.
- **Performance Metrics**: Execution time (milliseconds/seconds), solution quality (percentage gap to known optimal), memory usage (GB VRAM), and GPU speedup ratio (CPU time / GPU time).

[^statistical_power]: Sample size of n=30 is standard in experimental computer science for stochastic algorithms. With coefficient of variation (CV) of 15%, n=30 provides 80% statistical power to detect 10% mean differences at α=0.05 significance level. See Montgomery, D.C. (2017). _Design and Analysis of Experiments_, 9th ed., Wiley, for statistical power analysis methodology.

---

#### 3.4.4 Memory Footprint Analysis

**Distance Matrix Memory Formula**: For symmetric distance matrices (TSP, CVRP with EUC_2D):

$$
\text{memory}_{\text{GB}} = \frac{n \times n \times 8 \text{ bytes}}{1024^3}
$$

For asymmetric matrices (ATSP with EXPLICIT), memory footprint is identical but matrix is accessed asymmetrically ($d_{ij} \neq d_{ji}$).

**Critical Instances (Largest 5)**:

| Instance   | Nodes  | Distance Matrix | % of 4GB VRAM | Status                |
| ---------- | ------ | --------------- | ------------- | --------------------- |
| **d15112** | 15,112 | 1.70 GB         | 42.5%         | ✅ Feasible (maximum) |
| rl5934     | 5,934  | 0.26 GB         | 6.6%          | ✅ Comfortable        |
| pcb3038    | 3,038  | 0.07 GB         | 1.7%          | ✅ Comfortable        |
| d2103      | 2,103  | 0.03 GB         | 0.8%          | ✅ Comfortable        |
| fl1577     | 1,577  | 0.02 GB         | 0.5%          | ✅ Comfortable        |

**Memory Overhead Analysis**:

The maximum feasible instance (d15112) was determined based on VRAM allocation requirements for the implemented algorithms (Nearest Neighbor, 2-opt, Simulated Annealing):

> **Note**: Memory requirements vary by algorithm. Values below represent worst-case estimates for SA + 2-opt hybrid (highest memory overhead due to maintaining current/best tours and SA state). Simpler algorithms (NN, 2-opt only) require less working memory but same distance matrix allocation.

**1. Distance Matrix** (primary data structure - constant across all algorithms):

$$
\text{Memory}_{\text{dist}} = n^2 \times \text{sizeof(float64)} = 15112^2 \times 8 \text{ bytes} = 1,826,970,752 \text{ bytes} \approx 1.70 \text{ GB}
$$

This represents 42.5% of available 4GB VRAM.

**2. Algorithm Working Memory**:

- **Current tour**: $n \times \text{sizeof(int32)} = 15112 \times 4 = 60,448$ bytes $\approx 60$ KB
- **Best tour** (for SA): $n \times \text{sizeof(int32)} = 60,448$ bytes $\approx 60$ KB
- **SA state variables**: $\sim$100 bytes (temperature: float32, iteration counters: int32, acceptance statistics)

**Total algorithm working memory**: $\approx 120$ KB

**3. GPU Backend Overhead**:

- **CUDA context**: 150-400 MB (driver initialization, streams, memory management)[^cuda_context]
- **CuPy memory pool**: Dynamic allocation, empirically measured during experiments[^cupy_mempool]

[^cuda_context]: CUDA runtime initialization requires 150-400 MB VRAM for context creation, as documented in PyTorch GPU memory profiling (<https://github.com/pytorch/pytorch/issues/20532>) and NVIDIA developer forums reporting ~150 MB on TITAN X GPUs. Actual overhead varies by GPU architecture and driver version.
[^cupy_mempool]: CuPy official documentation states: "CuPy uses memory pool for memory allocations by default. The memory pool significantly improves the performance by mitigating the overhead of memory allocation and CPU/GPU synchronization" (<https://docs.cupy.dev/en/stable/user_guide/memory.html>). The pool dynamically caches freed memory blocks for reuse, with size determined by allocation patterns. Actual memory consumption will be measured empirically using `cupy.get_default_memory_pool().used_bytes()` during experiments.

**4. Operating System VRAM Reservation**:

Operating system display management and background GPU processes consume VRAM. This overhead will be **empirically measured** using `nvidia-smi` during experiments. Typical range in GPU computing literature: 200-800 MB, varying by:

- Operating system and display server architecture
- Number and resolution of displays
- Background applications using GPU acceleration
- GPU driver version and architecture

> **Note**: Experimental setup details (specific OS, desktop environment, hardware configuration) are documented in Section 3.5 (Experimental Methodology). VRAM overhead can be reduced by using compute-only GPU mode or dedicated compute GPU, but this is optional optimization not required for experimental validity.

**Total Estimated Memory** (d15112):

$$
\text{Memory}_{\text{total}} = 1.70 \text{ GB (distance matrix)} + 0.12 \text{ MB (algorithm)} + 0.15\text{-}0.40 \text{ GB (CUDA)} + 0.2\text{-}0.8 \text{ GB (OS/pool)}
$$

$$
\approx 2.0\text{-}2.9 \text{ GB} \text{ (50-73\% of 4GB VRAM)}
$$

**Why d15112 is the Maximum Feasible Instance**:

The selection of d15112 (1.70GB distance matrix = 42.5% VRAM) as the upper limit is conservative for several reasons:

1. **OS VRAM overhead is variable**: Desktop environment GPU usage varies with system load (200-800 MB), requiring headroom
2. **Memory pool fragmentation**: CuPy allocator may require contiguous blocks, reducing usable VRAM under fragmentation
3. **Out-of-memory safety margin**: Allocating $>90\%$ VRAM risks runtime failures (CUDA error: out of memory); conservative limit prevents crashes during experiments
4. **Empirical validation approach**: Actual maximum capacity will be determined experimentally by progressively testing larger instances until memory limits are reached

**Literature Justification**: GPU memory management for routing problems emphasizes conservative allocation strategies. Abdelatti & Sodhi (2020) discuss memory-aware algorithm design, recommending headroom for algorithmic overhead and avoiding near-capacity allocations that degrade performance due to memory bandwidth saturation [@abdelatti2020improvedgpuheuristic].

**Loading Strategy**: One instance at a time (no simultaneous loading needed for benchmarking). Sequential memory requirement: $2.0\text{-}2.9$ GB maximum (d15112). Parallel loading of all 30 instances is unnecessary for experimental workflow.

---

#### 3.4.4 Expected Experimental Results

**GPU Speedup Predictions**:

The speedup predictions presented below are based on the hardware parallelism ratio (GTX 1050 Mobile: 384 CUDA cores vs 4-core CPU = 96x theoretical peak) adjusted for GPU overhead and memory bandwidth limitations documented in the literature[^speedup_basis].

| Problem Size ($n$) | Expected Speedup | Interpretation                                   |
| ------------------ | ---------------- | ------------------------------------------------ |
| $n < 50$           | 0.3-1.2x         | CPU faster (overhead > benefit)[^small_overhead] |
| $n = 100$          | 1-3x             | Breakeven zone (±50%)[^breakeven]                |
| $n = 200$          | 5-8x             | GPU advantage emerges                            |
| $n = 500$          | 15-25x           | GPU sweet spot begins                            |
| $n = 1000$         | 30-40x           | Strong GPU advantage[^tsp_gpu_speedup]           |
| $n = 5000$         | 60-70x           | Peak GPU performance                             |
| $n = 15000$        | 50-80x           | Memory-bound (plateau)[^memory_plateau]          |

[^speedup_basis]: Speedup predictions are based on: (1) Hardware parallelism ratio (384 CUDA cores ÷ 4 CPU threads = 96x theoretical peak), (2) GPU overhead for small problems as documented in routing optimization literature [@schulz2013gpu], (3) Memory bandwidth limitations for large problems approaching VRAM capacity [@abdelatti2020improvedgpuheuristic].
[^small_overhead]: For small problem instances, GPU memory transfer overhead and kernel launch latency may exceed computational benefit. Schulz et al. (2013) provide a comprehensive analysis of when GPU acceleration becomes beneficial for discrete optimization problems, noting that problem size and computational intensity determine the break-even point [@schulz2013gpu].
[^breakeven]: Break-even point predictions based on TSP problem size where parallel distance computation benefit approximately equals GPU overhead cost. Literature on GPU-accelerated TSP suggests implementations typically achieve performance parity with CPU implementations around 100-200 nodes, depending on algorithm design and hardware specifications [@fujimoto2011highly; @tsp_gpu].
[^tsp_gpu_speedup]: GPU TSP solvers demonstrate significant speedups for large instances. Fujimoto & Tsutsui (2011) achieved substantial performance improvements for problems with thousands of cities using parallel 2-opt on CUDA [@fujimoto2011highly]. Rocki & Suda (2013) report strong scaling behavior for GPU-accelerated local search on large TSP instances [@tsp_gpu].
[^memory_plateau]: When distance matrix size approaches VRAM capacity (d15112 requires ~2.6GB total including overhead = 65% of 4GB), memory bandwidth saturation and reduced cache efficiency cause speedup plateau or degradation. Additionally, operating system VRAM reservations and GPU driver overhead reduce usable memory. Abdelatti & Sodhi (2020) discuss memory-aware GPU algorithm design for routing problems, emphasizing conservative allocation strategies [@abdelatti2020improvedgpuheuristic].

**Key Validations**:

1. **Overhead penalty**: burma14, berlin52 expected to show GPU slower than CPU (validates Q1)
2. **Breakeven point**: kroA100 (~100 nodes) expected where GPU ≈ CPU performance (validates Q1)
3. **Scaling behavior**: Superlinear growth expected from 100 → 5000 nodes (validates Q2)
4. **Memory plateau**: Speedup plateaus/drops for d15112 due to memory pressure (validates Q3)

> **Speedup Predictions Justification**: All predictions are supported by academic citations in footnotes above ([^speedup_basis], [^small_overhead], [^breakeven], [^tsp_gpu_speedup], [^memory_plateau]) referencing Schulz et al. (2013), Fujimoto & Tsutsui (2011), Rocki & Suda (2013), and Abdelatti & Sodhi (2020). These works provide empirical evidence for GPU performance characteristics on routing problems across problem sizes.

**Solution Quality Targets** (gap to optimal on TSP instances):

| Algorithm                 | Small (<200) | Medium (200-500) | Large (500+) |
| ------------------------- | ------------ | ---------------- | ------------ |
| Nearest Neighbor          | 20-35%       | 25-40%           | 30-50%       |
| 2-opt (first-improvement) | 5-15%        | 8-20%            | 10-25%       |
| SA + 2-opt                | 2-8%         | 3-12%            | 5-18%        |

**GPU Correctness Validation**: CPU and GPU 2-opt must produce **identical** final solutions (deterministic algorithm).

---

#### 3.4.5 Data Format Specification

Benchmark instances are loaded from standard TSPLIB and CVRPLIB repositories. Problem instances are represented as structured coordinate data with the following components:

- **Node Coordinates**: $(x_i, y_i)$ for each node $i \in \{1, \ldots, n\}$ (Euclidean 2D problems)
- **Problem Metadata**: Type (TSP/ATSP/CVRP), dimension $n$, known optimal cost (if available)
- **Distance Calculation**: Euclidean distance $d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$
- **CVRP Constraints**: Vehicle capacity $Q$, node demands $q_i$, fleet size $K$ (when applicable)

Complete database schema and loading procedures are documented in Appendix A. See `/documentation/reports/BENCHMARK_INSTANCES_30_SELECTED.md` for complete instance analysis and memory calculations.

---

### 3.5 Experimental Design

The experimental design is structured to rigorously compare the performance of deterministic and stochastic algorithms across CPU and GPU backends. The methodology adheres to the statistical benchmarking principles outlined by Hoefler & Belli (2015)[^hoefler2015] and Hothorn et al. (2005)[^hothorn2005], which establish best practices for reproducible performance evaluation in parallel computing systems.

[^hoefler2015]: Hoefler, T., & Belli, R. (2015). Scientific benchmarking of parallel computing systems: Twelve ways to tell the masses when reporting performance results. _SC '15: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis_, 1-12. DOI: [10.1145/2807591.2807644](https://doi.org/10.1145/2807591.2807644). This seminal work analyzed 120 HPC papers and found that most lack statistical rigor when reporting performance results, proposing concrete guidelines for statistically sound benchmarking.
[^hothorn2005]: Hothorn, T., Leisch, F., Zeileis, A., & Hornik, K. (2005). The design and analysis of benchmark experiments. _Journal of Computational and Graphical Statistics_, 14(3), 675-699. Establishes theoretical framework for algorithm comparison using cross-validation and statistical test procedures.

#### 3.5.1 Comparison 1: Deterministic Local Search (2-opt)

- **Objective:** To quantify the raw computational speedup of GPU acceleration for a deterministic, parallelizable algorithm.
- **Algorithm:** 2-opt Local Search (first-improvement).
- **Backends:** NumPy (CPU) vs. CuPy (GPU), using identical, vectorized logic.
- **Procedure:**
    1. For each of the **30** benchmark instances:
    2. Run the 2-opt algorithm from the same Nearest Neighbor initial solution until convergence (no further improvement is found).
    3. **Metric:** The primary metric is **Time to Convergence (seconds)**. This replaces the flawed "fixed-time-budget" approach, as convergence time is the only relevant metric for a deterministic algorithm[^deterministic_metric].
    4. **Repetitions:** The experiment will be repeated **30** times for each instance/backend combination. This sample size ($n=30$) satisfies the Central Limit Theorem's requirement for asymptotic normality of sample means[^clt_justification], enabling robust confidence interval construction even when underlying runtime distributions are non-normal due to system noise (context switches, cache effects, thermal throttling).
    5. **Validation:** The final tour cost _must_ be identical (within floating-point tolerance $\epsilon = 10^{-6}$) for both CPU and GPU backends to validate implementation correctness[^float_tolerance]. This deterministic property ensures any performance difference is purely computational, not algorithmic.

[^deterministic_metric]: For deterministic algorithms, time-to-convergence is the definitive performance metric. Fixed-time quality comparisons are inappropriate because deterministic algorithms produce identical solutions regardless of runtime, making solution quality non-informative for performance evaluation.
[^clt_justification]: The Central Limit Theorem (CLT) states that for independent, identically distributed random variables with finite mean $\mu$ and variance $\sigma^2$, the distribution of sample means converges to $\mathcal{N}(\mu, \sigma^2/n)$ as $n \to \infty$. In practice, $n \geq 30$ is the conventional threshold for CLT applicability (Montgomery, D.C., 2017, _Design and Analysis of Experiments_, 9th ed., Wiley, pp. 97-99). This enables parametric confidence interval construction via t-distribution even when individual runtimes are non-normal, with 95% CI: $\bar{x} \pm t_{0.025, n-1} \cdot s/\sqrt{n}$ where $t_{0.025, 29} \approx 2.045$ for $n=30$.
[^float_tolerance]: Floating-point arithmetic on CPU (IEEE 754 double precision) and GPU (CUDA double precision) may produce slightly different results due to operation ordering and fused multiply-add (FMA) instructions. A tolerance of $\epsilon = 10^{-6}$ (0.0001%) accounts for accumulated rounding errors while ensuring algorithmic equivalence. See Goldberg, D. (1991), "What Every Computer Scientist Should Know About Floating-Point Arithmetic," _ACM Computing Surveys_, 23(1), 5-48.

#### 3.5.2 Comparison 2: Stochastic Metaheuristics (SA vs. GA)

- **Objective:** To compare the solution quality and convergence speed of Simulated Annealing (SA) and Genetic Algorithms (GA) when accelerated by the CPU and GPU backends.
- **Algorithms:**
    1. **Hybrid SA + 2-opt:** SA provides the global search framework, using a vectorized 2-opt move generator for its neighborhood.
    2. **Hybrid GA + 2-opt:** GA provides population management and crossover, with 2-opt used for local search intensification (a Memetic Algorithm structure).
- **Procedure:**
    1. For each of the **30** benchmark instances:
    2. Run each of the four algorithmic combinations (SA-CPU, SA-GPU, GA-CPU, GA-GPU) for **30** independent repetitions (i.e., different random seeds)[^seed_independence].
    3. **Metrics:**
        - **Fixed-Time Quality:** Best solution quality found within a fixed time budget (e.g., **60.0** seconds). This is a valid metric for stochastic algorithms[^fixed_time_validity] as solution quality varies across runs even with identical algorithmic parameters.
        - **Time to Target:** Time required to reach a solution quality within **5.0%** of the known optimum[^target_gap]. This metric quantifies convergence speed and enables fair comparison across problem instances with different optimal values.
        - **Convergence Data:** Solution quality will be logged every **100** iterations to generate convergence curves[^convergence_logging]. Iteration-based logging (rather than time-based) ensures consistent sampling density across CPU and GPU backends with different execution speeds.

[^seed_independence]: Independent repetitions require statistically independent random number sequences. This is achieved using base seed $s_0 = 42$ with sequential offsets: $s_i = s_0 + i$ for run $i \in \{0, 1, \ldots, 29\}$. For GPU runs, both NumPy (CPU host code) and CuPy (GPU device code) random states must be seeded identically to ensure reproducibility.
[^fixed_time_validity]: Fixed-time quality is appropriate for stochastic algorithms because: (1) solution quality varies across runs due to randomness, making distribution analysis meaningful, and (2) practical deployment requires bounded execution time, making time-constrained quality a realistic performance metric. See Hoos, H. H., & Stützle, T. (2004), _Stochastic Local Search: Foundations and Applications_, Morgan Kaufmann, Chapter 4.
[^target_gap]: The 5% optimality gap is a standard benchmark threshold in TSP literature (see Helsgaun, K., 2000, "An Effective Implementation of the Lin-Kernighan Traveling Salesman Heuristic," _European Journal of Operational Research_, 126(1), 106-130). This gap balances difficulty (easy enough for SA/GA to achieve in reasonable time) with solution quality requirements (tight enough to demonstrate algorithm effectiveness).
[^convergence_logging]: Iteration-based logging every 100 iterations provides sufficient granularity for convergence analysis (typical runs perform 10,000-50,000 iterations, yielding 100-500 data points) while minimizing storage overhead. Time-based logging would produce variable sampling density between CPU and GPU, complicating comparative visualization.

#### 3.5.3 Statistical Methodology

- **Objective:** To ensure all conclusions are statistically valid and not the result of chance.
- **Step 1: Assumption Check:** Before analysis, the **Shapiro-Wilk test**[^shapiro_wilk] will be applied to all runtime and quality distributions ($n=30$) to test for normality at significance level $\alpha = 0.05$.
- **Step 2: Test Selection:**
  - If data is normal ($p \geq 0.05$), **Paired t-tests**[^paired_t] (for CPU vs. GPU) and **One-way ANOVA**[^anova] (for GA vs. SA) will be used.
  - If data is non-normal ($p < 0.05$), the non-parametric alternatives—**Wilcoxon signed-rank test**[^wilcoxon] (paired) and **Kruskal-Wallis test**[^kruskal_wallis] (multiple)—will be used.
- **Step 3: Reporting:**
  - All mean values will be reported with **95% Confidence Intervals (CI)**[^ci_justification].
  - All statistical comparisons will report **p-values** (for significance) and **Effect Size** (e.g., Cohen's $d$[^cohens_d]) to quantify the _magnitude_ of the difference.
- **Step 4: Multiple Comparison Correction:** When comparing $3+$ algorithms (GA vs. SA vs. 2-opt), a **Holm-Bonferroni correction**[^holm_bonferroni] will be applied to all $p$-values to avoid p-hacking and false positives.

[^shapiro_wilk]: Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). _Biometrika_, 52(3/4), 591-611. The Shapiro-Wilk test is generally more powerful than Kolmogorov-Smirnov for small-to-moderate sample sizes ($n < 50$) and is the recommended normality test in contemporary statistical practice.
[^paired_t]: The paired t-test is appropriate for comparing two related samples (same problem instance, different backends) under normality assumption. Test statistic: $t = \frac{\bar{d}}{s_d / \sqrt{n}}$ where $\bar{d}$ is mean difference and $s_d$ is standard deviation of differences. See Student (1908), "The Probable Error of a Mean," _Biometrika_, 6(1), 1-25.
[^anova]: One-way Analysis of Variance (ANOVA) tests whether means of multiple independent groups differ significantly. For algorithm comparison, null hypothesis $H_0: \mu_{\text{GA}} = \mu_{\text{SA}}$ is tested via F-statistic. See Fisher, R. A. (1925), _Statistical Methods for Research Workers_, Oliver & Boyd.
[^wilcoxon]: Wilcoxon, F. (1945). Individual comparisons by ranking methods. _Biometrics Bulletin_, 1(6), 80-83. The Wilcoxon signed-rank test is the non-parametric alternative to paired t-test, testing whether median difference is zero without assuming normality.
[^kruskal_wallis]: Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. _Journal of the American Statistical Association_, 47(260), 583-621. The Kruskal-Wallis test is the non-parametric alternative to one-way ANOVA, comparing medians of multiple independent groups.
[^ci_justification]: 95% confidence intervals are the standard in experimental computer science, providing intuitive interpretation: "if experiment were repeated infinitely, 95% of computed CIs would contain the true population mean." The 95% level balances Type I error control (5% false positive rate) with reasonable interval width. See Neyman, J. (1937), "Outline of a Theory of Statistical Estimation Based on the Classical Theory of Probability," _Philosophical Transactions of the Royal Society A_, 236(767), 333-380.
[^cohens_d]: Cohen's $d$ measures effect size: $d = \frac{\mu_1 - \mu_2}{\sigma_{\text{pooled}}}$ where $\sigma_{\text{pooled}} = \sqrt{(\sigma_1^2 + \sigma_2^2)/2}$. Interpretation: $|d| < 0.2$ (negligible), $0.2 \leq |d| < 0.5$ (small), $0.5 \leq |d| < 0.8$ (medium), $|d| \geq 0.8$ (large). See Cohen, J. (1988), _Statistical Power Analysis for the Behavioral Sciences_ (2nd ed.), Lawrence Erlbaum Associates.
[^holm_bonferroni]: Holm, S. (1979). A simple sequentially rejective multiple test procedure. _Scandinavian Journal of Statistics_, 6(2), 65-70. The Holm-Bonferroni method controls family-wise error rate (FWER) while being less conservative than Bonferroni correction, providing greater statistical power for multiple comparisons.

#### 3.5.4 Reproducibility Requirements

Following Hoefler & Belli (2015)[^hoefler2015] guidelines for reproducible performance evaluation, the following experimental details are documented:

**Hardware Configuration:**

- **CPU:** Intel i7-7700HQ @ 2.80GHz (4 cores, 8 threads)
- **GPU:** NVIDIA GeForce GTX 1050 Mobile (4GB VRAM, 384 CUDA cores, Pascal architecture, Compute Capability 6.1)
- **RAM:** 16GB DDR4
- **Operating System:** Debian GNU/Linux 13 (trixie), kernel version (to be recorded during experiments)

**Software Environment:**

- **Python:** 3.10.16 (virtual environment: `.venv`)
- **CUDA Toolkit:** 12.6 (nvcc)
- **CuPy:** 13.6.0 (cupy-cuda12x)
- **NumPy:** 2.2.6
- **Package Manager:** uv (for dependency management)

**System Configuration:**

- CPU frequency scaling disabled (use `performance` governor)
- GPU power mode set to maximum performance (no dynamic clocking)
- Background processes minimized during benchmark execution
- No concurrent GPU workloads (X server on integrated GPU or headless mode)

**Random Seed Management:**

- Base seed: $s_0 = 42$ (arbitrary constant for reproducibility)
- Run-specific seeds: $s_i = s_0 + i$ for run $i \in \{0, 1, \ldots, 29\}$
- Both NumPy and CuPy RNG states seeded identically for GPU runs

**Data Availability:**

- Source code: GitHub repository (URL to be added)
- Benchmark instances: TSPLIB standard collection (publicly available)
- Raw experimental results: CSV/JSON format in repository `/data/benchmarks/`
- Analysis scripts: Jupyter notebooks in `/code/examples/benchmarks/`

**Timing Methodology:**

- Wall-clock time measured using `time.perf_counter()` (highest resolution timer)
- GPU kernel time measured using CUDA events for device-only profiling
- Memory transfer time (host ↔ device) excluded from algorithm runtime
- Timing includes only algorithm execution (excludes problem loading and result validation)

## 4. RESULTADOS

This chapter presents the statistically validated results of the experimental design. All reported means are accompanied by 95% confidence intervals (CI), and all comparisons are validated with appropriate statistical tests and effect sizes, as specified in the Hoefler & Belli (2015) methodology.

### 4.1 Statistical Test Validation

- **Objective:** To ensure the validity of statistical conclusions.
- **Procedure:** The Shapiro-Wilk test was applied to the **000** collected data distributions (n=30) to test for normality.
- **Finding:** For **000** out of **000** distributions (e.g., runtimes for `d2103`), the data (p < 0.05) violated the normality assumption.
- **Conclusion:** Consequently, the non-parametric **Wilcoxon signed-rank test** and **Kruskal-Wallis test** are used for all subsequent analyses, as they provide robust conclusions without assuming a normal distribution.

### 4.2 Analysis 1: 2-opt (Deterministic) Performance

- **Objective:** Quantify raw GPU speedup for 2-opt time-to-convergence.
- **Key Result:** The GPU backend provided a mean speedup of **00.0x** (95% CI: [**00.0x**, **00.0x**]) over the CPU backend across all 30 instances.
- **Scalability:** [Figure 4.1: Speedup vs. Problem Size (n)] will show the breakeven point at n≈**000**, with speedup plateauing at n≈**0000** due to memory bandwidth.
- **Statistical Significance:** The difference was statistically significant (Wilcoxon p < **0.001**) with a **large** effect size (Cohen's d = **0.00**).

**Tabela 4.1: 2-opt Time-to-Convergence (n=30 runs)**
_All values in seconds. CI = 95% Confidence Interval._

| Instance          | CPU (Mean ± CI)     | GPU (Mean ± CI)    | Speedup (Mean ± 95% CI)          | p-value   | Effect Size      |
| :---------------- | :------------------ | :----------------- | :------------------------------- | :-------- | :--------------- |
| `berlin52`        | **0.000** [±0.000]  | **0.000** [±0.000] | **0.0x** [**0.0x**, **0.0x**]    | **0.000** | **0.00** (large) |
| `lin318`          | **0.000** [±0.000]  | **0.000** [±0.000] | **00.0x** [**00.0x**, **00.0x**] | < 0.001   | **0.00** (large) |
| `d2103`           | **00.000** [±0.000] | **0.000** [±0.000] | **00.0x** [**00.0x**, **00.0x**] | < 0.001   | **0.00** (large) |
| ... (27 more) ... |                     |                    |                                  |           |                  |

### 4.3 Analysis 2: Metaheuristic Quality (Fixed-Time Budget)

- **Objective:** Compare the solution quality of SA and GA on both backends within a **60**-second time budget.
- **Visualization:** [Figure 4.2: Box Plots of Final Solution Quality] will visualize the distributions from Table 4.2.

**Tabela 4.2: Mean Solution Quality (% Gap from Optimal) at 60 Seconds (n=30 runs)**
_CI = 95% Confidence Interval._

| Instance          | SA-CPU (Mean ± CI) | SA-GPU (Mean ± CI) | GA-CPU (Mean ± CI) | GA-GPU (Mean ± CI) |
| :---------------- | :----------------- | :----------------- | :----------------- | :----------------- |
| `berlin52`        | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  |
| `lin318`          | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  |
| `d2103`           | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  | **0.00%** [±0.00]  |
| ... (27 more) ... |                    |                    |                    |                    |

### 4.4 Analysis 3: Convergence Speed and Statistical Ranking

- **Objective:** Determine which metaheuristic finds good solutions the _fastest_ and which is statistically superior.
- **Visualization:** [Figure 4.3: Convergence Curves for `d2103`] will plot Mean Solution Quality vs. Time (log-scale) for the four stochastic methods. This will show that GPU variants find high-quality solutions _earlier_.
- **Statistical Ranking:** A Kruskal-Wallis test was performed on the final solution quality data from Table 4.2, followed by a post-hoc Dunn's test with Holm-Bonferroni correction.
- **Finding:** The analysis showed a significant difference (H=**00.0**, p < **0.001**). The post-hoc test (Table 4.3) revealed that `GA-GPU` was statistically superior to `SA-GPU` (p=**0.000**), but not statistically different from `GA-CPU` (p=**0.000**), indicating algorithm choice was more impactful than the backend.

**Tabela 4.3: Post-Hoc Pairwise p-values (Holm-corrected)**

| Comparison            | p-value   | Significant? (α=0.05) |
| :-------------------- | :-------- | :-------------------- |
| GA-GPU vs. SA-GPU     | **0.000** | Yes                   |
| GA-GPU vs. GA-CPU     | **0.000** | No                    |
| GA-GPU vs. SA-CPU     | **0.000** | Yes                   |
| GA-CPU vs. SA-GPU     | **0.000** | ...                   |
| ... (all 6 pairs) ... |           |                       |

## 5. DISCUSSÃO E CONSIDERAÇÕES

### 5.1 Performance Analysis

[Analysis of CPU vs GPU performance differences]

### 5.2 Algorithm Comparison

[Discussion of which algorithm combinations work best]

### 5.3 Scalability Observations

[How performance changes with problem size]

### 5.4 Limitations and Constraints

- GPU memory constraints limiting maximum problem size
- Implementation-specific optimizations
- Hardware dependency of results

---

## 6. CONCLUSÃO

[Summary of key findings and contributions]

### 6.1 Recomendações para Trabalhos Futuros

- Extension to VRP variants with time windows
- Implementation of additional metaheuristics
- Multi-GPU parallelization
- Adaptive parameter tuning mechanisms

---

## REFERÊNCIAS

[To be compiled from literature review]

---

## GLOSSÁRIO

- **TSP:** Traveling Salesman Problem
- **VRP:** Vehicle Routing Problem
- **CVRP:** Capacitated Vehicle Routing Problem
- **GPU:** Graphics Processing Unit
- **CUDA:** Compute Unified Device Architecture
- **2-opt:** Local search operator that swaps two edges
- **3-opt:** Local search operator that swaps three edges
- **GA:** Genetic Algorithm
- **SA:** Simulated Annealing
- **TS:** Tabu Search
- **FLS:** First Improvement Local Search

---

## RESEARCH QUESTIONS TO ANSWER

From roteiro_analise_critica.md:

1. **Há um problema posto que indique a necessidade de um trabalho?**

    - Yes: Routing problems are computationally expensive, GPU acceleration potential remains underexplored in modular heuristic frameworks despite growing interest in GPU-based metaheuristics [@osaba2020gpu; @schulz2013gpu]. While GPU implementations exist for specific algorithms, systematic comparisons of CPU vs GPU performance across problem sizes and algorithm types are limited in academic literature.

2. **Há uma questão a ser respondida?**

    - How effectively can GPU acceleration improve solution quality within fixed time budgets for different metaheuristic combinations? See Section 3.4.1 for detailed research questions Q1-Q5 and Section 3.5 for experimental methodology.

3. **Os objetivos estão claros?**

    - See Section 1.2 (Objetivos Gerais and Específicos)

4. **A metodologia é adequada?**

    **Methodology Justification**: The experimental methodology follows established benchmarking practices in GPU-accelerated combinatorial optimization, as outlined in Schulz et al. (2013) [@schulz2013gpu] and Fujimoto & Tsutsui (2011) [@fujimoto2011highly]. These seminal works emphasize three core principles for rigorous performance evaluation:

    1. **Controlled experiments**: Identical problem instances for CPU vs GPU comparison, eliminating confounding variables
    2. **Statistical rigor**: Multiple runs with confidence intervals for stochastic algorithms, paired statistical tests for deterministic algorithms
    3. **Standardized benchmarks**: TSPLIB/CVRPLIB instances with known optimal solutions for reproducibility and cross-study comparability

    See Section 3.5 for complete experimental design including:

    - **Comparison methodology**: Paired CPU vs GPU runs on identical TSPLIB/CVRPLIB instances
    - **Metrics**: Speedup ratio (GPU time / CPU time), solution quality gap (% above optimal), absolute execution time
    - **Statistical validation**:
        - Deterministic algorithms (NN, 2-opt): Paired t-tests on execution times across 30 instances
        - Stochastic algorithms (SA): 30 independent runs per instance, 95% confidence intervals on mean performance
    - **Standardized benchmarks**: 30 selected TSPLIB/CVRPLIB instances (see Section 3.4.2) with verified optimal solutions

    This approach ensures experimental results are reproducible, statistically sound, and directly comparable to prior literature in GPU-accelerated routing optimization.

5. **Os resultados são válidos?**
    - Validation through multiple runs and comparison against known optimal solutions from TSPLIB [@tsplib_ref] and CVRPLIB libraries. TSPLIB is the de facto standard for TSP research since 1991, providing 110+ instances with verified optimal solutions enabling reproducible quality assessment. CVRPLIB extends this standard to capacitated vehicle routing problems. These benchmarks are universally accepted in routing optimization literature, making results directly comparable to prior work.

---

## REFERÊNCIAS

> **Note on References**: This section will be automatically generated from BibTeX citations using the `documentation/refs.bib` file. All inline citations (e.g., [@schulz2013gpu], [@fujimoto2011highly]) appear as footnotes throughout the document and are compiled here in ABNT format during LaTeX compilation.

[References will be automatically generated from citations using BibTeX]

**Key Academic Sources:**

1. **GPU Computing for Discrete Optimization:**

    - Schulz et al. (2013) - GPU computing in discrete optimization survey (routing problems focus) [@schulz2013gpu]
    - Fujimoto & Tsutsui (2011) - Highly-parallel TSP solver for GPU [@fujimoto2011highly]
    - Rocki & Suda (2013) - High performance GPU accelerated local optimization in TSP [@tsp_gpu]

2. **GPU-Accelerated Vehicle Routing:**

    - Benaini et al. (2015) - GPU implementation of multi-depot VRP [@benaini2015gpu]
    - Benaini & Berrajaa (2018) - Genetic algorithm for large dynamic VRP on GPU [@benaini2018genetic]
    - Abdelatti & Sodhi (2020) - Improved GPU-accelerated heuristic for CVRP [@abdelatti2020improvedgpuheuristic]
    - Boschetti et al. (2017) - Route relaxations on GPU for VRP [@boschetti2017route]

3. **TSP/VRP Foundations:**

    - Cook (2014) - In Pursuit of the Traveling Salesman [@pursuit_travelling_salesman]
    - Reinelt (1991) - TSPLIB library [@tsplib_ref]
    - Tan & Yeh (2021) - Vehicle routing problem state-of-the-art classification [@tan2021vehicle]

4. **Metaheuristics:**
    - Voudouris & Tsang (1999) - Guided local search for TSP [@voudouris1999tsp]
    - Wang et al. (2015) - Parallel simulated annealing for VRP [@wang2015parallel]
    - Gendreau et al. (1999) - Tabu search for heterogeneous fleet VRP [@gendreau1993tabu]

**Complete bibliography available in `documentation/refs.bib`**

---

## APÊNDICE A - DETALHES DE IMPLEMENTAÇÃO

Este apêndice documenta os detalhes técnicos de implementação que suportam a metodologia apresentada no Capítulo 3, incluindo especificações de banco de dados, abstrações de backend, padrões de vetorização e protocolos de medição de desempenho.

### A.1 Esquema do Banco de Dados

**Tabela `problems`:**

```sql
id              INTEGER PRIMARY KEY
name            TEXT UNIQUE NOT NULL
dimension       INTEGER NOT NULL
type            TEXT CHECK(type IN ('TSP', 'ATSP', 'CVRP'))
edge_weight_type TEXT (EUC_2D, GEO, ATT, EXPLICIT, ...)
capacity        INTEGER  -- CVRP only
vehicles        INTEGER  -- CVRP only, número de veículos
optimal_cost    REAL     -- Known optimal solution (if available)
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Tabela `nodes`:**

```sql
problem_id      INTEGER NOT NULL
node_id         INTEGER NOT NULL
x               REAL NOT NULL
y               REAL NOT NULL
demand          REAL DEFAULT 0  -- CVRP only, demanda do nó
is_depot        BOOLEAN DEFAULT FALSE  -- CVRP only, identifica depot
PRIMARY KEY (problem_id, node_id)
FOREIGN KEY (problem_id) REFERENCES problems(id)
```

**Índices para Performance:**

```sql
CREATE INDEX idx_problems_type ON problems(type);
CREATE INDEX idx_problems_dimension ON problems(dimension);
CREATE INDEX idx_nodes_problem ON nodes(problem_id);
CREATE INDEX idx_nodes_depot ON nodes(problem_id, is_depot);
```

### A.2 Interface `Problem` - Especificação Completa

**Modelo de Dados (Python):**

```python
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Problem:
    """
    Unified interface for routing problem instances (TSP, ATSP, CVRP).

    Attributes:
        name: Instance identifier (e.g., 'berlin52')
        dimension: Number of nodes/cities
        problem_type: Problem classification ('TSP', 'ATSP', 'CVRP')
        edge_type: Distance calculation method ('EUC_2D', 'GEO', 'EXPLICIT', ...)
        coordinates: Node positions (n × 2) for geometric instances
        distances: Precomputed distance matrix (n × n)
        optimal_cost: Known optimal tour length (if available)

        # CVRP-specific attributes
        capacity: Vehicle capacity constraint
        demands: Node demand values (n,)
        depot: Depot node index (usually 0)
        vehicles: Number of available vehicles

    Type Invariants:
        - distances.shape == (dimension, dimension)
        - coordinates.shape == (dimension, 2) if edge_type geometric
        - demands.shape == (dimension,) if problem_type == 'CVRP'
        - For TSP: distances symmetric (D[i,j] == D[j,i])
        - For ATSP: distances may be asymmetric
    """
    name: str
    dimension: int
    problem_type: str  # "TSP", "ATSP", "CVRP"
    edge_type: str     # "EUC_2D", "GEO", "ATT", "EXPLICIT"
    coordinates: np.ndarray  # shape (n, 2)
    distances: np.ndarray    # shape (n, n)
    optimal_cost: Optional[float] = None

    # CVRP-specific fields
    capacity: Optional[int] = None
    demands: Optional[np.ndarray] = None  # shape (n,)
    depot: Optional[int] = 0
    vehicles: Optional[int] = None

    def __post_init__(self):
        """Validate data consistency after initialization."""
        # Shape validation
        n = self.dimension
        assert self.distances.shape == (n, n), f"Distance matrix shape mismatch"
        if self.coordinates is not None:
            assert self.coordinates.shape == (n, 2), f"Coordinates shape mismatch"

        # CVRP validation
        if self.problem_type == 'CVRP':
            assert self.capacity is not None, "CVRP requires capacity"
            assert self.demands is not None, "CVRP requires demands"
            assert self.demands.shape == (n,), "Demands shape mismatch"
            assert self.depot is not None, "CVRP requires depot"

        # Symmetry check for TSP
        if self.problem_type == 'TSP':
            is_symmetric = np.allclose(self.distances, self.distances.T)
            if not is_symmetric:
                import warnings
                warnings.warn(f"{self.name}: TSP distance matrix not symmetric")
```

### A.3 Consulta de Carregamento SQL

**Query Principal:**

```sql
SELECT
    p.id,
    p.name,
    p.dimension,
    p.type AS problem_type,
    p.edge_weight_type,
    p.capacity,
    p.vehicles,
    p.optimal_cost,
    n.node_id,
    n.x,
    n.y,
    n.demand,
    n.is_depot
FROM problems p
JOIN nodes n ON p.id = n.problem_id
WHERE p.name IN (
    -- MVP instances (3)
    'berlin52', 'lin318', 'd2103',

    -- Full benchmark (30 instances)
    'burma14', 'kroA100', 'pr152', 'gr202', 'rd400', 'pcb442',
    'd493', 'att532', 'd657', 'rat783', 'pr1002', 'd1291',
    'fl1577', 'rl1889', 'pcb3038', 'rl5934', 'd15112',

    -- ATSP instances (6)
    'br17', 'ftv47', 'ftv64', 'ftv70', 'ry48p', 'p43',

    -- CVRP instances (6)
    'E-n22-k4', 'E-n33-k4', 'E-n51-k5', 'E-n76-k7',
    'E-n101-k8', 'E-n200-k17'
)
ORDER BY p.type, p.dimension;
```

**Query para Estatísticas:**

```sql
-- Count instances by type and size tier
SELECT
    type,
    CASE
        WHEN dimension < 100 THEN 'Tiny/Small'
        WHEN dimension < 500 THEN 'Medium'
        WHEN dimension < 2000 THEN 'Large'
        ELSE 'Very Large'
    END AS size_tier,
    COUNT(*) AS num_instances,
    AVG(dimension) AS avg_dimension,
    MIN(dimension) AS min_dimension,
    MAX(dimension) AS max_dimension
FROM problems
WHERE name IN (/* benchmark instance list */)
GROUP BY type, size_tier
ORDER BY type, MIN(dimension);
```

### A.4 Backend Abstraction: Implementação Completa

**A.4.1 Protocol Definition**

Protocolo (PEP 544) para abstração de backend NumPy/CuPy (ver Seção 3.2.2):

```python
from typing import Protocol, Any, Optional
import numpy as np

class BackendModule(Protocol):
    """
    Protocol defining the interface for backend modules (NumPy/CuPy).

    Enables static type checking via MyPy while maintaining runtime flexibility.
    Ensures backend-agnostic algorithm implementations.

    References:
        - PEP 544: Protocols - Structural Subtyping (Static Duck Typing)
        - Okuta et al. (2017): CuPy: A NumPy-Compatible Library for NVIDIA GPU
    """

    # Module identification
    __name__: str  # 'numpy' or 'cupy'

    # Array creation
    def array(self, object: Any, dtype: Optional[Any] = None) -> Any: ...
    def zeros(self, shape: tuple, dtype: Optional[Any] = None) -> Any: ...
    def ones(self, shape: tuple, dtype: Optional[Any] = None) -> Any: ...
    def full(self, shape: tuple, fill_value: Any, dtype: Optional[Any] = None) -> Any: ...
    def arange(self, start: int, stop: Optional[int] = None,
               step: int = 1, dtype: Optional[Any] = None) -> Any: ...

    # Array operations
    def argmin(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def argmax(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def min(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def max(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def sum(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def mean(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def std(self, a: Any, axis: Optional[int] = None) -> Any: ...

    # Logical operations
    def where(self, condition: Any, x: Optional[Any] = None,
              y: Optional[Any] = None) -> Any: ...
    def all(self, a: Any, axis: Optional[int] = None) -> Any: ...
    def any(self, a: Any, axis: Optional[int] = None) -> Any: ...

    # Type constants
    float32: type
    float64: type
    int32: type
    int64: type
    bool_: type

    # Constants
    inf: float
```

**A.4.2 Backend Parameter Propagation Pattern**

Padrão para propagação de backend através da pilha de chamadas:

```python
from typing import Any, Optional
import numpy as np
from protocols.backend import BackendModule

def algorithm_entry_point(
    problem: Problem,
    backend: Optional[BackendModule] = None,
    **kwargs
) -> Any:
    """
    Top-level algorithm function with backend parameter.

    Pattern:
        1. Accept optional backend parameter (defaults to NumPy)
        2. Alias to 'xp' for convenience
        3. Propagate to all nested calls
    """
    # Step 1: Default to NumPy if not specified
    xp = backend if backend is not None else np

    # Step 2: Ensure distance matrix uses same backend
    distances = xp.array(problem.distances)

    # Step 3: Propagate backend to nested functions
    result = _internal_function(distances, backend=xp, **kwargs)

    return result

def _internal_function(
    data: Any,
    backend: BackendModule = np,
    **kwargs
) -> Any:
    """
    Internal function - backend parameter required (no default to None).

    This prevents accidental NumPy usage when caller intended CuPy.
    """
    # All operations use the aliased backend
    xp = backend

    # Example vectorized operations
    masked_data = xp.where(data > 0, data, xp.inf)
    indices = xp.argmin(masked_data, axis=1)

    return indices
```

**A.4.3 Memory Management Patterns**

Gerenciamento de memória para transferências CPU ↔ GPU:

```python
def transfer_to_device(problem: Problem, backend: BackendModule) -> Problem:
    """
    Transfer problem data to GPU device if using CuPy backend.

    For NumPy backend, this is a no-op (returns copy on CPU).
    """
    if backend.__name__ == 'cupy':
        import cupy as cp
        return Problem(
            name=problem.name,
            dimension=problem.dimension,
            problem_type=problem.problem_type,
            edge_type=problem.edge_type,
            coordinates=cp.array(problem.coordinates) if problem.coordinates is not None else None,
            distances=cp.array(problem.distances),
            optimal_cost=problem.optimal_cost,
            capacity=problem.capacity,
            demands=cp.array(problem.demands) if problem.demands is not None else None,
            depot=problem.depot,
            vehicles=problem.vehicles
        )
    else:
        # NumPy: return copy (defensive programming)
        return Problem(
            name=problem.name,
            dimension=problem.dimension,
            problem_type=problem.problem_type,
            edge_type=problem.edge_type,
            coordinates=problem.coordinates.copy() if problem.coordinates is not None else None,
            distances=problem.distances.copy(),
            optimal_cost=problem.optimal_cost,
            capacity=problem.capacity,
            demands=problem.demands.copy() if problem.demands is not None else None,
            depot=problem.depot,
            vehicles=problem.vehicles
        )

def transfer_to_host(result: Any, backend: BackendModule) -> np.ndarray:
    """
    Transfer computation result from GPU to CPU if needed.

    Returns NumPy array regardless of input backend.
    """
    if backend.__name__ == 'cupy':
        import cupy as cp
        if isinstance(result, cp.ndarray):
            return cp.asnumpy(result)
    return np.asarray(result)
```

### A.5 Padrões de Vetorização

**A.5.1 Construção Nearest Neighbor: Loop vs. Vetorização**

Comparação entre implementação ingênua (loops) e vetorizada:

**Versão Ingênua (Evitar):**

```python
def nearest_neighbor_naive(problem: Problem) -> np.ndarray:
    """
    Greedy nearest neighbor - NON-VECTORIZED implementation.

    WARNING: This version uses Python loops, poor GPU performance.
    O(n) kernel launches per iteration → O(n²) total launches.
    """
    n = problem.dimension
    distances = problem.distances
    tour = np.zeros(n, dtype=int)
    tour[0] = 0  # Start at depot

    visited = {0}
    current = 0

    # ANTI-PATTERN: Python loop over iterations
    for i in range(1, n):
        # ANTI-PATTERN: Python loop to find minimum
        min_dist = np.inf
        nearest = -1
        for j in range(n):
            if j not in visited:  # ANTI-PATTERN: Python membership test
                if distances[current, j] < min_dist:
                    min_dist = distances[current, j]
                    nearest = j

        tour[i] = nearest
        visited.add(nearest)
        current = nearest

    return tour
```

**Versão Vetorizada (Recomendado):**

```python
def nearest_neighbor_vectorized(
    problem: Problem,
    start_node: int = 0,
    backend: BackendModule = np
) -> Any:
    """
    Greedy nearest neighbor - VECTORIZED implementation.

    Reduces kernel launches from O(n²) to O(n) by using boolean masks
    and vectorized operations instead of Python loops.

    Args:
        problem: Problem instance with distance matrix
        start_node: Starting node index (default 0 = depot)
        backend: Computational backend (NumPy or CuPy)

    Returns:
        tour: Array of node indices in visit order (n,)
    """
    xp = backend
    n = problem.dimension

    # Ensure distances use the correct backend
    distances = xp.array(problem.distances)

    # Preallocate tour array (single allocation, not n appends)
    tour = xp.zeros(n, dtype=int)
    tour[0] = start_node

    # Boolean mask for visited nodes (vectorized operations)
    visited = xp.zeros(n, dtype=bool)
    visited[start_node] = True

    current = start_node

    # Iterative construction (inherently sequential due to dependencies)
    for i in range(1, n):
        # VECTORIZED: Mask out visited nodes (single kernel launch)
        distances_from_current = distances[current].copy()
        distances_from_current[visited] = xp.inf

        # VECTORIZED: Find nearest unvisited (single kernel launch)
        nearest = int(xp.argmin(distances_from_current))

        # Update tour and mask (array assignments, not Python operations)
        tour[i] = nearest
        visited[nearest] = True
        current = nearest

    return tour
```

**Kernel Launch Analysis:**

| Operation           | Naive (Python loops)                 | Vectorized (NumPy/CuPy)  | Benefit                  |
| ------------------- | ------------------------------------ | ------------------------ | ------------------------ |
| Find minimum        | $O(n)$ comparisons in loop           | `argmin()` single kernel | $n\times$ reduction      |
| Mask visited        | `if j not in visited` (set lookup)   | Boolean indexing         | Type-level optimization  |
| Total launches/iter | $2n$ (distance access + comparisons) | 3 (mask, argmin, update) | $\frac{2n}{3}$ reduction |

**A.5.2 Otimização de Kernel Launches**

Resultado da otimização documentada na Seção 3.3.5:

```python
# ORIGINAL: 4 operations per iteration
distances_masked = distances[current].copy()  # Kernel 1: array slice + copy
distances_masked[visited] = xp.inf            # Kernel 2: boolean indexing
min_dist = xp.min(distances_masked)          # Kernel 3: reduction
nearest = int(xp.argmin(distances_masked))   # Kernel 4: argmin

# OPTIMIZED: 3 operations per iteration (25% reduction)
distances_masked = xp.where(visited, xp.inf, distances[current])  # Kernel 1: fused mask+copy
nearest = int(xp.argmin(distances_masked))                       # Kernel 2: argmin (reuses min)
# min_dist calculation removed - not needed for correctness
```

Economia: $4n \rightarrow 3n$ kernel launches totais para $n$ nós (25% de redução).

**A.5.3 Vetorização de 2-opt (Improvement Heuristic)**

Diferença fundamental: improvement heuristics permitem paralelismo total (ao contrário de construction):

```python
def evaluate_2opt_moves_vectorized(
    tour: Any,
    distances: Any,
    backend: BackendModule = np
) -> tuple:
    """
    Evaluate ALL 2-opt moves in parallel using vectorization.

    For n-city tour, evaluates C(n,2) = n(n-1)/2 possible edge swaps.
    GPU advantage: Embarrassingly parallel evaluation.

    Returns:
        improvements: (n, n) matrix of tour length changes (negative = improvement)
        best_i, best_j: Indices of best improving move
    """
    xp = backend
    n = len(tour)

    # VECTORIZED: Create all (i,j) pairs via broadcasting
    i_indices = xp.arange(n)[:, None]  # Shape (n, 1)
    j_indices = xp.arange(n)[None, :]  # Shape (1, n)

    # VECTORIZED: Compute improvement for ALL pairs simultaneously
    # This is a single GPU kernel that processes n² elements in parallel
    # Tour segment: ... -> tour[i] -> tour[i+1] -> ... -> tour[j] -> tour[j+1] -> ...
    # 2-opt reverses segment between i+1 and j

    # Current edges: (tour[i], tour[i+1]) and (tour[j], tour[j+1])
    current_edges = (
        distances[tour[i_indices], tour[(i_indices + 1) % n]] +
        distances[tour[j_indices], tour[(j_indices + 1) % n]]
    )

    # New edges after 2-opt: (tour[i], tour[j]) and (tour[i+1], tour[j+1])
    new_edges = (
        distances[tour[i_indices], tour[j_indices]] +
        distances[tour[(i_indices + 1) % n], tour[(j_indices + 1) % n]]
    )

    # Improvement matrix (negative values = beneficial swaps)
    improvements = new_edges - current_edges

    # Mask invalid swaps (i >= j-1, no point reversing segment of length 0 or 1)
    mask = (j_indices - i_indices) <= 1
    improvements = xp.where(mask, 0, improvements)

    # Find best improving move (single argmin on flattened matrix)
    flat_idx = int(xp.argmin(improvements))
    best_i = flat_idx // n
    best_j = flat_idx % n
    best_improvement = improvements[best_i, best_j]

    return improvements, best_i, best_j, best_improvement
```

**Paralelismo:** 2-opt avalia $O(n^2)$ movimentos independentes → ganho quadrático com GPU.

### A.6 Implementação Multi-Start

Documentação da implementação multi-start criada na Task 3 (Seção 3.4.1, Q1):

```python
def multi_start_nearest_neighbor(
    problem: Problem,
    backend: BackendModule = np,
    batch_size: int = 1000,
    verbose: bool = True
) -> dict:
    """
    Execute Nearest Neighbor from ALL possible starting nodes.

    This multi-start approach enables:
        1. Solution quality characterization across all start points
        2. Statistical validation of CPU vs GPU performance
        3. Demonstration of GPU advantage with batched processing

    Args:
        problem: Problem instance to solve
        backend: Computational backend (NumPy or CuPy)
        batch_size: Maximum starts per batch (prevents OOM on large instances)
        verbose: Print progress messages

    Returns:
        dict with keys:
            'tours': List of all tours (n tours, each tour is array of shape (n,))
            'costs': Array of tour costs (n,)
            'best_tour': Tour with minimum cost
            'best_cost': Minimum cost found
            'times': Array of execution times per start (n,)
            'n_starts': Total number of starting points tested

    Memory Management:
        - For n ≤ batch_size: All starts processed in single batch
        - For n > batch_size: Processes in chunks to respect VRAM limits
        - d15112 (15,112 nodes) uses ~13 batches × 1000 starts
    """
    import time

    xp = backend
    n = problem.dimension
    all_costs = []
    all_times = []
    all_tours = []

    # Determine batching strategy
    if n > batch_size:
        num_batches = (n + batch_size - 1) // batch_size
        if verbose:
            print(f"  Large instance ({n} nodes) - using {num_batches} batches")
    else:
        num_batches = 1
        batch_size = n

    # Process in batches
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, n)

        if verbose and num_batches > 1:
            print(f"  Batch {batch_idx + 1}/{num_batches}: nodes {start_idx}-{end_idx-1}")

        # Run NN for each starting point in batch
        for start_node in range(start_idx, end_idx):
            # Time individual execution
            t_start = time.perf_counter()
            tour = nearest_neighbor_vectorized(problem, start_node=start_node, backend=xp)
            t_elapsed = time.perf_counter() - t_start

            # Compute tour cost
            cost = compute_tour_cost(problem, tour, backend=xp)

            # Convert to host memory (Python types) for storage
            if xp.__name__ == 'cupy':
                cost = float(cost)
                tour = xp.asnumpy(tour)
            else:
                cost = float(cost)

            all_costs.append(cost)
            all_times.append(t_elapsed)
            all_tours.append(tour)

    # Convert to arrays
    all_costs_array = np.array(all_costs)
    all_times_array = np.array(all_times)

    # Find best solution
    best_idx = np.argmin(all_costs_array)

    return {
        'tours': all_tours,
        'costs': all_costs_array,
        'best_tour': all_tours[best_idx],
        'best_cost': all_costs_array[best_idx],
        'times': all_times_array,
        'n_starts': len(all_costs)
    }
```

**Aplicação Experimental:**

```python
# Example: berlin52 multi-start comparison
import numpy as np

# CPU baseline
results_cpu = multi_start_nearest_neighbor(berlin52, backend=np)
print(f"CPU - Best: {results_cpu['best_cost']:.2f}, "
      f"Mean: {results_cpu['costs'].mean():.2f} ± {results_cpu['costs'].std():.2f}")

# GPU comparison (if available)
if gpu_available:
    import cupy as cp
    results_gpu = multi_start_nearest_neighbor(berlin52, backend=cp)
    print(f"GPU - Best: {results_gpu['best_cost']:.2f}, "
          f"Mean: {results_gpu['costs'].mean():.2f} ± {results_gpu['costs'].std():.2f}")

    # Speedup calculation
    speedup = results_cpu['times'].sum() / results_gpu['times'].sum()
    print(f"Multi-start speedup: {speedup:.2f}x")
```

### A.7 Especificações de Hardware e Software

**A.7.1 Hardware - GTX 1050 Mobile**

```
GPU Specifications:
    Model: NVIDIA GeForce GTX 1050 Mobile
    Architecture: Pascal (GP107)
    Compute Capability: 6.1
    CUDA Cores: 384 (single precision)
    Base Clock: 1354 MHz
    Boost Clock: 1493 MHz
    Memory: 4GB GDDR5
    Memory Bus: 128-bit
    Memory Bandwidth: 112 GB/s
    TDP: 75W (laptop variant)

    Performance Specifications:
        FP32 (float): 1.86 TFLOPS (boost clock)
        FP16 (half): Not supported (pre-Volta)
        INT8: Not supported

    Memory Constraints:
        Total VRAM: 4GB (4,294,967,296 bytes)
        Maximum allocation: ~3.5GB (OS reserves ~500MB)
        Maximum TSP instance: d15112 (1.70GB = 42.5% VRAM)

CPU Specifications:
    Model: Intel Core i7-7700HQ
    Architecture: Kaby Lake (7th gen)
    Cores: 4 physical, 8 logical (Hyper-Threading)
    Base Clock: 2.80 GHz
    Turbo Boost: 3.80 GHz (single core)
    Cache: 6MB L3 shared
    TDP: 45W

    Memory:
        System RAM: 16GB DDR4-2400
        Memory Channels: Dual-channel
        Peak Bandwidth: 38.4 GB/s
```

**A.7.2 Software Environment**

```bash
# Python environment (managed via uv)
Python: 3.10.16 (.venv virtual environment)

# Core dependencies (from uv.lock)
numpy==2.2.6                # CPU linear algebra
cupy-cuda12x==13.6.0       # GPU linear algebra (CUDA 12.x)
scipy==1.14.2              # Statistical tests
matplotlib==3.9.4          # Plotting
seaborn==0.13.2            # Enhanced visualizations
pandas==2.2.4              # Data manipulation

# Database & I/O
duckdb==1.1.3              # Embedded database
tsplib95==0.7.1            # TSPLIB parser

# Development tools
pytest==8.3.4              # Testing framework
mypy==1.15.0               # Static type checking
black==24.10.0             # Code formatter
ruff==0.9.6                # Fast linter

# CUDA environment
CUDA Toolkit: 12.6
CUDA Driver: 12.6 (compatible with 525.60.11+)
cuDNN: Not required (no deep learning operations)

# System
OS: Debian GNU/Linux 13 (trixie)
Kernel: 6.1.0-28-amd64
GCC: 12.2.0 (for CuPy compilation)
```

**A.7.3 Memory Profiling Setup**

```python
import cupy as cp
from contextlib import contextmanager

@contextmanager
def profile_gpu_memory():
    """
    Context manager for GPU memory profiling.

    Usage:
        with profile_gpu_memory():
            # GPU operations here
            result = algorithm(problem, backend=cp)
    """
    mempool = cp.get_default_memory_pool()
    pinned_mempool = cp.get_default_pinned_memory_pool()

    # Record baseline
    used_before = mempool.used_bytes()
    total_before = mempool.total_bytes()

    yield  # Execute wrapped code

    # Record after execution
    used_after = mempool.used_bytes()
    total_after = mempool.total_bytes()
    peak = mempool.peak_bytes()

    print(f"GPU Memory Profile:")
    print(f"  Used: {used_before / 1e9:.3f} GB → {used_after / 1e9:.3f} GB")
    print(f"  Peak: {peak / 1e9:.3f} GB")
    print(f"  Total allocated: {total_after / 1e9:.3f} GB")
    print(f"  Utilization: {peak / 4e9 * 100:.1f}% of 4GB VRAM")
```

### A.8 Protocolos de Medição de Desempenho

Implementação dos métodos estatísticos documentados na Seção 3.4.1 e no documento `gpu_cpu_comparison_methodology.md`:

**A.8.1 Medição de Tempo**

```python
import time
from typing import Callable, Any

def measure_execution_time(
    func: Callable,
    *args,
    repetitions: int = 1,
    warmup: int = 0,
    **kwargs
) -> tuple[Any, float, float]:
    """
    Measure function execution time with warmup runs.

    Args:
        func: Function to measure
        *args: Positional arguments to func
        repetitions: Number of timed repetitions
        warmup: Number of warmup runs (not timed)
        **kwargs: Keyword arguments to func

    Returns:
        result: Function return value (from last execution)
        mean_time: Mean execution time (seconds)
        std_time: Standard deviation (seconds)
    """
    times = []
    result = None

    # Warmup runs (GPU kernel compilation, cache warming)
    for _ in range(warmup):
        result = func(*args, **kwargs)

    # Timed runs
    for _ in range(repetitions):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    import numpy as np
    mean_time = np.mean(times)
    std_time = np.std(times, ddof=1)  # Sample std dev

    return result, mean_time, std_time
```

**A.8.2 Testes Estatísticos**

Seguindo a metodologia de Hoefler & Belli (2015):

```python
from scipy.stats import shapiro, ttest_rel, wilcoxon
import numpy as np

def compare_backends_statistically(
    cpu_times: np.ndarray,
    gpu_times: np.ndarray,
    alpha: float = 0.05
) -> dict:
    """
    Statistically rigorous comparison of CPU vs GPU execution times.

    Methodology from Hoefler & Belli (2015) "Scientific Benchmarking of
    Parallel Computing Systems".

    Args:
        cpu_times: Array of CPU execution times (n repetitions)
        gpu_times: Array of GPU execution times (n repetitions)
        alpha: Significance level (default 0.05 = 95% confidence)

    Returns:
        dict with statistical test results
    """
    results = {}

    # 1. Normality test (Shapiro-Wilk)
    _, p_cpu = shapiro(cpu_times)
    _, p_gpu = shapiro(gpu_times)
    both_normal = (p_cpu > alpha) and (p_gpu > alpha)

    results['normality'] = {
        'cpu_p_value': p_cpu,
        'gpu_p_value': p_gpu,
        'both_normal': both_normal
    }

    # 2. Paired comparison test
    if both_normal:
        # Parametric: Paired t-test
        stat, p_value = ttest_rel(cpu_times, gpu_times)
        test_name = "Paired t-test"
    else:
        # Non-parametric: Wilcoxon signed-rank test
        stat, p_value = wilcoxon(cpu_times, gpu_times)
        test_name = "Wilcoxon signed-rank"

    results['test'] = {
        'name': test_name,
        'statistic': stat,
        'p_value': p_value,
        'significant': p_value < alpha
    }

    # 3. Effect size (Cohen's d)
    mean_diff = cpu_times.mean() - gpu_times.mean()
    pooled_std = np.sqrt((cpu_times.std(ddof=1)**2 + gpu_times.std(ddof=1)**2) / 2)
    cohens_d = mean_diff / pooled_std

    # Interpret effect size
    if abs(cohens_d) < 0.2:
        interpretation = "negligible"
    elif abs(cohens_d) < 0.5:
        interpretation = "small"
    elif abs(cohens_d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    results['effect_size'] = {
        'cohens_d': cohens_d,
        'interpretation': interpretation
    }

    # 4. Speedup with confidence interval (bootstrap)
    speedups = cpu_times / gpu_times
    mean_speedup = speedups.mean()

    # Bootstrap CI (10,000 resamples)
    bootstrap_speedups = []
    n = len(cpu_times)
    for _ in range(10000):
        indices = np.random.randint(0, n, size=n)
        cpu_sample = cpu_times[indices]
        gpu_sample = gpu_times[indices]
        bootstrap_speedups.append(cpu_sample.mean() / gpu_sample.mean())

    ci_low, ci_high = np.percentile(bootstrap_speedups, [2.5, 97.5])

    results['speedup'] = {
        'mean': mean_speedup,
        'ci_95_low': ci_low,
        'ci_95_high': ci_high
    }

    return results
```

**A.8.3 Visualização de Resultados**

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_performance_comparison(
    cpu_times: np.ndarray,
    gpu_times: np.ndarray,
    instance_name: str,
    stats: dict
) -> None:
    """
    Create publication-quality performance comparison plot.

    Follows visualization guidelines from Hoefler & Belli (2015):
        - Box plots to show distribution
        - Error bars for confidence intervals
        - Statistical significance markers
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Box plot with distributions
    data = [cpu_times * 1000, gpu_times * 1000]  # Convert to ms
    bp = ax1.boxplot(data, labels=['CPU (NumPy)', 'GPU (CuPy)'],
                     patch_artist=True, notch=True)

    for patch, color in zip(bp['boxes'], ['#2E86AB', '#A23B72']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.set_ylabel('Execution Time (ms)')
    ax1.set_title(f'{instance_name} Performance Distribution')
    ax1.grid(axis='y', alpha=0.3)

    # Add statistical significance marker
    p = stats['test']['p_value']
    if p < 0.001:
        sig = '***'
    elif p < 0.01:
        sig = '**'
    elif p < 0.05:
        sig = '*'
    else:
        sig = 'n.s.'

    max_y = max(data[0].max(), data[1].max())
    ax1.text(1.5, max_y * 1.1, sig, ha='center', fontsize=16)
    ax1.text(1.5, max_y * 1.15, f"p={p:.2e}", ha='center', fontsize=9)

    # Plot 2: Speedup with confidence interval
    speedup = stats['speedup']
    ax2.bar(0, speedup['mean'], width=0.6, alpha=0.7, color='#F18F01')
    ax2.errorbar(0, speedup['mean'],
                yerr=[[speedup['mean'] - speedup['ci_95_low']],
                      [speedup['ci_95_high'] - speedup['mean']]],
                fmt='none', ecolor='black', capsize=10, capthick=2)

    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2,
               alpha=0.7, label='Break-even')
    ax2.set_ylabel('GPU Speedup')
    ax2.set_title(f'GPU Speedup: {speedup["mean"]:.2f}x '
                 f'(95% CI: [{speedup["ci_95_low"]:.2f}, '
                 f'{speedup["ci_95_high"]:.2f}])')
    ax2.set_xticks([0])
    ax2.set_xticklabels(['GPU vs CPU'])
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    # Add effect size annotation
    d = stats['effect_size']['cohens_d']
    interp = stats['effect_size']['interpretation']
    ax2.text(0, speedup['mean'] + 0.2,
             f"Cohen's d = {d:.3f}\n({interp} effect)",
             ha='center', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.show()
```

**A.8.4 Protocolo Completo de Benchmark**

```python
def benchmark_algorithm(
    algorithm: Callable,
    problem: Problem,
    backends: dict,
    repetitions: int = 30,
    warmup: int = 3
) -> dict:
    """
    Complete benchmarking protocol following academic standards.

    Args:
        algorithm: Algorithm function to benchmark
        problem: Problem instance
        backends: Dict mapping backend names to modules
        repetitions: Number of repetitions (≥30 for CLT)
        warmup: Number of warmup runs

    Returns:
        Complete benchmark results with statistical analysis
    """
    results = {}

    for backend_name, backend_module in backends.items():
        print(f"Benchmarking {algorithm.__name__} on {problem.name} ({backend_name})...")

        # Collect execution times
        times = []
        solutions = []

        # Warmup
        for _ in range(warmup):
            _ = algorithm(problem, backend=backend_module)

        # Timed repetitions
        for rep in range(repetitions):
            start = time.perf_counter()
            solution = algorithm(problem, backend=backend_module)
            elapsed = time.perf_counter() - start

            times.append(elapsed)
            solutions.append(solution)

        # Convert to NumPy arrays
        times = np.array(times)

        # Store results
        results[backend_name] = {
            'times': times,
            'mean': times.mean(),
            'std': times.std(ddof=1),
            'solutions': solutions
        }

    # Statistical comparison
    if 'NumPy' in results and 'CuPy' in results:
        stats = compare_backends_statistically(
            results['NumPy']['times'],
            results['CuPy']['times']
        )
        results['statistical_comparison'] = stats

    return results
```

---

## APÊNDICE B - PSEUDOCÓDIGO DOS ALGORITMOS

### B.1 Nearest Neighbor Construction

```
Algorithm: Nearest Neighbor Heuristic
Input: Distance matrix D (n × n)
Output: Tour π

1: π ← [0]  // Start at depot/first node
2: unvisited ← {1, 2, ..., n-1}
3: current ← 0
4: while unvisited ≠ ∅ do
5:     nearest ← argmin_{j ∈ unvisited} D[current, j]
6:     Append nearest to π
7:     Remove nearest from unvisited
8:     current ← nearest
9: end while
10: return π
```

### B.2 2-opt Improvement

```
Algorithm: 2-opt Local Search
Input: Tour π, Distance matrix D
Output: Improved tour π'

1: improved ← true
2: while improved do
3:     improved ← false
4:     for i ← 0 to n-2 do
5:         for j ← i+2 to n do
6:             δ ← D[π[i], π[j]] + D[π[i+1], π[j+1]]
7:                 - D[π[i], π[i+1]] - D[π[j], π[j+1]]
8:             if δ < 0 then  // Improvement found
9:                 Reverse segment π[i+1 : j]
10:                improved ← true
11:                break  // First-improvement strategy
12:            end if
13:        end for
14:        if improved then break
15:    end for
16: end while
17: return π
```

### B.3 Simulated Annealing with 2-opt

```
Algorithm: Simulated Annealing + 2-opt
Input: Initial tour π₀, T₀ (initial temp), α (cooling rate)
Output: Best tour found

1: π_current ← π₀
2: π_best ← π₀
3: T ← T₀
4: while T > T_min do
5:     π_neighbor ← Generate2OptMove(π_current)
6:     Δ ← cost(π_neighbor) - cost(π_current)
7:     if Δ < 0 then
8:         π_current ← π_neighbor  // Accept improvement
9:     else
10:        p ← exp(-Δ / T)
11:        if random() < p then
12:            π_current ← π_neighbor  // Accept with probability
13:        end if
14:    end if
15:    if cost(π_current) < cost(π_best) then
16:        π_best ← π_current
17:    end if
18:    T ← α × T  // Geometric cooling
19: end while
20: return π_best
```

---

## Academic References

### Benchmark Instance Sources

[^reinelt1991]: Reinelt, G. (1991). "TSPLIB—A traveling salesman problem library." _ORSA Journal on Computing_ (now _INFORMS Journal on Computing_), 3(4), 376-384. DOI: [10.1287/ijoc.3.4.376](https://doi.org/10.1287/ijoc.3.4.376)

> **Note**: TSPLIB includes both symmetric TSP and asymmetric TSP (ATSP) instances. All TSP instances (berlin52, lin318, d2103, etc.) and ATSP instances (br17, ry48p, ft53, ft70, ftv170, rbg403) used in this work are from the TSPLIB benchmark library maintained at Heidelberg University.

[^christofides1969]: Christofides, N., & Eilon, S. (1969). "An algorithm for the vehicle-dispatching problem." _Operational Research Quarterly_, 20(3), 309-318. DOI: [10.1057/jors.1969.75](https://doi.org/10.1057/jors.1969.75)

> **Note**: This seminal paper introduced the first set of VRP benchmark instances, later extended by Golden et al. (1984). CVRP instances (eil22, eil31, eilA76, eilA101) follow the naming convention established in this work. The Li_25 instance is from a later extension of this benchmark family.

### GPU Computing for Optimization

[^fujimoto2011]: Fujimoto, N., & Tsutsui, S. (2011). "A highly-parallel TSP solver for a GPU computing platform." In _Numerical Methods and Applications: 7th International Conference, NMA 2010_ (pp. 264-271). Springer. DOI: [10.1007/978-3-642-18466-6_31](https://doi.org/10.1007/978-3-642-18466-6_31)
[^tsp_gpu]: Rocki, K., & Suda, R. (2013). "High performance GPU accelerated local optimization in TSP." In _Proceedings of the 2013 IEEE 27th International Symposium on Parallel and Distributed Processing Workshops and PhD Forum_ (pp. 1788-1796). IEEE. DOI: [10.1109/IPDPSW.2013.227](https://doi.org/10.1109/IPDPSW.2013.227)

### Experimental Design and Statistical Methods

[^statistical_power]: Montgomery, D.C. (2017). _Design and Analysis of Experiments_, 9th edition. Wiley. ISBN: 978-1-119-32093-7

> **Note**: This textbook is the standard reference for experimental design in engineering and computer science. Chapter 2 covers sample size determination and statistical power analysis. The guidance that n=30 provides adequate power for detecting 10% differences with typical variation (CV ≤ 15%) is derived from Section 2.4 (Power and Sample Size).

---

**FIM DO DOCUMENTO**
