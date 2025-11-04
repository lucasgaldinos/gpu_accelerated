# Algorithm Demonstrations

This directory contains educational demonstrations of the algorithms implemented in this repository.

## Available Demos

### `demo_bin_packing.py` - CVRP Two-Phase Construction

**Purpose:** Demonstrates a complete CVRP (Capacitated Vehicle Routing Problem) solution using a two-phase approach: Bin Packing + TSP Routing.

**Features:**

- ✨ **Visual Flowchart** - ASCII art showing the complete algorithm pipeline
- 📊 **Step-by-Step Execution Trace** - Detailed logging of every major operation
- 📍 **Phase Markers** - Clear indication of WHEN and WHERE operations happen
- 📈 **Execution Statistics** - Summary of steps by phase
- 🎓 **Educational Explanations** - Complexity analysis and quality guarantees

**Running the Demo:**

```bash
# From repository root
source .venv/bin/activate
PYTHONPATH=code python code/examples/demo_bin_packing.py
```

**What It Shows:**

1. **Phase 1 - Vehicle Assignment (Bin Packing):**
   - Assigns customers to vehicles using FFD or BFD algorithms
   - Respects vehicle capacity constraints
   - O(n log n) complexity
   - Approximation guarantee: ≤ (11/9)OPT + 6/9 vehicles

2. **Phase 2 - Route Construction (TSP per Vehicle):**
   - Routes each vehicle's customers using Nearest Neighbor
   - Creates complete routes: Depot → customers → Depot
   - O(k·m²) complexity where k = vehicles, m = avg customers per vehicle
   - Greedy quality (typically 20-30% above optimal)

**Example Output:**

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           INPUT: CVRP PROBLEM                              │
│  • Customer locations (coordinates)                                        │
│  • Customer demands (weights)                                              │
│  • Vehicle capacity (constraint)                                           │
└────────────────┬───────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: VEHICLE ASSIGNMENT                             │
│                      (Bin Packing Problem)                                 │
│  Algorithm: First Fit Decreasing (FFD) or Best Fit Decreasing (BFD)       │
│  ...
```

**Algorithms Demonstrated:**

- `FirstFitDecreasing` - Bin packing heuristic
- `BestFitDecreasing` - Bin packing heuristic  
- `nearest_neighbor` - TSP construction heuristic

**Key Insights:**

- Two-phase approach separates capacity constraints from routing
- Bin packing handles vehicle assignment efficiently (O(n log n))
- Each vehicle's route is optimized independently via TSP
- Trade-off: Speed vs. quality (fast but not optimal)

## Adding New Demos

When creating new demonstration scripts:

1. Include clear docstrings explaining the purpose
2. Add step-by-step tracing where educational value is high
3. Provide complexity analysis and quality guarantees
4. Compare multiple algorithm variants when applicable
5. Update this README with the new demo

## Repository Integration

These demos use algorithms from `code/src/algorithms/`:

- Bin packing algorithms: `code/src/algorithms/bin_packing/construction/`
- TSP algorithms: `code/src/algorithms/construction/`
- Data models: `code/src/data_models/`
