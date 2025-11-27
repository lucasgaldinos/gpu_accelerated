#ifndef PARSING_TSPLIB_HPP // include a guard to prevent multiple inclusions of the header file. If PARSING_TSPLIB_HPP is not defined, the code between here and #endif will be processed by the compiler.
#define PARSING_TSPLIB_HPP

#include <vector>
#include <string>
#include <iostream>
#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>


// Structure for a 2D point
struct Node {
    int id;
    double x, y;
};

// Class for parsing and computing distance matrices
class TSPLIBParser {
public:
    static std::vector<Node> parseSymmetricTSPLIB(const std::string &filename);
    static std::vector<std::vector<double>> computeDistanceMatrix(const std::vector<Node> &node_vector);
};

#endif // PARSING_TSPLIB_HPP