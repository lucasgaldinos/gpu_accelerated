"""
Demonstration of CVRP two-phase construction heuristic with PATH TRACING.

This script demonstrates the complete CVRP solution pipeline:
1. Phase 1: Bin Packing (FFD/BFD) - Assign customers to vehicles
2. Phase 2: TSP Routing (Nearest Neighbor) - Route each vehicle's customers

Shows how bin packing + TSP routing = Complete CVRP solution.

Features:
- Step-by-step execution tracing
- Visual flowchart of algorithm pipeline
- Detailed logging of decision points
- Clear visualization of data transformations
"""

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from src.algorithms.bin_packing.construction.first_fit_decreasing import (
    FirstFitDecreasing,
)
from src.algorithms.bin_packing.construction.best_fit_decreasing import (
    BestFitDecreasing,
)
from src.algorithms.construction.nearest_neighbor import nearest_neighbor
from src.algorithms.construction.christofides import christofides
from src.data_models.problem import Problem


class Phase(Enum):
    """Execution phases for path tracing."""

    SETUP = "SETUP"
    BIN_PACKING = "BIN_PACKING"
    TSP_ROUTING = "TSP_ROUTING"
    EVALUATION = "EVALUATION"


@dataclass
class TraceStep:
    """Single step in execution trace."""

    step_num: int
    phase: Phase
    operation: str
    details: str
    data_snapshot: Dict[str, Any] = None


class PathTracer:
    """
    Execution path tracer for CVRP two-phase algorithm.

    Logs every significant operation and provides visualization of
    the algorithm's execution flow.
    """

    def __init__(self):
        self.steps: List[TraceStep] = []
        self.step_counter = 0

    def log(
        self,
        phase: Phase,
        operation: str,
        details: str,
        data_snapshot: Dict[str, Any] = None,
    ):
        """Log a single execution step."""
        self.step_counter += 1
        step = TraceStep(self.step_counter, phase, operation, details, data_snapshot)
        self.steps.append(step)

    def print_flowchart(self):
        """Display ASCII flowchart of CVRP solution pipeline."""
        print("\n" + "=" * 80)
        print("EXECUTION FLOWCHART - CVRP Two-Phase Construction")
        print("=" * 80)
        print(
            """
┌────────────────────────────────────────────────────────────────────────────┐
│                           INPUT: CVRP PROBLEM                              │
│                                                                            │
│  • Customer locations (coordinates)                                        │
│  • Customer demands (weights)                                              │
│  • Vehicle capacity (constraint)                                           │
└────────────────┬───────────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: VEHICLE ASSIGNMENT                             │
│                      (Bin Packing Problem)                                 │
│                                                                            │
│  Algorithm: First Fit Decreasing (FFD) or Best Fit Decreasing (BFD)       │
│  Input:     demands[], capacity                                           │
│  Process:   1. Sort demands in descending order                           │
│             2. For each demand:                                            │
│                - Try to fit in existing bin (vehicle)                     │
│                - Create new bin if no fit                                 │
│  Output:    bins[] = [[customer_ids], ...]                                │
│                                                                            │
│  Complexity: O(n log n)                                                    │
│  Quality:    ≤ (11/9)OPT + 6/9 vehicles                                    │
└────────────────┬───────────────────────────────────────────────────────────┘
                 │
                 │ bins[] = vehicle assignments
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                  PHASE 2: ROUTE CONSTRUCTION                               │
│                    (TSP per Vehicle)                                       │
│                                                                            │
│  For EACH vehicle with assigned customers:                                │
│                                                                            │
│  Algorithm: Nearest Neighbor (NN)                                         │
│  Input:     customer_coords[], distance_matrix[][]                        │
│  Process:   1. Start at depot                                             │
│             2. Repeat until all customers visited:                        │
│                - Find nearest unvisited customer                          │
│                - Move to that customer                                    │
│                - Mark as visited                                          │
│             3. Return to depot                                            │
│  Output:    tour[] = [depot → c₁ → c₂ → ... → cₙ → depot]                │
│                                                                            │
│  Complexity: O(k × m²) where k=vehicles, m=avg customers/vehicle          │
│  Quality:    Greedy (typically 20-30% above optimal)                      │
└────────────────┬───────────────────────────────────────────────────────────┘
                 │
                 │ routes[] = complete vehicle routes
                 │
                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                      OUTPUT: COMPLETE CVRP SOLUTION                        │
│                                                                            │
│  • Vehicle count                                                           │
│  • Route for each vehicle: Depot → [customers] → Depot                    │
│  • Cost per route                                                          │
│  • Load per vehicle                                                        │
│  • Total solution cost                                                     │
└────────────────────────────────────────────────────────────────────────────┘
"""
        )

    def print_trace(self, verbose: bool = True):
        """Print sequential execution trace."""
        print("\n" + "=" * 80)
        print("EXECUTION TRACE - Step-by-Step Algorithm Execution")
        print("=" * 80)

        current_phase = None
        for step in self.steps:
            # Print phase header when phase changes
            if step.phase != current_phase:
                current_phase = step.phase
                print(f"\n┌─ {step.phase.value} " + "─" * (75 - len(step.phase.value)))

            # Print step
            prefix = f"│ Step {step.step_num:2d}"
            print(f"{prefix} [{step.operation}]")
            print(f"│         {step.details}")

            # Print data snapshot if verbose
            if verbose and step.data_snapshot:
                for key, value in step.data_snapshot.items():
                    print(f"│         • {key}: {value}")

        print("└" + "─" * 79)

    def get_summary(self) -> Dict[str, int]:
        """Get execution summary statistics."""
        phase_counts = {}
        for step in self.steps:
            phase_name = step.phase.value
            phase_counts[phase_name] = phase_counts.get(phase_name, 0) + 1
        return {"total_steps": len(self.steps), "by_phase": phase_counts}


def calculate_euclidean_distance_matrix(coordinates: np.ndarray) -> np.ndarray:
    """Calculate Euclidean distance matrix from coordinates."""
    n = len(coordinates)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = coordinates[i, 0] - coordinates[j, 0]
            dy = coordinates[i, 1] - coordinates[j, 1]
            dist = np.sqrt(dx**2 + dy**2)
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix


def calculate_route_cost(
    tour: np.ndarray, dist_matrix: np.ndarray, depot: int = 0
) -> float:
    """Calculate total route cost including depot."""
    cost = dist_matrix[depot, tour[0]]  # Depot to first customer
    for i in range(len(tour) - 1):
        cost += dist_matrix[tour[i], tour[i + 1]]  # Customer to customer
    cost += dist_matrix[tour[-1], depot]  # Last customer to depot
    return cost


def solve_cvrp_two_phase(
    coordinates: np.ndarray,
    demands: np.ndarray,
    capacity: float,
    bin_packing_strategy: str = "BFD",
    tsp_strategy: str = "NN",
    depot_idx: int = 0,
    tracer: PathTracer = None,
) -> dict:
    """
    Solve CVRP using two-phase approach: Bin Packing + TSP Routing.

    Parameters
    ----------
    coordinates : np.ndarray
        (n+1, 2) array of node coordinates (includes depot at index depot_idx)
    demands : np.ndarray
        (n,) array of customer demands (excludes depot)
    capacity : float
        Vehicle capacity
    bin_packing_strategy : str
        "FFD" or "BFD" for bin packing phase
    tsp_strategy : str
        "NN" (Nearest Neighbor) or "CHR" (Christofides) for TSP phase
    depot_idx : int
        Index of depot in coordinates array
    tracer : PathTracer
        Optional path tracer for execution logging

    Returns
    -------
    dict
        Complete CVRP solution with routes, costs, and vehicle assignments
    """
    if tracer:
        tracer.log(
            Phase.SETUP,
            "Problem Setup",
            f"Initializing CVRP with {len(demands)} customers, capacity={capacity}",
            {
                "num_customers": len(demands),
                "total_demand": int(np.sum(demands)),
                "capacity": capacity,
                "strategy": bin_packing_strategy,
            },
        )

    # Phase 1: Bin Packing (assign customers to vehicles)
    if tracer:
        tracer.log(
            Phase.BIN_PACKING,
            "Algorithm Selection",
            f"Selected {bin_packing_strategy} for vehicle assignment",
        )

    if bin_packing_strategy == "FFD":
        packer = FirstFitDecreasing()
    else:  # BFD
        packer = BestFitDecreasing()

    if tracer:
        tracer.log(
            Phase.BIN_PACKING,
            "Sorting Items",
            "Sorting customer demands in descending order",
            {"demands_sorted": "largest first (core of FFD/BFD)"},
        )

    bins = packer.pack(demands, capacity)
    num_vehicles = len(bins)

    if tracer:
        tracer.log(
            Phase.BIN_PACKING,
            "Bin Packing Complete",
            f"Assigned {len(demands)} customers to {num_vehicles} vehicles",
            {
                "vehicles_used": num_vehicles,
                "assignments": str([len(b) for b in bins]),
            },
        )

    # Phase 2: TSP Routing (route each vehicle's customers)
    if tracer:
        tracer.log(
            Phase.TSP_ROUTING,
            "Distance Matrix Calculation",
            "Computing Euclidean distances between all nodes",
        )

    dist_matrix = calculate_euclidean_distance_matrix(coordinates)

    routes = []
    route_costs = []
    vehicle_loads = []

    for vehicle_idx, customer_indices in enumerate(bins):
        if len(customer_indices) == 0:
            continue

        if tracer:
            tracer.log(
                Phase.TSP_ROUTING,
                f"Routing Vehicle {vehicle_idx + 1}",
                f"Solving TSP for {len(customer_indices)} customers",
                {"customers": customer_indices},
            )

        # Map customer indices to coordinate indices (offset by depot if needed)
        # Customer index i in demands corresponds to coordinate index i+1 (if depot is at 0)
        coord_indices = np.array([idx + 1 for idx in customer_indices])

        # Create subproblem for this vehicle's customers
        vehicle_coords = coordinates[coord_indices]
        vehicle_dist_matrix = dist_matrix[np.ix_(coord_indices, coord_indices)]

        # Solve TSP for this vehicle
        vehicle_problem = Problem(
            name=f"vehicle_{vehicle_idx}",
            dimension=len(coord_indices),
            problem_type="TSP",
            edge_type="EXPLICIT",
            coordinates=vehicle_coords,
            distances=vehicle_dist_matrix,
        )

        if tracer:
            tracer.log(
                Phase.TSP_ROUTING,
                f"Nearest Neighbor (Vehicle {vehicle_idx + 1})",
                "Finding greedy nearest-neighbor tour",
            )

        # Solve TSP for this vehicle based on strategy
        if tsp_strategy == "NN":
            tour = nearest_neighbor(vehicle_problem, start_node=0, xp=np)
        else:  # CHR (Christofides)
            if tracer:
                tracer.log(
                    Phase.TSP_ROUTING,
                    f"Christofides (Vehicle {vehicle_idx + 1})",
                    "Computing 3/2-approximation tour (MST + matching)",
                )
            tour = christofides(vehicle_problem, xp=np)

        # Map tour back to original customer indices
        route_in_customer_indices = [
            customer_indices[tour[i]] for i in range(len(tour))
        ]
        route_in_coord_indices = [idx + 1 for idx in route_in_customer_indices]

        # Calculate route cost (depot → customers → depot)
        route_cost = calculate_route_cost(
            np.array(route_in_coord_indices), dist_matrix, depot=depot_idx
        )

        # Calculate vehicle load
        vehicle_load = sum(demands[idx] for idx in customer_indices)

        if tracer:
            tracer.log(
                Phase.TSP_ROUTING,
                f"Route Complete (Vehicle {vehicle_idx + 1})",
                f"Tour cost: {route_cost:.2f}, Load: {vehicle_load}/{capacity}",
                {
                    "route": route_in_customer_indices,
                    "cost": f"{route_cost:.2f}",
                    "load": vehicle_load,
                },
            )

        routes.append(route_in_customer_indices)
        route_costs.append(route_cost)
        vehicle_loads.append(vehicle_load)

    total_cost = sum(route_costs)

    if tracer:
        tracer.log(
            Phase.EVALUATION,
            "Solution Complete",
            f"Total: {num_vehicles} vehicles, cost={total_cost:.2f}",
            {
                "total_vehicles": num_vehicles,
                "total_cost": f"{total_cost:.2f}",
                "avg_cost_per_vehicle": f"{total_cost / num_vehicles:.2f}",
            },
        )

    return {
        "bin_packing_strategy": packer.get_name(),
        "tsp_strategy": "Nearest Neighbor" if tsp_strategy == "NN" else "Christofides",
        "num_vehicles": num_vehicles,
        "routes": routes,
        "route_costs": route_costs,
        "vehicle_loads": vehicle_loads,
        "total_cost": total_cost,
        "bins": bins,
    }


def demo_cvrp_complete_solution():
    """Demonstrate complete CVRP solution pipeline with path tracing."""
    print("=" * 80)
    print("CVRP Two-Phase Construction Heuristic - Complete Solution")
    print("=" * 80)

    # Sample CVRP instance with coordinates
    depot = np.array([0, 0])
    customer_coords = np.array(
        [
            [2, 3],  # c0: demand 18
            [5, 2],  # c1: demand 26
            [1, 1],  # c2: demand 11
            [7, 4],  # c3: demand 30
            [4, 6],  # c4: demand 21
            [3, 5],  # c5: demand 19
            [2, 2],  # c6: demand 15
            [6, 1],  # c7: demand 16
            [8, 5],  # c8: demand 29
            [5, 4],  # c9: demand 26
        ]
    )
    all_coords = np.vstack([depot, customer_coords])
    demands = np.array([18, 26, 11, 30, 21, 19, 15, 16, 29, 26])
    capacity = 60

    print("\nProblem Setup:")
    print(f"  Customers: {len(demands)}")
    print(f"  Demands: {[int(d) for d in demands]}")
    print(f"  Total demand: {int(np.sum(demands))}")
    print(f"  Vehicle capacity: {capacity}")
    print(
        f"  Minimum vehicles (lower bound): {int(np.ceil(np.sum(demands) / capacity))}"
    )

    tracer = PathTracer()
    tracer.print_flowchart()

    print("\n" + "=" * 80)
    print("SOLVING WITH FIRST FIT DECREASING (FFD) + NEAREST NEIGHBOR")
    print("=" * 80)

    ffd_solution = solve_cvrp_two_phase(
        all_coords, demands, capacity, "FFD", "NN", tracer=tracer
    )
    tracer.print_trace(verbose=True)

    tracer_bfd = PathTracer()
    print("\n" + "=" * 80)
    print("SOLVING WITH BEST FIT DECREASING (BFD) + NEAREST NEIGHBOR")
    print("=" * 80)

    bfd_solution = solve_cvrp_two_phase(
        all_coords, demands, capacity, "BFD", "NN", tracer=tracer_bfd
    )
    tracer_bfd.print_trace(verbose=False)

    print("\n" + "=" * 80)
    print("SOLUTION COMPARISON")
    print("=" * 80)

    for name, solution in [("FFD+NN", ffd_solution), ("BFD+NN", bfd_solution)]:
        print(f"\n{name} Solution:")
        print(f"  Vehicles: {solution['num_vehicles']}")
        print(f"  Total cost: {solution['total_cost']:.2f}")
        print("  Routes:")
        for i, (route, cost, load) in enumerate(
            zip(solution["routes"], solution["route_costs"], solution["vehicle_loads"])
        ):
            print(
                f"    Vehicle {i + 1}: Depot → {route} → Depot | Cost: {cost:.2f}, Load: {load}/{capacity}"
            )

    print("\n" + "-" * 80)
    print("Comparison:")
    if ffd_solution["num_vehicles"] == bfd_solution["num_vehicles"]:
        print(f"  Both use {ffd_solution['num_vehicles']} vehicles (tied)")
        cost_diff = abs(ffd_solution["total_cost"] - bfd_solution["total_cost"])
        if cost_diff < 0.01:
            print("  Same total routing cost")
        elif ffd_solution["total_cost"] < bfd_solution["total_cost"]:
            print(
                f"  FFD has lower cost: {ffd_solution['total_cost']:.2f} < {bfd_solution['total_cost']:.2f}"
            )
        else:
            print(
                f"  BFD has lower cost: {bfd_solution['total_cost']:.2f} < {ffd_solution['total_cost']:.2f}"
            )
    elif ffd_solution["num_vehicles"] < bfd_solution["num_vehicles"]:
        print(
            f"  FFD uses fewer vehicles: {ffd_solution['num_vehicles']} < {bfd_solution['num_vehicles']}"
        )
    else:
        print(
            f"  BFD uses fewer vehicles: {bfd_solution['num_vehicles']} < {ffd_solution['num_vehicles']}"
        )

    print("\n" + "=" * 80)
    print("EXECUTION STATISTICS")
    print("=" * 80)
    ffd_summary = tracer.get_summary()
    bfd_summary = tracer_bfd.get_summary()
    print("\nFFD Execution:")
    print(f"  Total steps: {ffd_summary['total_steps']}")
    print(f"  By phase: {ffd_summary['by_phase']}")
    print("\nBFD Execution:")
    print(f"  Total steps: {bfd_summary['total_steps']}")
    print(f"  By phase: {bfd_summary['by_phase']}")


def demo_algorithm_comparison():
    """Compare multiple algorithm combinations on different problem instances."""
    print("\n" + "=" * 80)
    print("MULTI-ALGORITHM COMPARISON")
    print("=" * 80)

    # Define test instances with different characteristics
    instances = {
        "Small Tight": {
            "coords": np.vstack(
                [np.array([0, 0]), np.array([[2, 3], [5, 2], [1, 1], [3, 4], [4, 1]])]
            ),
            "demands": np.array([15, 20, 18, 22, 19]),
            "capacity": 50,
            "description": "5 customers, tight capacity (avg 2 customers/vehicle)",
        },
        "Medium Balanced": {
            "coords": np.vstack(
                [
                    np.array([0, 0]),
                    np.array(
                        [[2, 3], [5, 2], [1, 1], [7, 4], [4, 6], [3, 5], [2, 2], [6, 1]]
                    ),
                ]
            ),
            "demands": np.array([12, 18, 10, 20, 15, 14, 11, 16]),
            "capacity": 40,
            "description": "8 customers, balanced capacity (avg 3 customers/vehicle)",
        },
        "Large Sparse": {
            "coords": np.vstack(
                [
                    np.array([0, 0]),
                    np.array(
                        [
                            [1, 2],
                            [8, 9],
                            [2, 1],
                            [9, 8],
                            [3, 3],
                            [7, 7],
                            [4, 2],
                            [6, 8],
                            [2, 4],
                            [8, 6],
                            [5, 5],
                            [3, 7],
                        ]
                    ),
                ]
            ),
            "demands": np.array([8, 12, 7, 15, 10, 11, 9, 14, 8, 13, 10, 12]),
            "capacity": 35,
            "description": "12 customers, sparse layout (avg 3-4 customers/vehicle)",
        },
    }

    # Algorithm combinations to test
    algorithm_combos = [
        ("FFD", "NN", "First Fit Decreasing + Nearest Neighbor"),
        ("BFD", "NN", "Best Fit Decreasing + Nearest Neighbor"),
        ("FFD", "CHR", "First Fit Decreasing + Christofides"),
        ("BFD", "CHR", "Best Fit Decreasing + Christofides"),
    ]

    # Run all combinations
    results = {}
    for instance_name, instance_data in instances.items():
        print(f"\n{'=' * 80}")
        print(f"Problem Instance: {instance_name}")
        print(f"  {instance_data['description']}")
        print(f"{'=' * 80}")

        instance_results = []
        for bp_strategy, tsp_strategy, full_name in algorithm_combos:
            solution = solve_cvrp_two_phase(
                instance_data["coords"],
                instance_data["demands"],
                instance_data["capacity"],
                bin_packing_strategy=bp_strategy,
                tsp_strategy=tsp_strategy,
                tracer=None,
            )
            instance_results.append(
                {
                    "name": full_name,
                    "bp": bp_strategy,
                    "tsp": tsp_strategy,
                    "vehicles": solution["num_vehicles"],
                    "cost": solution["total_cost"],
                }
            )
            print(
                f"  {full_name:50s} | Vehicles: {solution['num_vehicles']} | Cost: {solution['total_cost']:7.2f}"
            )

        results[instance_name] = instance_results

    # Summary analysis
    print("\n" + "=" * 80)
    print("SUMMARY ANALYSIS")
    print("=" * 80)

    for instance_name, instance_results in results.items():
        print(f"\n{instance_name}:")

        # Find best by vehicles
        min_vehicles = min(r["vehicles"] for r in instance_results)
        best_by_vehicles = [
            r for r in instance_results if r["vehicles"] == min_vehicles
        ]

        # Find best by cost among solutions with minimum vehicles
        best_solution = min(best_by_vehicles, key=lambda x: x["cost"])

        print(f"  Best solution: {best_solution['name']}")
        print(f"    Vehicles: {best_solution['vehicles']}")
        print(f"    Cost: {best_solution['cost']:.2f}")

        # Compare Christofides vs NN
        for bp in ["FFD", "BFD"]:
            nn_sol = next(
                r for r in instance_results if r["bp"] == bp and r["tsp"] == "NN"
            )
            chr_sol = next(
                r for r in instance_results if r["bp"] == bp and r["tsp"] == "CHR"
            )
            improvement = ((nn_sol["cost"] - chr_sol["cost"]) / nn_sol["cost"]) * 100
            print(f"  {bp}: Christofides improvement over NN: {improvement:+.2f}%")


if __name__ == "__main__":
    # Demo 1: Complete path-traced solution with FFD vs BFD
    demo_cvrp_complete_solution()

    # Demo 2: Algorithm comparison across multiple instances
    demo_algorithm_comparison()

    print("\n" + "=" * 80)
    print("ALGORITHMIC SUMMARY")
    print("=" * 80)
    print("\nTwo-Phase CVRP Construction:")
    print("  Phase 1 (Bin Packing): Assign customers to vehicles")
    print("    Algorithms tested: FFD, BFD")
    print("    - Input: Customer demands, vehicle capacity")
    print("    - Output: Vehicle assignments (which customers in which vehicle)")
    print("    - Complexity: O(n log n)")
    print("    - Approximation: ≤ (11/9)OPT + 6/9 vehicles")
    print("\n  Phase 2 (TSP Routing): Route each vehicle's customers")
    print("    Algorithms tested: Nearest Neighbor (NN), Christofides (CHR)")
    print("    - NN: Greedy O(n²), typically 20-30% above optimal")
    print("    - CHR: O(n³), guaranteed ≤ 1.5 × OPT for metric TSP")
    print("    - Input: Customer locations for each vehicle")
    print("    - Output: Complete routes (Depot → customers → Depot)")
    print("\nAlgorithm Combinations:")
    print("  FFD+NN:  Fast vehicle assignment + Fast routing")
    print("  BFD+NN:  Tight vehicle packing + Fast routing")
    print("  FFD+CHR: Fast vehicle assignment + Quality routing")
    print("  BFD+CHR: Tight vehicle packing + Quality routing (best quality)")
    print("\nKey Insights:")
    print("  - Two-phase approach separates capacity constraints from routing")
    print("  - Bin packing (FFD/BFD) handles vehicle assignment efficiently")
    print("  - Each vehicle's route is optimized independently")
    print("  - Christofides provides better tour quality but is slower")
    print("  - Trade-off: Speed (FFD+NN) vs Quality (BFD+CHR)")
    print("=" * 80)
