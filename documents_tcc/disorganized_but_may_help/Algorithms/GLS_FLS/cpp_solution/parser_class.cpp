
#include "parser_tsplib.h"
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

/*Trimming function to remove leading and trailing whitespaces*/
const std::string WHITESPACE = " \n\r\t\f\v";
std::string ltrim(const std::string &s) {
  size_t start = s.find_first_not_of(WHITESPACE);
  return (start == std::string::npos) ? "" : s.substr(start);
}

std::string rtrim(const std::string &s) {
  size_t end = s.find_last_not_of(WHITESPACE);
  return (end == std::string::npos) ? "" : s.substr(0, end + 1);
}

std::string trim_string(const std::string &s) { return rtrim(ltrim(s)); }

std::vector<Node>
TSPLIBParser::parseSymmetricTSPLIB(const std::string &filename) {
  std::ifstream file(filename);
  if (!file.is_open()) {
    throw std::runtime_error("Could not open file");
  }

  std::string line;
  std::vector<Node> node_vector;
  bool reading_coords = false;

  while (std::getline(file, line)) {
    line = trim_string(line);
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
      node.id = std::stoi(keyword); // Convert the keyword to an integer. iss >>
                                    // node.id would not work here because the
                                    // keyword has already been extracted.
      iss >> node.x >> node.y;
      // if (!(iss >> node.id >> node.x >> node.y)) {
      // 	std::cerr << "Error parsing line: " << line << std::endl;
      // 	continue; // Skip this line if parsing fails
      // }
      node_vector.push_back(node);
    }
  }

  // Debugging output
  // for (const auto& nodes: node_vector) {
  // std::cout << "Node " << nodes.id << " x: " << nodes.x << " y: " << nodes.y
  // << "\n";
  // }

  return node_vector;
}

std::vector<std::vector<double>>
TSPLIBParser::computeDistanceMatrix(const std::vector<Node> &node_vector) {
  size_t n = node_vector.size();
  std::vector<std::vector<double>> distanceMatrix(n,
                                                  std::vector<double>(n, 0.0));

  for (size_t i = 0; i < n; ++i) {
    for (size_t j = 0; j < n; ++j) {
      if (i != j) {
        double dx = node_vector[i].x - node_vector[j].x;
        double dy = node_vector[i].y - node_vector[j].y;
        distanceMatrix[i][j] = std::sqrt(dx * dx + dy * dy);
        // std::cout << "i:" << i << " dxi:" << dx << " j:" << j << " dyj:" <<
        // dy << " " << distanceMatrix[i][j] << " ";
      }
    }
  }

  return distanceMatrix;
}

void printDistanceMatrix(
    const std::vector<std::vector<double>> &distanceMatrix) {
  for (size_t i = 0; i < distanceMatrix.size(); ++i) {
    for (size_t j = 0; j < distanceMatrix[i].size(); ++j) {
      std::cout << distanceMatrix[i][j] << " ";
    }
    std::cout << std::endl; // Move to the next line after printing each row
  }
}