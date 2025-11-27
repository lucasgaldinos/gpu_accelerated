# 1. Heuristic Approaches for the TSP

- [1. Heuristic Approaches for the TSP](#1-heuristic-approaches-for-the-tsp)
    - [1.1. Introduction](#11-introduction)
    - [1.2. Assumptions](#12-assumptions)
    - [1.3. Tour Construction Heuristics](#13-tour-construction-heuristics)
        - [1.3.1. Nearest Neighbor Heuristic](#131-nearest-neighbor-heuristic)
            - [1.3.1.1. Pseudocode](#1311-pseudocode)
                - [1.3.1.1.1. Python](#13111-python)
            - [1.3.1.2. Pure Python](#1312-pure-python)
        - [1.3.2. Clark and Wright savings](#132-clark-and-wright-savings)
            - [1.3.2.1. Pseudocode](#1321-pseudocode)

## 1.1. Introduction

This is based on the article **Routing and scheduling of vehicles and crews**.

Defining three broad categories of heuristic approaches:

1. **Tour Construction Heuristics**: These heuristics build a solution from scratch. They start with an empty solution and iteratively add elements to it until a complete solution is obtained. Examples include the nearest neighbor heuristic and the greedy heuristic.
2. **Tour Improvement Heuristics**: These heuristics start with an initial solution and iteratively improve it. They search for better solutions in the neighborhood of the current solution. Examples include the 2-opt heuristic and the 3-opt heuristic.
3. **Metaheuristics or Composite Procedures**: These heuristics use a higher-level strategy to guide the search for a good solution. They often use a combination of tour construction and tour improvement heuristics. Examples include simulated annealing, genetic algorithms, and ant colony optimization.

## 1.2. Assumptions

- The TSP is symmetric, i.e., the distance between any two cities is the same in either direction.
- The TSP is complete, i.e., there is a path between every pair of cities.
- The TSP is Euclidean, i.e., the cities are points in a plane and the distance between any two cities is the straight-line distance between them.

<h2> Historical Background </h2>

## 1.3. Tour Construction Heuristics

### 1.3.1. Nearest Neighbor Heuristic

Developed by Rosenkrantz, Stearns, and Lewis in 1977.

The nearest neighbor heuristic is a simple and deterministic heuristic for the TSP. It starts with an arbitrary city and iteratively adds the nearest unvisited city to the tour until all cities have been visited.

#### 1.3.1.1. Pseudocode

**From the book:**
Step 1
: Start with any node as the beginning of a path

Step 2
: Find the node closest to the last node added to the path. Add this node to the path.

Step 3
: Repeat step 2 until all nodes are contained in the path.Then, join the first and last nodes Worst case behavior

1. Initialize all vertices as unvisited.
2. Select an arbitrary vertex, set it as the current vertex u. Mark u as visited.
3. Attribute a cost function.
4. Find out the shortest edge connecting the current vertex u and and unvisited vertex v.
5. Set v as the current vertex u. Mark v as visited.
6. If all the vertices in the domain are visited, then terminate. Else,
7. go to step 3.

```pseudocode
For a given set of coordinates, find the nearest neighbor tour
Procedure nearest_neighbor(coordinates: dict, starting_city: string | int | dict, destination_city: string):

        # 1. Initialize all vertices as unvisited.
        # unvisited = len(coordinates) - 1
        unvisited = coordinates.pop(starting_city). Can also be an enumeration of all cities.
        
        #2. Select an arbitrary vertex, set it as the current vertex u. Mark u as visited. (already done in function entries)
        tour = [starting_city_index] # starting_city can be arbitrary

        # 3. Attribute a cost function.
        cost = distance(starting_city, tour_size)
        tour_size = 0

        while len(unvisited) != 0: # or while unvisited is not empty:
            current = tour[-1] #nice way to get the last member of a list
            next = min(unvisited, key=lambda x: distance(current, ))
            tour.append(next)
            unvisited.remove(next)
        tour.append(start)
        return tour

coordinates = {
    'A': (0, 0),
    'B': (1, 2),
    'C': (4, 3),
    ...,
}
```

<font class="worst_case">Worst case behavior</font>
: The nearest neighbor heuristic can produce a tour that is arbitrarily bad. For example, consider the network shown in Figure 11.1. The nearest neighbor heuristic produces a tour of length 1000, whereas the optimal tour has length 1. $$\frac{\mathrm{length~of~nearest~neighbor~tour}}{\mathrm{length~of~optimal~tour}}\leq\frac{1}{2}\biggl[\lg(n)\biggr]+\frac{1}{2}$$ where lg denotes the logarithm to the base 2, $\lceil X\rceil$ is the smallest integer $\geq X$, and $n$ is the number of nodes in the network.

<font class="num_comput">Number of computations</font>
: The nearest neighbor algorithm requires on the order of $n^2$ computations.

<font class="comment">Comments</font>
: In a computational setting，the procedure outlined above may be repeated n times,each time with a new node selected as the starting node.The best solution obtained would then be listed as the answer.Notice that this strategy runs in an amount of time proportional to $n^3$

##### 1.3.1.1.1. Python

1. Set a cost function

```
Procedure distance(starting_city, tour_size):
    # Euclidean distance between each pair of points

```

<details open>
<summary>
<font size="+1">
<b>
Codes
</b>
</font>
</summary>

#### 1.3.1.2. Pure Python

```python

```

</details>

| name  | output  | isDeterministic |
|---|---| --- |
| nearest neighbor  | approximate | no |

### 1.3.2. Clark and Wright savings

#### 1.3.2.1. Pseudocode

Step 1
: Select any node as the central depost which we denote as node 1.

Step 2
: Compute savings $ s_{ij}= c_{1i}+c_{1j}-c_{ij}$ for all pairs of nodes $i, j$.

Step 3
: Order the savings from largest to smallest.

Step 4
: Starting at the top of the savings list and moving downwards, form larger subtours by linking appropriate nodes $i, j$.

<font class="worst_case">Worst case behavior</font>
: Known for both sequential and concurrent versions. Golden[289] demonstrate that for a sequential version of this algorihtm where at each step we select the best savings from the last node added to the subtour, the worst ratio is boudndd by a linear function in $\log_{2} n$. Ong [517] derived a similar result for the concurrent version.

<font class="num_comput">Number of computations</font>
Number of computations {.num_comput}
: The calculation of the matrix $S=[s_{ij}]$ in *step 2* requires about $cn^2$ operations for some constant $c$. Next, in *step 3*, savings can be sorted into nonincreasing order via the "Heapsort" method of Williams[674] and Floyd[226] in a maximum of $cn^{2}\lg(n)$ comparisons and displacements. *Step 4* involves at most $n^2$ operations since there are that many savings to consider. Thus, the Clark and Wright savings procedure requires on the order of $n^2\lg(n)$ computations.

<style>
   .worst_case {
      color: red;
   }
   .num_comput {
      color: green;
   }
   .comment {
     color: yellow;
   }
</style>
