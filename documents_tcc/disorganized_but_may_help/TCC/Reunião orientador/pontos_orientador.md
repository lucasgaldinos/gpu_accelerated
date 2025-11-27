# Things I did not understand

## 4.1 Proposed heuristics

Each pair $[dist(s,i_n), \hat{g}(x_n)]$ corresponds to a point in the chart depicted in figure and is associated with a specific interval index calculated as $r=\min \{k \in Z_+|k \geq \frac{dist(s,i_n)}{\Delta} \}$. For this interval, $\alpha_r$ is:

$$
\begin{align}
    \alpha_r =
        \begin{cases}
            \frac{\hat{g}(x_n)}{dist(s,i_n)} & \text{if} \quad \alpha_r \quad \text{is not defined} \\
            \min \left[\alpha_r, \frac{\hat{g}(x_n)}{dist(s, i_n)} \right] & \text{otherwise}
        \end{cases}
\end{align}
$$

$\alpha_r$ is used to estimate $\hat{h}_{III}(x_n)$ **as function of the straight line distance of stoppage location** $i_n$ to the trip destination$t$, denoted by $dist(i_n, t)$. These interval is now calculated as $r=\max \{k \in Z_+|k \leq \frac{dist(s,i_n)}{\Delta} \}$

## 4.2

### Definition 1

In other words, two stoppage configurations are similar in elements (i, p), if the stop occurs in the same location and the type of the stop is the same, i.e., if the stop will be for rest, for meal, for overnight, or for weekend downtime in both stoppage configurations. Nodes that are similar in elements (i, p) likely will have different arrival times and different costs ˆg(x) because incurred time is a continuous variable and any difference in elapsed time will lead to different costs to date.

**I was considering each stop as a city, but there can be multiple stops in a city. Location $i$ must refer to the city, then?**

### Proposition

Pruning nodes in the graph is not without disadvantages as the guarantee of optimality for the problem is lost for both heuristics if the graph is pruned.

**Are the losses really that significant? The figure 1 graph is already counting this pruned states or is $\hat{h}(x)$ the optimal solution?** *As I understand, it's the optimal solution calculated at first*

**The heuristics for real-time are used with the pruned graph, then?** *I understood as this real-time is counted as if the driver had some problems and couldn't go for the optimal route*

## 4.3 Algorithm

**in S3 (node selection), if the program exits with failure, what should the driver then do? What can cause this problem to happen?**

**In S4, the change for $\hat{h}_{III}(x)$ is needed because this heuristic the optimal? It's acting like a control heuristic?**  
**when $X_T \leftarrow X_T - \{x_m\}$, $X_P \leftarrow X_P \cup \{x_m\}, am I considering the preceding node as the actual node?** *This step is really not clear to me*

## Other questions

**Does the algorithm take into account things as roadblocks or other possible problems?** *Must be hard to implement this type of things*

**How was the database created?**

**Didn't understand $X_T$ and $X_P$ really well**
