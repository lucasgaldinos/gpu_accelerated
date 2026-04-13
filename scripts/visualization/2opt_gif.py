import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from typing import Iterator, Tuple, List


def generate_random_coordinates(num_points: int, seed: int = 42) -> np.ndarray:
    """
    Generates a fixed set of random 2D coordinates.

    Parameters
    ----------
    num_points : int
        The number of nodes to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        A (num_points, 2) array of coordinates.
    """
    np.random.seed(seed)
    return np.random.rand(num_points, 2)


def calculate_path_distance(points: np.ndarray, order: np.ndarray) -> float:
    """
    Calculates the total Euclidean distance of the closed tour.

    Parameters
    ----------
    points : np.ndarray
        The coordinates of the nodes.
    order : np.ndarray
        The current permutation of node indices.

    Returns
    -------
    float
        The total distance of the tour.
    """
    # Reorder points and append the first point to the end to close the loop
    ordered_points = points[order]
    diffs = ordered_points - np.roll(ordered_points, -1, axis=0)
    return np.sum(np.sqrt(np.sum(diffs**2, axis=1)))


def two_opt_solver(points: np.ndarray) -> Iterator[Tuple[np.ndarray, int, float]]:
    """
    A generator that yields the path order after every successful 2-opt swap.

    The 2-opt algorithm iteratively removes two edges and replaces them with
    two different edges that reconnect the fragments created by edge removal
    into a shorter tour. This effectively reverses the segment between the
    swapped edges.

    Parameters
    ----------
    points : np.ndarray
        The coordinates of the nodes.

    Yields
    ------
    Tuple[np.ndarray, int, float]
        A tuple containing:
        - The current path order (indices).
        - The current iteration count.
        - The current total distance.
    """
    num_points = len(points)
    current_order = np.arange(num_points)

    # Shuffle initially to ensure we have a "bad" starting path to optimize
    np.random.shuffle(current_order)

    improved = True
    iteration = 0

    # Yield initial state
    yield (
        current_order.copy(),
        iteration,
        calculate_path_distance(points, current_order),
    )

    while improved:
        improved = False
        best_distance = calculate_path_distance(points, current_order)

        for i in range(num_points - 1):
            for j in range(i + 1, num_points):
                if j - i == 1:
                    continue  # Skip adjacent edges

                # New improved distance check
                # We only need to calculate the delta of the two edges changing,
                # but calculating full distance is safer for visualization integrity.
                new_order = current_order.copy()
                # Reverse the segment between i+1 and j
                new_order[i + 1 : j + 1] = new_order[i + 1 : j + 1][::-1]

                new_distance = calculate_path_distance(points, new_order)

                if new_distance < best_distance:
                    current_order = new_order
                    best_distance = new_distance
                    improved = True
                    iteration += 1
                    # Yield the state immediately after a swap found
                    yield current_order.copy(), iteration, best_distance

                    # Restart search from the beginning (First Improvement heuristic)
                    # This looks better in animation than Best Improvement
                    break
            if improved:
                break

    # Yield final state a few times to make the GIF pause at the end
    for _ in range(3):
        yield current_order.copy(), iteration, best_distance


def main():
    """
    Main execution block to generate coordinates, run the optimization,
    and save the animation.
    """
    # Configuration
    N_POINTS = 20
    SEED = 102  # Specific seed to ensure crossing lines are generated
    OUTPUT_FILENAME = "2opt_process.gif"
    FRAME_DURATION_MS = 3000  # 3 seconds per frame

    coords = generate_random_coordinates(N_POINTS, SEED)

    # Create generator
    history = list(two_opt_solver(coords))

    # Setup Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    def update(frame_data):
        order, iteration, dist = frame_data
        ax.clear()

        # Order points for plotting, close the loop
        plot_order = np.concatenate([order, [order[0]]])
        path_x = coords[plot_order, 0]
        path_y = coords[plot_order, 1]

        # Plot edges
        ax.plot(
            path_x,
            path_y,
            "o-",
            mfc="white",
            mec="black",
            color="black",
            lw=1.5,
            markersize=6,
        )

        # Highlight the "Start" node for orientation
        ax.plot(path_x[0], path_y[0], "o", color="red", markersize=8, label="Start")

        ax.set_title(
            f"2-Opt Optimization\nIteration: {iteration} | Distance: {dist:.2f}"
        )
        ax.axis("off")  # Clean look
        return (ax,)

    # Create Animation
    # Note: frames=history explicitly passes the pre-calculated list
    anim = FuncAnimation(fig, update, frames=history, blit=False)

    print(f"Generating animation with {len(history)} frames...")

    # Save
    # FPS = 1000 / duration_ms. For 3000ms, fps is 0.333
    writer = PillowWriter(fps=1000 / FRAME_DURATION_MS)
    anim.save(OUTPUT_FILENAME, writer=writer)

    print(f"Saved to {OUTPUT_FILENAME}")


if __name__ == "__main__":
    main()
