#include "parser_tsplib.h"
#include <random>

struct Solution {
	std::vector<int> tour;
	double cost;
};

// Evaluate tour cost
double evaluateTour(const std::vector<int>& tour, const std::vector<std::vector<double>>& distanceMatrix) {
	double cost = 0.0;
	for (size_t i = 0; i < tour.size() - 1; ++i) {
		cost += distanceMatrix[tour[i]][tour[i + 1]];
	}
	cost += distanceMatrix[tour.back()][tour[0]]; // Return to start
	return cost;
}

// Generate an initial solution using the Nearest Neighbor heuristic
Solution generateNearestNeighborSolution(const std::vector<std::vector<double>>& distanceMatrix) {
	int numNodes = distanceMatrix.size();
	std::vector<int> tour;
	std::vector<bool> visited(numNodes, false);

	std::cout << numNodes << std::endl;

	// Start from node 0 (or choose randomly)
	std::random_device rd; // random number from hardware
	std::mt19937 gen(rd()); // seed of 32-bit Mersenne Twister generator
	std::uniform_int_distribution<> dist_range(0, numNodes - 1); // define the range in which to generate random numbers
	int currentNode = dist_range(gen);
	//int currentNode = 0;

	tour.push_back(currentNode);
	visited[currentNode] = true;

	for (int step = 1; step < numNodes; ++step) {
		double minDistance = std::numeric_limits<double>::infinity();
		int nextNode = -1;

		// Find the nearest unvisited node
		for (int i = 0; i < numNodes; ++i) {
			if (!visited[i] && distanceMatrix[currentNode][i] < minDistance) {
				minDistance = distanceMatrix[currentNode][i];
				nextNode = i;
			}
		}

		// Move to the nearest node
		if (nextNode != -1) {
			tour.push_back(nextNode);
			visited[nextNode] = true;
			currentNode = nextNode;
		}
	}

	double cost = evaluateTour(tour, distanceMatrix);
	std::cout << "Initial solution cost: " << cost << "\n";
	return {tour, cost};
}

// Solution generateFirstRandomSolution(const std::vector<std::vector<double>>& distanceMatrix) {
//     int numNodes = distanceMatrix.size();
//     std::vector<int> tour;
//     std::vector<bool> visited(numNodes, false);

//     int currentNode = 0;
//     tour.push_back(currentNode);
//     visited[currentNode] = true;
//     while (tour.size() < numNodes) {
//         int nextNode = rand() % numNodes;
//         if (!visited[nextNode]) {
//             tour.push_back(nextNode);
//             visited[nextNode] = true;
//         }
//     }

//     return {tour, cost};
// }

Solution generateFirstSolution(const std::vector<std::vector<double>>& distanceMatrix) {
	// Initialize solution in the dumbest way possible. Just go through the nodes in order.

	int numNodes = distanceMatrix.size(); // number of nodes
	std::vector<int> tour; // tour vector
	std::vector<bool> visited(numNodes, false); // visited vector

	// int currentNode = 0; // start at node 0
	// tour.push_back(currentNode); // add node 0 to tour
	// visited[currentNode] = true; // mark node 0 as visited
	
	// Start from node 0 (or choose randomly)
	std::random_device rd; // random number from hardware
	std::mt19937 gen(rd()); // seed of 32-bit Mersenne Twister generator
	std::uniform_int_distribution<> dist_range(0, numNodes - 1); // define the range in which to generate random numbers
	int currentNode = dist_range(gen);
	//int currentNode = 0;

	// Add random node to the tour
	tour.push_back(currentNode);
	visited[currentNode] = true;


	for (int i = 0; i < numNodes; ++i) {
		tour.push_back(i);
		visited[i] = true;
	}

	double cost = evaluateTour(tour, distanceMatrix);
	std::cout << "Initial solution cost: " << cost << "\n";
	return {tour, cost};
}

// Perform local search (e.g., 2-opt)
Solution localSearch(const Solution& initialSolution, const std::vector<std::vector<double>>& distanceMatrix) {
	Solution best = initialSolution;
	bool improved = true;
	int iter_count = 0;

	while (improved) {
		improved = false; // will iter indefinitely until no improvement
		for (size_t i = 1; i < best.tour.size() - 1; ++i) {
			for (size_t j = i + 1; j < best.tour.size(); ++j) {
				// Swap two edges
				std::reverse(best.tour.begin() + i, best.tour.begin() + j + 1);
				double newCost = evaluateTour(best.tour, distanceMatrix);
				if (newCost < best.cost) {
					best.cost = newCost;
					improved = true;
				} else {
					std::reverse(best.tour.begin() + i, best.tour.begin() + j + 1); // Undo swap
				}
				iter_count++;
			}
		}
	}
	std::cout << "final Local search cost: " << best.cost << "\n";
	return best;
}

// Guided Local Search
Solution guidedLocalSearch(const Solution& initialSolution, const std::vector<std::vector<double>>& distanceMatrix, double lambda) {
	Solution current = initialSolution;
	std::vector<int> penalties(distanceMatrix.size() * distanceMatrix.size(), 0);
	double bestCost = current.cost;
	int counter = 0;


	std::cout << "GLS started" << "\n";
	
	while (true) {
		// Apply local search
		counter++;
		std::cout << "GLS Iteration: " << counter << std::endl;
		current = localSearch(current, distanceMatrix);
		
		// Update penalties
		int maxEdge = 0;
		double maxUtility = -std::numeric_limits<double>::infinity();
		for (size_t i = 0; i < current.tour.size() - 1; ++i) {
			int u = current.tour[i];
			int v = current.tour[i + 1];
			double cost = distanceMatrix[u][v];
			double utility = cost / (1 + penalties[u * distanceMatrix.size() + v]);
			if (utility > maxUtility) {
				maxUtility = utility;
				maxEdge = u * distanceMatrix.size() + v;
			}
		}
		penalties[maxEdge] += 1;

		// Update cost with penalties
		double augmentedCost = current.cost + lambda * penalties[maxEdge];
		if (augmentedCost >= bestCost) break; // Terminate if no improvement
		std::cout << "Augmented cost: " << augmentedCost << std::endl;
		// bestCost = augmentedCost;
		// bestSolution = current;
	}
	std::cout << "GLS finished" << "\n";
	return current;
}

int main() {

		std::cout << "Enter the file name: ";
		std::string filename;
		std::cin >> filename;

		std::vector<std::vector<double>> distanceMatrix;

	// Parse file and create distance matrix
	try {
		auto node_vector = TSPLIBParser::parseSymmetricTSPLIB("../../tsplib_problems/maybe_all/sourcesSymmetricTSP/" + filename + ".tsp");
		distanceMatrix = TSPLIBParser::computeDistanceMatrix(node_vector);
		std::cout << "Parsed " << node_vector.size() << " nodes and computed distance matrix.\n";
	} catch (const std::exception &e) {
		std::cerr << "Error: " << e.what() << "\n";
	}

	// Create a first solution with nearest neighbor algorithm
	// Solution initialSolution = generateNearestNeighborSolution(distanceMatrix);
	Solution initialSolution = generateFirstSolution(distanceMatrix);

	// Apply `guidedLocalSearch` to improve the solution.
	double lambda = 1;
	Solution optimizedSolution =
		guidedLocalSearch(initialSolution, distanceMatrix, lambda);

	std::cout << "Optimized solution cost: " << optimizedSolution.cost << "\n";
	std::cout << "Tour: ";
	for (int node : optimizedSolution.tour) {
		std::cout << node << " ";
	}
		std::cout << "\n";

	
	return 0;
}
