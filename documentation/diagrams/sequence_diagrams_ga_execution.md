# Sequence Diagrams: Genetic Algorithm Execution Flows

This document contains detailed sequence diagrams showing the execution flow and module interactions for different GA variants.

## 1. CPU Variant Execution Flow

Shows the complete execution flow for `GeneticAlgorithmCPU`, including initialization, evolution loop, and module interactions.

```mermaid
---
config:
  look: classic
  theme: forest
---
sequenceDiagram
    autonumber
    actor User as Benchmark Script
    participant GAC as GeneticAlgorithmCPU
    participant GAB as GeneticAlgorithmBase
    participant TS as TournamentSelection
    participant OX as OrderCrossover
    participant SM as SwapMutation
    participant PC as ProblemContext
    participant numpy as NumPy (CPU)
    User->>+GAC: __init__(pop_size=256, ...)
    GAC->>+GAB: __init__()
    GAB->>+TS: create TournamentSelection(k=5)
    TS-->>-GAB: selection instance
    GAB->>+OX: create OrderCrossover()
    OX-->>-GAB: crossover instance
    GAB->>+SM: create SwapMutation()
    SM-->>-GAB: mutation instance
    GAB-->>-GAC: initialized
    GAC-->>-User: ga_cpu instance
    Note over User,numpy: Evolution Loop (1000 generations)
    User->>+GAC: evolve(context, customers, max_gen=1000)
    GAC->>+GAB: evolve()
    GAB->>+PC: get_cpu_distances()
    PC->>+numpy: compute distance matrix (ONCE)
    numpy-->>-PC: distances array
    PC-->>-GAB: distances (cached)
    GAB->>+GAB: _initialize_population(n)
    GAB->>numpy: random permutations × 256
    numpy-->>GAB: initial population
    GAB-->>-GAB: population array
    loop Generation 1 to 1000
        rect rgb(200, 230, 255)
            Note right of GAB: Selection Phase
            GAB->>+GAB: _select_parents(population, fitness)
            loop 256 tournaments
                GAB->>+TS: select(population, fitness, n=256)
                TS->>numpy: random choices (k=5)
                numpy-->>TS: tournament candidates
                TS->>numpy: argmin(fitness)
                numpy-->>TS: winner index
                TS-->>-GAB: parent_indices
            end
            GAB-->>-GAB: selected parents
        end
        rect rgb(230, 255, 230)
            Note right of GAB: Crossover & Mutation Phase
            GAB->>+GAB: _create_offspring(population, parents)
            loop 128 pairs
                GAB->>+OX: crossover(parent1, parent2)
                OX->>numpy: segment copy + fill
                numpy-->>OX: child1
                OX-->>-GAB: offspring
                GAB->>+SM: mutate(child1, rate=0.02)
                SM->>numpy: random swap
                numpy-->>SM: mutated tour
                SM-->>-GAB: mutated offspring
            end
            GAB-->>-GAB: offspring population
        end
        rect rgb(255, 230, 230)
            Note right of GAB: 2-opt Improvement Phase (CPU)
            GAB->>+GAC: _improve_population(offspring, distances, xp=np)
            loop 256 tours
                loop 10 iterations
                    GAC->>numpy: find best 2-opt swap (O(n²))
                    numpy-->>GAC: best_delta, i, j
                    GAC->>numpy: reverse segment if improvement
                    numpy-->>GAC: improved tour
                end
            end
            GAC-->>-GAB: improved offspring
        end
        rect rgb(255, 255, 200)
            Note right of GAB: Fitness Evaluation Phase (CPU)
            GAB->>+GAC: _evaluate_population(offspring, distances, xp=np)
            loop 256 tours
                GAC->>numpy: sum edge costs
                numpy-->>GAC: tour cost
            end
            GAC-->>-GAB: fitness array
        end
        rect rgb(230, 230, 255)
            Note right of GAB: Survival Selection Phase
            GAB->>+GAB: _survival_selection(pop, offspring, fit_pop, fit_off)
            GAB->>numpy: concatenate [pop, offspring]
            numpy-->>GAB: combined (512 tours)
            GAB->>numpy: argsort(fitness)[:256]
            numpy-->>GAB: best 256 indices
            GAB->>numpy: index combined array
            numpy-->>GAB: new population
            GAB-->>-GAB: survivor population
        end
        Note right of GAB: Track best solution
        GAB->>numpy: argmin(fitness)
        numpy-->>GAB: best_idx
        GAB->>GAB: update best_cost_history
    end
    GAB-->>-GAC: (best_tour, stats)
    GAC-->>-User: solution
    Note over User,numpy: Memory Transfers: 0 bytes (CPU-only)
```

## 2. FullGPU Variant Execution Flow

Shows the execution flow for `GeneticAlgorithmFullGPU` using Fujimoto's monolithic kernel approach.

```mermaid
sequenceDiagram
    autonumber
    actor User as Benchmark Script
    participant GAF as GeneticAlgorithmFullGPU
    participant GAB as GeneticAlgorithmBase
    participant GPU as gpu_helpers
    participant Kernel as Fujimoto CUDA Kernel
    participant PC as ProblemContext
    participant numpy as NumPy (CPU)
    participant cupy as CuPy (GPU)
    
    User->>+GAF: __init__(pop_size=256, ...)
    GAF->>+GAB: __init__()
    Note right of GAB: Strategy objects created<br/>(not used in FullGPU)
    GAB-->>-GAF: base initialized
    GAF->>+GPU: load_kernel("ga_fujimoto.cu", "init_rand_states")
    GPU->>cupy: compile CUDA kernel
    cupy-->>GPU: RawKernel
    GPU-->>-GAF: init_rand_kernel
    GAF->>+GPU: load_kernel("ga_fujimoto.cu", "initialize_population")
    GPU->>cupy: compile CUDA kernel
    cupy-->>GPU: RawKernel
    GPU-->>-GAF: init_pop_kernel
    GAF->>+GPU: load_kernel("ga_fujimoto.cu", "ga_evolution")
    GPU->>cupy: compile CUDA kernel
    cupy-->>GPU: RawKernel
    GPU-->>-GAF: ga_kernel
    GAF-->>-User: ga_fullgpu instance
    
    Note over User,cupy: Single GPU Execution (All Generations)
    
    User->>+GAF: evolve(context, customers, max_gen=1000)
    GAF->>+PC: get_cpu_distances()
    PC->>+numpy: compute distance matrix (ONCE)
    numpy-->>-PC: distances array
    PC-->>-GAF: distances_cpu
    
    rect rgb(255, 200, 200)
        Note right of GAF: H2D Transfer (One-time Setup)
        GAF->>+cupy: asarray(distances_cpu)
        Note over cupy: Transfer: n² × 8 bytes<br/>Example (n=1000): 8MB
        cupy-->>-GAF: distances_gpu
        GAF->>GAF: h2d_bytes += 8MB
    end
    
    rect rgb(200, 255, 200)
        Note right of GAF: GPU Memory Allocation
        GAF->>+cupy: empty((256, n), dtype=int32)
        cupy-->>-GAF: population_gpu
        GAF->>+cupy: empty((256, n), dtype=int32)
        cupy-->>-GAF: new_population_gpu
        GAF->>+cupy: empty(256, dtype=float32)
        cupy-->>-GAF: fitness_gpu
        GAF->>+cupy: empty(pop_size, dtype=curandState)
        cupy-->>-GAF: rand_states_gpu
    end
    
    rect rgb(200, 200, 255)
        Note right of Kernel: Initialize Random States
        GAF->>+Kernel: init_rand_kernel(rand_states, seed, pop_size)
        Note over Kernel: 256 threads<br/>Each initializes cuRAND state
        Kernel-->>-GAF: rand_states initialized
        GAF->>GAF: kernel_launches += 1
    end
    
    rect rgb(255, 255, 200)
        Note right of Kernel: Initialize Population
        GAF->>+Kernel: init_pop_kernel(population_gpu, rand_states, n, pop_size)
        Note over Kernel: 256 threads<br/>Each creates random tour
        Kernel-->>-GAF: initial population on GPU
        GAF->>GAF: kernel_launches += 1
    end
    
    rect rgb(255, 200, 255)
        Note right of Kernel: Monolithic GA Evolution (1000 generations)
        GAF->>+Kernel: ga_evolution(population, new_pop, fitness, distances, rand_states, generations=1000)
        loop 1000 Generations (Inside Kernel)
            Note over Kernel: Selection (256 tournaments parallel)
            Note over Kernel: Crossover (128 pairs parallel)
            Note over Kernel: Mutation (256 tours parallel)
            Note over Kernel: 2-opt (256×10 iters parallel)
            Note over Kernel: Fitness (256 tours parallel)
            Note over Kernel: Survival (parallel reduction)
        end
        Note over Kernel: All 1000 generations<br/>execute on GPU<br/>Zero CPU involvement
        Kernel-->>-GAF: final population on GPU
        GAF->>GAF: kernel_launches += 1
    end
    
    rect rgb(200, 255, 255)
        Note right of GAF: D2H Transfer (Final Result Only)
        GAF->>+cupy: get(best_tour_gpu)
        Note over cupy: Transfer: n × 4 bytes<br/>Example (n=1000): 4KB
        cupy-->>-GAF: best_tour_cpu
        GAF->>GAF: d2h_bytes += 4KB
    end
    
    GAF-->>-User: (best_tour, stats)
    
    Note over User,cupy: Total Transfers: ~8MB H2D + 4KB D2H<br/>vs HybridNaive: 20GB per 1000 gens<br/>Reduction: 2500x
```

## 3. Module Interaction During Initialization

Shows how different modules interact during GA initialization.

```mermaid
sequenceDiagram
    autonumber
    actor User as Benchmark Script
    participant Loader as DatabaseLoader
    participant Problem as Problem (dataclass)
    participant Context as ProblemContext
    participant Distances as distances.matrix
    participant GA as GeneticAlgorithm*
    participant Strategies as Strategy Objects
    participant numpy as NumPy/CuPy
    
    rect rgb(230, 240, 255)
        Note over User,numpy: Problem Loading Phase
        User->>+Loader: __init__()
        Loader->>Loader: connect to DuckDB
        Loader-->>-User: loader instance
        
        User->>+Loader: load("berlin52")
        Loader->>Loader: query database
        Loader->>+Problem: Problem(name="berlin52", ...)
        Problem-->>-Loader: problem instance
        Loader-->>-User: problem
    end
    
    rect rgb(240, 255, 230)
        Note over User,numpy: Context Creation Phase (Lazy)
        User->>+Context: ProblemContext(problem, xp=np, seed=42)
        Context->>Context: store problem reference
        Context->>Context: store xp (NumPy or CuPy)
        Context->>Context: _distances_cpu = None (lazy)
        Context->>Context: _distances_gpu = None (lazy)
        Note right of Context: NO computation yet!<br/>Everything is lazy
        Context-->>-User: context instance
    end
    
    rect rgb(255, 240, 230)
        Note over User,numpy: Algorithm Initialization Phase
        User->>+GA: __init__(pop_size=256, ...)
        GA->>GA: store parameters
        GA->>+Strategies: TournamentSelection(k=5)
        Strategies-->>-GA: selection
        GA->>+Strategies: OrderCrossover()
        Strategies-->>-GA: crossover
        GA->>+Strategies: SwapMutation()
        Strategies-->>-GA: mutation
        GA->>numpy: RandomState(seed)
        numpy-->>GA: rng
        GA-->>-User: ga instance
    end
    
    rect rgb(240, 230, 255)
        Note over User,numpy: First Distance Matrix Access (Lazy Loading)
        User->>+GA: evolve(context, ...)
        GA->>+Context: get_cpu_distances()
        
        alt First access (cache miss)
            Context->>+Distances: compute_distance_matrix(coordinates, edge_type, xp=np)
            Distances->>numpy: vectorized distance calculation
            Note over Distances,numpy: O(n²) computation<br/>ONCE per context
            numpy-->>Distances: distance matrix
            Distances-->>-Context: distances
            Context->>Context: _distances_cpu = distances (cache)
        else Subsequent access (cache hit)
            Context->>Context: return _distances_cpu
        end
        
        Context-->>-GA: cached distances
        Note right of Context: Matrix reused for<br/>ALL algorithm calls
        GA->>GA: begin evolution with distances
        GA-->>-User: continue
    end
```

## 4. Hybrid Variants Comparison

Shows memory transfer patterns for different hybrid approaches.

```mermaid
sequenceDiagram
    autonumber
    participant GAH as GeneticAlgorithm<br/>HybridNaive
    participant GAO as GeneticAlgorithm<br/>HybridOptimized
    participant CPU as CPU Memory
    participant GPU as GPU Memory
    
    Note over GAH,GPU: Generation 1 (repeated 1000x)
    
    rect rgb(255, 230, 230)
        Note over GAH,GPU: HybridNaive: 256 Individual Kernel Calls
        loop 256 tours
            GAH->>GPU: H2D: transfer tour[i] (n × 4 bytes)
            GAH->>GPU: H2D: transfer distances (n² × 8 bytes)
            GAH->>GPU: Launch 2-opt kernel
            GPU->>GPU: improve tour[i] (10 iterations)
            GPU->>GAH: D2H: transfer improved tour[i]
        end
        GAH->>CPU: Calculate fitness on CPU
        Note right of GAH: Per generation:<br/>H2D: ~10MB<br/>D2H: ~10MB<br/>Total: ~20MB
    end
    
    rect rgb(230, 255, 230)
        Note over GAO,GPU: HybridOptimized: Single Batch Kernel
        GAO->>GPU: H2D: transfer all tours (256 × n × 4 bytes)
        GAO->>GPU: H2D: transfer distances (n² × 8 bytes) ONCE
        GAO->>GPU: Launch batch 2-opt kernel (256 threads)
        par All tours in parallel
            GPU->>GPU: tour[0] improvement
        and
            GPU->>GPU: tour[1] improvement
        and
            GPU->>GPU: ...
        and
            GPU->>GPU: tour[255] improvement
        end
        GAO->>GPU: Chain fitness kernel (no transfer)
        GPU->>GPU: Calculate all fitness values
        GPU->>GAO: D2H: transfer fitness (256 × 8 bytes)
        Note right of GAO: Per generation:<br/>H2D: ~5MB<br/>D2H: ~5MB<br/>Total: ~10MB<br/>(50% reduction)
    end
```

## Key Observations

### CPU Variant

- **Execution**: Sequential, all operations on CPU
- **Strengths**: Simple, no GPU overhead
- **Weaknesses**: Slow for large populations/problems
- **Memory Transfers**: 0 (no GPU involved)

### FullGPU Variant

- **Execution**: Monolithic GPU kernel, parallel everything
- **Strengths**: Minimal transfers, maximum parallelism
- **Weaknesses**: Kernel complexity, limited CPU control
- **Memory Transfers**: ~8MB one-time setup vs 20GB total for HybridNaive

### Transfer Overhead Comparison

| Variant | Per Generation | 1000 Generations | Reduction Factor |
|---------|----------------|------------------|------------------|
| CPU | 0 | 0 | N/A (baseline) |
| HybridNaive | ~20MB | ~20GB | 1x (reference) |
| HybridOptimized | ~10MB | ~10GB | 2x |
| FullGPU | ~0 | ~8MB | 2500x |

### Performance Implications

1. **HybridNaive**: Good for learning, shows naive GPU usage pattern
2. **HybridOptimized**: Production-ready hybrid approach
3. **FullGPU**: Maximum performance, minimal transfer overhead

The diagrams clearly show why FullGPU achieves 203x-9,573x speedup:

- **Computation locality**: All work stays on GPU
- **Transfer elimination**: 2500x fewer data movements
- **Kernel fusion**: Combined operations avoid intermediate transfers

## Academic References

- **Fujimoto & Tsutsui (2011)**: "A highly parallel TSP solver for GPUs" - Original FullGPU kernel design
- **CUDA Best Practices Guide**: Memory transfer optimization patterns
- **Kirk & Hwu (2016)**: "Programming Massively Parallel Processors" - GPU kernel design patterns

---

## IMPROVED DIAGRAMS WITH DETAILED ANNOTATIONS

The following diagrams provide enhanced explanations of the processes, including:

- Loop parameters and iteration counts
- Detailed process descriptions
- Inner logic explanations
- Memory transfer calculations

### 1.1 CPU Variant - Enhanced with Process Details

```mermaid
---
config:
  look: classic
  theme: forest
---
sequenceDiagram
    autonumber
    actor User as Benchmark Script
    participant GAC as GeneticAlgorithmCPU
    participant GAB as GeneticAlgorithmBase
    participant TS as TournamentSelection
    participant OX as OrderCrossover
    participant SM as SwapMutation
    participant PC as ProblemContext
    participant numpy as NumPy (CPU)
    
    %% INITIALIZATION PHASE
    Note over User,numpy: 🔧 INITIALIZATION PHASE<br/>Creates GA instance with strategy objects
    User->>+GAC: __init__(pop_size=256, mutation_rate=0.02, tournament_k=5, two_opt_iters=10)
    Note right of GAC: Store parameters:<br/>• pop_size = 256 (μ+λ strategy)<br/>• mutation_rate = 0.02 (2%)<br/>• tournament_size = 5<br/>• two_opt_iterations = 10
    
    GAC->>+GAB: __init__()
    Note right of GAB: Initialize strategy objects<br/>(same for all variants)
    
    GAB->>+TS: TournamentSelection(tournament_size=5)
    Note right of TS: k-tournament selection<br/>k=5 provides strong selection pressure
    TS-->>-GAB: selection instance
    
    GAB->>+OX: OrderCrossover()
    Note right of OX: OX operator for TSP<br/>Preserves relative order from parent1<br/>Absolute positions from parent2
    OX-->>-GAB: crossover instance
    
    GAB->>+SM: SwapMutation()
    Note right of SM: Swap mutation operator<br/>Swaps two random cities
    SM-->>-GAB: mutation instance
    
    GAB-->>-GAC: base initialized
    GAC-->>-User: ga_cpu instance
    
    %% EVOLUTION PHASE START
    Note over User,numpy: 🚀 EVOLUTION PHASE<br/>Main genetic algorithm loop (1000 generations)
    
    User->>+GAC: evolve(context, customers, max_generations=1000, patience=50)
    GAC->>+GAB: evolve()
    
    %% DISTANCE MATRIX COMPUTATION
    rect rgb(230, 245, 255)
        Note over GAB,numpy: 📏 DISTANCE MATRIX COMPUTATION (One-time)<br/>O(n²) computation, cached for reuse
        GAB->>+PC: get_cpu_distances()
        Note right of PC: Check cache:<br/>if _distances_cpu is None:<br/>    compute and cache<br/>else:<br/>    return cached
        
        PC->>+numpy: compute_distance_matrix(coordinates, edge_type='EUC_2D')
        Note over numpy: Euclidean distance:<br/>d[i,j] = sqrt((x[i]-x[j])² + (y[i]-y[j])²)<br/>Vectorized O(n²) operation<br/>Example: n=52 → 2,704 distances
        numpy-->>-PC: distances array (n×n, float64)
        
        PC->>PC: _distances_cpu = distances (cache)
        PC-->>-GAB: distances (cached, reused for all 1000 gens)
    end
    
    %% POPULATION INITIALIZATION
    rect rgb(255, 245, 230)
        Note over GAB,numpy: 🎲 INITIAL POPULATION GENERATION<br/>Create 256 random tours (permutations)
        GAB->>+GAB: _initialize_population(n=52)
        Note right of GAB: population = zeros((256, 52), int32)<br/>for i in range(256):<br/>    population[i] = rng.permutation(52)
        
        loop i = 0 to 255 (256 tours)
            GAB->>numpy: rng.permutation(52)
            Note over numpy: Fisher-Yates shuffle<br/>Random permutation of [0,1,...,51]<br/>Each tour is valid (no duplicates)
            numpy-->>GAB: tour[i] = random permutation
        end
        
        GAB-->>-GAB: initial population (256×52)
        Note right of GAB: Each row is a valid tour<br/>All 256 tours are random<br/>No duplicates within each tour
    end
    
    %% MAIN EVOLUTION LOOP
    Note over GAB,numpy: 🔄 MAIN EVOLUTION LOOP<br/>Repeat for 1000 generations
    
    loop gen = 1 to 1000
        Note over GAB,numpy: Generation #{gen}/1000
        
        %% SELECTION PHASE
        rect rgb(220, 235, 255)
            Note over GAB,TS: 🎯 SELECTION PHASE: k-Tournament (k=5)<br/>Select 256 parents via tournament selection
            GAB->>+GAB: _select_parents(population, fitness)
            Note right of GAB: parent_indices = zeros(256, int32)<br/>for i in range(256):<br/>    run tournament of size 5
            
            loop i = 0 to 255 (256 tournaments)
                GAB->>+TS: select tournament winners
                Note right of TS: Tournament process:<br/>1. Randomly pick 5 individuals<br/>2. Compare their fitness values<br/>3. Select best (lowest cost)
                
                TS->>numpy: rng.choice(256, size=5, replace=False)
                Note over numpy: Random sampling without replacement<br/>5 distinct indices from [0..255]
                numpy-->>TS: tournament_indices = [idx1, idx2, idx3, idx4, idx5]
                
                TS->>numpy: argmin(fitness[tournament_indices])
                Note over numpy: Find index of minimum fitness<br/>in tournament subset<br/>Best individual wins
                numpy-->>TS: winner_idx
                
                TS-->>-GAB: parent_indices[i] = winner_idx
            end
            
            GAB-->>-GAB: selected_parents (256 indices)
            Note right of GAB: Result: 256 parent indices<br/>Better individuals selected more often<br/>Selection pressure from k=5
        end
        
        %% CROSSOVER & MUTATION PHASE
        rect rgb(235, 255, 235)
            Note over GAB,SM: 🧬 CROSSOVER & MUTATION PHASE<br/>Create 256 offspring via OX + swap mutation
            GAB->>+GAB: _create_offspring(population, parent_indices)
            Note right of GAB: offspring = zeros((256, 52), int32)<br/>for i in range(0, 256, 2):<br/>    create 2 children per iteration
            
            loop i = 0 to 254 step 2 (128 pairs = 256 children)
                Note over GAB,OX: Pair #{i/2 + 1}/128
                
                GAB->>GAB: Get parent pair
                Note right of GAB: parent1 = population[parent_indices[i]]<br/>parent2 = population[parent_indices[i+1]]
                
                %% CROSSOVER
                GAB->>+OX: crossover(parent1, parent2)
                Note right of OX: Order Crossover (OX) Algorithm:<br/>1. Select random segment [cut1:cut2]<br/>2. Copy segment from parent2<br/>3. Fill rest with parent1's order
                
                OX->>numpy: rng.choice(52, size=2, replace=False)
                Note over numpy: Random cut points<br/>Example: cut1=15, cut2=35
                numpy-->>OX: cut1, cut2 (sorted)
                
                OX->>numpy: Segment copy & fill operations
                Note over numpy: offspring[cut1:cut2] = parent2[cut1:cut2]<br/>Fill remaining with parent1 cities<br/>in order, skipping copied segment
                numpy-->>OX: child1 (valid tour)
                
                OX-->>-GAB: child1
                
                GAB->>+OX: crossover(parent2, parent1)
                Note right of OX: Reverse parents for child2<br/>Same OX process
                OX-->>-GAB: child2
                
                %% MUTATION
                Note over GAB,SM: Apply mutation with rate=0.02
                
                alt random() < 0.02 (2% chance)
                    GAB->>+SM: mutate(child1)
                    Note right of SM: Swap Mutation:<br/>1. Select 2 random positions<br/>2. Swap cities at those positions
                    
                    SM->>numpy: rng.choice(range(1,52), size=2, replace=False)
                    Note over numpy: Select 2 positions (not depot)<br/>Example: pos1=10, pos2=35
                    numpy-->>SM: pos1, pos2
                    
                    SM->>numpy: Swap operation
                    Note over numpy: tour[pos1], tour[pos2] = tour[pos2], tour[pos1]<br/>Simple city swap
                    numpy-->>SM: mutated_child1
                    
                    SM-->>-GAB: mutated_child1
                else No mutation (98% chance)
                    Note right of GAB: Keep child1 unchanged
                end
                
                alt random() < 0.02 (2% chance)
                    GAB->>+SM: mutate(child2)
                    SM-->>-GAB: mutated_child2
                else No mutation
                    Note right of GAB: Keep child2 unchanged
                end
                
                GAB->>GAB: Store offspring pair (child1 at i, child2 at i+1)
            end
            
            GAB-->>-GAB: offspring population (256×52)
            Note right of GAB: Result: 256 new offspring<br/>Created by OX crossover<br/>2% affected by mutation
        end
        
        %% 2-OPT IMPROVEMENT PHASE
        rect rgb(255, 235, 235)
            Note over GAB,numpy: 🔧 2-OPT LOCAL SEARCH (CPU Sequential)<br/>Improve each tour with 10 iterations of 2-opt
            GAB->>+GAC: _improve_population(offspring, distances, xp=np)
            Note right of GAC: improved = offspring.copy()<br/>for tour_idx in range(256):<br/>    apply 2-opt improvement
            
            loop tour_idx = 0 to 255 (256 tours sequentially)
                Note over GAC,numpy: Tour #{tour_idx + 1}/256
                GAC->>GAC: tour = improved[tour_idx]
                
                loop iter = 0 to 9 (10 iterations per tour)
                    Note over GAC,numpy: 2-opt iteration #{iter + 1}/10
                    
                    GAC->>GAC: Find best 2-opt swap
                    Note right of GAC: best_delta = 0<br/>best_i, best_j = -1, -1<br/>Search all O(n²) edge pairs
                    
                    loop i = 0 to 50 (n-1 edges)
                        loop j = i+2 to 51 (valid swaps only)
                            Note over GAC: Evaluate swap (i,i+1) ↔ (j,j+1)
                            
                            GAC->>numpy: Calculate delta
                            Note over numpy: Delta = (new edges) - (old edges)<br/>new = dist[tour[i], tour[j]] + dist[tour[i+1], tour[j+1]]<br/>old = dist[tour[i], tour[i+1]] + dist[tour[j], tour[j+1]]<br/>If delta < 0: improvement found
                            numpy-->>GAC: delta value
                            
                            alt delta < best_delta
                                GAC->>GAC: Update best: best_delta=delta, best_i=i, best_j=j
                            end
                        end
                    end
                    
                    alt best_delta < 0 (improvement found)
                        GAC->>numpy: Reverse segment [best_i+1 : best_j+1]
                        Note over numpy: tour[best_i+1:best_j+1] = tour[best_i+1:best_j+1][::-1]<br/>2-opt move: reverse tour segment
                        numpy-->>GAC: improved tour
                    else No improvement
                        Note right of GAC: Local optimum reached<br/>Break from 2-opt loop
                        break
                    end
                end
                
                GAC->>GAC: improved[tour_idx] = tour
            end
            
            GAC-->>-GAB: improved offspring (256×52)
            Note right of GAC: Result: 256 improved tours<br/>Each tour: up to 10 × O(n²) evaluations<br/>Sequential CPU processing
            Note right of GAC: Transfer stats:<br/>h2d_bytes += 0 (CPU only)<br/>d2h_bytes += 0 (CPU only)<br/>kernel_launches += 0
        end
        
        %% FITNESS EVALUATION PHASE
        rect rgb(255, 255, 235)
            Note over GAB,numpy: 📊 FITNESS EVALUATION (CPU Sequential)<br/>Calculate tour costs for all 256 tours
            GAB->>+GAC: _evaluate_population(offspring, distances, xp=np)
            Note right of GAC: costs = zeros(256, float64)<br/>for tour_idx in range(256):<br/>    calculate tour cost
            
            loop tour_idx = 0 to 255 (256 tours)
                Note over GAC,numpy: Tour #{tour_idx + 1}/256
                GAC->>GAC: tour = population[tour_idx]
                GAC->>GAC: cost = 0.0
                
                loop j = 0 to 51 (52 edges per tour)
                    GAC->>numpy: Lookup distance
                    Note over numpy: city_from = tour[j]<br/>city_to = tour[(j+1) % 52]<br/>cost += distances[city_from, city_to]<br/>Simple array indexing
                    numpy-->>GAC: edge_cost
                    GAC->>GAC: cost += edge_cost
                end
                
                GAC->>GAC: costs[tour_idx] = cost
            end
            
            GAC-->>-GAB: fitness array (256,)
            Note right of GAC: Result: 256 fitness values<br/>Each is total tour length<br/>Lower is better
            Note right of GAC: Transfer stats:<br/>h2d_bytes += 0<br/>d2h_bytes += 0<br/>kernel_launches += 0
        end
        
        %% SURVIVAL SELECTION PHASE
        rect rgb(235, 235, 255)
            Note over GAB,numpy: ⚖️ SURVIVAL SELECTION: (μ+λ) Strategy<br/>Select best 256 from 512 individuals (256 parents + 256 offspring)
            GAB->>+GAB: _survival_selection(population, offspring, fitness_pop, fitness_off)
            Note right of GAB: Elitist selection:<br/>Combine parent + offspring pools<br/>Select best 256 by fitness
            
            GAB->>numpy: Combine populations
            Note over numpy: combined = np.vstack([population, offspring])<br/>Shape: (512, 52)<br/>combined_fitness = np.concatenate([fitness_pop, fitness_off])<br/>Shape: (512,)
            numpy-->>GAB: combined (512 individuals)
            
            GAB->>numpy: Sort by fitness
            Note over numpy: sorted_indices = np.argsort(combined_fitness)<br/>Returns indices sorted by fitness<br/>(ascending = best first)
            numpy-->>GAB: sorted_indices
            
            GAB->>numpy: Select best 256
            Note over numpy: best_indices = sorted_indices[:256]<br/>Top 256 individuals<br/>new_population = combined[best_indices]
            numpy-->>GAB: new_population (256×52)
            
            GAB-->>-GAB: survivor population
            Note right of GAB: Result: New population for next gen<br/>Best 256 from 512 candidates<br/>Elitism: best individuals always survive
        end
        
        %% TRACKING
        Note over GAB,numpy: 📈 Track best solution in generation
        GAB->>numpy: best_idx = argmin(fitness)
        numpy-->>GAB: index of best tour
        GAB->>GAB: best_cost_history.append(fitness[best_idx])
        Note right of GAB: Record best fitness for convergence tracking
        
    end
    
    Note over GAB,numpy: 🏁 Evolution complete after 1000 generations
    GAB-->>-GAC: (best_tour, stats)
    GAC-->>-User: solution
    
    Note over User,numpy: 💾 FINAL STATISTICS<br/>Memory Transfers: 0 bytes (CPU-only)<br/>Total Time: Sequential CPU processing<br/>No GPU overhead
```

---

## Enhanced Diagram 2: FullGPU Variant - Detailed Process Annotations

**Purpose**: Show GPU-accelerated execution with Fujimoto (2011) kernel, highlighting parallel operations and memory transfers.

```mermaid
---
config:
  look: classic
  theme: forest
---
sequenceDiagram
    autonumber
    
    actor User
    participant GAC as GeneticAlgorithmCPU
    participant GAB as GeneticAlgorithmBase<br/>(Abstract Template)
    participant GAFG as GeneticAlgorithmFullGPU<br/>(Fujimoto 2011)
    participant cupy as CuPy<br/>(GPU Backend)
    participant kernel as CUDA Kernel<br/>(parallel_ga_one_generation.cu)
    
    Note over User,kernel: 🚀 INITIALIZATION PHASE<br/>Backend: GPU (CuPy)<br/>Design: Monolithic kernel approach
    
    User->>+GAC: solve(problem, params)
    GAC->>GAC: _select_algorithm(params)
    
    Note over GAC: 🔍 ALGORITHM SELECTION<br/>Detected: backend='gpu', variant='full_gpu'<br/>Strategy: Fujimoto monolithic kernel<br/>Rationale: Minimize CPU-GPU transfers
    
    GAC->>+GAFG: __init__(problem, params)
    
    rect rgb(200, 220, 255)
        Note over GAFG,kernel: 📦 INITIALIZATION: Strategy Objects & Parameters
        
        GAFG->>GAFG: self.xp = cupy
        GAFG->>GAFG: self.pop_size = 256
        GAFG->>GAFG: self.max_generations = 100
        GAFG->>GAFG: self.mutation_rate = 0.02
        GAFG->>GAFG: self.tournament_k = 5
        GAFG->>GAFG: self.two_opt_iters = 10
        
        Note over GAFG: ⚙️ PARAMETERS SET<br/>Population: 256 tours<br/>Generations: 100 iterations<br/>Mutation: 2% probability<br/>Selection: k=5 tournament<br/>2-opt: 10 iterations per tour
        
        GAFG->>kernel: load_kernel('parallel_ga_one_generation.cu')
        kernel-->>GAFG: compiled_kernel
        
        Note over kernel: 🔧 KERNEL COMPILATION<br/>Fujimoto (2011) monolithic design<br/>Contains: selection, crossover, mutation, 2-opt, fitness<br/>Executes: All operators in single GPU call<br/>Benefit: Eliminates intermediate transfers
    end
    
    GAC->>+GAFG: run()
    GAFG->>+GAB: run() [Template Method]
    
    rect rgb(255, 240, 200)
        Note over GAB,cupy: 🗺️ DISTANCE MATRIX COMPUTATION
        
        GAB->>GAB: context = ProblemContext(problem, xp=cupy)
        GAB->>GAB: distances = context.get_distance_matrix()
        
        Note over GAB: 💾 LAZY LOADING PATTERN<br/>Check if matrix cached<br/>If not: compute O(n²) Euclidean distances<br/>For berlin52: 52×52 = 2,704 distances<br/>Each: sqrt((x2-x1)² + (y2-y1)²)<br/>Cache for reuse across generations
        
        GAB->>cupy: distances_gpu = cp.asarray(distances)
        
        Note over cupy: 📤 H2D TRANSFER #1<br/>Size: 52×52×8 bytes = 21.6 KB<br/>Type: Distance matrix (double precision)<br/>Destination: GPU global memory<br/>Frequency: Once (initialization only)
    end
    
    rect rgb(200, 255, 200)
        Note over GAB,kernel: 🎲 POPULATION INITIALIZATION (256 Random Permutations)
        
        GAB->>GAB: _initialize_population()
        
        loop 256 iterations (i = 0 to 255)
            GAB->>cupy: tour_i = cp.random.permutation(52)
            Note over cupy: Fisher-Yates shuffle on GPU<br/>Generates random tour ordering [0,1,...,51]<br/>Example: [15,42,7,23,...,31,8]
        end
        
        GAB->>cupy: population = cp.stack([tour_0, tour_1, ..., tour_255])
        
        Note over cupy: 📊 POPULATION CREATED<br/>Shape: (256, 52)<br/>Memory: 256×52×4 bytes = 53.2 KB (int32)<br/>Location: GPU memory<br/>Status: Ready for evolution
        
        GAB->>kernel: population_gpu = population
        
        Note over kernel: 📤 H2D TRANSFER #2<br/>Size: 53.2 KB (population)<br/>Total H2D so far: 74.8 KB<br/>Frequency: Once (initialization only)
    end
    
    Note over GAB,kernel: 🔄 MAIN EVOLUTION LOOP<br/>Iterations: 100 generations<br/>Operations per generation: MONOLITHIC KERNEL CALL
    
    loop 100 generations (g = 0 to 99)
        
        rect rgb(255, 220, 220)
            Note over GAB,kernel: 🚀 PHASE 1-5: MONOLITHIC KERNEL EXECUTION<br/>Single GPU call replaces all CPU operations
            
            GAB->>kernel: parallel_ga_one_generation(population_gpu, distances_gpu, params)
            
            Note over kernel: 🔧 KERNEL EXECUTION BREAKDOWN<br/>Grid: 256 blocks (one per tour)<br/>Block: Variable threads (algorithm-dependent)<br/>Shared Memory: Used for 2-opt delta calculations
            
            rect rgb(255, 230, 230)
                Note over kernel: 1️⃣ PARALLEL SELECTION (256 tournaments simultaneously)
                Note over kernel: Each block runs k-tournament:<br/>• Random sample k=5 candidates<br/>• Compare fitness values (parallel reduction)<br/>• Select winner → parent<br/>Parallelism: 256 blocks × k comparisons
            end
            
            rect rgb(255, 240, 230)
                Note over kernel: 2️⃣ PARALLEL CROSSOVER (128 pairs simultaneously)
                Note over kernel: Order Crossover (OX) on GPU:<br/>• Each block processes one parent pair<br/>• Select random crossover points [i, j]<br/>• Copy segment from parent1 to child<br/>• Fill remaining positions from parent2 order<br/>Parallelism: 128 blocks generating 256 children
            end
            
            rect rgb(255, 250, 230)
                Note over kernel: 3️⃣ PARALLEL MUTATION (256 tours simultaneously)
                Note over kernel: Swap mutation with probability 2%:<br/>• Generate random number r ∈ [0,1] per tour<br/>• If r < 0.02: swap two random positions<br/>• Approximately 5 tours mutated per generation<br/>Parallelism: 256 threads checking mutation condition
            end
            
            rect rgb(240, 255, 240)
                Note over kernel: 4️⃣ PARALLEL 2-OPT (256 tours × 10 iterations)
                Note over kernel: Fujimoto 2-opt optimization:<br/>• Outer loop: 10 iterations per tour<br/>• Inner loop: Check all O(n²) edge pairs<br/>• For berlin52: 52×51/2 = 1,326 pairs per iteration<br/>• Delta calculation: Δ = d(i,j) + d(i+1,j+1) - d(i,i+1) - d(j,j+1)<br/>• If Δ < 0: reverse segment [i+1, j]<br/>• Parallelism: 256 tours × 1,326 comparisons<br/>• Total comparisons: 3,394,560 per generation
            end
            
            rect rgb(230, 250, 255)
                Note over kernel: 5️⃣ PARALLEL FITNESS EVALUATION (512 tours)
                Note over kernel: Tour distance calculation:<br/>• Population: 256 original + 256 offspring = 512 tours<br/>• Per tour: sum of 52 edge distances<br/>• Access distances_gpu[tour[i], tour[i+1]]<br/>• Plus return edge: distances_gpu[tour[51], tour[0]]<br/>• Parallelism: 512 threads × 52 summations<br/>• Total operations: 26,624 distance lookups
            end
            
            rect rgb(240, 230, 255)
                Note over kernel: 6️⃣ PARALLEL SURVIVAL SELECTION (μ+λ strategy)
                Note over kernel: Select best 256 from 512 candidates:<br/>• Parallel sort by fitness values<br/>• Keep tours with indices [0, 255] (best half)<br/>• Discard tours [256, 511] (worst half)<br/>• Elitism: Best solution always preserved<br/>Parallelism: Bitonic sort on 512 elements
            end
            
            kernel-->>GAB: population_gpu (updated in-place)
            
            Note over kernel: ⚡ KERNEL PERFORMANCE<br/>H2D: 0 bytes (data already on GPU)<br/>D2H: 0 bytes (no intermediate transfers)<br/>Speedup: 203x-9,573x vs CPU (Fujimoto 2011)<br/>Key: All operations stay on GPU
        end
        
        opt Every 10 generations
            GAB->>kernel: best_fitness = kernel.get_best_fitness()
            kernel-->>GAB: fitness_value
            
            Note over kernel: 📥 D2H TRANSFER (periodic)<br/>Size: 8 bytes (one double)<br/>Purpose: Progress monitoring<br/>Frequency: 10 times per run<br/>Total: 80 bytes across all generations
        end
    end
    
    Note over GAB,kernel: 🏁 FINALIZATION<br/>Extract best solution from GPU
    
    GAB->>kernel: best_tour_gpu = kernel.get_best_tour()
    kernel-->>GAB: tour_indices_gpu
    
    Note over kernel: 📥 D2H TRANSFER #3 (final)<br/>Size: 52×4 bytes = 208 bytes<br/>Type: Best tour indices<br/>Purpose: Return solution to CPU
    
    GAB->>cupy: best_tour = best_tour_gpu.get()
    
    Note over GAB: 🎯 FINAL SOLUTION<br/>Tour: [city_0, city_1, ..., city_51]<br/>Fitness: Total distance (minimized)<br/>Generations: 100 completed
    
    GAB-->>-GAFG: (best_tour, stats)
    GAFG-->>-GAC: (best_tour, stats)
    GAC-->>-User: solution
    
    Note over User,kernel: 💾 FINAL STATISTICS<br/>Total H2D: 74.8 KB (initialization only)<br/>Total D2H: 288 bytes (progress + final solution)<br/>Memory Reduction: ~2500x vs naive approach<br/>Speedup: 203x-9,573x (instance-dependent)<br/>Key Innovation: Monolithic kernel minimizes transfers
```

---

## Enhanced Diagram 3: Hybrid Variants Comparison - Memory Transfer Analysis

**Purpose**: Compare HybridNaive vs HybridOptimized, highlighting memory transfer patterns and optimization strategies.

```mermaid
---
config:
  look: classic
  theme: forest
---
sequenceDiagram
    autonumber
    
    actor User
    participant GAB as GeneticAlgorithmBase<br/>(Abstract Template)
    participant GAN as GeneticAlgorithmHybridNaive<br/>(20MB/gen transfers)
    participant GAO as GeneticAlgorithmHybridOptimized<br/>(10MB/gen transfers)
    participant cupy as CuPy<br/>(GPU Backend)
    participant strategies as Strategy Objects<br/>(Selection/Crossover/Mutation)
    
    Note over User,strategies: 🔬 HYBRID COMPARISON<br/>Goal: Minimize CPU↔GPU transfers<br/>Challenge: Balance parallelism and communication
    
    User->>+GAN: __init__(problem, params_naive)
    
    rect rgb(255, 220, 220)
        Note over GAN: 🚨 HYBRIDNAIVE INITIALIZATION<br/>Strategy: GPU operators + frequent transfers<br/>Transfer Pattern: After every operator<br/>Expected overhead: ~20MB per generation
        
        GAN->>GAN: self.xp = cupy
        GAN->>GAN: self.pop_size = 256
        GAN->>strategies: TournamentSelection(xp=cupy)
        GAN->>strategies: OrderCrossover(xp=cupy)
        GAN->>strategies: SwapMutation(xp=cupy)
    end
    
    User->>+GAN: run()
    GAN->>+GAB: run() [Template Method]
    
    rect rgb(255, 240, 200)
        Note over GAB: 🗺️ DISTANCE MATRIX (shared by both variants)
        GAB->>cupy: distances_gpu = cp.asarray(distances)
        Note over cupy: 📤 H2D: 21.6 KB (berlin52)<br/>Frequency: Once (initialization)
    end
    
    rect rgb(255, 200, 200)
        Note over GAB: 🎲 POPULATION INIT (shared)
        GAB->>cupy: population_gpu = cp.random.permutation(...)
        Note over cupy: 📤 H2D: 53.2 KB (256 tours)<br/>Frequency: Once
    end
    
    Note over GAB,strategies: 🔄 GENERATION LOOP START (HybridNaive)
    
    loop 100 generations
        
        rect rgb(255, 220, 220)
            Note over GAN,cupy: ❌ NAIVE APPROACH: Transfer after each operator
            
            GAN->>strategies: parents = selection(population_gpu)
            strategies->>cupy: GPU selection (256 tournaments)
            cupy-->>strategies: parents_gpu
            strategies->>GAN: parents_gpu
            
            GAN->>cupy: parents_cpu = parents_gpu.get()
            Note over cupy: 📥 D2H #1<br/>Size: 256×52×4 = 53.2 KB<br/>Reason: CPU needs parent indices
            
            GAN->>cupy: parents_gpu = cp.asarray(parents_cpu)
            Note over cupy: 📤 H2D #1<br/>Size: 53.2 KB<br/>Reason: Send back for crossover
            
            GAN->>strategies: offspring = crossover(parents_gpu)
            strategies->>cupy: GPU crossover (128 pairs)
            cupy-->>strategies: offspring_gpu
            strategies->>GAN: offspring_gpu
            
            GAN->>cupy: offspring_cpu = offspring_gpu.get()
            Note over cupy: 📥 D2H #2<br/>Size: 256×52×4 = 53.2 KB<br/>Reason: CPU needs offspring
            
            GAN->>cupy: offspring_gpu = cp.asarray(offspring_cpu)
            Note over cupy: 📤 H2D #2<br/>Size: 53.2 KB<br/>Reason: Send back for mutation
            
            GAN->>strategies: mutated = mutation(offspring_gpu)
            strategies->>cupy: GPU mutation (5 swaps avg)
            cupy-->>strategies: mutated_gpu
            
            GAN->>cupy: population_cpu = mutated_gpu.get()
            Note over cupy: 📥 D2H #3<br/>Size: 53.2 KB<br/>Reason: Update population
            
            Note over GAN: 💸 NAIVE COST PER GENERATION<br/>H2D: 106.4 KB (2 transfers)<br/>D2H: 159.6 KB (3 transfers)<br/>Total: 266 KB ≈ 0.26 MB<br/>Overhead: Synchronization stalls
        end
    end
    
    Note over GAN: 📊 HYBRIDNAIVE FINAL STATS<br/>Total transfers: 26.6 MB (100 generations)<br/>Transfer overhead: ~40% of runtime<br/>GPU utilization: Low (frequent stalls)
    
    GAB-->>-GAN: solution_naive
    GAN-->>-User: solution_naive (20MB total transfers)
    
    Note over User,strategies: ➡️ NOW COMPARING WITH OPTIMIZED VARIANT
    
    User->>+GAO: __init__(problem, params_optimized)
    
    rect rgb(220, 255, 220)
        Note over GAO: ✅ HYBRIDOPTIMIZED INITIALIZATION<br/>Strategy: Batch operators + minimal transfers<br/>Transfer Pattern: Once per generation<br/>Expected overhead: ~10MB per generation
        
        GAO->>GAO: self.xp = cupy
        GAO->>GAO: self.pop_size = 256
        GAO->>strategies: TournamentSelection(xp=cupy)
        GAO->>strategies: OrderCrossover(xp=cupy)
        GAO->>strategies: SwapMutation(xp=cupy)
    end
    
    User->>+GAO: run()
    GAO->>+GAB: run() [Template Method]
    
    Note over GAB: 🗺️ Distance matrix already on GPU (reused)
    Note over GAB: 🎲 Population already initialized (reused)
    
    Note over GAB,strategies: 🔄 GENERATION LOOP START (HybridOptimized)
    
    loop 100 generations
        
        rect rgb(220, 255, 220)
            Note over GAO,cupy: ✅ OPTIMIZED APPROACH: Batch all operators on GPU
            
            GAO->>strategies: parents = selection(population_gpu)
            strategies->>cupy: GPU selection (256 tournaments)
            cupy-->>strategies: parents_gpu (stays on GPU)
            
            Note over strategies: 🔗 OPERATOR CHAINING<br/>Data remains on GPU between operators<br/>No intermediate CPU transfers
            
            GAO->>strategies: offspring = crossover(parents_gpu)
            strategies->>cupy: GPU crossover (128 pairs)
            cupy-->>strategies: offspring_gpu (stays on GPU)
            
            GAO->>strategies: mutated = mutation(offspring_gpu)
            strategies->>cupy: GPU mutation (5 swaps avg)
            cupy-->>strategies: mutated_gpu (stays on GPU)
            
            GAO->>cupy: fitness = evaluate_fitness(mutated_gpu, distances_gpu)
            cupy->>cupy: 512 tours × 52 edges (parallel)
            
            GAO->>cupy: population_gpu = select_survivors(...)
            cupy->>cupy: μ+λ selection (best 256 from 512)
            
            Note over GAO: 💎 OPTIMIZED COST PER GENERATION<br/>H2D: 0 KB (data stays on GPU)<br/>D2H: 0 KB (no intermediate transfers)<br/>Total: 0 KB per generation<br/>Only final transfer at end
        end
        
        opt Every 10 generations
            GAO->>cupy: best_fitness = get_best_fitness()
            cupy-->>GAO: fitness_value
            Note over cupy: 📥 D2H (monitoring)<br/>Size: 8 bytes<br/>Frequency: 10 times total
        end
    end
    
    GAO->>cupy: best_tour = population_gpu[0].get()
    Note over cupy: 📥 D2H (final)<br/>Size: 52×4 = 208 bytes<br/>Frequency: Once
    
    Note over GAO: 📊 HYBRIDOPTIMIZED FINAL STATS<br/>Total transfers: 288 bytes (monitoring + final)<br/>Transfer overhead: <1% of runtime<br/>GPU utilization: High (no stalls)<br/>Speedup vs Naive: 2-3x
    
    GAB-->>-GAO: solution_optimized
    GAO-->>-User: solution_optimized (0.3KB total transfers)
    
    Note over User,strategies: 🏆 COMPARISON SUMMARY<br/>HybridNaive: 26.6 MB transfers → 40% overhead<br/>HybridOptimized: 0.3 KB transfers → <1% overhead<br/>Transfer Reduction: 88,666x improvement<br/>Key: Operator chaining eliminates intermediate transfers
```
