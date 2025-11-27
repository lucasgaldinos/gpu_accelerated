<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>

# TSP-HEURISTIC APPROACHES Heuristics examined

<!--Pages 24-32 of raff1983stateofart.pdf-->

- [TSP-HEURISTIC APPROACHES Heuristics examined](#tsp-heuristic-approaches-heuristics-examined)
  - [Tour construction procedures](#tour-construction-procedures)
    - [Nearest neighbor procedure (Rosenkrantz,Stearns, and Lewis\[568\])](#nearest-neighbor-procedure-rosenkrantzstearns-and-lewis568)
  - [(c) Insertion procedures (Rosenkrantz, Sterns and Lewis \[568\])](#c-insertion-procedures-rosenkrantz-sterns-and-lewis-568)
  - [c4)Farthest Insertion](#c4farthest-insertion)
    - [c6) Convex hull insertion It has been shown that if the costs $c\_{ij}$ represent Euclidean distance and $H$ is the convex hull](#c6-convex-hull-insertion-it-has-been-shown-that-if-the-costs-c_ij-represent-euclidean-distance-and-h-is-the-convex-hull)
    - [Procedure](#procedure)
  - [c7) Greatest Angle Insertion](#c7-greatest-angle-insertion)
    - [Procedure](#procedure-1)
  - [Procedure](#procedure-2)
    - [Procedure Step 1. Find a minimal spanning tree $T$ of $G$](#procedure-step-1-find-a-minimal-spanning-tree-t-of-g)
  - [2.3.2 Tour improvement procedures Perhaps the best known heuristics for the TSP are branch exchange heuristics. The 2-opt and](#232-tour-improvement-procedures-perhaps-the-best-known-heuristics-for-the-tsp-are-branch-exchange-heuristics-the-2-opt-and)
  - [2.3.3 Composite procedures The basic composite procedure can be stated as follows](#233-composite-procedures-the-basic-composite-procedure-can-be-stated-as-follows)
    - [2.3.4 Akl's directed TSP approach](#234-akls-directed-tsp-approach)
    - [2.4. SINGLE DEPOT/MULTIPLE VEHICLE ROUTING](#24-single-depotmultiple-vehicle-routing)
  - [2.4.2 The multiple traveling salesmen problem](#242-the-multiple-traveling-salesmen-problem)

The heuristics we examine fall into three broad classes-tour construction procedures, tour improvement procedures, and composite procedures. Tour construction procedures generate an approximately optimal tour from the distance matrix.Tour improvement procedures attempt to find a better tour given an initial tour. Composite procedures construct a starting tour from one of the tour construction proceduresand then attempt tofind a better tour using one or more of the tour improvement procedures.Most of these procedures are described in the literature and.hence.will be sketched only briefly:but newer procedures will be studiedin more detail.We assume for the sake of simplicity that the costs are symmetric, (i.e. $c_{ij}=c_{ji}$ )satisfy the triangle inequality,and are defined for each (i,j) pair,unless otherwise specified

## Tour construction procedures

### Nearest neighbor procedure (Rosenkrantz,Stearns, and Lewis[568])

Step 1
: Start with any node as the beginning of a path  

Step 2
: Find the node closest to the last node added to the path. Add this node to the path.  

Step 3
: Repeat step 2 until all nodes are contained in the path.Then, join the first and last nodes Worst case behavior

$$\frac{\mathrm{length~of~nearest~neighbor~tour}}{\mathrm{length~of~optimal~tour}}\leq\frac{1}{2}\biggl[\lg(n)\biggr]+\frac{1}{2}$$

where lg denotes the logarithm to the base 2, $\lceil X\rceil$ is the smallest integer $\geq X$, and $n$ is the number of nodes in the network Number of computations.The nearest neighbor algorithm requires on the order of $n^2$ computations,

Comments: In a computational setting，the procedure outlined above may be repeated n times,each time with a new node selected as the starting node.The best solution obtained would then be listed as the answer.Notice that this strategy runs in an amount of time proportional to $n^3$

bClark and Wright Savings Clark and Wright[145],Golden [291]

Procedure

Step 1. Select any node as the central depot which we denote as node 1. Step 2.Compute savings $s_{ij}=c_{1i}+c_{1j}-c_{ij}$ for i j=2.3 $j=2,3$ $,j=2,3,\ldots,n$

Step3.Order the savings from largest to smallest.

Step 4. Starting at thc top of thc savings list and moving downwards,form larger subtours by

linking appropriate nodes i and j. Repeat until a tour is formed

sequwenrst ase behaviortTheswors lae behavior for thisaprachisk nown for both a this algorithm where at each step we select the best savings from the last node added to the subtour, the worst case ratio is bounded by a linear function in lg(n). Ong[517] has derived a similar result for the concurrent version. Number of computations. The calculation of the matrix $S=[s_{ij}]$ in step 2requires about $cn^2$

operations for some constant c.Next,in step 3,savings can be sorted into nonincreasing order via the“Heapsort”method of Williams[674] and Floyd[226] in a maximum of $cn^{2}\log(n)$ comparisons and displacements.Step 4 involves at most $n^2$ operations since there are thatmany savings to consider.Thus,the Clark and Wright savings procedure requires on the order of $n^2\log(n)$ computations

------------------------------------------------------------------

Comments.Each node may be selected as node1 for the above procedure (yielding $n^3|g(n)$ computations). The best solution obtained would be listed as thc answer.In practice one can exploit geometric properties when distances are Euclidean; as a result,only a fraction of the almost $n^2$ saving are calculated which reduces running times by an order of magnitude (see Golden,Magnanti and Nguyen[306] for details

## (c) Insertion procedures (Rosenkrantz, Sterns and Lewis [568])

An insertion procedure takes a subtour on $k$ nodes at iteration $k$ and attempts to determine which node (not already in the subtour) should join the subtour next (the selection step) and then determines where in the subtour it should be inserted (the insertion step）.For the first four insertion procedures we discuss,each node in the network can be used as a starting node Notice that when each node is used as a starting node,the complexity of the entire procedure increases by an order of magnitude (that is,the number of computations is multiplied by $n$ )

c1Nearest insertion

Procedure

Step 1. Start with a subgraph consisting of node i only. Step 2.Find node k such that $c_{ik}$ is minimal and form the subtour i-k-i

Step 3.Selection step.Given a subtour,find node $k$ not in the subtour closest to any node in

the subtour. Step 4.Insertion step.Find the arc $(i,j)$ in the subtour which minimizes $c_{ik}+c_{kj}-c_{ij}$ Insert $k$

between i andj Step 5. Go to step 3 unless we have a Hamiltonian cycle.

Worst case havior Iength of narest inserion tour 2. length of optimal tour

Number of Computations. The nearest insertion algorithm requires on the order of $n^2$ computations

c2 Cheapest insertion

Procedure

Same as for nearest insertion except that steps3 and4 are replaced by the following step Step 3'. Find (i, $j)$ in subtour and $k$ not,such that $c_{ik}+c_{kj}-c_{ij}$ is minimal and, then, insert

betweeni and $j.$

Worst case behavior:Same as for nearest insertion Number of computations.The cheapest insertion algorithm requires on the order of $n^2\log(n)$

computations.

(c3) Arbitrary Insertion

Procedure

Same as for nearest insertion except that in step 3,arbitrarily select node $k$ not in the subtour to enter the subtour.

Worst case behavior

$$\frac{\mathrm{length~of~arbitrary~insertion~tour}}{\mathrm{length~of~optimal~tour}}\leq\left\lceil\lg(n)\right\rceil+1.$$

Number of computations. The arbitrary insertion algorithm requires on the order of $n^2$ computations.

------------------------------------------------------------------

## c4)Farthest Insertion

Procedure

Same as for nearest insertion except that in step 3replace“closest to”by“farthest from and in step 2 replace "minimal" by "maximal"

Worst case behavior. Same as for arbitrary insertion Comments.Since the worst caseresult holdsfor any arbitrary ordering of the nodes,it holds in particular for the ordering induced by the farthest insertion procedure.It is,however, quite possible that a tighterworst case bound can be derived

c5 Quick Insertion or Nearest Addition

Procedure

Step 1.Pick any node as a starting circuit T, with one node (and 0 edges) Step 2.Given the $k$ -node circuit $T_{k}$, find the node $Zk$ not on $T_{k}$ that is closest to a node,cal it $y_{k}$, on $T_{k}$ Step 3.Let $T_{k+1}$ be the $k+$ I——node circuit obtained by inserting $Zk$ immediately in front of $y_{k}$ in $T_{k}.$ Step 4.Repeat Steps 2 and 3until a Hamiltonian circuit （containing all nodes)is formed Worst case behavior.Same as for nearest insertion.Number of Computations: Same as for nearest insertion

### c6) Convex hull insertion It has been shown that if the costs $c_{ij}$ represent Euclidean distance and $H$ is the convex hull

of the nodes in two-dimensional space,then the order in which the nodes on the boundary of $H$ appear in the optimal tour will follow theorder in whichtheyappear in $H$ (see Eilon Watson-Gandy and Christofides[201] for a discussion of the implications of this result). This ohservation serves as impetus for the convex hull heuristic procedure (which is discussed along with a host ofvariants in Stewart's doctoral dissertation[627]).See also the work of Golden and Stewart [308]

### Procedure

Step 1.Form the convex hull of the set of nodes. The hull gives an initial subtour Step 2.For each node $k$ not yet contained in the subtour decide between which two nodesi

and $j$ on the subtour to insert node $k.$ That is,for each such k,find $(i,j)$ such that $c_{ik}+c_{kj}-c_{ij}$ is minimal. Step 3.From all(i, k, j) found in Step 2, determine the (i*， k*,j*) such that $(c_{i^{*}k}+c_{k^{*}j^{*}})/c_{i^{*}j}$

is minimal. Step 4.Insert node $k^*$ in subtour between nodes $i^*$ and $j^*$

Step 5. Repeat Steps 2 through 4 until a Hamiltonian cycle is obtained Worst case behavior. Unknown

Number of computations.This procedure involves,in the worst case,about as much com-

putational complexity as the cheapest insertion algorithm—on the order of $n^2\log(n)$ com putations.

Comments.Wiorkowski and McElvain[685] introduced an insertion algorithm also based on convexity ideas a number of years ago.However,their procedure performed with rather poor accuracy. More recently, Norback and Love[514] have proposed two geometric methods closcly relatcd to algorithm (c6).

## c7) Greatest Angle Insertion

### Procedure

Step 1.From the convex hull of the set of nodes.The hull gives an initial subtour Step 2.Choose the node $k^*$ not in the subtour and the arc $(i^{*},j^{*})$ in the subtour such that the angle formed by the two arcs $(i^*,k^*)$ and $(k^*,j^*)$ is the largest possible

------------------------------------------------------------------

Step 3.Insert node $k^*$ in subtour between nodes $i^*$ and $j^*$

Step 4.Repeat Steps 2 and 3until a Hamiltonian cycle is obtained

Worst case Behavior. Unknown.However,Yang[696] has demonstrated the negative result that there does not exist a constant that bounds the ratio of“greatest angle'tour length to optimal tour length. Number of computations. Same as for cheapest insertion. Comments: Norback and

Love[514] sccm to have first suggcsted this approach as well as a related procedure known as the eccentric ellipse method

c8Difference $x$ ratio insertion Or [518]

Procedure

Same as for greatest angle insertion except that Step 2is replaced by the following step Step2.Choose the node $k^{*}$ not in the subtour and the arc (i*, j*) in the subtour such that the product $\{c_{i}^{*}k^{*}+c_{k}^{*}j^{*}-c_{i}^{*}j^{*}\}\times\{(c_{i}^{*}k^{*}+c_{k}^{*}j^{*})/c_{i}^{*}j\}$ is smallest possible Worst case behavior.Unknown Number of computations. Same as for cheapest insertion

(d）Minimal spanning tree approach (Kim [387])

## Procedure

Step 1. Find a minimal spanning tree $T$ of $U$

Step 2. Double the edges in the minimal spanning tree (MST) to obtain an Euler cycle Step 3. Remove polygons over the nodes with degree greater than 2 and transform the Euler

cycle into a Hamiltonian cycle

Worst case behavior

 length of MST pprach our 2.

Number of computations.This approach requires on the order of $n^2$ computations

Christofides[132] recently proposed the following interesting e Christofides' heuristic technique for solving TSP's

### Procedure Step 1. Find a minimal spanning tree $T$ of $G$

Step 2. Identify all the odd degree nodes in $T.$ Solve a minimum cost perfect matching on the odd degree nodes using the original cost matrix.Add the branches from the matching solution to the branches already inT,obtaining an Euler cycle.In this subgraph,every node is of even degree although some nodesmay have degree greater than 2. Step 3.Remove polygons over the nodes with degree greater than 2 and transform the Euler

cycle into a Hamiltonian cycle.

Worst case behavior

lengthof Chrstondes' tor 1.s.

Cornuejols and Nemhauscr[151] havc improved this bound slightly (although not asymptotic. ally)in obtaining a tight bound for every $n\geq3$ Number of computations.Since the most time-consuming component of this procedure is

the minimum matching segment which requires $O(n^3)$ operations, this heuristic is $O(n^3)$ .In most cases,the number of odd nodes will be considerably less than n

(f) Nearest merger (Rosenkrantz et al. [568])

The nearest merger method when applied to a TSP on n nodes constructs a sequence $S_{1},\ldots,S_{n}$ such that each $S_i$ is a set of $n-i+1$ disjoint subtours covering all the nodes

------------------------------------------------------------------

Procedure

Step 1. $S_{1}$ consists of $It$ subtours,cach containing a singlc nodc. Step 2.For each $i<n$ ,find an edge $(a_i,b_i)$ such that $c_{a_ib_i}=\min\left\{c_{xy}\right\}$ for $X$ and $y$ in different subtours in $S_{i}\}$ Then, $S_{i+1}$ is obtained from $S_{i}$ by merging the subtours containing $a_{i}$ and $b_i.$ (At each step in the procedure，the two subtours closest to one another are merged.）

Worst case behavior

$$\frac{\mathrm{length~of}}{\mathrm{length~of}}\frac{\mathrm{nearest~tour}}{\mathrm{optimal~tour}}\leq2.$$

Number of computations. This approach requires on the order of $n^2$ computations

Comments.To merge two tours $T_{1}$ and $T_{2}$ when one or both consist ofa single nodeis trivial. If $T_{1}$ and 77 each contain at least twomodes.let (a,b)be an edge in $T_{1}$ and d.ean edge in $T_{2}$ such that

$$c_{ad}+c_{be}-c_{ab}-c_{de}$$

is minimized. Then MERGE ( $T.$ ， $T_{2})$ is the tour derived from $T_{\mathrm{t}}$ and $T_{2}$ by deleting （a,b)and (d,e) and adding (a, d) and $(b$ e) Other tour construction algorithms have been proposed recently by Stinson[634] and

Karp[376]. Stinson's heuristic is a modification of Vogel's approximation method which has been used extensively in obtaining an initialfeasible solution to the transportation problem Karp[376]presents a partitioning algorithm for the TSP in the plane and performs a

probabilistic analysis in order to obtain some interesting theoretical results.From a practical point of view,his procedure is a decomposition algorithm which should be capable of solving extremely large TSP's.The key idea is to partition a large rectangle into a number of subrectangles and solve a TSP in each subrectangle. The outcome is an Euler cycle which can be transformed into a tour over all the nodes with minimal efort.A simpler,but somewhat related approach, is described by Platzman and Bartholdi[546] they include a BASIC program listing in the appendix

## 2.3.2 Tour improvement procedures Perhaps the best known heuristics for the TSP are branch exchange heuristics. The 2-opt and

3-opt heuristics were introduced by Lin[444] in 1965and the $k$ -opt procedure,for $k\geq3$ ,was presented by Lin and Kernighan[446] more recently.These branch exchange heuristics work as follows: Step 1.Find an initial tour. Generally, this tour is chosen randomly (this need not.however

be the case) from the set of all possible tours. Step 2.Improve the tour using one of the branch exchange heuristics.

Step 3.Continue Step 2 until no additional improvement can be made

The branch exchange procedure terminates at a local optimum.For a given $k$ if we define a

k-change of a tour as consisting of the deletion of $k$ branches in a tour and their replacement by $k$ other branches to form a new tour,thcn a tour is $k$ optimal if it is not possiblc toimprove the tour via a $k$ -change.Steps 2 and 3 would generate this $k$ -optimal tour.Since the 2-opt exchange procedure is weaker than the 3-opt exchange procedure,it will generally terminate at aninferior local optimum. Similarly, a $k$ -opt exchange procedure will generally terminate with a better local optimum than will a 3-opt exchange procedure for $k\geq4$ .Figure 2.10 illustrates a 2-opt exchange. Note that the exchange is well-defined at each step. Once we have dccidcd to drop arcs (A, B) and $( E$, $F)$ from the current solution in order to reduce tour length,we must introduce arcs (A,E) and $( B$, $F)$ ,since introducing （A,F) leads to a subtour solution and introducing(A,B) leads to the original solution.Note that symmetry is required here since the direction on arcs B,C).C,Dand $(D,E)$ is reversed Thcsc branch cxchangc procedures areimportant since they illustrate a general approach to

heuristics for combinatorial optimization problems. In addition, they have been used to generate excellent solutions to large-scale traveling salseman problems in a reasonable amount of time.

------------------------------------------------------------------

![](https://storage.simpletex.cn/view/fXGmP4oG2oiTgVG4F3E7qTgDcBkGIxBHS)

Fig. 2.10. Initial tour and feasible 2-opt swap

In terms of worst case performance, Rosenkrantz, Stearns, and Lewis [568] give some partial results.For example,they show (assuming the triangle inequality) that a 2-optimal tour can be almost twice the lengthof an optimal tour. Roughly speaking, a 3-opt procedure requires $n$ times the work that a 2-optprocedure

needs.To obtain close approximations to thelength of the optimal tour using this strategy.one should repeat a 3-opt procedure for a number of starting tours[568]. Computationally，this approach becomes burdensome quickly. We, therefore, consider a class of heuristic methods whichis computationally less expensivebut as accurate as the repeated use of the 3-opt procedure. These are composite procedures.

## 2.3.3 Composite procedures The basic composite procedure can be stated as follows

Step 1. Obtain an initial tour using one of the tour construction procedures

Step 2. Apply a 2-opt procedure to the tour found in Step 1.

Step 3.Apply a 3-opt procedure to the tour found in Step 2.

The composite procedure is relatively fast computationally and gives excellent results The idea behind the composite procedure is toget a good initial solution rapidly and hope

that the 2-opt and 3-opt procedures will then find an almost-optimal solution. In this way, the 3-opt procedure which is the computationally most expensive step of the three, need only be used once. The following are some possible variants of the composite procedure outlined above:

Variant 1.Run the composite procedure without Step 2. Variant 2.Run the composite procedure without Step 3.This variant gives very fast running

times and very accurate results but would not be expected toperform as accurately as the three-step composite procedure Variant 3. Run the composite procedure a few times,using different tour construction

algorithns in Step 1. This variant, although more expensive computationally than the three-step composite procedure, is expected to give better results

Variant 4.In Step 1of the composite procedure,only run the tour construction procedure from a small number of starting nodes.Then perform Steps 2 and3 from the best of these solutions. All of the heuristic algorithms described in this section are intended for symmetric TSP's

(although some can be applied to asymmetric problems as well).Algorithms specifically designed for asymmetric TSP's have been proposed by Akl[4],Frieze et al.[236],Karp[373] Van Der Cruyssen and Rijckaert[659], and Kanellakis and Papadimitriou[370]. We discuss only the firstof these methodshere

### 2.3.4 Akl's directed TSP approach

The procedure described in this section was especially designed for directed (i.e.asymmetric) TSP's by Akl[4] and is closely related to Christofides’heuristic.Before we describe the procedure,we need to define a minimal directed spanning graph (MDSG).An MDSG is a subgraph spanning n nodes of a complete directed graphwith weights $w(i,j)$ ，which has minimum weight and forms a tree when directions are ignored.In other words,when directions are ignored, the graph is aminimal spanning tree with arc lengths $l_{q}=\min\left\{w_{q},w_{q}\right\}$ Given a directed TSP on graph $G$ the algorithm stated below computes a nearly optimal

solution.First,we present the steps briefly and then we comment on them in more detail

------------------------------------------------------------------

Table 2.1. Directed TSP distance matrix

<table>
 <tbody>
  <tr>
   <th> </th>
   <th>1</th>
   <th>2</th>
   <th>3</th>
   <th>4</th>
   <th>5</th>
   <th>6</th>
  </tr>
  <tr>
   <th>1</th>
   <th>0</th>
   <th>7</th>
   <th>65</th>
   <th>68</th>
   <th>34</th>
   <th>81</th>
  </tr>
  <tr>
   <td>2</td>
   <td>19</td>
   <td>0</td>
   <td>22</td>
   <td>27</td>
   <td>59</td>
   <td>29</td>
  </tr>
  <tr>
   <td>3</td>
   <td>14</td>
   <td>43</td>
   <td>0</td>
   <td>62</td>
   <td>77</td>
   <td>65</td>
  </tr>
  <tr>
   <td>4</td>
   <td>76</td>
   <td>53</td>
   <td>64</td>
   <td>0</td>
   <td>6</td>
   <td>51</td>
  </tr>
  <tr>
   <td>5</td>
   <td>39</td>
   <td>58</td>
   <td>38</td>
   <td>27</td>
   <td>0</td>
   <td>13</td>
  </tr>
  <tr>
   <td>6</td>
   <td>46</td>
   <td>67</td>
   <td>27</td>
   <td>11</td>
   <td>39</td>
   <td>TO</td>
  </tr>
 </tbody>
</table>

Procedure

Step 1. Find a MDSG of $G$

Step 2.Add a set of arcs to the MDSG in order to make the directed graph thus obtained Eulerian. Step3.Find an Euler cyclein this directed graph.

Step 4. Transform the Euler cycle into a Hamiltonian cycle.

Step 1 involves solving a minimal spanning tree (MST) on the graph $G$ which is now taken

to be undirected with arc costs $l_{ij}=\min\left\{w_{ij},w_{\bar{\mu}}\right\}$ .If an arc (ij, $j1$ appears in theresulting MSTit is given the direction (i, $j)$ if $I_{ij}=w_{ij}$ and $(i,i)$ if $l_{ij}=w_{i\bar{\mu}^{*}}$ This directed subgraph is an MDSG of G.In Step 2,we identify nodes with excess in-degree as supply points and nodes with excess out-degree as demand points and solve an associated transportation problem in order to balance the graph.Step 3 is straightforward (see Nijenhuis and Wilf[512]). Step 4 is also quite easy: Assume the Euler cycleis $n_{1}-n_{2}-\ldots-n_{l-1}-n_{l}$ where the $n_{i}$ 's are not necessarily distinct nodes.A Hamiltonian cycle can beformedby starting at node $n_1$ ，moving to the right and introducing a node into the Hamiltonian cycle only if it appears for the first time.In order,to generate all Hamiltonian cycles obtainable from the Euler cycle,two copies of the Euler cycle are placed contiguously, $n_{1}-n_{2}-\ldots-n_{l-1}-n_{l}-n_{l}-n_{2}-\ldots-n_{l-l}-n_{l}$ and the method just described is repeated times,every time using the next node in $\{n_1,n_2,\ldots,n_l\}$ as a start node. We now ilustrate theprocedure byquicklyworking through the small example shown in

Table 2.1.Note that in this example,which is taken from Akl[4], the triangle inequality is not preserved.

The results of Steps 1,2 and 4 are displayed in Fig. 2.11-2.13.The length of the resulting tour is 94 units.

![](https://storage.simpletex.cn/view/fLxs53epDIcy26GVnkVOqtdDcx8153WRg)

Fig. 2.12. Directed TSP step 2 Fig. 2.13. Directed TSP step 4

![](https://storage.simpletex.cn/view/fp1PZT0HliGqYVEUqaWUT3x5FUV1KORPW)

Fig. 2.11. Directed TSP step 1.

------------------------------------------------------------------

2.3.5 Heuristic approaches to the time-constrained traveling salesman problem Suppose that cach ordered pair (i $j)$ of nodes has associatedwith it a nct profit anda travel

time.In the time-constrained TSP,the objective is to find a subtour that begins and ends at the origin (node 1),which maximizes proft while requiring less than 7 units of time.This is amuch morerealistic statement of theproblem a traveling salesmanfaces andit has been thefocus of research attention by Cloonan[146], Gensch[264], and, more recentlyGolden et al. [304] In particular, let $p=[p(i,j)]$ be the net profit matrix and $t=[t(i,j)]$ be the time matrix and

let both of these be $N\times N$ We nowpresent an iterative heuristic solution procedure.At each iteration $l$ welet $P$ and $T$ denote the total profit and total time of the subtour just generated Also, $\Delta P$ and $\Delta T$ are the changes in total profit and time associatedwith eachpermissible insertion. Our initial idea was to use the ratio $\Delta P/\Delta T$ as a measure of the attractiveness of an insertion. However, since these changes might be negative, we sought an alternative approach

Procedure TCTSP Step 0. Set I, $P$ and 7 to 0.Initialize $R_{l}$ Choose $a$

Step 1.For each node $i$, compute

$$\Delta T=t(1,\:i)+t(i,\:1),$$

and

$$\Delta P-R_0\Delta T=\{p(1,\:i)+p(i,\:1)\}-R_0\{t(1,\:i)+t(i,\:1)\}.$$

Find the node $i^*$ such that $\Delta T\leq\tau$ and $\Delta P-R_{0}\Delta T$ is maximized.Ifno such node exists,stop Otherwise, form the subtour $1-i^{*}=1$ and record it.Set $P$ to $P+\Delta P$ and $T$ to $T+\Delta T$ Step $2.1\leftarrow1+1$

$$R_{l}=\alpha(P/T)+(1-\alpha)\:R_{l-1}.$$

Step 3. For each node $k$ not in the present subtour and adjacent nodes i and $j$ in the subtour compute
$$\Delta T=t(i,\:k)+t(k,\:j)-t(i,\:j),$$

and

$$\Delta P-R_{i}\Delta T=\{p(i,\:k)+p(k,\:j)-p(i,\:j)\}-R_{i}\{t(i,\:k)+t(k,\:j)-t(i,\:j)\}.$$

Find the i, k, $j$ triple $i^{*}$ ， $k^{*}$ $j^*$ such that $T+\Delta T\leq\tau$ and $\Delta P-R_{l}\Delta T$ is maximized.If no such triple exists, go to Step 5.Otherwise, insert $k^{*}$ between $i^{*}$ and $j^*$ in the subtour andrecord the subtour. Set $P$ to $P+\Delta P$ and $T$ to $T+\Delta T$ Step 4.Go to Step 2.

Step 5.From all the subtours recorded, select the one with the largest $P$

Several points still need clarification. First, the ratio $P/T$ is the worth of a unit of time in the

current subtour. $R_{i}$ is thebest estimate of the worth of a unit of time at iteration $l.$ That is, $R_{i}$ is an estimate which takes into account all previous ratios $P/T$ but weights the more recent ones more heavily. $R_{o}$ should represent an educated guess (possibly based on preliminary analysis） of the profit to time ratio for the optimal subtour.The expression for $R_{l}$ isthe standard exponential smoothing model that is used in a variety of forecasting situations.Finally，in order topromote flexibility and generate a number of heuristic solutions,one may vary $\alpha$ between 0 and I and select different initial values for $R_{0}$ We remark that each application of this insertion procedure requires on the order of $N^{3}$ operations in the worst case. Consider a traditional traveling salesman problem with arc lengths $l(i,j)$ ,in which we seek a

minimum-length Hamiltonian tour over the points. Procedure TCTSP will generate a near optimal solution to the TSP if we set

$$p(i,j)=\tau-l(i,j),\mathrm{~and}$$

$$t(i,\:j)=0\:\mathrm{for}\:\mathrm{all}\:i\:\mathrm{and}\:j,$$

------------------------------------------------------------------

Table 2.2. TCTSP example

![](https://storage.simpletex.cn/view/fSUSauF7GpSOIbxCz3KKq5wRRlbbgokgC)

where $\tau\geq2$ max $\{l(i,j)\}$ . In this case, the heuristic becomes the well-known cheapest-insertion algorithm. The transformation from $l(i,j)$ to $p(i,j)$ ） $j)$ is needed in order to ensure that each node will be included in the subtour obtained. An example of a time-constrained TSP with $\tau=72$ is given in Table 2.2.

If we let $R_{0}=1$ and $\alpha=1$ Procedure TCTSP determines the subtour 1-2-5-4-1 with a total profit of 223 anda total time of 63.The intermediate subtours are 1-2-1 and 1-2-5-1with total profits of 112 and 181 and total travel times of 34 and 46 units. The optimal solution is 134-5-1 with a total profit of 228and a total travel time of 58

### 2.4. SINGLE DEPOT/MULTIPLE VEHICLE ROUTING

2.4.1Introduction

In addition to its practical relevance,which has already been illustrated,the routing and scheduling ofvehicles is an area of importance to operations research theoreticians as well Recent research in this field has provided significant breakthroughs in problem formulations and in the design and analysis of algorithms. These advances have an important bearing on future research in routing and scheduling,as well as in related combinatorial and computational research endeavors. In this section we focus primarily on node routing problems in which demands at nodes

must be satisfied by a feet of vehicles that is domiciled at a central depot.In a later section,we study multi-vehicle arc routing problems.

## 2.4.2 The multiple traveling salesmen problem

The multiple traveling salesmen problem (MTSP) is a generalization of the traveling salesman problem (TSP) that comes closer to accommodating real world problems where there is a need to account for more than one salesman (vehicle).Multiple traveling salesmen problems arise in various scheduling and sequencing applications. For example, this framework could be used to develop the basic route structure for a pickup or delivery service (perhaps a school bus or rural bus service—see Chapter 4).It has already proved to be an appropriate model for the problem of bank messenger scheduling, where a crew of messengers picks up deposits at branch banks and returns them to the central office for processing (see [638]) In the multiple traveling salesmen problem, $M$ salesmen are tovisit the nodesofagivenn

node network in such a way that the total distance traveled by all $M$ salesmen is a minimum Each salesman must travel along a subtour of the nodes,which includes a common depot,and every node except the depot must be visited exactly once by exactly one salesman.The mathematical programming formulation of the (MTSP) displayed below is a natural extension of the assignment-based formulation of the traveling salesman problem.

$$\text{Minimize}\quad\sum_{i=1}^{n}\sum_{j=1}^{n}c_{ij}x_{ij}$$

subject to

$$\left.\sum_{i=1}^{n}x_{ij}=b_{i}=\left\{\begin{matrix}{M}&{\mathrm{if}}&{j=1}\\{1}&{\mathrm{if}}&{j=2,3,\ldots,n}\\\end{matrix}\right.\right.\\\sum_{i=1}^{n}x_{ij}=a_{i}=\left\{\begin{matrix}{M}&{\mathrm{if}}&{i=1}\\{1}&{\mathrm{if}}&{i=2,3,\ldots,n}\\\end{matrix}\right.$$
