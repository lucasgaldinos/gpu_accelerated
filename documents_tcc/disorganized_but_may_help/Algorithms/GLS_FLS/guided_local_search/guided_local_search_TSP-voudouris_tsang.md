### Title

Guided Local Search and Its Application to the Traveling Salesman Problem

Authors: Christos Voudouris Intelligent Systems Research Group, Advanced Research & Technology Dept. BT Laboratories British Telecommunications plc.e United Kingdom e-mail: <chrisv@info.bt.co.uk>

Edward Tsang Department of Computer Science University of Essex United Kingdom. e-mail: <edward@essex.ac.uk>

To appear in European Journal of Operational Research (accepted for publication, March 1998)

### Correspondence Address

Christos Voudouris BT Laboratories MLB 1/PP 12 Martlesham Heath IPSWICH Suffolk IP5 3RE England

Telephone ++441473 605465 Fax ++441473 642459

------------------------------------------------------------------

# Abstract

The Traveling Salesman Problem (TSP) is one of the most famous problems in combinatorial optimization. In this paper, we are going to examine how the techniques of Guided Local Search (GLS) and Fast Local Search (FLS) can be applied to the problem. Guided Local Search sits on top of local search heuristics and has as a main aim to guide these procedures in exploring efficiently and effectively the vast search spaces of combinatorial optimization problems. Guided Local Search can be combined with the neighborhood reduction scheme of Fast Local Search which significantly speeds up the operations of the algorithm.

The combination of GLS and FLS with TSP local search heuristics of different efficiency and effectiveness is studied in an effort to determine the dependence off GLS on the underlying local search heuristic used. Comparisons are made with some of the best TSP heuristic algorithms and general optimization techniques which demonstrate the advantages of GLS over alternative heuristic approaches suggested for the problem.

Keywords: Heuristics, Combinatorial Optimization, Traveling Salesman, Guided Local Search, Tabu Search.

------------------------------------------------------------------

# 1. Introduction

The Traveling Salesman Problem or TSP for short is one of the most famous combinatorial optimization problems. The problem is known to be NP-hard and over the years has been the testing ground for numerous techniques inspired from a variety of sources. Nowadays, TSP plays a very importat role in the development, tsting and demonstration of new optimization techniques. In this context, we are presenting the application to the TSP of a new metaheuristic approach called Guided Local Search (GLS) and its accompanying neighborhood reduction scheme called Fast Local Search (FLS)

Guided Local Search originally proposed by Voudouris and Tsang [47] is a generaloptimizationtechnique suitablefor awiderangeof combinatorial optimization problems. Successful applications of the technique so far include practical problems such as Frequency Allocation [47], Workforce Scheduling [45] and Vehicle Routing [2, 25] and also classic problems such as the Traveling Salesman Problem (TSP), Quadratic Assignment Problem (QAP) and Global Optimization [48]. In this paper, we present the technique to the wider Operations Research audience by explaining its application to the TSP, a widely known problem in the OR community.

Guided Local Search (GLS) belongs to a class of techniques known as Metaheuristics [37, 38,40].Prominent members of this class include Tabu Search [12-18], Simulated Annealing [1, 9, 26, 28], GRASP [10], Genetic Algorithms [8, 19, 39], Scatter Search [13] and others. Metaheuristics aim at enhancing the performance of heuristic methods in solving large and difficult combinatorial optimization problems.

------------------------------------------------------------------

In the case of GLS, the main focus is on the exploitation of problem and search-related information to effectively guide local search heuristics in the vast search spaces of NP-hard optimization problems. This is achieved by augmenting the objective function of the problem to be minimized with a set of penalty terms which are dynamically manipulated during the search process to steer the heuristic to be guided. Higher goals, such as the distribution of the search effort to the areas of the search space acording to the promise of these areas to contain high quality solutions. can be expressed and pursued.

GLS is closely related to the Frequency-Based Memory approaches introduced in Tabu Search [14,18], extending these approaches to take into account the quality of structural parts of the solution and also react to feedback from the local optimization heuristic under guidance.

The paper is structured as follows.We first describe the basics of local search which is the foundation for most metaheuristics. Following that we explain the different components of GLS and how it can be combined with the sister scheme of Fast Local Search particularly suited for speeding up the search of neighborhoods when GLS is used. The rest of the paper is devoted to the application of GLS and FLS to the famous Traveling Salesman Problem when these are combined with commonly used heuristics such as 2-Opt, 3-Opt and Lin-Kernighan.The benefits from using GLS and FLS with these heuristics are demonstrated and the dependence of GLS on them is investigated. Conclusions are drawn on the relation between GLS and the underlying local search procedures. Finally comparisons are conducted with other well knowngeneralorTsP-specificmetaheuristictechniquessuchasSimulated Annealing, Tabu Search, Iterated Lin-Kernighan and Genetic Algorithms. GLS is shown to perform equally well compared with state-of-the-art specialized methods

------------------------------------------------------------------

while outperforming classic variants of well known general optimization techniques

In all cases, publicly available TSP instances are used for which the optimal solutions are known so that the performance of algorithms can be measured with respect to approximating the optimal solutions

# 2.Local Search

Local Search, also referred to as Neighborhood Search or Hill Climbing, is the basis of many heuristic methods for combinatorial optimization problems. In isolation, it is a simple iterative method for finding good approximate solutions. The idea is that of trial and err. For the purposes of explaining local search, we willconsider the following definition of a combinatorial optimization problem.

A combinatorial optimization problem is defined by a pair $( S$, $g;$ , where $S$ is the set of all feasible solutions (i.e. solutions which satisfy the problem constraints) and $g$ is the objective function that maps each element $s$ in $S$ to a real number. The goal is to find the solution $s$ in S that minimizes the objective function $g$ .The problem is stated as:

min g(s), s ES.

In the case where constraints difficult to satisfy are also present, penalty terms may be incorporated in $g(s)$ to drive toward satisfying these constraints. A neighborhood $N$ for the problem instance $( S$, $g)$ can be defined as a mapping from $S$ to its powerset:

$$N\colon S\to2^{S}.$$

$N(s)$ is called the neighbourhood of $s$ and contains all the solutions that can be reached from $S$ by a single move. Here, the meaning of a move is that of an operator which

------------------------------------------------------------------

transforms one solution to another with small modifications.A solution $X$ is called a local minimum of $g$ with respect to the neighborhood $N$ iff:

$$g(x)\leq g(y),\forall y\in N(x)\:.$$

Local search is the procedure of minimizing the cost function $g$ in a number of successive steps in each of which the current solution $X$ is being replaced by a solution y such that:

$$g(y)<g(x),y\in N(x)\:.$$

A basic local search algorithm begins with an arbitrary solution and ends up in a local minimum where no further improvement is possible. In between these stages there are many different ways to conduct local search. For example, best improvemen (greedy) local search replaces the current solution with the solution that improves most in cost after searching the whole neighborhood. Another example is first improvement local search which accepts a better solution when it is found. The computational complexity of a local search procedure depends on the size of the neighborhood and also the time needed to evaluate a move. In general, the larger the neighborhood, the more the time one needs to search it and the better the local minima.

Localminima are the main problem with local search. Although these solutions may be of good quality, they are not necessarily optimal. Furthermore if local search gets caught in a local minimum, there is no obvious way to proceed any further toward solutions of better cost. Metaheuristics are trying to remedy that. One of the first methods in this class is Repeated Local Search where local search is restarted from a new arbitrary solution every time it reaches a local minima until a

------------------------------------------------------------------

number of restarts is completed. The best local minimum found over the many runs is returned as an approximation of the global minimum. Modern metaheuristics tend to be much more sophisticated than repeated local search pursuing a range objectives that go beyond simply escaping from local minima. Also, the way they utilize local search may vary and not limited to applying it to a single solution but to a population of solutions as it is the case in some Hybrid Genetic Algorithms.

## 3.Guided Local Search

Guided Local Search has its root in a Neural Network architecture named GENET developed by Wang and Tsang [49]. GENET is applicable to a class of problems known as Constraint SatisfactionProblems [46]which are closely related to the class of SAT problems. GLS generalizes some of the elements present in the GENET architecture and applies them to the general class of combinatorial optimization problems. For more information on GENET and related techniques for CSP and SAT problems the reader can refer to the following publications [7, 36, 43]

GLS augments the cost function of the problem to include a set of penalty terms and passes this, instead of the original one, for minimization by the local search procedure. Local search is confined by the penalty terms and focuses attention on promising regions of the search space. Iterative calls are made to local search. Each time local search gets caught in a local minimum, the penalties are modified and local search is called again to minimize the modified cost function.

## 3.1 Solution Features

GLS employs solution features to characterize solutions. A solution feature can be any solution property that satisfies the simple constraint that is a non-trivial one. What it is

------------------------------------------------------------------

meant by that is that not all solutions have this property. Some solutions have the property while others do not. Solution features are problem dependent and serve as the interface between the algorithm and a particular application.

Constraints on features are introduced or strengthened on the basis of information about the problem and also the course of local search. Information pertaining to the problem is the cost of features. The cost of features represents the direct or indirect impact of the corresponding solution properties on the solution cost Feature costs may be constant or variable.Information about the search process pertains to the solutions visited by local search and in particular local minima. A feature $f_{i}$ is represented by an indicator function in the following way:

$$I_i(s)=\begin{cases}1,&\text{solution}s\text{has property}i\\0,&\text{otherwise}\end{cases},s\in S.$$

The notion of solution features is very similar to the notion solution atributes used in Tabu Search. The only difference is that features, as considered in here, are always associated with a binary state given by their indicator function. They also have certain properties such as their penalty and cost. The indicator functions of features are directly incorporated in the problem's cost function to produce the augmented cost function. The augmete cot funetion replacestheojetive funetion o the problem during the search process and it is dynamically manipulated by GLS to guide the local optimization algorithm used. In the next paragraph, we explain constrains on features and the augmented cost function.

------------------------------------------------------------------

What composes fi? -indicator fn - a cost penalty -入

## 3.2 Augmented Cost Function

Constraints on features are made possible by augmenting the cost function $g$ of the problem to include a set of penalty terms. The new cost function formed is called the Shouldn't 入 be inside the sum augmented cost function and it is defined as follows: With an index i?

$$
\begin{equation}
h(s) = g(s) +\lambda\sum_{i=1}^{M}p_i\cdot I_i(s)
\label{eq:augmented_cost_function}
\end{equation}
$$

where $M$ is the number of features defined over solutions, $p_i$ is the penalty parametet corresponding to feature $f_{i}$ and $\lambda$ (lambda) a parameter for controlling the strength of constraints with respect to the actual solution cost. The penalty parameter $p_{i}$ gives the degree up to which the solution feature $f_i$ is constrained.The parameter 入represents the relative importance of penalties with respect to the solution cost and it provides a means to control the influence of the information on the search process.We are going to further explain the role of $\lambda$ later in this paper when we refer to the application of the algorithm on the TSP.For an in depth analysis of the role of the parameter $\lambda$ the reader is directed to[48].

GLS iteratively uses local search passing it the augmented cost function for minimization and it simply modifies the penalty vector $p$ given by:

$$p=(p_{1},...,p_{M})$$

each time local search settles in a local minimum. Modifications are made on the basis of information. Initially, all the penalty parameters are set to O (i.e. no features are constrained) and a call is made to local search to find a local minimum of the augmented cost function.After the first local minimum and every other local minimum, the algorithm takes a modification action on the augmented cost function and re-applies local search, starting from the previously found local minimum. The

------------------------------------------------------------------

modification action is that of simply incrementing by one the penalty parameter of one or more of the local minimum features. Prior and historical information is gradually utilized toguide the search process by selecting which penalty parameters to increment. Sources of information are the cost of features and the local minimum itself. Let us assume that each feature $f_{i}$ defined over the solutions is assigned a cost C This cost may be constant or variable. In order to simplify our analysis, we consider feature costs to be constant and given by the cost vectorc:

$$c=(c_{I},...,c_{M})$$

which contains positive or zero elements.

Before explaining the penalty modification scheme in detail, we would like to draw the reader's attention to the meaning of local minima in the context of GLS. The local minima encountered by local search when GLS is used are with respect to the augmented cost function and may be different from the local minima with respect to the original cost function of the problem. Hereafter and whenever we refer to a local minimum in the context of GLS, we mean the former and not the later. Before any penalties are applied, the two are identical but as the search progresses the local minima with respect to the original cost function may not be local minima with respect to the augmented cost function. This allows local search to escape from the local minima of the original cost function since GLS is altering their local minimum status under the augmented cost function using the penalty modification mechanism to be explained next.

But don't I stumble into other local minima,then? Local Minima but for the new cost function with penalies

------------------------------------------------------------------

## 3.3 Penalty Modifications

 The penalty modification mechanism is responsible for manipulating the augmented cost function when local search is trapped in a local minimum. A particular local minimum solution ss exhibits a number of features and the indicators of the features $f_i$ exhibited take the value 1 (i.e. $I_i(s_*)=1$ ). When local search is trapped in $Sr$ , the penalty parameters are incremented by one for all features $f_i$ that maximize the utility expression:

$1+p_i+1,...$ increases while $c_i$ and $I_i$ keep being the same

$$
util\big(s_{*},f_{i}\big)=I_{i}\big(s_{*}\big)\cdot\frac{c_{i}}{1+p_{i}}\:.
$$

In other words, incrementing the penalty parameter of the feature $f_{i}$ is considered an action with utility given by (2). In a local minimum, the actions with maximum utility are selected and then performed. The penalty parameter $p_i$ is incorporated in (2) to prevent the scheme from being totally biased towards penalizing features of high cost

The role of the penalty parameter in (2) is that of a counter which counts how many times a feature has been penalized. If a feature is penalized many times over a number of teraton tete er $\frac{c_i}{1+p_i}$ in 2 deceasesfo te eate disesisin hiees and giving the chance for other features to also be penalized. The policy implemented is that features are penalized with a frequency proportional to their cost. Due to (2), features of high cost are penalized more frequently than those of low cost. The search effort is distributed according to promise as it is expressed by the feature costs and the already visited local minima, since only the features of local minima are penalized.

Depending on the value of $\lambda$ (i.e. strength of penalties) in (1) one or more penalty modification iterations as described above may be required before a move is made out of the local minimum.High values for $\lambda$ make the algorithm more

------------------------------------------------------------------

aggressive escaping quickly out of the local minima encountered while low values for make the algorithm more cautious requiring more penalty increases before an escape is achieved. Low values, although slow down the method in terms of escaping from local minima, lead to a more careful exploration of the search space putting less weight on the penalty part of the augmented cost function $h(s)$ as given by (1).

Another issue to consider is the always increasing penalties for features and what is the impact of that. Actually, as soon as penalties reach the same value for all features in a vicinity of the search space,they tend to cancel out each other.For example, if all the features have their penalties set to 1 this has the same effect as all the features have their penalties set to O. This is because moves look at the cost differences from exchanging certain features with others rather than the actual costs incurred.The basic GLS algorithm as described so far is depicted in Figure 1

```code
procedure GuidedLocalSearch(S, g, lambda, [I_1, ...,I_M], [c_1,...,c_M], M)

begin
  
  k = 0;
  s_0 = random or heuristically generated solution in S;
  
  for i = 1; i=M; do /* set all penalties to 0 */
    p_i = 0;
  
  /* Until here are just initialization steps /*



  while local_minimum do
  begin
    h = g + lambda * sum(p_i *I_i); /* should do another for here? /*
    s_k+1 = LocalSearch(s_k, h); /* finds a solution with a cost
  
    for i=1; i=M; do
      utility = I_i(s_k+1) * c_i / (1+p_i);
    
    for each i such that utility is maximum do /* should do another for here? Is this the right indentation? */
      p_i = p_i + 1;
    
    k = k+1;
  
  end
  s* = best solution found with respect to cost function g;
  return s*;
end
```

where S: search space, g: cost function, h: augmented cost function, : lambda parameter, I: indicator function for feature i, c;: cost for feature i, M: number of features, p.: penalty for feature i.

------------------------------------------------------------------

Applying the GLS algorithm to a problem usually involves defining the features to be used, assigning costs to the them and finally substituting the procedure LocalSearch in the GLS loop with a local search algorithm for the problem in hand

# 3.4Fast Local Search and Other Improvements

There are both minor and major optimizations that significantly improve the basic GLS method. For example, instead of calculating the utilities for all the features, we can restrict ourselves to the local minimum features since for non-local minimum features the utility as given by (2) takes the value 0. Also, the evaluation mechanism for moves needs to be changed to work efficiently on the augmented cost function Usually, this mechanism is not directly evaluating the cost of the new solution generated by themove but it calculates the difference $4g$ caused to the costfunction This difference in cost should be combined with the difference in penalty. This can be easily done and has no significant impact on the time needed to evaluate a move. In particular,we have to take into account only features that change state (being deleted or added). The penalty parameters of the features deleted are summed together. The same is done for the penalty parameters of features added. The change in penalty due to the move is then simply given by the difference:

$$
- \underset{\text{over all features j added}}{\sum p_j} + \underset{\text{over all features k deleted}}{\sum p_k}
$$

Leaving behind the minor improvements, we turn our attention to the major improvements. In fact, these improvements do not directly refer to GLS but to local search. Greedy local search selects the best solution in the whole neighborhood. This can be very time-consuming, especially if we are dealing with large instances of

------------------------------------------------------------------

problems. Next, we are going to present Fast Local Search (FLS),which drastically speeds up the neighborhood search process by redefining it. The method is a generalization of the approximate 2-opt method proposed in[3] for the Traveling Salesman Problem.The method also relates to Candidate List Strategies used in tabu search [14].

FLS works as follows. The current neighborhood is broken down into a number of small sub-neighborhoods and an activation bit is attached to each one of them. The idea is to scan continuously the sub-neighborhoods in a given order. searching only those with the activation bit set to 1. These sub-neighborhoods are called active sub-neighborhoods. Sub-neighborhoods with the bit set to O are callec inactive sub-neighborhoods and they are not being searched. The neighborhood search process does not restart whenever we find a better solution but it continues with the next sub-neighborhood in the given order. This order may be static or dynamic (i.e change as a result of the moves performed)

Initially, all sub-neighborhoods are active. If a sub-neighborhood is examinec and does not contain any improving moves then it becomes inactive. Otherwise, it remains active and the improving move found is performed. Depending on the move performed, a number of other sub-neighborhoods are also activated. In particular, we activate all the sub-neighborhoods where we expect other improving moves to occun as a result of the move just performed. As the solution improves the process dies out with fewer and fewer sub-neighborhoods being active until all the sub-neighborhooc bits turn to O. The solution formed up to that point is returned as an approximate local minimum.

The overall procedure could be many times faster than conventional local search.The bit setting scheme encourages chains of moves that improve specific parts

------------------------------------------------------------------

of the overall solution. As the solution becomes locally better the process is settling down, examining fewer moves and saving enormous amounts of time which woulc otherwise be spent on examining predominantly bad moves.

Although fast local search procedures do not generally find very good solutions,when they are combined with GLS they become very powerful optimization tools. Combining GLS with FLS is straightforward. The key idea is to associate solution features to sub-neighborhoods. The associations to be made are such that for each feature we know which sub-neighborhoods contain moves that have an immediate effect upon the state of the feature (i.e. moves that remove the feature from the solution). The combination of the GLS algorithm with a generic FLS algorithm is depicted in Figure 2.

The procedure GuidedFastLocalSearch in Figure 2 works as follows. Initially all the activation bits are set to 1 and FLS is allowed to reach the first local minimum (i.e. all bits O). Thereafter, and whenever a feature is penalized, the bits of the associated sub-neighborhoods and only those are set to 1. In this way, after the first local minimum, fast local search calls examine only a number of sub-neighborhoods and in particular those which associate to the features just penalized. This dramatically speeds up GLS. Moreover, local search is focusing on removing the penalized features from the solution instead of considering all possible modifications.

------------------------------------------------------------------

procedure GuidedFastLocalSearchS,g[][C.c],ML) begin

$k\leftarrow0$ $S_{0}\leftarrow$ random or heuristically generated solution in S; for $i\leftarrow1$ until M do $p_{i}\leftarrow0$ $I^*$ set all penalties to 0 */ for $i\leftarrow1$ until L dobit $\leftarrow$ 1； $I^*$ set all sub-neighborhoods to the active state $^{\star}/$ while StoppingCriterion da begin
$$h\leftarrow g+\lambda^{\star}\sum p_{i}^{\star}I_{i};$$
$S_{k+1}\leftarrow$ FastLocalSearch(s,h[bit...bit],L) for $i\leftarrow1$ until M do util $\leftarrow I_{i}(\mathbf{s}_{k+1})^{\star}\mathbf{c}_{i}/\left(1+\mathbf{p}_{i}\right)$ for each i such that util is maximum do begin
$$p_{i}\leftarrow p_{i}+1;$$
SetBits $\leftarrow$ SubNeighbourhoodsForFeature(i) $f^*$ activate sub-neighborhoods relating to feature i penalized*/ for each bit b in SetBits do $b\leftarrow1$ end $k\leftarrow k+1$ end $S^{\star}\leftarrow$ best solution found with respect to cost function g return $S^{\star}$ end

procedure FastLocalSeach(s, h, [bit, ...,bit,], L] begin while bit, bit =1 do

for $i\leftarrow1$ until Ldo begin if bit =1 then $I^*$ search sub-neighborhood for improving moves *begin Moves $\leftarrow$ set of moves in sub-neighborhoodi; for each move m in Moves do begin $S^{\prime}\leftarrow$m$(\mathbf{s})$ $f^*$ s' is the solution generated by move m when applied to s $^{*}/$ if $h(\mathbf{s}^{\prime})<h(\mathbf{s})$ then $I^{*}$ for minimization*/ begin
$$\mathrm{bit}_{\mathrm{i}}\leftarrow1;$$
SetBits $\leftarrow$ SubNeighbourhoodsForMove(m) $f^*$ spread activation to other sub-neighborhoods $^{*}/$ for each bit b in SetBits do $b\leftarrow1$ $s\leftarrow s^{\prime}$ goto ImprovingMoveFound end end bit $\leftarrow0;/^*$ noimproving move found */ end ImprovingMoveFound: continue end; return s;

end

where S:search space,g: cost function, h: augmented cost function,:GLS parameter,1: indicato function for feature i,c: cost for feature i,M: number of features,L:number of sub-neighborhoods,P penalty for feature i, bit: activation bit for sub-neighborhood i, SubNeighbourhoodsForFeature(i) procedure which returns the bits of the sub-neighborhoods corresponding to feature i, anc SubNeighbourhoodsForMove(m): procedure which returns the bits of the sub-neighborhoods to spread activation to when move m is performed..

------------------------------------------------------------------

Apart from the combination of GLS with fast local search, other useful variations of GLS include

·features with variable costs where the cost of a feature is calculated during search and in the context of a particular local minimum, ·penalties with limited duration , ·multiple feature sets where each feature set is processed in parallel by a differen penalty modification procedure, and : feature set hierarchies where more important features overshadow less important feature sets in the penalty modification procedure

More information about these variations can be found in [48]. Also for a combination of GLS with Tabu Search the reader may refer to the work by Backer et. al [2]

# 4. Connections with Other General Optimisation Techniques

# 4.1 Simulated Annealing

Non-monotonic temperature reduction schemes used in Simulated Annealing (SA) also referred to as re-annealing or re-heating schemes are of interest in relation to the work presented in this paper. In these schemes, the temperature is decreased as well as increased in a attempt to remedy the problem that the annealing process eventually settles down failing to continuously explore good solutions. In a typical SA,good solutions are mainly visited during the mid and low parts of the cooling schedule. Fon resolving this problem, it has been even suggested annealing at a constant temperature high enough to escape local minima but also low enough to visit them [5]. It is seems extremely difficult to find such a temperature because it has to be landscape

------------------------------------------------------------------

dependent (i.e. instance dependent) if not dependent of the area of the search space currently searched

Guided Local Search presented can be seen as addressing this problem of visiting local minima but also being able to escape from them. Instead of random up-hill moves, penalties are utilized to force local search out of local minima. The amount of penalty applied is progressively increased in units of appropriate magnitude (i.e. parameter $\lambda$ ) until the method escapes from the local minimum. GLS can be seer adapting to the different parts of the landscape. The algorithm is continuously visiting new solutions rather than converging to any particular solution as SA does

Another important difference between this work and SA is that GLS is a deterministic algorithm. This is also the case for a wide number of algorithms developed under the tabu search framework

# 4.2Tabu Search

GLS is directly related to Tabu Search and to some extent can be considered a Tabu Search variant. Solution features are very similar to solution attributes used in Tabu Search. Both Tabu Search and GLS impose constrains on them to guide the underlying local search heuristics.

Tabu Searchin its Short-Term Memory form of Recency-Based Memory is imposing hard constraints on solutions attributes of recently visited solutions or recently performed moves [14, 18]. This prevents local search from returning to recently visited solutions. Local search is not getting trapped in a local minimum given the duration of these constraints is long enough to lead to an area outside the local minimum basin. Variable duration of these constraints is sometimes advantageous allowing Tabu Search to adapt better to the varying radius of the

------------------------------------------------------------------

numerous local minimum basins that could be encountered during the search [44] Nonetheless, there is always the risk of cycling if all the escaping routes require constraint duration longer than those prescribed in the beginning of the search

The approach taken by GLS is not to impose hard constraints but instead to leave local search to settle in a local minimum (of the augmented cost function) before any of the guidance mechanisms are triggered. The purpose of doing that is to allow GLS to explore a number of alternative escape routes from the local minimum basin by first allowing local search to setle in that and consequently applying one or more penalty modification cycles which depending on the structure of the landscape may or may not result in a escaping move.Furthermore the continuous penalization procedure has the effect of progressively “filling up" the local minimum basin present in the original cost function. The risks of cycling are minimized since penalties are not retracted but are permanently marking substantially big areas of the search space that incorporate the specific features penalized. Local minima for the original cost function may not have a local minimum status under the augmented cost function after a number of penalty increases is performed. This allows local search to leave them and start exploring other areas of the search space

Long-Term Memory strategies for diversification used in Tabu Search such as Frequency-Based Memory have many similarities to the GLS penalty modification scheme. Frequency-Based Memory based on solution attributes is increasing the penalties for attributes incorporated in a solution every time this is solution is visited [14, 18]. This leads to a diversification function which guides local search towards attributes not incorporated frequently in solutions

GLS is also increasing the penalties for features though not in every iteration but only in a local minimum. Furthermore not all features have their penalties

------------------------------------------------------------------

increased but a selective penalization is implemented which bases its decisions on the quality of the features (i.e. cost), decisions made by the algorithm in previous iterations (i.e. penalties already applied) and also the current landscape of the problem which may force more than one penalization cycles before a move to a new solution is achieved. If GLS is used in conjunction with FLS, the different escaping directions from the localminimum can be quickly evaluatedallowing the selective diversification of GLS to also direct local search through the moves evaluated and not only through the augmented cost function

In general, GLS can alone perform similar functions to those achieved by the simultaneous use of both Recency-Based and Frequency-Based memory as this is the case in many Tabu Search variants. Other elements like intensification based on elite solution sets may well be incorporated in GLS as in Tabu Search.

Concluding, Tabu Search and GLS share a lot of common ground in both taking the approach of constraining solution attributes (features) to guide a loca search procedure. Tabu Search mechanisms are usually triggered in every iteration and local search is not allowed to settle in a local minimum. GLS mechanism are triggered when local search settles in a local minimum and thereafter until it escapes. Usually Tabu Search uses a Short-Term Memory and a Long-Term Memory component, GLS is not using separate components and it is trying to perform similar functions using a single penalty modification mechanism. There is a lot of promise in investigating hybrids that combine elements from both GLS and Tabu Search in a single scheme For an example, the reader can refer to the work by Backer et. al on the Vehicle Routing Problem [2].

------------------------------------------------------------------

# 5. The Traveling Salesman Problem

In the previous sections, we examined the method of GLS and its generic framework We are now going to examine the application of the method to the well-known Traveling Salesman Problem. There are many variations of the TSP. In this work, we examine the classic symmetric TSP. The problem is defined by $N$ cities and a symmetric distance matrix $D=[d_{ij}]$ which gives the distancebetween any two cities $i$ and $j$ . The goal in TSP is to find a tour (i.e. closed path) which visits each city exactly once and is of minimum length. A tour can be represented as a cyclic permutation $7t$ on the $N$ cities if we interpret $\pi(i)$ to be the city visited after city $i$ ， i= 1 $i=1$ $i=1,...,N$ The cost of a permutation is defined as:

$$g(\pi)=\sum_{i=1}^Nd_{i\pi(i)}$$

and gives the cost function of the TSP

Recent and comprehensive surveys of TSP methods are those by Laporte [29] Reinelt [42] and Johnson & McGeoch [21]. The reader may also refer to [30] for a classical text on the TSP. The state of the art is that problems up to 1,00o.000 cities are within the reach of specialized approximation algorithms [3]. Moreover, the optimal solutions have been found and proven for non-trivial problems of size up to 7397 cities [21]. Nowadays, TSP plays a very important role in the development and testing of new optimization techniques. In this context, we examine how guided local search and fast local search can be applied to this problem.

------------------------------------------------------------------

## 6. Local Search Heuristics for the TSP

Local search for the TSP is synonymous with $k$ -Opt moves. Using $k$ -Opt moves. neighboring solutions can be obtained by deleting $k$ edges from the current tour and reconnecting the resulting paths using $k$ new edges.The $k$ -Opt moves are the basis of the three most famous local search heuristics for the TSP, namely 2-Opt [6],3-Opi [31] and Lin-Kernighan (LK) [32]. These heuristics define neighborhood structures which can be searched by the different neighborhood search schemes described in sections 2 and 3.4, leading to many local optimization algorithms for the TSP. The neighborhood structures defined by 2-Opt, 3-Opt and LK are as follows [20]:

2-Opt.A neighboring solution is obtained from the current solution by deleting two edges, reversing one of the resulting paths and reconnecting the tour (see Figure 3). The worst case complexity for searching the neighborhood defined by 2 Opt is $O(n^2)$

![](https://storage.simpletex.cn/view/f4oKnfhzmq9VIZF5qAknFD9EHVoBoVQfF)

a) 2-Opt move

b) 3-Opt move

c) Non-sequential 4-Opt move

Figure 3.k-Opt moves for the TSP.

3-Opt. In this case, three edges are deleted. The three resulting paths are put together in a new way, possibly reversing one or more of them (see Figure 3). 3-Opt is much more effective than 2-Opt,though the size of the neighborhood (possible 3-Opi

------------------------------------------------------------------

moves)is larger and hence more time-consuming to search.The worst case complexity for searching the neighborhood defined by 3-Opt is $O(n^{3}$,

Lin-Kernighan (LK). One would expect “4-Opt"to be the next step after 3 Opt but actually that is not the case. The reason is that 4-Opt neighbors can be remotely apart because “non-sequential” exchanges such as that shown in Figure 3 are possible for $k\geq4$ .To improve 3-Opt further,Lin and Kernighan developed a sophisticated edge exchange procedure where the number $k$ of edges to be exchanged is variable [32]. The algorithm is mentioned in the literature as the Lin-Kernighan (LK) algorithm and it was considered for many years to be the “uncontested champion” of local search heuristics for the TSP. Lin-Kernighan uses a very complex neighborhood structure which we will briefly describe here.

LK,instead of examining a particular 2-Opt or 3-Opt exchange,is building an exchange of variable size $k$ by sequentially deleting and adding edges to the current tour while maintaining tour feasibility. Given node $t_l$ in tour $T$ as a starting point: In step 177. of this sequential building of the exchange: edge $(t_l,t_{2m})$ is deleted, edge ( $t_{2m}$ $t_{2m+I})$ is added,and then edge $( t_{2m+ I}$, $t_{2m+ 2})$ is picked so that deleting edge $( t_{2m+ I}$, $t_{2m+ 2})$ and joining edge $( t_{2m+ 2}$, $t_{I})$ will close up the tour giving tour $T_{m}$ .The edge $( t_{2m+ 2}$, $t_{I})$ is deleted if and when step $m+l$ is executed. The first three steps of this mechanism are illustrated in Figure 4.

![](https://storage.simpletex.cn/view/fhqFofc3gTR9sdQimXozNOVpp6k29Vihs)

Figure 4. The first three steps of the Lin-Kernighan edge exchange mechanism

------------------------------------------------------------------

As we can see in this figure,the method is essentially executing a sequence of 2-Opt moves. The length of these sequences (i.e. depth of search) is controlled by the LK's gain criterion which limits the number of the sequences examined. In addition to that, limited backtracking is used to examine the sequences that can be generated if a number of different edges are selected for addition at steps 1 and 2 of the process

The neighborhood structure described so far, although it provides the depth needed, is lacking breadth, potentially missing improving 3-Opt moves. To gain breadth, LK temporarily allows tour infeasibility, examining the so-called "infeasibility' moves which consider various choices for nodes $t_4$ to $t_8$ in thesequence generation process, examining all possible 3-Opt moves and more. Figure 5 illustrates the infeasibility-move mechanism

![](https://storage.simpletex.cn/view/feqsCKnDipxUYCtcfsdqUegSindM47erW)

Figure 5. Lin-Kerhighan's infeasibility moves.

The interested reader may refer to the original paper by Lin and Kernighan [32] for a more elaborate description of this mechanism. LK is the standard benchmark against which all heuristic methods are tested. The worst case complexity for searching the LK neighborhood is $O(n^5)$

Implementations of 2-Opt, 3-Opt and LK-based local search methods may vary in performance. A very good reference for efficiently implementing local searcl procedures based on 2-Opt and 3-Opt is that by Bentley [3]. In addition to that Reinelt [42] and also Johnson and McGeoch [21] describe some improvements that

------------------------------------------------------------------

are commonly incorporated in local search algorithms for the TSP. We will refer to some of them later in this paper. The best reference for the LK algorithm is the original paper by Lin and Kernighan [32]. In addition to that, Johnson and McGeoch [21] provide a good insight into the algorithm and its operations along with information on the many variants of the method. A modified LK version which avoids the complex infeasibility moves without significant impact on performance is described in [33]

Fast local search and guided local search can be combined with the neighborhood structures of 2-Opt, 3-Opt and LK with minimal effort. This will become evident in the next sections where fast local search and guided local search for the TSP are presented and discussed

# 6.1 Fast Local Search Applied to the TSP

A fast local search procedure for the TSP using 2-Opt has already been suggested by Bentley [3]. Under the name Don't Look Bits, the same approach has been used in the context of 2-Opt, 3-Opt and LK by Codenotti et al. [4] to reduce the running times of these heuristics in very large TSP instances. More recently, Johnson et al. [24] also use the technique to speed up their LK variant (see [21]). In the following, we are going to describe how fast local search variants of 2-Opt, 3-Opt and LK can be developed on the guidelines for fast local search presented in section 3.4.

2-Opt, 3-Opt and LK-based local search procedures are seeking tour improvements by considering for exchange each individual edge in the current toun and trying to extend this exchange to include one (2-Opt), two (3-Opt) or more (LK)

------------------------------------------------------------------

other edges from the tour. Usually, each city is visited in tour order and one or both the edges adjacent to the city are checked if they can lead to an edge exchange which improves the solution

We can exploit the way local search works on the TSP to partition the neighborhood in sub-neighborhoods as required by fast local search. Each city in the problem may be seen as defining a sub-neighborhood which contains all edge exchanges originating from either one of the edges adjacent to the city. For a problem with $N$ cities, the neighborhood is partitioned into $N$ sub-neighborhoods, one for each city in the instance.Given the sub-neighborhoods,fast local search for the TSP works in the following way (see also 3.4).

Initially all sub-neighborhoods are active. The scanning of the sub neighborhoods, defined by the cities,is done in an arbitrary static order (e.g. from 1st to Nth city). Each time an active sub-neighborhood is found, it is searched for improving moves. This involves trying either edge adjacent to the city as bases for 2- Opt, 3-Opt or LK edge exchanges, depending on the heuristic used. If a subneighborhood does not contain any improving moves then it becomes inactive (i.e.bit is set to O). Otherwise, the first improving move found is performed and the cities (corresponding sub-neighborhoods） at the ends of the edges involved (deleted or added by the move) are activated (i.e. bits are set to 1). This causes the subneighborhood where the move was found to remain active and also a number of other sub-neighborhoods to be activated. The process always continues with the next subneighborhood in the static order.If ever a fullrotation around the static order is completed without making a move, the process terminates and returns the tour found

------------------------------------------------------------------

The tour is declared 2-Optimal, 3-Optimal or LK-Optimal, depending on the type of the $k$ -Opt moves used.

## 6.2 Local Search Procedures for the TSP

Apart from fast local search, first improvement and best improvement local search (see section 2) can also be applied to the TSP. First improvement local search immediately performs improving moves while best improvement (greedy) local search performs the best move found after searching the complete neighborhood.

Fast local search for the TSP described above can be easily converted to first improvement local search by searching all sub-neighborhoods irrespective of their state (active or inactive). The termination criterion remains the same with fast local search: that is, to stop the search when a full rotation of the static order is completec without making a move. The LK algorithm as originally proposed by Lin and Kernighan [32] performs first improvement local search.

Fast local search can also be modified to perform best improvement local search. In this case, the best move is selected and performed after all the subneighborhoods have been exhaustively searched. The algorithm stops when a solution is reached where no improving move can be found. The scheme is very time consuming to be combined with the 3-Opt and LK neighborhood structures and it is mainly intended for use with 2-Opt. Considering the above options, we implementec seven local search variants for the TSP (implementation details will be given later) These variants were derived by combining the different search schemes at the neighborhood level (i.e. fast, first improvement, and best improvement local search) with any of the 2-Opt, 3-Opt, or LK neighborhood structures. Table 1 illustrates the variants and also the names we will use to distinguish them in the rest of the paper

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th>Name</th>
   <th>Local Search Type</th>
   <th>Neighborhood $1Typr$</th>
  </tr>
  <tr>
   <td>BI- 2Opt</td>
   <td>Best Improvement</td>
   <td>$2-Opt$</td>
  </tr>
  <tr>
   <td>FI- 2Opt</td>
   <td>First Improvement</td>
   <td>$2-Opt$</td>
  </tr>
  <tr>
   <td>FLS- 2Opt</td>
   <td>Fast Local Search</td>
   <td>$2-Opt$</td>
  </tr>
  <tr>
   <td>FI- 3Opt</td>
   <td>First Improvement</td>
   <td>$3-Opt$</td>
  </tr>
  <tr>
   <td>$FLS-3Opt$</td>
   <td>Fast Local Search</td>
   <td>$3-Opt$</td>
  </tr>
  <tr>
   <td>$FI-LK$</td>
   <td>First Improvement</td>
   <td>$LK$</td>
  </tr>
  <tr>
   <td>FLS- LK</td>
   <td>Fast Local Search</td>
   <td>$LK$</td>
  </tr>
 </tbody>
</table>

Table 1. Local search procedures implemented for the study of GLS on the TSP

# 7. Guided Local Search Applied to the TSP

## 7.1 Solution Features and Augmented Cost Function

The first step in the process of applying GLS to a problem is to find a set of solution features that are accountable for part of the overall solution cost. For the TSP, a tou includes a number of edges and the solution cost (tour length)is given by the sum of the lengths of the edges in the tour (see (3)).Edges are ideal features for the TSP First, they can be used to define solution properties (a tour either includes an edge or not) and second, they carry a cost equal to the edge length, as this is given by the distance matrix $D=[d_{ij}]$ of the problem.A set of features can be defined by considering all possible undirected edges $e_{ij}$ ( $i=1.N,j=i+1..N$,i$\neq$j ）that may appear in a tour with feature costs given by the edge lengths $d_{ij}$ . Each edge $e_{ij}$ connecting cities $i$ andcity $j$ is attached a penalty $p_{ij}$ initially set to O which is increased by GLS during search.These edge penalties can be arranged in a symmetric penalty matrix $P=[p_{ij}]$ .As mentioned in section 3.2, penalties have to be combined with the problem's cost function to form the augmented cost function which is minimized by local search. This can be done by considering the auxiliary distance matrix:

$$\mathrm{D^{\prime}=D+\lambda{\cdot}P=[d_{ij}+\lambda{\cdot}p_{ij}]\:.}$$

------------------------------------------------------------------

Local search must use $D^{\prime}$ instead of $D$ in move evaluations. GLS modifies $P$ and (through that) $D^{\prime}$ whenever local search reaches a local minimum. The edges penalized in a local minimum are selected according to the utility function (2), which for the TSP takes the form:

$$Util\Big(tour,e_{ij}\Big)=I_{e_{ij}}(tour)\cdot\frac{d_{ij}}{1+p_{ij}},$$

where

$$I_{e_{ij}}\left(tour\right)=\begin{cases}1,&e_{ij}\in tour\\0,&e_{ij}\not\in tour\end{cases}.$$

# 7.2 Combining GLS with TSP Local Search Procedures

GLS as depicted in Figure 1 makes no assumptions about the internal mechanisms of local search and therefore can be combined with any local search algorithm for the problem, no matter how complex this algorithm is.

The TSP local searches of section 6.2 to be integrated with GLS need only to be implemented as procedures which, provided with a starting tour, return a locally optimal tour with respect to the neighborhood considered. The distance matrix used by local search is the auxiliary matrix $D$ 'described in the last section. A reference to the matrix $D$ is still needed to enable the detection of better solutions whenever moves are executed and new solutions are visited. There is no need to keep track of the value of the augmented cost function since local search heuristics make move evaluations using cost differences rather than re-computing the cost function from scratch

Interfacing GLS with fast local searches for the TSP requires a little more effort (see also 3.4). In particular, each time we penalize an edge in GLS,the

------------------------------------------------------------------

sub-neighborhoods corresponding to the cities at the ends of this edge are activatec (i.e. bits set to 1). After the first local minimum, calls to fast local search start by examining only a number of sub-neighborhoods and in particular those which associate to the edges just penalized. Activation may spread to a limited number of other sub-neighborhoods because of the moves performed though, in general, local search quickly settles in a new local minimum. This dramatically speeds up GLS forcing local search to focus on edge exchanges that remove penalized edges instead of evaluating all possible moves

# 7.3How GLSWorks on the TSP

Let us now give an overview of the way GLS works on the TSP. Starting from an arbitrary solution, local search is invoked to find a local minimum. GLS penalizes one or more of the edges appearing in the local minimum, using the utility function (4) to select them. After the penalties have been increased, local search is restarted from the last local minimum to search for a new local minimum. If we are using fast local search then the sub-neighborhoods (i.e. cities) at the ends of the edges penalized need also to be activated. When a new local minimum is found or local search cannot escape from the current local minimum, penalties are increased again and so forth.

The GLS algorithm constantly attempts to remove edges appearing in local minima by penalizing them. The effort invested by GLS to remove an edge depends on the edge length. The longer the edge, the greater the effort put in by GLS. The effect of this effort depends on the parameter $\lambda$ of GLS.A high causes GLS decisions to be in full control of local search, overriding any local gradient information while a low $\lambda$ causes GLS to escape from local minima with great difficulty, requiring many penalty cycles before a move is executed. However, there is

------------------------------------------------------------------

always a range of values for $\lambda$ for which the moves selected aim at the combinec objective to improve the solution (taking into account the gradient) and also remove the penalized edges (taking into account the GLS decisions). If longer edges persist in appearing in solutions despite the penalties, the algorithm will diversify its choices trying to remove shorter edges too.

As the penalties build up for both bad and good edges frequently appearing in local minima, the algorithm starts exploring new regions in the search space, incorporating edges not previously seen and therefore not penalized. The speed of this "continuous"diversification of search is controlled by the parameter .A low $\lambda$ slows down the diversification process, allowing the algorithm to spend more time in the current area before it is forced by the penalties to explore other areas. Conversely,a high $\lambda$ speeds up diversification, at the expense of intensification.

From another viewpoint, GLS realizes a "selective' diversification which pursues many more choices for long edges than short edges by penalizing the former many more times than the later. This selective diversification achieves the goal of distributing the search effort according to prior information as expressed by the edge lengths. Selective diversification is smoothly combined with the goal of intensifying search by setting $\lambda$ to a value low enough to allow the local search gradients to influence the course of local search. Escaping from local minima comes at no expense because of the penalties but alone without the goal of distributing the search effort, as implemented by the selective penalty modification mechanism, is not enough to produce high quality solutions.

------------------------------------------------------------------

# 8. Evaluation of GLS in the TSP

To investigate the behavior of GLS on the TSP, we conducted a series of experiments The results presented in subsequent sections attempt to provide a comprehensive picture of the performance of GLS on the TSP. First, we examine the combination of GLS with 2-Opt, the simplest of the TSP heuristics. The benefits from using fast local search instead of best improvement local search are clearly demonstrated, along with the ability of GLS to find high quality solutions in small to medium size problems These results for GLS are compared with results for Simulated Annealing and Tabu Search when these techniques use the 2-Opt heuristic

From there on, we focus on efficient techniques for the TSP based on GLS The different combinations of GLS with the local search procedures of 6.2 are examined and conclusions are drawn on the relation between GLS and local search Efficient GLS variants are compared with methods based on the Lin-Kernighar algorithm (known to be the best heuristic techniques for the TSP)

# 8.1 Experimental Setting

In the experiments conducted, we used problems from the publicly available library of TSP problems, TSPLIB [41]. Most of the instances included in TSPLIB have already been solved to optimality and they have been used in many papers in the TSF literature.

For each algorithm evaluated, ten runs from different random initial solutions were performed and the various performance measures (solution quality, running time etc.） were averaged. The solution quality was measured by the percentage exces above the best known solution (or optimal solution if known),as given by the formula:

------------------------------------------------------------------

Unless otherwise stated, all experiments were conducted on DEC Alpha 3000/600 machines ( 175 MHz )with algorithms implemented in GNU $C++$

## 8.2 Parameter

The only parameter of GLS which requires tuning is the parameter $\lambda$ .The GLS algorithm performed well for a relatively wide range of values when we tested it on problems from TSPLIB with either one of the 2-Opt, 3-Opt or LK heuristics Experiments showed that GLS is quite tolerant to the choice of $\lambda$ as long as $\lambda$ is equal to a fraction of the average edge length in good solutions (e.g. local minima). These findings were expressed by the following equation for calculating $\lambda$

$$\lambda=a\cdot\frac{g(\text{local minimum})}{N}\:,$$

where g(local minimum) is the cost of a local minimum tour produced by local search (e.g. first local minimum before penalties are applied) and $N$ the number of cities in the instance. Eq. (6) introduces a parameter $a$ which, although instance-dependent results in good GLS performance for values in the more manageable range (O,1] Experimenting with $U$ ,we found that it depends not only on the instance but also on the local search heuristic used. In general, there is an inverse relation between a and local search effectiveness. Not-so-effective local search heuristics such as 2-Opt require higher $a$ values than more effective heuristics such as 3-Opt and LK. This is because the amount of penalty needed to escape from local minima decreases as the effectiveness of the heuristic increases and therefore lower values for $a$ have to be used to allow the local gradients to affect the GLS decisions. For 2-Opt, 3-Opt and

------------------------------------------------------------------

LK, the following ranges for $a$ generated high quality solutions in the TSPLIB problems.

<table>
 <tbody>
  <tr>
   <th>Heuristic</th>
   <th>Suggested T range for c</th>
  </tr>
  <tr>
   <td>$2-Opt$</td>
   <td>$1/8\leq a\leq1/2$</td>
  </tr>
  <tr>
   <td>$3-Opt$</td>
   <td>$1/10\leq a\leq1/4$</td>
  </tr>
  <tr>
   <td>$LK$</td>
   <td>$1/12\leq a\leq1/6$</td>
  </tr>
 </tbody>
</table>

Table 2.Suggested ranges for parameter a when GLS is combined with different TSP heuristics.

The lower bounds of these intervals represent typical values for $a$ that enable GLS to escape from local minima at a tolerable rate. If values less than the lower bounds are used, then GLS requires too many penalty cycles to escape from local minima. In general, the lower bounds depend on the local search heuristic used and also the structure of the landscape (i.e. depth of local minima). On the other hand, the upper boundsgive a good indication of the maximum values for $a$ that can still produce good solutions. If values greater than the upper bounds are used then the algorithm is exhibiting excessive bias towards removing long edges and failing to reach high quality local minima. In general, the upper bounds also depend on the local search heuristic used but they are mainly affected by the quality of the information contained in the feature costs (ie. how accurate is the assumption that long edges are preferable over short edges in the particular instance).

# 8.3Guided Local Search and 2-Opt

In this section,we look into the combination of GLS with the simple 2-Opt heuristic More specifically,we present results for GLS with best improvement 2-Opt local search (BI-2Opt) and fast 2-Opt local search (FLS-2Opt).The set of problems used in the experiments consistedof 28small tomedium sizeTSPs from 48 to318cities all from TSPLIB. The stopping criterion used was a limit on the number of iterations not to be exceeded. An iteration for GLS with BI-2Opt was considered one local search

------------------------------------------------------------------

iteration (i.e. complete search of the neighborhood) and for GLS with FLS-2Opt,a call to fast local search as in Figure 2. The iteration limit for both algorithms was set to 200,000 iterations. In both cases, we tried to provide the GLS variants with plenty of resources in order to reach the maximum of their performance.

The exact value of $\lambda$ used in the runs was manually determined by running a number of test runs and observing the sequence of solutions generated by the algorithm. A well-tuned algorithm generates a smooth sequence of gradually improving solutions. A not so well tuned algorithm either progresses very slowly ( $\lambda$ is lower than it should be) or very quickly finds no more than a handful of good local minima ( $\lambda$ is higher than it should be). The values for $\lambda$ determined in this way were corresponding to values for $U$ around 0.3. Ten runs from different random solutions were performed on each instance included in the set of problems and the various performance measures (excess, running time to reach the best solution etc.） were averaged. The results obtained are presented in Table 3.

Both GLS variants found solutions with cost equal to the optimal cost in the majority of runs. GLS with BI-2Opt failed to find the optimal solutions (as reportec by Reinelt in [41] and also [42]) in only 15 out of the total 280 runs. From another viewpoint, the algorithm was successful in finding the optimal solution in $94.6\%$ of the runs. Ten out of the 14 failures referred to a single instance namely d198 However, the solutions found for d198 were of high quality and on average within $0.08\%$ of optimality

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem</th>
   <th colspan="3">with BI-2Opt CIS</th>
   <th colspan="3">GLS with FLS-2Opt</th>
  </tr>
  <tr>
   <th>optimal runs out of 10</th>
   <th>Mean Excess $(\%)$</th>
   <th>Mean $CPU$ Time (sec)</th>
   <th>optimal runs out of 10</th>
   <th>Mean $\operatorname{Excess}(\%)$</th>
   <th>Mean $CPU$ Time (sec)</th>
  </tr>
  <tr>
   <td>$att48$</td>
   <td>10</td>
   <td>0.0</td>
   <td>0.77</td>
   <td>10</td>
   <td>0.0</td>
   <td>0.4</td>
  </tr>
  <tr>
   <td>eil51</td>
   <td>10</td>
   <td>0.0</td>
   <td>1.62</td>
   <td>10</td>
   <td>0.0</td>
   <td>0.46</td>
  </tr>
  <tr>
   <td>st70</td>
   <td>10</td>
   <td>0.0</td>
   <td>7.68</td>
   <td>10</td>
   <td>0.0</td>
   <td>1.2</td>
  </tr>
  <tr>
   <td>$eil76$</td>
   <td>10</td>
   <td>0.0</td>
   <td>3.83</td>
   <td>10</td>
   <td>0.0</td>
   <td>0.97</td>
  </tr>
  <tr>
   <td>$pr76$</td>
   <td>10</td>
   <td>0.0</td>
   <td>15.1</td>
   <td>10</td>
   <td>0.0</td>
   <td>3.01</td>
  </tr>
  <tr>
   <td>$gr96$</td>
   <td>10</td>
   <td>0.0</td>
   <td>16.48</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.26</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>10</td>
   <td>0.0</td>
   <td>11.27</td>
   <td>10</td>
   <td>0.0</td>
   <td>1.25</td>
  </tr>
  <tr>
   <td>$\operatorname{kroB100}$</td>
   <td>10</td>
   <td>0.0</td>
   <td>16.36</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.46</td>
  </tr>
  <tr>
   <td>kroCl00</td>
   <td>10</td>
   <td>0.0</td>
   <td>12.2</td>
   <td>10</td>
   <td>0.0</td>
   <td>0.74</td>
  </tr>
  <tr>
   <td>kroDl00</td>
   <td>10</td>
   <td>0.0</td>
   <td>12.94</td>
   <td>10</td>
   <td>0.0</td>
   <td>1.78</td>
  </tr>
  <tr>
   <td>kroEl00</td>
   <td>10</td>
   <td>0.0</td>
   <td>35.68</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.46</td>
  </tr>
  <tr>
   <td>$rd100$</td>
   <td>10</td>
   <td>0.0</td>
   <td>10.75</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.74</td>
  </tr>
  <tr>
   <td>eill0l</td>
   <td>10</td>
   <td>0.0</td>
   <td>19.49</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.37</td>
  </tr>
  <tr>
   <td>$\lim105$</td>
   <td>10</td>
   <td>0.0</td>
   <td>17.46</td>
   <td>10</td>
   <td>0.0</td>
   <td>2.06</td>
  </tr>
  <tr>
   <td>ml</td>
   <td>10</td>
   <td>$U.0$</td>
   <td>1/.40</td>
   <td>10</td>
   <td>0.0</td>
   <td>$\angle LLL$</td>
  </tr>
  <tr>
   <td>prl07</td>
   <td>10</td>
   <td>0.0</td>
   <td>150.28</td>
   <td>10</td>
   <td>0.0</td>
   <td>5.41</td>
  </tr>
  <tr>
   <td>$prl24$</td>
   <td>10</td>
   <td>0.0</td>
   <td>22.47</td>
   <td>10</td>
   <td>0.0</td>
   <td>1.56</td>
  </tr>
  <tr>
   <td>bierl27</td>
   <td>10</td>
   <td>0.0</td>
   <td>254.36</td>
   <td>10</td>
   <td>0.0</td>
   <td>24.67</td>
  </tr>
  <tr>
   <td>$prl36$</td>
   <td>9</td>
   <td>0.0009</td>
   <td>416.78</td>
   <td>10</td>
   <td>0.0</td>
   <td>32.16</td>
  </tr>
  <tr>
   <td>$grl37$</td>
   <td>10</td>
   <td>0.0</td>
   <td>66.54</td>
   <td>10</td>
   <td>0.0</td>
   <td>7.82</td>
  </tr>
  <tr>
   <td>prl44</td>
   <td>10</td>
   <td>0.0</td>
   <td>52.84</td>
   <td>10</td>
   <td>0.0</td>
   <td>6.95</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>10</td>
   <td>0.0</td>
   <td>257.06</td>
   <td>10</td>
   <td>0.0</td>
   <td>7.03</td>
  </tr>
  <tr>
   <td>kroB150</td>
   <td>10</td>
   <td>0.0</td>
   <td>289.02</td>
   <td>10</td>
   <td>0.0</td>
   <td>44.85</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>10</td>
   <td>0.0</td>
   <td>74.35</td>
   <td>10</td>
   <td>0.0</td>
   <td>6.9</td>
  </tr>
  <tr>
   <td>ratl95</td>
   <td>8</td>
   <td>0.01</td>
   <td>525.48</td>
   <td>10</td>
   <td>0.0</td>
   <td>55.15</td>
  </tr>
  <tr>
   <td>$d198$</td>
   <td>0</td>
   <td>0.08</td>
   <td>1998.37</td>
   <td>0</td>
   <td>0.05</td>
   <td>353.97</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>10</td>
   <td>0.0</td>
   <td>614.6</td>
   <td>10</td>
   <td>0.0</td>
   <td>50.16</td>
  </tr>
  <tr>
   <td>$\operatorname{kroB200}$</td>
   <td>10</td>
   <td>0.0</td>
   <td>665.3</td>
   <td>10</td>
   <td>0.0</td>
   <td>61.79</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>8</td>
   <td>0.01</td>
   <td>4484.4</td>
   <td>9</td>
   <td>0.005</td>
   <td>346.44</td>
  </tr>
 </tbody>
</table>
Table 3. Performance of 2-Opt based variants of GLS on small to medium size TSP instances

GLS with FLS-2Opt found the optimal solutions in 3 more runs than GLS with BI-2Opt, missing the optimal solution in only 11 out of the 280 runs $(96.07\%$ success rate). In particular, the algorithm missed only once the optimal solution for lin318 but still found no optimal solution for dl98 which proved to be a relatively “hard problemfor bothvariants.GLSusing fast local search was on average ten times faster than GLS using best improvement local search and that without compromising on solution quality. In the worst case (att48), it was two times faster while in the best case (kroAl50) it was thirty seven times faster. Remarkably,GLS with fast local search was ablein most problems to find a solution with cost equal to the optimum

------------------------------------------------------------------

(already known) in less than 10 seconds of CPU time on the DEC Alpha 3000/600 machines used

The results presented in this section clearly demonstrate the ability of GLS even when combined with 2-Opt the simplest of TSP heuristics to find consistently the optimal solutions for small to medium size TSPs. The use of fast local search introduces substantial savings in running times without compromising in solution quality.

# 8.4Comparisonwith General Methods for the TSP

The above performance of GLS is remarkable considering that GLS is not an exact method and that in this case it only used the short-sighted 2-Opt heuristic. Searching the related TSP literature, we could not find any other approximation methods that use only the simple 2-Opt move and consistently find optimal solutions for problems up to 318 cities. Only the Iterated Lin-Kernighan algorithm and its variants [20, 21, 24] share the same consistency in reaching the optimal solutions. These algorithms will be considered later in this chapter.

A meaningful comparison that can be made is between GLS using 2-Opt and other general methods that also use the same heuristic. For that purpose,we implemented simulated annealing [1, 9, 22, 23, 26, 28] and a tabu search variant fo1 the TSP suggested by Knox [27]

# 8.4.1 Simulated Annealing

The Simulated Annealing (SA) algorithm implemented for the TSP was the one described by Johnson in [20] and uses geometric cooling schedules. The algorithn generates random 2-Opt moves. If a move improves the cost of the current solutior

------------------------------------------------------------------

then it is always accepted. Moves that do not improve the cost of the current solution are accepted with probability:

$$e^{\frac{-\Delta}r}$$

where $\Delta$ is the difference in cost due to the move and $T$ is the current temperature. In the final runs, we started the algorithm from a relatively high temperature (arounc $50\%$ of moves were accepted). At each temperature level the algorithm was allowec toperform a constant number of trials to reach equilibrium.After reaching equilibrium, the temperature was multiplied by the cooling rate a which was set to a high value $(a=0.9]$ ).To stop the algorithm,we used the scheme with the counten described in [22]

# 8.4.2 Tabu Search

The tabu search variant implemented was the one proposed by Knox [27] using a combination of tabu restrictions and aspiration level criteria.The method is briefly described in here.

Tabu search performs best improvement local search selecting the best move in the neighborhood but only amongst those not characterized as tabu. Determining the tabu status of a move is very important in tabu search and holds the key for the development of efficient recency-based memory

In this tabu search variant for the TSP, a 2-Opt move is classified as tabu only if both added edges of the exchange are on the tabu list. If one or both of the addec edges are not on the tabu list, then the candidate move is not classified as tabu Updating the tabu list involves placing the deleted edges of the 2-Opt exchanges performed on the list. If the list is full, the oldest elements of the list are replaced by the new deleted edge information.

------------------------------------------------------------------

In order for a 2-Opt exchange to override tabu status, both added edges of the exchange must pass the aspiration test. An individual edge passes the aspiration test if the new tour resulting from the candidate exchange is better than the aspiration values associated with the edge. The aspiration values of edges are the tour cost which exists prior to making the candidate 2-Opt move. Only edges deleted by the exchanges performed have their values updated.

For the experiments reported here, the tabu list size was set to $3N$ (where $N$ is the number of cities in the problem) as suggested by Knox [27]. Tabu search was allowed to run for 20o,000 iterations which is equivalent in terms of number of moves evaluated to the number of iterations GLS with BI-2Opt was given on the same instances.

# 8.4.3 Simulated Annealing and Tabu Search Compared with GLS

Simulated annealing and tabu search were tested on 8 instances from the greater set of 28 instances mentioned above. The results were averaged as with GLS. Table 4 illustrates the results for simulated annealing and tabu search compared with those for GLS with FLS-2Opt on the same instances.Results are also contrasted with the best solution found by repeating BI-2Opt starting from random tours until a total of 200,000 local search iterations were completed

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem Name</th>
   <th colspan="2">GLS with FLS-2Opt</th>
   <th colspan="2">Simulated Annealing</th>
   <th>Tabu Sea</th>
   <th>$\iota rch$</th>
   <th colspan="2">RepeatedBI- 2Opt (200,000 iterations)</th>
  </tr>
  <tr>
   <th>Mean Excess $(\%)$</th>
   <th>Mean $CPU$ Time (sec)</th>
   <th>Mean Excess $(\%)$</th>
   <th>Mean $CPU$ Time (sec)</th>
   <th>Mean Excess $(\%)$</th>
   <th>Mean $CPU$ Time (sec)</th>
   <th>Mean Excess $(\mathbb{C}_0)$</th>
   <th>Mean $CPU$ Time (sec)</th>
  </tr>
  <tr>
   <td>eil51</td>
   <td>0.0</td>
   <td>0.46</td>
   <td>0.73</td>
   <td>6.34</td>
   <td>0.0</td>
   <td>1.14</td>
   <td>0.23</td>
   <td>42.4</td>
  </tr>
  <tr>
   <td>eil76</td>
   <td>0.0</td>
   <td>0.97</td>
   <td>1.21</td>
   <td>18.0</td>
   <td>0.0</td>
   <td>5.24</td>
   <td>1.85</td>
   <td>153.45</td>
  </tr>
  <tr>
   <td>eill0l</td>
   <td>0.0</td>
   <td>2.37</td>
   <td>1.76</td>
   <td>33.29</td>
   <td>0.0</td>
   <td>61.41</td>
   <td>3.97</td>
   <td>319.15</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>0.0</td>
   <td>1.25</td>
   <td>0.42</td>
   <td>37.36</td>
   <td>0.0</td>
   <td>21.34</td>
   <td>0.34</td>
   <td>706.35</td>
  </tr>
  <tr>
   <td>kroCl00</td>
   <td>0.0</td>
   <td>0.74</td>
   <td>0.80</td>
   <td>36.58</td>
   <td>0.25</td>
   <td>4.80</td>
   <td>0.33</td>
   <td>1301.98</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>0.0</td>
   <td>7.03</td>
   <td>1.86</td>
   <td>103.32</td>
   <td>0.03</td>
   <td>413.06</td>
   <td>1.41</td>
   <td>3290.95</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>0.0</td>
   <td>50.16</td>
   <td>1.04</td>
   <td>229.38</td>
   <td>0.72</td>
   <td>776.93</td>
   <td>1.7</td>
   <td>731.1</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>0.005</td>
   <td>346.44</td>
   <td>1.34</td>
   <td>829.46</td>
   <td>1.31</td>
   <td>2672.80</td>
   <td>3.11</td>
   <td>9771.28</td>
  </tr>
 </tbody>
</table>

Table 4. GLS, Simulated Annealing, and Tabu Search performance on TSPLIB instances

As we can see in Table 4, the superiority of GLS over the tabu search variant and simulated annealing is evident.The tabu searchvariant found easily the optimal solutions for small problems and it scaled well for larger problems. However, it was many times slower than GLS and moreover failed to reach the solution quality of GLS in the larger problems. Simulated annealing had a consistent behavior finding good solutions for all problems but failed to reach the optimal solutions in all but 3 runs. All three meta-heuristics significantly improved over the performance of repeated 2-Opt.

## 8.5 Efficient GLS Variants for the TSP

In order to study the combinations of GLS with higher order heuristics such as 3-Opt and LK,a library of TSP local search procedures was developed in $C++$ .The library comprises all local search procedures of 6.2 and allows combinations of GLS with any one of these procedures. Furthermore, a number of approximations (not used in the GLS of section 8.3) are adopted which further reduce the computation times of local search and GLS as reported in section 8.3. In the rest of the chapter, we will examine and report results fortheseefficient variants of GLS.

------------------------------------------------------------------

The most significant approximation introduced is the use of a pre-processing stage which finds and sorts by distance the 20 nearest neighbors of each city in the instance. 2-Opt, 3-Opt and LK were considering in exchanges only edges to these 20 nearest neighbors (see also [21, 42]). Each time the penalty was increased for an edge the nearest neighbor lists of the cities at the ends of the edge were reordered though no new neighbors were introduced.

To reduce the computation times required by 3-Opt, 3-Opt was implementec as two locality searches each of which looks for a “short enough" edge to extend further the exchange (see [3] for details). The LK implementation was exactly as proposed by Lin and Kernighan [32] incorporating their lookahead and backtracking suggestions (i.e. backtracking at the first two levels of the sequence generation considering at each step only the five smallest and available candidate edges that can be added to the tour and taking into account in the selection of the edges to be addec the length of the edges to be deleted by these additions)

The library is portable to most UNIX machines though experiments reported in here were solely performed on DEC Alpha workstations 3000/600 (175 MHz) using a library executable generated by the GNU $C++$ compiler.

The set of problems used in the evaluation of the GLS variants included 20 problems from 48 to 1002 cities all from TSPLIB. For each variant tested, 10 runs were performed and 5 minutes of CPU time were allocated to each algorithm in each run. To measure the success of the variants, we considered the percentage excess above the optimal solution as in (5). The normalized lambda parameter a was provided as input to the program and $\lambda$ was determined after the first local minimum using (6). For GLS variants using 2-Opt, $a$ was set to $a=1/6$ while the GLS variants based on 3-Opt used the slightly lower value $a=1/8$ and the LK variants the ever

------------------------------------------------------------------

lower value $a=1/10$ .The full set of results for the various combinations of GLS with local search can be found in the Appendix. Next, we focus on selected results from this set.

## 8.5.1 Results for GLS with First Improvement Local Search

Figure 6 graphically illustrates the results for the first improvement versions of 2-Opt, 3-Opt and LK when combined with GLS. In this figure, we see that the combination of GLS with FI-3Opt and FI-LK significantly improves over the performance of GLS with FI-2Opt especially when applied to large problems.FI-LK combined with GLS achieved the best performance amongst the three methods tested.

![](https://storage.simpletex.cn/view/feCQHPhxM2f9Ehac5TMcBrcnKenzp5dyE)

Figure 6.Performance of GLS variants using first improvement local search procedures.

------------------------------------------------------------------

![](https://storage.simpletex.cn/view/fuuSXVw6kZsZ4oOFOLsKXbZKCpmVxNewN)

Figure 7. Performance of GLS variants using fast local search procedures.

## 8.5.2 Results for GLS with Fast Local Search

Figure 7graphically illustrates the results obtained for GLS when combined with the fast local search variants of 2-Opt, 3-Opt and LK. GLS with FI-LK (found to be best amongst the first improvement versions of GLS) is also displayed in the figure as a point of reference.In this figure,we can see that the fast local search variants of GLS aremuchbetter than the best of the first improvement localsearch variants (i.e. GLS-FI-LK).Another far more important observation is that for fast local search the 2-Opt variant is better than the 3-Opt variant which in turn is better than the LK variant. This is exactly the opposite order than one would have expected. One possible explanation can be derived by considering the strength of GLS. More specifically, FLS-2Opt allows GLS to perform many more penalty cycles in the time given than its FLS-3Opt or FLS-LK counterparts.More GLS penalty cycles seem to increase

------------------------------------------------------------------

efficiency at a level which outweighs the benefits from using a more sophisticated local search procedure such as 3-Opt or LK.

The remarkable effects of GLS on local search are further demonstrated in Figure 8 where GLS with FLS-2Opt is compared against Repeated FLS-2Opt and Repeated FI-LK. In Repeated FLS-2Opt and Repeated FI-LK,local search is simply restarted from a random solution after a local minimum and the best solution found over the many runs is returned. These two algorithms along with other versions of repeated local search were tested under the same settings with the GLS variants. The Appendix includes the full set of results for repeated local search. In Figure 8,we can see the huge improvement in the basic 2-Opt heuristic when this is combined with GLS.GLS is the only technique known to us which when applied to 2-Opt can outperform the Repeated LK algorithm (and that without requiring excessive amounts of CPU time) as illustrated in the same figure.

![](https://storage.simpletex.cn/view/f7uaKP4ZVgsyl4KgveiwkzFugXlgD4zft)

------------------------------------------------------------------

# 8.6 Comparison with Specialised TSP algorithms

# 8.6.1 Iterated Lin-Kernighan

The Iterated Lin-Kernighan algorithm (not to be confused with Repeated LK) has been proposed by Johnson [20] and it is considered to be one of the best if not the best heuristic algorithm for the TSP [21]. Iterated LK uses LK to obtain a first local minimum. To improve this local minimum, the algorithm examines other local minimum tours “near” the current local minimum. To generate these tours, Iterated LK first applies a random and unbiased non-sequential 4-Opt exchange (see Figure 3) to the current local minimum and then optimizes this 4-Opt neighbor using the LK algorithm. If the tour obtained by the process (i.e. random 4-Opt followed by LK) is better than the current local minimum then Iterated LK makes this tour the current local minimum and continues from there using the same neighbor generation process Otherwise, the current local minimum remains as it is and further random 4-Opt moves are tried. The algorithm stops when a stopping criterion based either on the number of iterations or computation time is satisfied. Figure 9 contains the origina description of the algorithm as given in [20]

1. Generate a random tour T

2. Do the following for some prespecified number $M$ of iterations:

 2.1. Perform an (unbiased) random 4-Opt move on $T$ , obtaining $T$ 2.2. Run Lin-Kernighan on 7 , obtaining $T^{\prime\prime}$ 2.3. If length $(T^{\prime})\leq$ length $T^{\prime})$ ,set $T=T^{\prime\prime}$

3. Return $T$

Figure 9.Iterated Lin-Kernighan as described by Johnson in [20]

------------------------------------------------------------------

The random 4-Opt exchange performed by Iterated LK is mentioned in the literature as the “double-bridge”move and plays a diversification role for the search process, trying to propel the algorithm to a different area of the search space preserving at the same time large parts of the structure of the current local minimum Martin et al. [35] describe this action as a “kick" and show that can be also used with 3-Opt in the place of LK. The same authors also suggest the combination of the method with Simulated Annealing (Long Markov Chains method). Martin and Otto [34] further demonstrate the efficiency of this last algorithm on the TSP and also the Graph Partitioning problem though they admit that simulated annealing does not significantly improve the method for TSP problems up to 783 cities.Finally, Johnson and McGeoch [21] review Iterated LK and its variants and provide results for both structured and random TSP instances

Iterated LK or Iterated 3-Opt share some of the principles of GLS in the sense that they produce a sequence of diversified local minima though this is conducted in a random rather than a systematic way. Furthermore,iterated local search accepts the new solution, produced by the 4-Opt exchange and the subsequent LK or 3-Opt optimization, only if it improves over the current local minimum (or it is slightly worse in the case of Large Markov Chains Method which uses simulated annealing).

Iterated LK outperforms Repeated LK previously thought to be the "champion" of TSP heuristics and also long simulated annealing runs [34]. More recent experiments show that even sophisticated tabu search variants of LK cannot improve over Iterated LK [50] which rightly deserves the title of the “champion” of TSP meta-heuristics.

------------------------------------------------------------------

To compare Iterated LK and its other variants such as Iterated 3-Opt with GLS, we extended our $C++$ library mentioned above to allow the iteratedlocal search scheme to be combined with the local search procedures of Table 1 included in the library. In particular,a random and unbiased Double-Bridge (DB) move was performed in a local minimum. The solution obtained was optimized by either one of the procedures of Table 1 before compared against the current local minimum. The new solution was accepted only if it improved over the current local minimum. To combine iterated local search with fast local search procedures, we activated the subneighborhoods corresponding to the cities at the ends of the edges involved in the Double-Bridge move (see also [4]). The above extensions to the library made available a general meta-heuristic method applicable to all the local search procedures of Table 1. We will refer to this method as the Double-Bridge (DB) meta-heuristic

We tested all the possible combinations of the DB meta-heuristic with the local searches of Table 1 (except for BI-2Opt) on the set of 20 problems used to test the GLS combinations. The same time limit (5 minutes of CPU time on DEC Alpha 3000/600 machines) was used and ten runs were performed on each instance in the set. The percentage excess was averaged in each problem for each DB variant. The best combination proved to be that of the DB heuristic with FLS-LK which outperformed DB with FI-LK (this last algorithm is similar to the original method proposed by Johnson [20]). The results for the various combinations of DB with local search are included in the Appendix

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th rowspan="2">$\mathbf{Problem}$</th>
   <th colspan="4">Mean Excess $(\%)$ over 10 runs</th>
  </tr>
  <tr>
   <th>GLS with FLS-2Opt</th>
   <th>$|DB~with~FLS-LK$</th>
   <th>$DB$ with FI-LK</th>
   <th>Repeated FI-LK</th>
  </tr>
  <tr>
   <td>$att48$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>eil76</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0 1</td>
  </tr>
  <tr>
   <td>$bier127$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0.0301</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0.00226</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0 1</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0.02452</td>
  </tr>
  <tr>
   <td>$gr202$</td>
   <td>0</td>
   <td>0</td>
   <td>0.00921</td>
   <td>0.14143</td>
  </tr>
  <tr>
   <td>$gr229$</td>
   <td>0.00431</td>
   <td>0.00475</td>
   <td>0.01412</td>
   <td>0.0977</td>
  </tr>
  <tr>
   <td>$gil262$</td>
   <td>0.00421</td>
   <td>0</td>
   <td>0.01682</td>
   <td>0.05467</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>0.02641</td>
   <td>0.24079</td>
   <td>0.25578</td>
   <td>0.62957</td>
  </tr>
  <tr>
   <td>$gr431$</td>
   <td>0.02392</td>
   <td>0.22239</td>
   <td>0.3327</td>
   <td>0.67964</td>
  </tr>
  <tr>
   <td>pcb442</td>
   <td>0.04431</td>
   <td>0.08173</td>
   <td>0.06637</td>
   <td>0.48525</td>
  </tr>
  <tr>
   <td>$att532$</td>
   <td>0.08994</td>
   <td>0.08163</td>
   <td>0.22502</td>
   <td>0.53023</td>
  </tr>
  <tr>
   <td>$u574$</td>
   <td>0.14144</td>
   <td>0.0924</td>
   <td>0.11435</td>
   <td>0.73838</td>
  </tr>
  <tr>
   <td>$rat575$</td>
   <td>0.09892</td>
   <td>0.09745</td>
   <td>0.13731</td>
   <td>0.80762</td>
  </tr>
  <tr>
   <td>$gr666$</td>
   <td>0.20628</td>
   <td>0.17587</td>
   <td>0.41888</td>
   <td>0.83762</td>
  </tr>
  <tr>
   <td>$u724$</td>
   <td>0.16822</td>
   <td>0.16655</td>
   <td>0.35696</td>
   <td>0.93367</td>
  </tr>
  <tr>
   <td>$rat783$</td>
   <td>0.16125</td>
   <td>0.15331</td>
   <td>0.24075</td>
   <td>1.00045</td>
  </tr>
  <tr>
   <td>prl002</td>
   <td>0.62063</td>
   <td>0.44633</td>
   <td>1.04742</td>
   <td>1.5046</td>
  </tr>
  <tr>
   <td>Average Excess</td>
   <td>0.07949</td>
   <td>0.08816</td>
   <td>0.16178</td>
   <td>0.42488</td>
  </tr>
 </tbody>
</table>
Table 5. GLS with FLS-2Opt compared with variants of Iterated Lin-Kernighan.

Table 5 presents the results obtained for DB with FLS-LK and DB with FI-LK compared with those for GLS with FLS-2Opt found to be the best GLS variant.As a point of reference, we also provide results for FI-LK when repeated from random starting points and for the same amount of time.As we can see in Table 5, GLS with FLS-2Opt is better on average than both DB with FLS-LK and DB with FI-LK. The solution quality improvement over these methods although small it is very significant. given that these methods are amongst the best heuristic techniques for the TSP. Note here that GLS with FLS-2Opt is by far a simpler method requiring only a fraction of the programming effort required to develop the DB variants based on LK.

To further test GLS against the DB variants of LK, we used a set of 66 TSPLIB problems from 48 to 2392 cities but this time we performed longer runs lasting 30 minutes of CPU time each.Because of the large number of instances used

------------------------------------------------------------------

and the long time the algorithms were allowed to run, one run was performed on each instance.The results from the experiments are presented in Table 6.

Even in these longer runs, GLS with FLS-2Opt still finds better solutions than the DB variants of LK. This result is of great significance since it further supports our claim that the application of GLS on FLS-2Opt successfully converted the method to a powerful algorithm. As we can see in Table 6, the method is able to compete and even outperform highly specialized heuristic methods for the TSP.

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem</th>
   <th>GLS with $FLS-2Opt$</th>
   <th>DB with $FLS-LK$</th>
   <th>DB with Fl. $|LK$</th>
   <th rowspan="2">Problem</th>
   <th>GLS with $FLS-2Opt$</th>
   <th>DB with $FLS-LK$</th>
   <th>DB with $FI-LK$</th>
  </tr>
  <tr>
   <th>Excess (96)</th>
   <th colspan="2">cess $(96)in$ one TIT r per instance</th>
   <th colspan="3">Excess (%) in one run per instance</th>
  </tr>
  <tr>
   <td>$att48$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pr264</td>
   <td>0</td>
   <td>0</td>
   <td> </td>
  </tr>
  <tr>
   <td>eil51</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pr299</td>
   <td>0</td>
   <td>0</td>
   <td> </td>
  </tr>
  <tr>
   <td>st70</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$lin318$</td>
   <td>0</td>
   <td>0.27124</td>
   <td> </td>
  </tr>
  <tr>
   <td>$eil76$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$f1417$</td>
   <td>0.00843</td>
   <td>0.00843</td>
   <td>0.42998</td>
  </tr>
  <tr>
   <td>$pr76$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$qr431$</td>
   <td>0</td>
   <td>0</td>
   <td>0.01458</td>
  </tr>
  <tr>
   <td>$qr96$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$pr439$</td>
   <td>0.00653</td>
   <td>0.04104</td>
   <td> </td>
  </tr>
  <tr>
   <td>rat99</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pcb442</td>
   <td>0.01182</td>
   <td>0</td>
   <td> </td>
  </tr>
  <tr>
   <td>kroA100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$d493$</td>
   <td>0.02</td>
   <td>0.00857</td>
   <td>0.09142</td>
  </tr>
  <tr>
   <td>kroB100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>att532</td>
   <td>0.06501</td>
   <td>0</td>
   <td>0.04690</td>
  </tr>
  <tr>
   <td>kroC100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$ali535$</td>
   <td>0.02323</td>
   <td>0.01433</td>
   <td>0.01433</td>
  </tr>
  <tr>
   <td>kroD100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$u574$</td>
   <td>0</td>
   <td>0.08129</td>
   <td>0.10568</td>
  </tr>
  <tr>
   <td>kroE100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>rat575</td>
   <td>0.04429</td>
   <td>0.08859</td>
   <td>0.05906</td>
  </tr>
  <tr>
   <td>rd100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$p654$</td>
   <td>2.04659</td>
   <td>2.27174</td>
   <td>0.04619</td>
  </tr>
  <tr>
   <td>eil101</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$d657$</td>
   <td>0.0184</td>
   <td>0.0368</td>
   <td>0.13289</td>
  </tr>
  <tr>
   <td>$\lim105$</td>
   <td>0</td>
   <td>1. 1</td>
   <td>0</td>
   <td>$gr666$</td>
   <td>0.00612</td>
   <td>0.09988</td>
   <td>0.20315</td>
  </tr>
  <tr>
   <td>pr107</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$u724$</td>
   <td>0.05727</td>
   <td>0.09783</td>
   <td>0.04534</td>
  </tr>
  <tr>
   <td>WIL</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>U/24</td>
   <td>U.US/2/</td>
   <td>M n</td>
   <td> </td>
  </tr>
  <tr>
   <td>$pr124$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>rat783</td>
   <td>0</td>
   <td>0.06814</td>
   <td>0.01130</td>
  </tr>
  <tr>
   <td>UIIZA</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>100 T</td>
   <td> </td>
   <td>Jopo $\|A_{1}\|$</td>
   <td> </td>
  </tr>
  <tr>
   <td>bier127</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>dsj1000</td>
   <td>0.31222</td>
   <td>0.40289</td>
   <td>0.88742</td>
  </tr>
  <tr>
   <td>DIeriz ne</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>JSTUU TI</td>
   <td>1.3124</td>
   <td>1 1 T</td>
   <td> </td>
  </tr>
  <tr>
   <td>pr136</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pr1002</td>
   <td>0.12315</td>
   <td>0.07566</td>
   <td>0.11658</td>
  </tr>
  <tr>
   <td>prloo</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>MIUUL</td>
   <td>$\mathbf{U},\mathbf{I}_{\mathbf{Z}\mathbf{D}}\mathbf{I}$ 1</td>
   <td> </td>
   <td> </td>
  </tr>
  <tr>
   <td>$qr137$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>u1060</td>
   <td>0.05132</td>
   <td>0.15663</td>
   <td>0.43285</td>
  </tr>
  <tr>
   <td>W</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>IUbu</td>
   <td>U.U5I32</td>
   <td>1.15 TA</td>
   <td> </td>
  </tr>
  <tr>
   <td>$pr144$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pcb1173</td>
   <td>0.14765</td>
   <td>0.02461</td>
   <td>0.43767</td>
  </tr>
  <tr>
   <td>UITH</td>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>111</td>
   <td>.141 $\int_{a}$</td>
   <td> </td>
   <td> </td>
  </tr>
  <tr>
   <td>kroA150</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>d1291</td>
   <td>0.22244</td>
   <td>0.63581</td>
   <td>1.16139</td>
  </tr>
  <tr>
   <td>kroB150</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$r11304$</td>
   <td>0.20241</td>
   <td>0</td>
   <td>0.50360</td>
  </tr>
  <tr>
   <td>$pr152$</td>
   <td>0.18458</td>
   <td>0</td>
   <td>0</td>
   <td>r11323</td>
   <td>0.18542</td>
   <td>0.14027</td>
   <td>0.22909</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$f11400$</td>
   <td>1.56009</td>
   <td>2.58359</td>
   <td>3.11025</td>
  </tr>
  <tr>
   <td>rat195</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>u1432</td>
   <td>0.05295</td>
   <td>0.27783</td>
   <td>0.30464</td>
  </tr>
  <tr>
   <td>$d19B$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$d1655$</td>
   <td>0.40722</td>
   <td>0.27846</td>
   <td>1.19753</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>vm1748</td>
   <td>0.33219</td>
   <td>0.32387</td>
   <td>0.75678</td>
  </tr>
  <tr>
   <td>kroB200</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>u1817</td>
   <td>0.57517</td>
   <td>0.3916</td>
   <td>1.02096</td>
  </tr>
  <tr>
   <td>$qr202$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$r11889$</td>
   <td>0.37279</td>
   <td>0.90953</td>
   <td>0.52443</td>
  </tr>
  <tr>
   <td>pr226</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>$u2152$</td>
   <td>0.61476</td>
   <td>0.46379</td>
   <td>0.75327</td>
  </tr>
  <tr>
   <td>qr229</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>u2319</td>
   <td>0.00726</td>
   <td>0.25229</td>
   <td>0.28729</td>
  </tr>
  <tr>
   <td rowspan="3">$gil262$</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>pr2392</td>
   <td>0.35209</td>
   <td>0.27458</td>
   <td>0.90019</td>
  </tr>
  <tr>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>Mean</td>
   <td>0.12138</td>
   <td>0.15575</td>
   <td>0.20947</td>
  </tr>
  <tr>
   <td> </td>
   <td> </td>
   <td> </td>
   <td>Standard Deviation</td>
   <td>0.33047</td>
   <td>0.43627</td>
   <td>0.47290</td>
  </tr>
 </tbody>
</table>
Table 6.GLS with FLS-2Opt compared with variants of Iterated Lin-Kernighan (long runs).

The relative gains from the GLS and also DB meta-heuristic are further illustrated in Figure 10. In this figure,we give the absolute improvement in average

------------------------------------------------------------------

solution quality (i.e.excess above the optimal solution) by the GLS and DB variants over the corresponding repeated local search variants in the set of 20 problems from TSPLIB.

![](https://storage.simpletex.cn/view/fUpEcZUEkTHrGW2GUSzZ1D5GbZO9X1a0C)

Figure10.Improvements in solution quality by the GLS andDB meta-heuristics in a set of 20 TSPLIB problems.

As shown in Figure 10, the DB meta-heuristic is more effective than GLS when combined with LK. In fact, GLS when combined with FI-LK is even worse than Repeated FI-LK. This situation dramatically changes for fast local search variants where GLS is better than DB when combined with the FLS-3Opt or FLS-2Opt local searchesimproving the solution quality over repeated local search up to $5.14\%$ in the case of FLS-2Opt. The overall ranking of all the variants developed in terms of average excess in the set of 20 TSPLIB problems is given Figure 11. GLS with FLS- 2Opt was found to be best amongst the18 algorithms tested.

------------------------------------------------------------------

![](https://storage.simpletex.cn/view/fxGr1FqPasX515GsFGNfS9NdosLw4B5f5)

Figure 11. Overall ranking of the algorithms in terms of solution quality when tested on a set of 20 TSPLIB problems

## 8.6.2Genetic Local Search

In an effort to further improve the LK heuristic, Genetic Algorithms recently appearec which internally use LK for improving offspring solutions generated by crossover operations.An example of such a technique is the GeneticLocalSearch algorithm proposed by Freisleben and Merz [11]. This method, in addition to using LK for improving offspring solutions, uses a mutation operator which performs first an 4-Opt exchange on a population solution and then runs LK to convert this solution to a local minimum.Iterated LK mentioned above can be seen as a special case of this method. In [11], results are reported for Genetic Local Search on TSPLIB instances. The authors consider the results produced by the technique as superior to those publishec

------------------------------------------------------------------

for any GA approaches known to them and comparable to top quality non-GA heuristic techniques. Fortunately, the experiments in [11] were also conducted on a DEC Alpha workstation running at 175 MHz. This permits a meaningful comparison between this GA variant and GLS. We ran GLS-FLS-2Opt on the same instances with $a=1/6$ and for an equal number of times as the GA approach. In Table 7, the results from [11] are compared with those we obtained for GLS using FLS-2Opt.

<table>
 <tbody>
  <tr>
   <th rowspan="2">$\mathbf{Problem}$</th>
   <th colspan="2">GLS with FLS-20pt</th>
   <th colspan="2">Genetic Local Search</th>
  </tr>
  <tr>
   <th>Mean Excess</th>
   <th>$\mathbf{MeanCPU}$ $time(sec)$</th>
   <th>Mean Excess</th>
   <th>Mean $CPU$ $time(sec)$</th>
  </tr>
  <tr>
   <td>eil51 (20 runs)</td>
   <td>$0\%$</td>
   <td>1.2</td>
   <td>$0\%$</td>
   <td>6</td>
  </tr>
  <tr>
   <td>kroAl00 ( 20 $D$ runs)</td>
   <td>$0\%$</td>
   <td>1.59</td>
   <td>$0\%$</td>
   <td>ll</td>
  </tr>
  <tr>
   <td>$d198(20$ runs)</td>
   <td>$0\%$</td>
   <td>435</td>
   <td>$0\%$</td>
   <td>253</td>
  </tr>
  <tr>
   <td>att532 ( 10 runs) </td>
   <td>$0\%$</td>
   <td>3526</td>
   <td>$0.05\%$</td>
   <td>6076</td>
  </tr>
  <tr>
   <td>rat783 (10 runs)</td>
   <td>$0\%$</td>
   <td>5232</td>
   <td>$0.04\%$</td>
   <td>14925</td>
  </tr>
 </tbody>
</table>

Table 7. GLS with FLS-2Opt compared with Genetic Local Search on five TSPLIB instances

Except for d198 which is a hard instance for GLS (see results in section 8.3), GLS was better than the GA approach finding solutions of better quality for att532 and rat783 while running faster between 1.7 to 6.9 times.Note here that the GA is using the best heuristic for the TSP (i.e.DB followed by LK) while GLS the worst (i.e. 2-Opt). Another remarkable result which emerged from these experiments was that GLS with FLS-2Opt can consistently find the optimal solutions for problems att532 and rat783. As far as we know, optimal solutions to such large problems can be consistently found only by heuristic methods that are using LK (e.g. Iterated LK or its variant Large-Step Markov Chains method).

In fact, GLS was able to find the optimal solution in even larger problems. For example, GLS with FLS-3Opt found the optimal solution for a 2319-city problem from TSPLIB (u2319)in less than 20 minutes while GLS with FLS-2Opt found the optimal solution to a 1002-city problem from TSPLIB (pr1002)in 14 hours of CPU

------------------------------------------------------------------

time despite running on Sparcstation 5 workstation which is much slower than the DEC Alpha machines used in the rest of the experiments.

# 9. Summary and Conclusions

In this paper, we described the technique of GLS in detail and examined its application to the Traveling Salesman Problem. Eight combinations of GLS with commonly used TSP heuristics were described and evaluated on publicly available instances of the TSP. GLS with FLS-2Opt was found to be the best GLS variant for the TSP. The variant was compared and found to be superior to commonly used variants of general search methods such as simulated annealing and tabu search Furthermore, we demonstrated that GLS with FLS-2Opt is highly competitive (if not better) than some of the best specialized algorithms for the TSP such as Iterated LinKernighan and Genetic Local Search. In total sixteen alternative TSP algorithms were compared against the GLS variants and many of the GLS variants were found to outperform or perform equally well to all these techniques. In total 24 algorithms for the TSP considered and extensive results were presented on publicly available instances of the problem

Experimental results should be treated with care. Experimentation no matter how elaborate and extensive it may be, it can only give indications of which algorithms are better than others and that because of the many parameters involved in the algorithms, differences in implementation, and the limited number of instances used in experiments.

We can safely conclude that the evidence provided in this paper is enough to place GLS amongst what somebody will characterize as efficient and effective methods for the TSP. Given the simplicity of the algorithm and the ease of tuning (i.e

------------------------------------------------------------------

single parameter), GLS with FLS-2Opt could be considered as an ideal practical method for the TSP especially when no programming effort can be devoted in implementing one of the complex specialized TSP algorithms.

More generally, GLS is applicable not only to TSP but to a range of other problems in combinatorial optimization. Open research issues include the use of incentives implemented as negative penalties which encourage the use of specific solution features is one promising direction to be explored. Other potentially interesting research directions include automated tuning of the parameter lambda definition of effective termination criteria, and different utility functions for selecting the features penalized. GLS could also be used to distribute the search effort in other techniques such as Genetic Algorithms

Finally, from our experience on the TSP and other domains we found it very easy to adapt GLS and FLS to problem in hand something which suggests that it may be possible to built a generic software platform for combinatorial optimization based on GLS. Although local search is problem dependent, most of the other structures of GLS and also FLS are problem independent. Furthermore, a step by step procedure is usually followed when GLS is applied to a new problem (i.e. identify features, assign costs, etc.) something which makes easier the use of the technique by OR practitioners and Optimization Systems engineers

------------------------------------------------------------------

### References

[1] Aarts, E.H.L., and Korst, J.H.M., Simulated Annealing and Boltzmann machines Wiley, Chichester, 1989

[2] Backer, B.D., Furnon, V., Prosser, P., Kilby, P., and Shaw, P., "Solving vehicle routing problems using constraint programming and metaheuristics", Submitted to the Journal of Heuristics special issue on Constraint Programming, July 1997.

[3] Bentley, J.L., "Fast Algorithms for Geometric Traveling Salesman Problems" ORSA Journal on Computing, Vol. 4, 387-411, 1992.

[4] Codenotti, B., Manzini, G., Margara, L., and Resta, G., Pertrubation: An Efficien Technique for the Solution of Very Large Instances of the Euclidean TSP",ORSA Journal on Computing, Vol. 8, No. 2, 125-133, 1996

[5] Connoly, D.T., "An improved annealing scheme for the QAP", European Journal of Operational Research, 46, 93-100, 1990

[6] Croes, A., *A Method for Solving Traveling-Salesman Problems", Operations Research, 5, 791-812, 1958.

[7] Davenport, A., Tsang,E., Wang, C.J., and Zhu, K. GENET: A connectionis architecture for solving constraint satisfaction problems by iterative improvement, Proceedings of AAAI-94, 325-330, 1994.

[8] Davis, L., Handbook of Genetic Algorithms, Van Nostrand Reinhold, 1991

[9] Dowsland, A., "Simulated Annealing", in: Reeves, C. R. (ed.), Modern Heuristic Techniques for Combinatorial Problems, Blackwell Scientific Publishing, 20-691993.

[10] Feo, T.A., and Resende, M.G.C., "Greedy Randomized Adaptive Search Procedures", Journal of Global Optimization, vol. 6, pp. 109-133, 1995.

[11] Freisleben, B., and Merz, P., "A Genetic Local Search Algorithm for Solving the Symmetric and Asymmetric TSP", Proceedings of IEEE International Conference on Evolutionary Computation, Nagoya, Japan, 616-621, 1996.

------------------------------------------------------------------

[12] Glover, F., “Future paths for integer programming and links to artificial intelligence", Computers Ops Res., 5, 533-549, 1986

[13] Glover, F., "Tabu Search and Adaptive Memory Programming - Advances Applications and Challenges", in: Interfaces in Computer Science and Operations Research, Barr, Helgason and Kennington eds., Kluwer Academic Publishers, 1996

[14] Glover, F.,“Tabu Search Fundamentals and Uses", Graduate School of Business University of Colorado, Boulder, 1995

[15] Glover, F.,“Tabu search Part I"', ORSA Journal on Computing,Vol. 1,190-2061989

[16] Glover, F.,“Tabu search Part Ir", ORSA Journal on Computing,Vol. 2, 4-321990. [17] Glover, F., “Tabu Search: improved solution alternatives for real world problems", in: Birge & Murty (ed.), Mathematical Programming: State of the Art, 6492, 1994. [18] Glover, F.,and Laguna, M.,“Tabu Search", in: Reeves, C. R. (ed.), Moderr Heuristic Techniques for Combinatorial Problems, Blackwell Scientific Publishing 71-141, 1993. [19] Goldberg, D.E., Genetic algorithms in search, optimization, and machine learning, Addison-Wesley, 1989 [20] Johnson, D., “Local Optimization and the Traveling Salesman Problem" Proceedings of the 17th Colloquium on Automata Languages and Programming Lecture Notes in Computer Science, 443, 446-461, Springer-Verlag, 1990. [21] Johnson, D., and McGeoch, L.,"The Traveling Salesman Problem: A Case Study in Local Optimization", Manuscript, November, 1995 (revised version appeared in Local Search in Optimization, Ed.E. H. L.Aarts and J. K. Lenstra, Wiley,Chichester Pp. 215-310, 1997). [22] Johnson, D., Aragon, C., McGeoch, L., and Schevon, C.,“Optimization by simulated annealing: an experimental evaluation, part I, graph partitioning", Operations Research, 37, 865-892, 1989

------------------------------------------------------------------

[23] Johnson, D., Aragon, C., McGeoch, L., and Schevon, C., "Optimization by simulated annealing: an experimental evaluation, part Il, graph coloring and number partitioning", Operations Research, 39, 378-406, 1991.

[24] Johnson, D., Bentley, J., McGeoch, L., and Rothberg, E.,“Near-optimal solutions to very large traveling salesman problems", in preparation. (for experimental results. from this work see also [21])

[25] Kilby, P., Prosser, P., and Shaw, P., "Guided local search for the vehicle routing problem", Proceedings of the 2nd International Conference on Metaheuristics, July 1997.

[26] Kirkpatrick, S., Gelatt, C.D., and Vecchi, M.P., Optimization by Simulatec Annealing", Science, Vol. 220, 671-680, 1983.

[27] Knox, J., "Tabu Search Performance on the Symmetric Traveling Salesman Problem", Computers Ops Res., Vol. 21, No. 8, pp. 867-876, 1994.

[28] Laarhoven, P.J.M.V., and Aarts, E.H.L., Simulated Annealing: Theory and Applications, Kluwer, Dordrecht, 1988

[29] Laporte,G.，“The Traveling Salesman Problem: An overview of exact and approximate algorithms", European Journal of Operational Research, 59, 231-2471992.

[30] Lawler, E.L.,Lenstra, J.K., Rinnooy Kan,A.H.G., and Shmoys, D.B., eds.), The Traveling Salesman Problem: A guided tour in combinatorial optimization, John Wiley & Sons, 1985.

[31] Lin, S., "Computer Solutions of the Traveling-Salesman Problem, Bell Systems Technical Journal, 44,2245-2269, 1965

[32] Lin, S., and Kernighan, B.W., "An effective heuristic algorithm for the traveling salesman problem", Operations Research, 21, 498-516, 1973.

[33] Mak, K., and Morton, A.J., A modified Lin-Kernighan traveling-salesman heuristic", Operations Research Letters, 13, 127-132, 1993.

[34] Martin,O., and Otto, S.W.,“Combining Simulated Annealing with Local Search Heuristics', in: G.Laporte and I. H. Osman (eds.), Metaheuristics in Combinatorial Optimization, Annals of Operations Research, Vol. 63, 1996.

------------------------------------------------------------------

[35] Martin, O., Otto, S.W., and Felten, E.W., “Large-step Markov chains for the TSP incorporating local search heuristics", Operations Research Letters, 11, 219-2241992.

[36] Morris, P., “"The breakout method for escaping from local minima", Proceeding. of AAAI-93, 40-45, 1993

[37] Osman, IH., "An Introduction to Meta-Heuristics", M. Lawrence and C. Wilsor (eds.), in: Operational Research Tutorial Papers, Operational Research Society Press Birmingham, UK, 92-122, 1995.

[38] Reeves, C.R. (ed.), Modern Heuristic Techniques for Combinatorial Problems Blackwell Scientific Publishing, 1993

[39] Reeves, C.R.,“Genetic Algorithms", in: Reeves, C. (ed.), Modern Heuristic Techniques for Combinatorial Problems, Blackwell Scientific Publishing, 151-1961993.

[40] Reeves, C.R., “Modern Heuristic Techniques", in: V. J. Rayward-Smith, I. H Osman, C.R.Reeves and G.D. Smith (ed.), John Wiley & Sons, Modern Heuristi Search Methods, 1-25, 1996. [41] Reinelt, G.,“A Traveling Salesman Problem Library", ORSA Journal on Computing, 3, 376-384, 1991. [42] Reinelt, G., The Traveling Salesman: Computational Solutions for TSP Applications, Lecture Notes in Computer Science, 840, Springer-Verlag, 1994 [43] Selman, B., and Kautz, H., “Domain independent versions of GSAT solving large structured satisfiability problems", Proceedings of IJCAI-93, 290-295, 1993 [44] Taillard, E., Robust taboo search for the QAP.Parallel Computing, 17, 443-4551991. [45] Tsang, E., and Voudouris, C., "Fast local search and guided local search and thein application to British Telecom's workforce scheduling problem", Operations Research Letters, Vol. 20, No. 3, 119-127, 1997. [46] Tsang, E., Foundations of Constraint Satisfaction, Academic Press, 1993

------------------------------------------------------------------

[47] Voudouris, C., and Tsang, E., Partial Constraint Satisfaction Problems and Guided Local Search", Proceedings of $2^{nd}$ Int. Conf. on Practical Application of Constraint Technology (PACT'96), London, April, 337-356, 1996.

[48] Voudouris, C., Guided Local Search for Combinatorial Optimization Problems PhD Thesis, Department of Computer Science, University of Essex, Colchester, UK July, 1997

[49] Wang, C.J., and Tsang, E., Solving constraint satisfaction problems using neural-networks", Proceedings of IEE Second International Conference on Artificial Neural Networks,295-299,1991

[50] Zachariasen, M., and Dam, M.,Tabu Search on the Geometric Traveling Salesman Problem", in: I. H. Osman and J. P. Kelly (ed.), Meta-heuristics: Theory and Applications, Kluwer, Boston, 571-587, 1996.

------------------------------------------------------------------

# Appendix

The set of problems used in the evaluation of the Repeated Local Search, Guidec Local Search and Iterated Local Search (using the Double Bridge move)variants on the TSP included 20 problems from 48 to 1002 cities all from TSPLIB. For each variant tested, 10 runs were performed from random solutions and 5 minutes of CPU time were allocated to each algorithm in each run on a DEC Alpha 3000/600 (175MHz) machine. To measure the success of the variants,we considered the percentage excess above the optimal solution as in (5). For GLS variants,the normalized lambda parameter a was provided as input and $\lambda$ was determined after the first local minimum using (6). For GLS variants using 2-Opt, α was set to $a=1/6$ while the GLS variants based on 3-Opt used the slightly lower value $a=1/8$ and the LK variants the even lower value $a=1/10$ .Results for GLS are shown in Table A.1.

Iterated Local Search was using the Double Bridge move.No simulatec annealing was used which is roughly equivalent to the Large-Markov Chains Methods with temperature $T$ set to O. Results for Iterated Local Search are shown in Table A.2.

Finally,Repeated Local Search was restarting from a random solution whenever local search was reaching a local minimum.Results for Repeated Local Search are shown in Table A.3. The names of the variants were formed according to the following convention:

<meta-heuristic >-<local search type >-<neighbourhood type >

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem</th>
   <th rowspan="2">|No. Cities</th>
   <th colspan="6">Mean Excess $(\%)$ over 10 runs</th>
  </tr>
  <tr>
   <th>GLS-FI-LK</th>
   <th>GLS- FI- 3Opt</th>
   <th>GLS- FI- 2Opt</th>
   <th>GLS-FLS-LK</th>
   <th>${\mathrm{GLS-FLS-3Opt}}$</th>
   <th>GLS- FLS- 2Opt</th>
  </tr>
  <tr>
   <td>att48</td>
   <td>48</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>eil76</td>
   <td>76</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>bierl27</td>
   <td>127</td>
   <td>0.218207</td>
   <td>0.116586</td>
   <td>0.019699</td>
   <td>0.206625</td>
   <td>0.002198</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>150</td>
   <td>0.029784</td>
   <td>0.084075</td>
   <td>0.000754</td>
   <td>0.001508</td>
   <td>0.001131</td>
   <td>0</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>159</td>
   <td>0</td>
   <td>0.460551</td>
   <td>0.225285</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>200</td>
   <td>0.436189</td>
   <td>0.526083</td>
   <td>0.257083</td>
   <td>0.088872</td>
   <td>0.00681</td>
   <td>0</td>
  </tr>
  <tr>
   <td>gr202</td>
   <td>202</td>
   <td>0.732321</td>
   <td>0.406375</td>
   <td>0.309512</td>
   <td>0.252988</td>
   <td>0.011703</td>
   <td>0</td>
  </tr>
  <tr>
   <td>gr229</td>
   <td>229</td>
   <td>0.392788</td>
   <td>0.468195</td>
   <td>0.381644</td>
   <td>0.152969</td>
   <td>0.015007</td>
   <td>0.004309</td>
  </tr>
  <tr>
   <td>gil262</td>
   <td>262</td>
   <td>0.328007</td>
   <td>0.723297</td>
   <td>0.428932</td>
   <td>0.084104</td>
   <td>0.046257</td>
   <td>0.004205</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>|318</td>
   <td>1.00264</td>
   <td>1.74284</td>
   <td>1.33884</td>
   <td>0.583407</td>
   <td>0.129197</td>
   <td>0.02641</td>
  </tr>
  <tr>
   <td>gr431</td>
   <td>431</td>
   <td>1.69438</td>
   <td>2.71862</td>
   <td>2.34071</td>
   <td>0.563665</td>
   <td>0.134003</td>
   <td>0.023919</td>
  </tr>
  <tr>
   <td>pcb442</td>
   <td>442</td>
   <td>0.966363</td>
   <td>0.80783</td>
   <td>1.36634</td>
   <td>0.38816</td>
   <td>0.038403</td>
   <td>0.044311</td>
  </tr>
  <tr>
   <td>att532</td>
   <td>532</td>
   <td>1.04746</td>
   <td>2.28599</td>
   <td>2.52871</td>
   <td>0.386116</td>
   <td>0.224662</td>
   <td>0.089937</td>
  </tr>
  <tr>
   <td>$u574$</td>
   <td>574</td>
   <td>1.36892</td>
   <td>2.81263</td>
   <td>3.66807</td>
   <td>0.580951</td>
   <td>0.278824</td>
   <td>0.141444</td>
  </tr>
  <tr>
   <td>rat575</td>
   <td>575</td>
   <td>0.806142</td>
   <td>1.77174</td>
   <td>2.25011</td>
   <td>0.287908</td>
   <td>0.171268</td>
   <td>0.098922</td>
  </tr>
  <tr>
   <td>$gr666$</td>
   <td>666</td>
   <td>1.66056</td>
   <td>4.38707</td>
   <td>6.00476</td>
   <td>0.855251</td>
   <td>0.497863</td>
   <td>0.206279</td>
  </tr>
  <tr>
   <td>$u724$</td>
   <td>724</td>
   <td>1.02505</td>
   <td>2.25101</td>
   <td>3.03054</td>
   <td>0.61298</td>
   <td>0.336674</td>
   <td>0.168218</td>
  </tr>
  <tr>
   <td>rat783</td>
   <td>783</td>
   <td>0.897116</td>
   <td>2.24052</td>
   <td>3.36929</td>
   <td>0.511015</td>
   <td>0.285033</td>
   <td>0.161254</td>
  </tr>
  <tr>
   <td>prl002</td>
   <td>1002</td>
   <td>1.97877</td>
   <td>3.31969</td>
   <td>5.54336</td>
   <td>1.04229</td>
   <td>0.945357</td>
   <td>0.620626</td>
  </tr>
  <tr>
   <td colspan="2">Average Excess</td>
   <td>0.729235</td>
   <td>1.356155</td>
   <td>1.653182</td>
   <td>0.32994</td>
   <td>0.15622</td>
   <td>0.079492</td>
  </tr>
 </tbody>
</table>
TableA.1Resultsfor GLS on the TSP.

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem</th>
   <th rowspan="2">No.Cities</th>
   <th colspan="6">Mean Excess $(\%)$ over 10 runs</th>
  </tr>
  <tr>
   <th>$DB-FI-LK$</th>
   <th>$DB-FI-3Opt$</th>
   <th>$DB-FI-2Opt$</th>
   <th>$DB-FLS-LK$</th>
   <th>$|DB-FLS-3Opt$</th>
   <th>$DB-FLS-2Opt$</th>
  </tr>
  <tr>
   <td>att48</td>
   <td>48</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>eil76</td>
   <td>76</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>100</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>bierl27</td>
   <td>127</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>150</td>
   <td>0</td>
   <td>0.001508</td>
   <td>0.003393</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>159</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>|200</td>
   <td>0</td>
   <td>0.077295</td>
   <td>0.10113</td>
   <td>0</td>
   <td>0.004767</td>
   <td>0.075252</td>
  </tr>
  <tr>
   <td>$gr202$</td>
   <td>|202</td>
   <td>0.009213</td>
   <td>0.088396</td>
   <td>0.457171</td>
   <td>0</td>
   <td>0.155129</td>
   <td>0.257719</td>
  </tr>
  <tr>
   <td>$gr229$</td>
   <td>|229</td>
   <td>0.014116</td>
   <td>0.157576</td>
   <td>0.382387</td>
   <td>0.004755</td>
   <td>0.064115</td>
   <td>0.124515</td>
  </tr>
  <tr>
   <td>$gil262$</td>
   <td>|262</td>
   <td>0.016821</td>
   <td>0.20185</td>
   <td>0.626577</td>
   <td>0</td>
   <td>0.075694</td>
   <td>0.475189</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>|318</td>
   <td>0.255776</td>
   <td>0.719027</td>
   <td>1.14588</td>
   <td>0.240786</td>
   <td>0.279093</td>
   <td>0.3519</td>
  </tr>
  <tr>
   <td>gr431</td>
   <td>431</td>
   <td>0.332703</td>
   <td>0.94403</td>
   <td>2.13495</td>
   <td>0.222386</td>
   <td>0.394192</td>
   <td>0.615294</td>
  </tr>
  <tr>
   <td>pcb442</td>
   <td>442</td>
   <td>0.066367</td>
   <td>0.368861</td>
   <td>1.8961</td>
   <td>0.081728</td>
   <td>0.309977</td>
   <td>0.684745</td>
  </tr>
  <tr>
   <td>att532</td>
   <td>|532</td>
   <td>0.225023</td>
   <td>1.03554</td>
   <td>2.64971</td>
   <td>0.08163</td>
   <td>0.270534</td>
   <td>0.422957</td>
  </tr>
  <tr>
   <td>$u574$</td>
   <td>|574</td>
   <td>0.114348</td>
   <td>1.20038</td>
   <td>2.94269</td>
   <td>0.092399</td>
   <td>0.404823</td>
   <td>0.553042</td>
  </tr>
  <tr>
   <td>rat575</td>
   <td>|575</td>
   <td>0.13731</td>
   <td>1.15016</td>
   <td>3.75904</td>
   <td>0.097446</td>
   <td>0.445888</td>
   <td>0.649638</td>
  </tr>
  <tr>
   <td>gr666</td>
   <td>666</td>
   <td>0.418878</td>
   <td>1.25178</td>
   <td>3.27054</td>
   <td>0.175874</td>
   <td>0.359528</td>
   <td>0.816489</td>
  </tr>
  <tr>
   <td>$u724$</td>
   <td>724</td>
   <td>0.356955</td>
   <td>1.43617</td>
   <td>3.94106</td>
   <td>0.166547</td>
   <td>0.367693</td>
   <td>0.627535</td>
  </tr>
  <tr>
   <td>rat783</td>
   <td>783</td>
   <td>0.240745</td>
   <td>1.79764</td>
   <td>5.00454</td>
   <td>0.153305</td>
   <td>0.516693</td>
   <td>0.744947</td>
  </tr>
  <tr>
   <td>prl002</td>
   <td>1002</td>
   <td>1.04742</td>
   <td>2.05625</td>
   <td>5.19902</td>
   <td>0.446332</td>
   <td>0.872049</td>
   <td>1.05727</td>
  </tr>
  <tr>
   <td colspan="2">Average e Excess</td>
   <td>0.161784</td>
   <td>0.624323</td>
   <td>1.675709</td>
   <td>0.088159</td>
   <td>0.226009</td>
   <td>0.372825</td>
  </tr>
 </tbody>
</table>
Table A.2 Results for Iterated Local Search on the TSP

------------------------------------------------------------------

<table>
 <tbody>
  <tr>
   <th rowspan="2">Problem</th>
   <th rowspan="2">No.Cities</th>
   <th colspan="6">Mean Excess $(\%)$ over 10 runs</th>
  </tr>
  <tr>
   <th>REP-FI-LK</th>
   <th>REP- FI- 3Opt</th>
   <th>REP- FI- 2Opt</th>
   <th>REP- FLS- LK</th>
   <th>REP- FLS- 3Opt</th>
   <th>REP- FLS- 2Opt</th>
  </tr>
  <tr>
   <td>att48</td>
   <td>48</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
   <td>0</td>
  </tr>
  <tr>
   <td>eil76</td>
   <td>76</td>
   <td>0</td>
   <td>0</td>
   <td>1.35688</td>
   <td>0</td>
   <td>0</td>
   <td>1.48699</td>
  </tr>
  <tr>
   <td>kroAl00</td>
   <td>100</td>
   <td>0</td>
   <td>0.39564</td>
   <td>0.222254</td>
   <td>0</td>
   <td>0.225543</td>
   <td>0.215205</td>
  </tr>
  <tr>
   <td>bierl27</td>
   <td>127</td>
   <td>0.030098</td>
   <td>0.403696</td>
   <td>1.19629</td>
   <td>0.027899</td>
   <td>0.370386</td>
   <td>1.29513</td>
  </tr>
  <tr>
   <td>kroAl50</td>
   <td>150</td>
   <td>0.002262</td>
   <td>0.8317</td>
   <td>2.00912</td>
   <td>0.002262</td>
   <td>0.8038</td>
   <td>2.01553</td>
  </tr>
  <tr>
   <td>$u159$</td>
   <td>159</td>
   <td>0</td>
   <td>0.30038</td>
   <td>1.62619</td>
   <td>0</td>
   <td>0.265447</td>
   <td>2.05894</td>
  </tr>
  <tr>
   <td>kroA200</td>
   <td>200</td>
   <td>0.024517</td>
   <td>1.00688</td>
   <td>3.30768</td>
   <td>0.004767</td>
   <td>0.922092</td>
   <td>3.23583</td>
  </tr>
  <tr>
   <td>gr202</td>
   <td>202</td>
   <td>0.141434</td>
   <td>1.22958</td>
   <td>3.58591</td>
   <td>0.129731</td>
   <td>1.19995</td>
   <td>3.68352</td>
  </tr>
  <tr>
   <td>gr229</td>
   <td>229</td>
   <td>0.097695</td>
   <td>1.36774</td>
   <td>3.40129</td>
   <td>0.094427</td>
   <td>1.27301</td>
   <td>3.56443</td>
  </tr>
  <tr>
   <td>gil262</td>
   <td>262</td>
   <td>0.054668</td>
   <td>1.3709</td>
   <td>5.12195</td>
   <td>0.054668</td>
   <td>1.2868</td>
   <td>5.77796</td>
  </tr>
  <tr>
   <td>$\lim318$</td>
   <td>318</td>
   <td>0.629565</td>
   <td>2.17992</td>
   <td>4.37936</td>
   <td>0.636703</td>
   <td>2.022676</td>
   <td>4.9128</td>
  </tr>
  <tr>
   <td>gr431</td>
   <td>431</td>
   <td>0.679641</td>
   <td>2.07801</td>
   <td>5.33877</td>
   <td>0.665232</td>
   <td>2.20915</td>
   <td>5.97495</td>
  </tr>
  <tr>
   <td>pcb442</td>
   <td>442</td>
   <td>0.48525</td>
   <td>1.77636</td>
   <td>6.65012</td>
   <td>0.516956</td>
   <td>1.72417</td>
   <td>7.19544</td>
  </tr>
  <tr>
   <td>att532</td>
   <td>532</td>
   <td>0.530232</td>
   <td>2.29033</td>
   <td>6.28368</td>
   <td>0.579354</td>
   <td>2.29141</td>
   <td>7.13899</td>
  </tr>
  <tr>
   <td>$u574$</td>
   <td>574</td>
   <td>0.738382</td>
   <td>2.91397</td>
   <td>7.46674</td>
   <td>0.703157</td>
   <td>2.6934</td>
   <td>8.4788</td>
  </tr>
  <tr>
   <td>rat575</td>
   <td>575</td>
   <td>0.807618</td>
   <td>2.69895</td>
   <td>7.69231</td>
   <td>0.887347</td>
   <td>2.70781</td>
   <td>8.61066</td>
  </tr>
  <tr>
   <td>$gr666$</td>
   <td>666</td>
   <td>0.837619</td>
   <td>3.18259</td>
   <td>8.14712</td>
   <td>0.847811</td>
   <td>2.97203</td>
   <td>9.94096</td>
  </tr>
  <tr>
   <td>$u724$</td>
   <td>724</td>
   <td>0.933667</td>
   <td>2.90551</td>
   <td>7.76903</td>
   <td>1.0241</td>
   <td>2.87473</td>
   <td>8.83202</td>
  </tr>
  <tr>
   <td>rat783</td>
   <td>783</td>
   <td>1.00045</td>
   <td>3.2864</td>
   <td>8.46468</td>
   <td>1.06518</td>
   <td>3.39882</td>
   <td>9.38792</td>
  </tr>
  <tr>
   <td>prl002</td>
   <td>1002</td>
   <td>1.5046</td>
   <td>3.50511</td>
   <td>8.62028</td>
   <td>1.39138</td>
   <td>3.59138</td>
   <td>10.5847</td>
  </tr>
  <tr>
   <td colspan="2">Average Excess</td>
   <td>0.424885</td>
   <td>1.686183</td>
   <td>4.631983</td>
   <td>0.431549</td>
   <td>1.64163</td>
   <td>5.219539</td>
  </tr>
 </tbody>
</table>
Table A.3 Results for Repeated Local Search on the TSP
