#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

// Structure for a 2D point
struct Node {
  int id;
  double x, y;
};

// Parse a TSPLIB file
std::vector<Node> parseSymmetricTSPLIB(const std::string &filename) {

  std::ifstream file(filename); // Open the file and check for errors
  if (!file.is_open()) {
    throw std::runtime_error("Could not open file");
  }

  std::string line;
  std::vector<Node> node_vector;
  bool reading_coords = false;

  while (std::getline(file, line)) {
    std::istringstream iss(line);
    std::string keyword;
    iss >> keyword;

    if (keyword == "NODE_COORD_SECTION") {
      reading_coords = true;
      continue; // Skip to the next line to avoid the if condition of reading_coords below
    }

    if (keyword == "EOF") {
      break;
    }

    if (reading_coords) {
      Node node;
      iss >> node.id >> node.x >> node.y; // Read the node data from istringstream
      node_vector.push_back(node);
    }
  }
  return node_vector;
}

// Compute distance matrix based on each coordinate
std::vector<std::vector<double>> computeDistanceMatrix(const std::vector<Node> &node_vector) {
  size_t n = node_vector.size();
  std::vector<std::vector<double>> distanceMatrix(n,std::vector<double>(n, 0.0)); 

  for (size_t i = 0; i < n; ++i) {
    for (size_t j = 0; j < n; ++j) {
      if (i != j) {
        double dx = node_vector[i].x - node_vector[j].x;
        double dy = node_vector[i].y - node_vector[j].y;
        distanceMatrix[i][j] = std::sqrt(dx * dx + dy * dy);
      }
    }
  }

  return distanceMatrix;
}

int main() {
  try {

    std::cout << "Enter the file name: ";
    std::string filename; // Replace with your file path
    std::cin >> filename;

    auto node_vector = parseSymmetricTSPLIB("../../tsplib_problems/maybe_all/sourcesSymmetricTSP/"+filename+".tsp");
    auto distanceMatrix = computeDistanceMatrix(node_vector);
    std::cout << "Parsed " << node_vector.size() << " node_vector and computed distance matrix.\n";
  } catch (const std::exception &e) {
    std::cerr << "Error: " << e.what() << "\n";
  }
  return 0;
}

