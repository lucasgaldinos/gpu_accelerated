import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.spatial.distance import pdist, squareform
from typing import Iterator, Tuple, List, Optional


def generate_random_coordinates(num_points: int, seed: int = 42) -> np.ndarray:
    """
    Generates a fixed set of random 2D coordinates.

    Parameters
    ----------
    num_points : int
        Number of nodes.
    seed : int
        Random seed.

    Returns
    -------
    np.ndarray
        (num_points, 2) array of coordinates.
    """
    np.random.seed(seed)
    return np.random.rand(num_points, 2)


def compute_christofides_tour(points: np.ndarray) -> np.ndarray:
    """
    Computes an initial tour using the Christofides algorithm.
    Guarantees a solution within 1.5x of the optimal length.

    Parameters
    ----------
    points : np.ndarray
        Node coordinates.

    Returns
    -------
    np.ndarray
        Array of indices representing the tour order.
    """
    num_points = len(points)
    dist_matrix = squareform(pdist(points))

    # 1. Create a complete graph with negative weights (since nx uses max_weight_matching)
    G = nx.complete_graph(num_points)
    for u, v in G.edges():
        G[u][v]["weight"] = -dist_matrix[
            u, v
        ]  # Negate for minimization via max matching
        G[u][v]["real_dist"] = dist_matrix[u, v]

    # 2. Minimum Spanning Tree (using real distances, so we negate the negative weights back or use default)
    # NetworkX MST minimizes weight. We need positive weights for this standard call.
    G_pos = G.copy()
    for u, v in G_pos.edges():
        G_pos[u][v]["weight"] = dist_matrix[u, v]

    T = nx.minimum_spanning_tree(G_pos)

    # 3. Find vertices with odd degree in T
    odd_degree_nodes = [v for v, d in T.degree() if d % 2 == 1]

    # 4. Minimum Weight Perfect Matching on induced subgraph of odd nodes
    # We use the negated weights graph G to effectively find min weight matching
    subgraph = G.subgraph(odd_degree_nodes)
    matching = nx.max_weight_matching(subgraph, maxcardinality=True)

    # 5. Combine MST and Matching to form a MultiGraph
    M = nx.MultiGraph()
    M.add_nodes_from(range(num_points))
    M.add_edges_from(T.edges())
    M.add_edges_from(matching)

    # 6. Find Eulerian Circuit
    eulerian_circuit = list(nx.eulerian_circuit(M, source=0))

    # 7. Shortcut to Hamiltonian Path (skip repeated nodes)
    path = []
    visited = set()
    for u, v in eulerian_circuit:
        if u not in visited:
            path.append(u)
            visited.add(u)

    return np.array(path)


def calculate_path_distance(points: np.ndarray, order: np.ndarray) -> float:
    """
    Calculates Euclidean distance of the closed tour.

    Parameters
    ----------
    points : np.ndarray
        Coordinates.
    order : np.ndarray
        Tour indices.

    Returns
    -------
    float
        Total distance.
    """
    ordered = points[order]
    diffs = ordered - np.roll(ordered, -1, axis=0)
    return np.sum(np.sqrt(np.sum(diffs**2, axis=1)))


def two_opt_solver(
    points: np.ndarray, initial_order: np.ndarray
) -> Iterator[Tuple[np.ndarray, int, float, Optional[Tuple[int, int]]]]:
    """
    Generator for 2-opt optimization. Yields twice per swap:
    1. Preview state (edges to be cut highlighted).
    2. Swapped state (edges reconnected).

    Parameters
    ----------
    points : np.ndarray
        Coordinates.
    initial_order : np.ndarray
        Starting tour permutation.

    Yields
    ------
    Tuple
        (current_order, iteration, distance, highlight_indices)
        highlight_indices is a tuple (i, j) indicating indices of edges to cut, or None.
    """
    current_order = initial_order.copy()
    num_points = len(points)
    improved = True
    iteration = 0

    # Yield initial state
    yield (
        current_order.copy(),
        iteration,
        calculate_path_distance(points, current_order),
        None,
    )

    while improved:
        improved = False
        best_dist = calculate_path_distance(points, current_order)

        for i in range(num_points - 1):
            for j in range(i + 1, num_points):
                if j - i == 1:
                    continue

                new_order = current_order.copy()
                new_order[i + 1 : j + 1] = new_order[i + 1 : j + 1][::-1]
                new_dist = calculate_path_distance(points, new_order)

                if new_dist < best_dist - 1e-6:  # Float tolerance
                    # 1. Yield Preview (Red Lines)
                    yield current_order.copy(), iteration, best_dist, (i, j)

                    # 2. Apply Swap
                    current_order = new_order
                    best_dist = new_dist
                    improved = True
                    iteration += 1

                    # 3. Yield Result
                    yield current_order.copy(), iteration, best_dist, None

                    break  # First improvement
            if improved:
                break

    # Final pause
    for _ in range(2):
        yield current_order.copy(), iteration, best_dist, None


def main():
    """
    Main execution block.
    """
    # Configuration
    N_POINTS = 25
    SEED = 150  # Adjusted seed to create a tangible mess for Christofides
    OUTPUT_FILE = "2opt_christofides.gif"
    FRAME_DURATION_MS = 3000

    coords = generate_random_coordinates(N_POINTS, SEED)

    # Initial Tour via Christofides
    print("Computing Christofides initial tour...")
    init_tour = compute_christofides_tour(coords)

    # Generate Frames
    print("Running 2-opt optimization...")
    history = list(two_opt_solver(coords, init_tour))

    # Plotting Setup
    fig, ax = plt.subplots(figsize=(8, 6))

    def update(frame_data):
        order, itr, dist, highlights = frame_data
        ax.clear()

        # Basic Tour Plot
        # We manually construct segments to allow individual edge coloring
        full_order = np.concatenate([order, [order[0]]])

        # Default color for all edges
        for k in range(len(order)):
            start_node = full_order[k]
            end_node = full_order[k + 1]

            color = "black"
            width = 1.5
            style = "-"

            # If highlights exist, check if this edge corresponds to (i, i+1) or (j, j+1)
            if highlights:
                i, j = highlights
                # Edge 1: from index i to i+1
                if k == i:
                    color = "red"
                    width = 2.5
                # Edge 2: from index j to j+1
                # Note: j is the index of the node. The edge being cut is from j to j+1
                # However, in standard 2-opt notation, we cut edge (i, i+1) and (j, j+1).
                elif k == j:
                    color = "red"
                    width = 2.5

            ax.plot(
                [coords[start_node, 0], coords[end_node, 0]],
                [coords[start_node, 1], coords[end_node, 1]],
                color=color,
                lw=width,
                linestyle=style,
                zorder=1,
            )

        # Plot Nodes
        ax.plot(
            coords[:, 0],
            coords[:, 1],
            "o",
            mfc="white",
            mec="black",
            markersize=6,
            zorder=2,
        )
        ax.plot(
            coords[full_order[0], 0],
            coords[full_order[0], 1],
            "o",
            color="blue",
            markersize=8,
            label="Start",
            zorder=3,
        )

        status = "Preview Swap" if highlights else "Optimized"
        ax.set_title(
            f"Method: Christofides + 2-Opt\nIteration: {itr} | Dist: {dist:.2f} | Status: {status}"
        )
        ax.axis("off")

    anim = FuncAnimation(fig, update, frames=history, blit=False)

    print(f"Saving GIF ({len(history)} frames)...")
    writer = PillowWriter(fps=1000 / FRAME_DURATION_MS)
    anim.save(OUTPUT_FILE, writer=writer)
    print(f"Done: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
