# Module Import and Dependency Graph

This diagram shows all import relationships and dependencies between modules in the `code/src` directory.

```mermaid
---
config:
  theme: redux
  look: classic
  layout: elk
---
flowchart TB
 subgraph External["External Libraries"]
        numpy["numpy"]
        cupy["cupy"]
        duckdb["duckdb"]
        pathlib["pathlib"]
        logging["logging"]
  end
 subgraph DataModels["code/src/data_models"]
        Problem["problem.py<br>---<br>• Problem dataclass<br>• frozen=True"]
        Exceptions["exceptions.py<br>---<br>• Custom exceptions"]
  end
 subgraph Protocols["code/src/protocols"]
        BackendModule["backend.py<br>---<br>• BackendModule Protocol"]
        ProblemContext["problem_context.py<br>---<br>• ProblemContext class<br>IMPORTS:<br>• Problem<br>• BackendModule<br>• distances.matrix"]
        AlgorithmStrategies["algorithm_strategies.py<br>---<br>• Strategy Protocols<br>IMPORTS:<br>• BackendModule<br>• ProblemContext"]
  end
 subgraph Utils["code/src/utils"]
        gpu_helpers["gpu_helpers.py<br>---<br>• load_kernel()<br>IMPORTS:<br>• pathlib<br>• cupy"]
  end
 subgraph Distances["code/src/distances"]
        matrix["matrix.py<br>---<br>• compute_distance_matrix()<br>IMPORTS:<br>• numpy"]
        pairwise["pairwise.py<br>---<br>• euclidean_distance()<br>• geo_distance()"]
  end
 subgraph Loaders["code/src/loaders"]
        DatabaseLoader["database_loader.py<br>---<br>• DatabaseLoader class<br>IMPORTS:<br>• duckdb<br>• Problem"]
  end
 subgraph Strategies["code/src/algorithms/strategies"]
        Selection["selection_strategies.py<br>---<br>• TournamentSelection<br>• RouletteWheelSelection<br>IMPORTS:<br>• numpy"]
        Crossover["crossover_strategies.py<br>---<br>• OrderCrossover<br>IMPORTS:<br>• numpy"]
        Mutation["mutation_strategies.py<br>---<br>• SwapMutation<br>• InversionMutation<br>IMPORTS:<br>• numpy"]
  end
 subgraph Metaheuristics["code/src/algorithms/metaheuristics"]
        GABase["genetic_algorithm_base.py<br>---<br>• GeneticAlgorithmBase (ABC)<br>IMPORTS:<br>• numpy<br>• logging<br>• Problem<br>• ProblemContext<br>• TournamentSelection<br>• OrderCrossover<br>• SwapMutation"]
        GACPU["genetic_algorithm_cpu.py<br>---<br>• GeneticAlgorithmCPU<br>IMPORTS:<br>• numpy<br>• logging<br>• GeneticAlgorithmBase"]
        GAHybridNaive["genetic_algorithm_hybrid_naive.py<br>---<br>• GeneticAlgorithmHybridNaive<br>IMPORTS:<br>• numpy<br>• cupy<br>• logging<br>• GeneticAlgorithmBase"]
        GAHybridOptimized["genetic_algorithm_hybrid_optimized.py<br>---<br>• GeneticAlgorithmHybridOptimized<br>IMPORTS:<br>• numpy<br>• cupy<br>• logging<br>• GeneticAlgorithmBase<br>• gpu_helpers"]
        GAFullGPU["genetic_algorithm_full_gpu_iso.py<br>---<br>• GeneticAlgorithmFullGPU<br>IMPORTS:<br>• numpy<br>• cupy<br>• logging<br>• pathlib<br>• GeneticAlgorithmBase<br>• gpu_helpers"]
        GAFullGPUEarlyStop["genetic_algorithm_full_gpu_early_stop.py<br>---<br>• GeneticAlgorithmFullGPUEarlyStop<br>IMPORTS:<br>• numpy<br>• cupy<br>• logging<br>• GeneticAlgorithmBase<br>• gpu_helpers"]
  end
 subgraph Kernels["code/src/algorithms/kernels"]
        TwoOptSingle["two_opt_single.cu<br>---<br>• CUDA kernel<br>• Single tour improvement"]
        TwoOptBatch["two_opt_batch.cu<br>---<br>• CUDA kernel<br>• Batch tour improvement"]
        CostCalculator["cost_calculator.cu<br>---<br>• CUDA kernel<br>• Parallel fitness"]
        GAFujimoto["ga_fujimoto.cu<br>---<br>• CUDA kernel<br>• Complete GA evolution"]
        GAFujimotoEarlyStop["ga_fujimoto_early_stop.cu<br>---<br>• CUDA kernel<br>• GA + early stopping"]
  end
 subgraph Benchmarking["code/src/benchmarking"]
        Statistics["statistics.py<br>---<br>• Statistical functions<br>IMPORTS:<br>• numpy"]
        FixNaN["fix_nan_values.py<br>---<br>• Data cleaning<br>IMPORTS:<br>• numpy"]
  end
    numpy --> BackendModule & matrix & Selection & Crossover & Mutation & Statistics & FixNaN
    cupy --> BackendModule & gpu_helpers
    duckdb --> DatabaseLoader
    pathlib --> gpu_helpers
    logging --> GABase & GACPU & GAHybridNaive & GAHybridOptimized & GAFullGPU & GAFullGPUEarlyStop
    Problem --> DatabaseLoader & ProblemContext & GABase
    BackendModule --> ProblemContext
    matrix --> ProblemContext
    ProblemContext --> AlgorithmStrategies & GABase
    Selection --> GABase
    Crossover --> GABase
    Mutation --> GABase
    GABase --> GACPU & GAHybridNaive & GAHybridOptimized & GAFullGPU & GAFullGPUEarlyStop
    gpu_helpers --> GAHybridOptimized & GAFullGPU & GAFullGPUEarlyStop
    TwoOptSingle -.-o gpu_helpers
    TwoOptBatch -.-o gpu_helpers
    CostCalculator -.-o gpu_helpers
    GAFujimoto -.-o gpu_helpers
    GAFujimotoEarlyStop -.-o gpu_helpers
    GAHybridOptimized -.-> TwoOptBatch & CostCalculator
    GAFullGPU -.-> GAFujimoto
    GAFullGPUEarlyStop -.-> GAFujimotoEarlyStop
    n1["Untitled Node"]

     numpy:::externalStyle
     cupy:::externalStyle
     duckdb:::externalStyle
     pathlib:::externalStyle
     logging:::externalStyle
     Problem:::dataStyle
     Exceptions:::dataStyle
     BackendModule:::protocolStyle
     ProblemContext:::protocolStyle
     AlgorithmStrategies:::protocolStyle
     gpu_helpers:::utilStyle
     matrix:::utilStyle
     pairwise:::utilStyle
     DatabaseLoader:::utilStyle
     Selection:::strategyStyle
     Crossover:::strategyStyle
     Mutation:::strategyStyle
     GABase:::algorithmStyle
     GACPU:::algorithmStyle
     GAHybridNaive:::algorithmStyle
     GAHybridOptimized:::algorithmStyle
     GAFullGPU:::algorithmStyle
     GAFullGPUEarlyStop:::algorithmStyle
     TwoOptSingle:::kernelStyle
     TwoOptBatch:::kernelStyle
     CostCalculator:::kernelStyle
     GAFujimoto:::kernelStyle
     GAFujimotoEarlyStop:::kernelStyle
     Statistics:::benchmarkStyle
     FixNaN:::benchmarkStyle
    classDef externalStyle fill:#eceff1,stroke:#546e7a,stroke-width:2px
    classDef dataStyle fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef protocolStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef utilStyle fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    classDef strategyStyle fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef algorithmStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef kernelStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef benchmarkStyle fill:#e0f2f1,stroke:#00796b,stroke-width:2px
```

## Import Analysis

### Top-Level Module Structure

```
code/src/
├── data_models/          # Immutable data structures
├── protocols/            # Interface definitions
├── utils/                # Helper functions
├── distances/            # Distance calculations
├── loaders/              # Data loading
├── algorithms/
│   ├── strategies/       # Strategy implementations
│   ├── metaheuristics/   # GA implementations
│   └── kernels/          # CUDA kernels (.cu files)
└── benchmarking/         # Statistical tools
```

### Critical Import Chains

#### 1. Algorithm Execution Chain

```
User Script
  → GeneticAlgorithm* (concrete variant)
    → GeneticAlgorithmBase (abstract)
      → TournamentSelection/OrderCrossover/SwapMutation
      → ProblemContext
        → Problem
        → distances.matrix
          → numpy/cupy
```

#### 2. GPU Kernel Loading Chain

```
GeneticAlgorithmHybridOptimized/FullGPU
  → gpu_helpers.load_kernel()
    → pathlib (find .cu file)
    → cupy.RawKernel (compile)
      → CUDA Runtime (execute)
```

#### 3. Data Loading Chain

```
Benchmark Script
  → DatabaseLoader
    → duckdb (query)
    → Problem (construct)
```

### Import Dependencies by Module

#### genetic_algorithm_base.py

```python
import numpy as np
import logging
from typing import List, Tuple, Dict, Any, Optional

from src.data_models.problem import Problem
from src.protocols.problem_context import ProblemContext
from src.algorithms.strategies.selection_strategies import TournamentSelection
from src.algorithms.strategies.crossover_strategies import OrderCrossover
from src.algorithms.strategies.mutation_strategies import SwapMutation
```

#### genetic_algorithm_cpu.py

```python
import numpy as np
import logging
from typing import Any

from src.algorithms.metaheuristics.genetic_algorithm_base import (
    GeneticAlgorithmBase,
)
```

#### genetic_algorithm_full_gpu_iso.py

```python
import numpy as np
import cupy as cp
import logging
import time
from typing import Any, Optional
from pathlib import Path

from src.algorithms.metaheuristics.genetic_algorithm_base import (
    GeneticAlgorithmBase,
)
from src.utils.gpu_helpers import load_kernel
```

#### problem_context.py

```python
import numpy as np
from typing import Optional

from ..data_models.problem import Problem
from ..protocols.backend import BackendModule
from ..distances.matrix import compute_distance_matrix

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False
```

#### gpu_helpers.py

```python
from pathlib import Path
import cupy as cp

def load_kernel(kernel_filename: str, kernel_function_name: str, caller_file_path: str):
    # Navigate to algorithms/kernels/ from any algorithm subdirectory
    caller_dir = Path(caller_file_path).parent
    kernel_dir = caller_dir.parent / "kernels"
    kernel_path = kernel_dir / kernel_filename
    
    kernel_source = kernel_path.read_text()
    return cp.RawKernel(kernel_source, kernel_function_name)
```

### Circular Dependency Prevention

The architecture prevents circular dependencies through:

1. **Layered Architecture**: Dependencies flow in one direction (bottom-up)
   - Data Models → Protocols → Strategies → Algorithms

2. **Protocol-Based Design**: Interfaces defined separately from implementations
   - `BackendModule` protocol allows NumPy/CuPy abstraction
   - Strategy protocols in `algorithm_strategies.py`

3. **Dependency Injection**: Backend and context passed as parameters
   - No hardcoded backend references
   - ProblemContext injected into algorithms

### Module Responsibilities

| Module | Responsibility | Imports From |
|--------|---------------|--------------|
| `data_models/` | Data structures | None (leaf nodes) |
| `protocols/` | Interface definitions | `data_models/`, external libs |
| `distances/` | Distance calculations | `numpy` |
| `loaders/` | Data loading | `duckdb`, `data_models/` |
| `strategies/` | GA operators | `numpy`, `protocols/` |
| `metaheuristics/` | GA algorithms | All layers above |
| `utils/` | Helper functions | `cupy`, `pathlib` |
| `kernels/` | CUDA code | None (compiled by CuPy) |

### Key Design Decisions

1. **Protocols over Inheritance**: Strategy protocols enable duck typing
2. **Lazy Loading**: ProblemContext delays computation until needed
3. **Kernel Consolidation**: All CUDA kernels in single `kernels/` directory
4. **No Circular Dependencies**: Strict bottom-up dependency flow
5. **Optional GPU Support**: `try/except` for CuPy imports

## Imports Visualization by File

### Most Imported Modules (Dependencies)

1. **numpy** - Used by 90% of modules
2. **logging** - Used by all GA variants
3. **GeneticAlgorithmBase** - Parent of all variants
4. **Problem** - Core data structure
5. **ProblemContext** - Backend abstraction

### Most Importing Modules (Dependents)

1. **GeneticAlgorithmBase** - Imports 8 different modules
2. **GeneticAlgorithmFullGPU** - Imports 7 modules + kernels
3. **ProblemContext** - Imports 4 modules

### Minimal Import Modules

- **Problem** - Zero imports (frozen dataclass)
- **BackendModule** - Protocol-only definition
- **CUDA kernels** - Standalone C++ files

## Academic References

- **Martin (2017)**: "Clean Architecture" - Dependency rule and layered design
- **Fowler (2002)**: "Patterns of Enterprise Application Architecture" - Lazy loading pattern
- **PEP 544**: "Protocols: Structural subtyping" - Protocol-based design in Python
