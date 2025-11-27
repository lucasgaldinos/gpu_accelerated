# Code Implementation details

## C++

For the first implementation, I asked chatGPT to sketch a c++ code bsed on the solution proposed by Tsang and Voudouris.

### TSPLIB Parser

#### AI sketched parser

```c++
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>

// Structure for a 2D point
struct Node {
    int id;
    double x, y;
};

// Parse a TSPLIB file
std::vector<Node> parseTSPLIB(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    std::string line;
    std::vector<Node> nodes;
    bool reading_coords = false;

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string keyword;
        iss >> keyword;

        if (keyword == "NODE_COORD_SECTION") {
            reading_coords = true;
            continue;
        }
        if (keyword == "EOF") {
            break;
        }

        if (reading_coords) {
            Node node;
            iss >> node.id >> node.x >> node.y;
            nodes.push_back(node);
        }
    }
    return nodes;
}

// Compute distance matrix
std::vector<std::vector<double>> computeDistanceMatrix(const std::vector<Node>& nodes) {
    size_t n = nodes.size();
    std::vector<std::vector<double>> distanceMatrix(n, std::vector<double>(n, 0.0));
    
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            if (i != j) {
                double dx = nodes[i].x - nodes[j].x;
                double dy = nodes[i].y - nodes[j].y;
                distanceMatrix[i][j] = std::sqrt(dx * dx + dy * dy);
            }
        }
    }
    return distanceMatrix;
}

int main() {
    try {
        auto nodes = parseTSPLIB("example.tsp");
        auto distanceMatrix = computeDistanceMatrix(nodes);
        std::cout << "Parsed " << nodes.size() << " nodes and computed distance matrix.\n";
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
    }
    return 0;
}
```

In the code above, TSPLIB files are parsed. Kinda terrible though.

### GLS implementation

#### AI sketched GLS

```c++
#include <iostream>
#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>

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

// Perform local search (e.g., 2-opt)
Solution localSearch(const Solution& initialSolution, const std::vector<std::vector<double>>& distanceMatrix) {
    Solution best = initialSolution;
    bool improved = true;

    while (improved) {
        improved = false;
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
            }
        }
    }
    return best;
}

// Guided Local Search
Solution guidedLocalSearch(const Solution& initialSolution, const std::vector<std::vector<double>>& distanceMatrix, double lambda) {
    Solution current = initialSolution;
    std::vector<int> penalties(distanceMatrix.size() * distanceMatrix.size(), 0);
    double bestCost = current.cost;

    while (true) {
        // Apply local search
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
    }
    return current;
}

int main() {
    // Define distance matrix and an initial solution here.
    // Apply `guidedLocalSearch` to improve the solution.
}
```

The GLS metaheuristic modifies a standard local search by introducing penalties for frequently used solution components.

1. Perform a local search to find an initial solution.
2. Introduce penalties for edges (or solution components) to escape local optima:

    Penalty Function: $p(e)=p(e)+1$ for penalized edge $e$.
3. Update the cost function to include penalties:

    Augmented Cost Function: $f'(S)=f(S)+λ⋅∑_{e \in S}p(e)$, where $λ$ controls the influence of penalties.
4. Repeat local search with the updated cost function.
