# The long-haul full-load vehicle routing and truck driver scheduling problem with intermediate stops: An economic impact evaluation of Brazilian policy

Sergio Fernando Mayerlea, Daiane Maria De Genaro Chirolib,* Joao Neiva de Figueiredo, Hidelbrando Ferreira Rodriguesd.

a Departnent of Production Engineering and Systems, Federal University of Santa Catarina, Florianopolis, Brazil b Department of Textil Engineering, Federal Technoiogy University Parand, Apucarana, Brazil ^ Department of Management, Haub School of Business, Saint Joseph's University, 5600 City Ave, Philadelphio, USA d Federal University of Amazonas, Itacoatiara, Brazil

### ARTICLE INFO

### Keywords Trucking policy planning and evaluation

Road freight in emerging markets Vehicle routing and driver scheduling problem Full-load long haul trip optimization Driver regulatory constraints

### ABST R A C T

This paper presents a methodology to identify the economic impact of different policies for heavy vehicle routing and driver scheduling in long-haul full-load trips with intermediate stops for refueling and for regulation-driven meal and rest periods. This methodology can be used both as a planning tool to help policy-makers define policies through scenario simulations, and as an evaluation tool to examine ex-post economic impact once policies have been changed as illustrated herein for the Brazilian case. The paper introduces a mathematical formulation, proposes a state-space graph search approach, and develops an algorithmic solution for a variant of the vehicle routing and truck driver scheduling problem with intermediate stops (VRTDSPIS), which is especially important in countries with vast territory where long-range freight trucking trips are common. In addition, it is particularly relevant for the economies of emerging markets that may have evolving regulatory frameworks and suboptimal infrastructure environments. Regulatory maximum driving and minimum driver resting time windows impose significant constraints to trucker routines, especially in sparsely populated regions through which long range vehicle trips with full load are common. Such trips can take days to be concluded and numerous alternative routes are possible, each with very different alternatives for refueling and rest. While the lit erature to date has focused mostly on truck driver scheduling given pre-determined routes and individual country's laws and regulations, this paper proposes a joint solution for the routing and scheduling problem with time window constraints, determining simultaneously a routing and scheduling plan that meets all maximum driving and minimum resting time interval regulatory requirements at minimum cost. An illustration applying the methodology to evaluate the eco nomic impact of truck driver regulatory changes in Brazil is presented

### 1.Introduction

Many markets lack sophisticated rail networks, so land-based commercial freight is often accomplished by trucking, much of it

------------------------------------------------------------------

long-haul, in which drivers may travel continental distances and spend days on the road to deliver full loads to destinations. To promote public highway safety through improved professional truck driver working conditions, countries have implemented different regulations, such as limiting continuous driving time and establishing daily and weekly aggregate driving time limits. Despite the vast academic literature on vehicle routing and scheduling, research focusing simultaneously on routing restrictions and on regulatory constraints that impose rigid upper and lower bounds respectively on driving and resting times is still blossoming (Chiroli et al. 2016). Algorithms that identify optimal routing with necessary intermediate fueling stops while taking into account time windows of travel and rest can be very useful not only for trucking operations, but also for policy-makers. First, they can be a very importan policy tool in the planning stage to examine the economic impact of different proposed policy alternatives. Second, they can be very useful in the ex-post evaluation stage to assess outcomes after policies have been implemented. The latter is exemplified by the case study reported herein. This paper proposes a joint solution for the truck routing and stop scheduling problem, which optimizes the route of long-haul

full-load trips with intermediate stops both for refueling and for required rest periods, and illustrates its use for regulatory policy evaluation purposes. The problem is treated as a variant of the vehicle routing and truck driver scheduling problem with intermediate stops (VRTDSPIS) for refueling and required time windows for rest. In summary, the problem addressed in this paper consists of determining the optimal route and the complete schedule of stops between two locations taking into account driving time regulations and the available potential stop options both for refueling and for meals/rest/overnight stops along the way. Only the origin and the destination are pre-defined: to obtain the minimum cost solution, changes in routing and in intermediate stop locations are possible and permitted as long as they satisfy regulatory constraints, such as maximum permitted driving times or minimum required driver resting times. This VRTDSPIS in which intermediate stops are either for refueling or to satisfy regulatory truck driver service requirements consists of minimizing the total cost of a trip in which: (a) a full payload or cargo needs to be transported from a known origin to a known final destination; (b) a set of regulatory constraints governing truck driver active and resting intervals needs to be complied with; (c) a network of roads connects origin to final destination often leading to a significant number of potential alternative routes; (d) many locations with different service offerings and costs, which provide the means to comply with regulatory driving constraints, are components of the network. In this paper four different types of stops regulating driver disengagement hours are considered: rest, meal, overnight, and weekly break. These stops necessarily need to occur in places with adequate infrastructure and are bookends for truck driving periods of different lengths, depending on local regulations. While regulations require stops for several reasons, no single location along the way is a required stop location and different services and locations most often exhibit different costs. This is a combinatorial problem in which the number of possible alternatives increases exponentially with distance. This problem is especially relevant in countries with vast territory in which long-range freight trucking trips are common, such as

the U.S., Canada,Australia, as well as in environments with many regulatory considerations, such as the European Union Importantly, the combination of trucking regulations, infrastructure conditions, and the availability of meal and overnight stop options, are constraints that significantly affect freight transport in emerging economies with large area, in which alternative rest locations are sometimes sparsely located. By way of example, until a few years ago Brazil's trucking regulations were considered insufficient to provide drivers with adequate rest, and had erratic enforcement. In a country in which an estimated two-thirds of registered professional truck drivers operate independently, highway accidents were common and had been increasing, so an important public health objective was to provide more sustainable working conditions for all truck drivers, whether trucking company employees or individual truck owners operating independently. Law $n^{\circ}$ 13.103 was passed in March 2015 to establish maximum uninterrupted truck driving hours and minimum required rest periods at various levels (BRASIL, 2015). Restrictions in the law are complex and depend on state-specific and local considerations. For example, the daily driving load is limited at 8 h with possibility of overtime for another several hours depending on labor agreements. Law $\mathrm{n}^{\circ}13.103$ establishes a minimum duration of one hour for meal breaks, an 11-hour period of rest in every 24-hour period, and weekly rest periods of $35h$ . In long-haul driving situations other restrictions were imposed, such as a required half-hour break for every continuous five-and-a-half hours of driving. These constraints together with the sparse distribution of rest options in some parts of Brazil underline the importance of developing algorithms to ensure efficient freight transportation and highway safety The paper contributes to the academic literature on vehicle routing and scheduling with intermediate stops in several ways: (a) by

formulating an optimization model for the trucking freight problem of the long-haul full-truckload in which intermediate stops are required either for refueling or to satisfy regulatory active driver time-window requirements; (b) by suggesting a state-space methodology that incorporates both the spatial and the temporal dimensions of the problem to provide an algorithmic solution; (c) by suggesting the use of tools such as the one developed herein for regulatory policy planning and evaluation purposes; and (d) by using the methodology to evaluate the economic impact of a significant regulatory policy change in Brazil

This section introduces the paper, summarizes the main characteristics of the VRTDSPIS, and describes its relevance for policy purposes. Section 2 positions this paper within the vast literature on vehicle routing and truck driver scheduling, differentiating it from other problems that have been previously addressed in the literature. Section 3 formulates the basic full-load vehicle routing and driver scheduling problem with intermediate stops as a large size nonlinear mixed integer programming problem. Section 4 introduces a state-space approach to address the problem, represents it as a graph integrating spatial and temporal dimensions to reflect all efficient solutions for this problem, and describes a progressive iterative node generation process which expands the graph in order to find an optimal solution. Section 5 provides an algorithm for identifying the optimal routing and scheduling pattern within the state-space graph. Section 6 applies the methodology and algorithm to the evaluation of the economic impact of recent long-haul trucking regulatory changes in Brazil. Section 7 discusses the Brazilian case and suggests ways in which such a tool can help policymakers, concluding the paper.

------------------------------------------------------------------

## 2.Background on the vehicle routing and truck driver scheduling problem with intermediate stops

By the end of the first decade of this century, the academic literature on vehicle routing was extensive and Eksioglu et al. (2009) provided a comprehensive taxonomic review of related problems. Since then dynamic solutions for different types of vehicle routing and driver scheduling problems have become increasingly relevant both for policy planning and evaluation and for trucking operations. Gendreau et al. (2015) surveyed the expanded use of heuristics for time-dependent routing in real time and proposed a two tiered classification. The first is whether the objective is point-to-point or multipoint. The second is the availability of information i.e., whether time-dependent data is static and deterministic, static and stochastic, or dynamic. Vidal et al.'s (2019) concise guide to vehicle routing problem variants classifies the routing problem subject to working hour regulations under the heading “Specificity of Drivers and Vehicles” within the broader category of refined planning problems. The problem addressed herein is a vehicle routing problem categorized by node routing, time window constraints, and hours of service (HOS) regulations, to use the categorization proposed by Schiffer et al.'s (2019) comprehensive survey on the literature of VRTDSP with intermediate stops. In the classifications above, the VRTDSPIS addressed in this paper is characterized as an extension of the time-dependent quickest

path problem subject to regulatory HOS window constraints. Such regulatory HOS window constraints are different from the delivery time windows normally understood in the VRP literature (e.g., Vidal et al., 2015) in that they do not refer to periods in which delivery is possible/permitted/forbidden, but rather to continuous truck driving time limits. The truck driver routing and scheduling problem with HOS restrictions imposed by regulation addressed in the literature considers different regulatory environments focusing mostly on pick-up and delivery time restrictions, and uses several approaches, most of which are unique to a particular situation. In these papers, routes are pre-defined including delivery/collction stops and meal/rest stops, and the objective is to establish a schedule which conforms to station HOS regulatory requirements. Savelsbergh and Sol (1998) were the first to explicitly consider time restrictions (such as meals and rest) in the vehicle routing problem, using a column generation approach. Xu et al. (2003) used the same methodology and incorporated actual U.S. truck driving time regulations to the routing and scheduling problem. The complexity derives from the impact of alternative driving schedules and the number of possible regulatory HOS requirements in ensuing activities, which need to be satisfied within specific time windows given meal and rest alternatives available in respective neighboring geographies. Because regulations vary from country to country, different formulations may be best suitable to different locations. Ceselli et al.

(2009) investigated the VRP with driver work rules and developed a column generation algorithm with branch-and-price, where the pricing problem is a particular resource-constrained elementary shortest-path problem solved through a bounded bidirectional dynamic programming algorithm. Goel (2009) modeled the VRP with time windows (VRPTW) as an extension of the one-vehicle timedependent routing problem and suggested a formulation for truck driver visits to several locations within predetermined time windows satisfying European Union regulations. Prescott-Gagnon et al. (2010) also addressed the EU regulatory requirements for multiple stop routes proposing a column generation heuristic in a neighborhood search. Goel and Kok (2011) addressed the truck driver scheduling problem (TDSP - visiting a sequence of locations in given time windows) subject to the U.S. regulatory requirements. Goel and Rousseau (2011) described regulations in Canada and proposed two heuristics and an exact method to solve the TDSP in that country. Goel (2012a) proposed a mixed integer programming model to optimize the stops of a truck driver visiting a sequence of locations in Canada subjeet to the country's set ofregulations for driving south of the $60^{\circ}$ N latitude. Goel (2012b) and Goel et al. (2011) described and solved the TDSP given regulations in Australia, respectively with a mixed integer programming method, and with four heuristics besides an exact method. Goel and Vidal (2014) described an algorithm combining population-based metaheuristics with local search and forward-labeling techniques to minimize costs of a fleet of vehicles given customer business hours and regulatory constraints. Goel and Irnich (2017) introduced the first VRTDSP exact algorithm, using a bidirectional dynamic programming approach to solve the pricing problem as an elementary shortest path problem. Koc et al. (2018) abbreviated the VRTDSP with idling options as VRTDSPIO and developed a multi-start metaheuristic algorithm that combined an adaptive large neighborhood search with mixed integer linear programming. Goel (2018) addressed the significant legal requirement impact on vehicle routing and driver scheduling in European long-distance freight and identified gaps in current algorithms. Alcaraz et al. (2019) examined the long-haul routing problem from a fleet management perspective, taking into account driver hour regulations and time windows, but also focusing on alternative arrangements such as last mile delivery outsourcing and multiple pickup and drop-off locations. Goel et al. (2019) addressed another relevant alternative in long-haul transportation, that of using team driving, as they analyzed the use of relay-driving in road freight fleet transport management in the European Union by examining the conditions under which single or team driving are preferable. The recent literature also proposed efficient solutions to time-dependent quickes path problems based on seminal algorithms by Dijkstra (1959) and Hart et al. (1968). Several Dijkstra-like algorithms have been proposed, such as Dell'Amico et al. (2008), who allowed for waiting at nodes in a non-FIFO formulation with a delay function. Wen et al. (2014) used a modification of Dijkstra's algorithm with two different heuristic methods to find the lowest cost path between two nodes with a congestion charge in a time-varying network. In the VRTDSPIS addressed in this paper, uninterrupted driving regulatory time limits, daily driving regulatory time limits

weekly driving regulatory limits, required meal time intervals or windows, required overnight time intervals or windows, and availability of possible rest locations significantly constrain routing and scheduling alternatives. In addition, different meal and rest support locations likely have different costs, which sometimes differ to the point that a longer route may lead to a combination of lower meal and rest costs and/or more favorable time windows relative to a shorter route. The objective is to select the route and rest location schedule which result in lowest overall operating costs for the trip subject to all other constraints including possible final destination arrival deadlines. To achieve this goal, we propose a state-space approach and a Dijkstra-based search algorithm to find the lowest cost path in a graph of states that is iteratively built. To our knowledge the regulatory-constrained time-dependen

------------------------------------------------------------------

quickest path problem has not been yet addressed in the literature with the state-space optimization techniques such as the meth odology proposed herein. Following Laporte et al. (20oo), which focused specifically on the various possible heuristic approaches to vehicle routing, the algorithm proposed herein can also be expanded to include heuristic techniques

## 3. Problem characterization and mathematical programming formulatior

The full-load routing and scheduling problem with driver regulatory constraints belongs to the more general category of vehicle routing and truck driver scheduling with intermediate stops (VRTDSPIS) which was informally stated in the introduction is now characterized as a mathematical programming problem. The operational constraints of this problem are similar to those of traditional routing problems, but the addition of timing and regulatory restrictions significantly increases its complexity because every stoppage choice along the way will have a unique impact on the ensuing route/schedule due to time-window regulatory and operationa constraints as well as different stoppage availability alternatives, thus significantly influencing the number of feasible options Regulatory restrictions include length of uninterrupted driving time, meal duration, maximum allowed daily driving times, minimun overnight rest duration, and allowed time intervals for one (or more) daily meals.

## 3.1. Decision variables and objective function

LetN be the set of all allowed stop locations, places offering different levels of services needed by drivers such as rest, meal, and/ or overnight facilities, in the region under consideration, i.e., the travel region, including the origin and destination of a full-load complete trip, respectively denoted by $s\in N$ and $t\in N$ . LetA be the set of trip segments linking any two of these locations such that travel time along the respective connection is lower than the maximum allowed uninterrupted driving time, denoted by $L_{\mathrm{d}rv}$ . In other words, only physical connections on which travel can be covered in less time than the maximum regulatory driving time are feasible Let $y_{ij}^k\in\{0,1\}$ be a variable indicating whether travel between a given pair of locations $(i,j)\in A$ occurs on the $k^{th}$ day with travel time $t(i,j)$ and cost $(i,j)$ . Let $w_{\mathrm{tp}}^k\in\{0$ ， $1\}$ be a variable indicating whether location $i\in N$ is used for a stop of type $p\in F$ on day $k$ where $p\in\{1$ , 2, 3} represent different stop modes, respectively rest, meal, and overnight downtime. A cost $l(i,p)$ and a required minimum length of time $T(p)$ are associated to each stop of type $F$ Then, the following binary decision variables consist of deciding whether to use (or not) a given trip leg linking two locations and

whether to stop (or not) at a given location:

$y_{y}^k$ one if the driver decides to go from $i$ to $j$ on day $k$ , zero otherwise;

$w_{lp}^k$ one if the driver decides to stop at location $i$ for reason $P$ on day $k$ , zero otherwise.

The number of driving hours each day, $h_{k}$ , results from these decisions. Two other categories of decision variables (both continuous) are the times at which the driver decides (or is able) to enter and leave stop location i. These are represented by

$a_{i}$ arrival time in location i; $d_1$ departure time from location i.

The goal is to minimize the total cost to travel from $s\in N$ to $l\in\mathcal{N}$ ,defined by the objective function (1) that consists in minimizing the sum of four cost components as explained below. The first component of this objective function comprises all travel displacement costs excluding driver labor. This cost component is given by the sum of these displacement costs along every chosen trip that connects location pair $(i,j)$ . These costs are specified in Section 4.2, items b and c. As mentioned above, a cost $c(i,j)$ is associated to each such trip.

The second component comprises all types of stoppage costs and is the sum of all costs incurred during required stops for rest, meals, overnight and weekend downtime. These costs are specified in Section 4.2, items c, d, and e. As mentioned above, a cost d(i, p) is associated with each stop type and location.

The third component, denoted by $\eta(h_{k})$ , represents driver labor costs, which most often are not proportional to the expected normal daily work time because if that is surpassed, overtime pay is added. In addition, if driving time is less than the normal daily work time, the driver still receives a base salary. This cost component is referred to again in Section 4.2 item a. Therefore, the objective function represents this component as a function of $h_{k}$ , the number of hours driving during the $k^{n}$ day. A fourth cost component, $\phi(d_{s},a_{|})$ , is the opportunity cost of having a truck in use, the forgone contribution to operating profits of

a transportation asset (in this case the truck) not being utilized in another alternative transportation task. This opportunity cost of asset utilization is often considered when a truck is tied up in a lower income generating activity than might be otherwise possible, for example due to prior long-term contractual obligation. More relevant to the problem herein, when comparing any two alternative routing and scheduling options from location $s\in N$ to location $l\in N$ , the alternative taking more time will have an additional cost component, namely an opportunity cost of asset utilization (the truck) resulting from the additional time incurred in the route. This opportunity cost associated to the longest route results from computing the difference in opportunity costs (i.e., the difference in expected contributions to operating profits) for the two routes being compared

------------------------------------------------------------------

### 3.2. Constraints

The incoming flow into every location needs to equal the outgoing flow, except for the origin $s\in N$ and destination $\in N$ .Eq. (2） below ensures this flow conservation. The origin and the destination of the complete route are identified through Eqs. (3) and (4). The constraints represented by Eqs. (2)(4) ensure that the route begins in location S on the first day and ends in location I. If locationi is chosen as a stop of type $F$ on day $k$ , that is, if there is a flow into location i on the $k^{m}$ day, and a stop of type $P$ occurs

this is represented as $w_{\mathrm{Ip}}^k=1$ . More than one stop in a given location is not allowed. Eqs. (5) and (6) represent these constraints and characterize all stop locations either a location has one stop or none Let $L_{\mathrm{mov}}$ and $L_{0tv}$ be the regulatory maximum permitted daily driving time respectively in normal and overtime labor hour con

ditions. Consider minimum daily rest time requirements (overnight stops) which restrict early rising on the $k^{lh}$ day from occurring before time $W_k^{\text{start}(day)}$ Eq. (7)） accumulates travel times on the $k^{bh}$ day and Eq. (8)restrictsthis accumulated daily travel time to the maximum permitted daily driving, $(L_{\mathrm{mor}}+L_{\mathrm{otr}})$ Consider the arrival and departure times in each location, $a_ied_i$ , defined above. Then Eq. (9) determines the departure time from

each location in which a stop occurs and Eq. (10) sets the departure time from the origin, ie., the beginning of the route. Eq. (11) establishes the arrival time at each stop defined as the time of departure from the previous stop plus the travel time between the two locations. Eq. (12) requires that the departure time after the $k^{th}$ day overnight be not before the earliest permitted departure time for day $k+1$ . Consider that the main meal of the day needs to occur within specific daily time windows $[W_k^{\prime\text{start }(\text{mal})}]$ $W_k^{\text{end}(\text{masal})}$ .Constraints (13) and (14) stipulate that arrival time intervals at a location $i\in N$ for a meal on the $k^{lh}$ day must occur within the time interval $[W_k^{\prime\text{start }(\text{moal})}]$ $W_k^{\mathrm{end}(\text{meaf})}$I .The objectives of these three Eqs. (12)-(14) are achieved by using a sufficiently large parameter $M$ that is a penalty to either enable or disable the respective equation depending on the situation. Constraints (15) and (16), respectively ensure at least one stop for meal and for an overnight rest period in each working day. Finally, Eqs. (17)(21) identify the types of extension of the network flow problem as follows

$$\begin{aligned}
&\mathrm{Min}z=\sum_{k}\sum_{(i,j)\in A}c(i,j)y_{ij}^{k}+\sum_{k}\sum_{p\in P}\sum_{i\in N}d(i,p)w_{ip}^{k}+\sum_{k}\eta(h_{k}) \\
&\mathrm{s.~t:}\sum_{k}\sum_{j|(j,i)\in A}y_{ji}^{k}=\sum_{k}\sum_{j|(i,j)\in A}y_{ij}^{k}\quad\forall\:i\in N-[s,\:t] \\
&\sum_{i}y_{ii}^{1}=1 \\
&\sum_{k}\sum_{i|(i,t)\in A}y_{it}^{k}=1 \\
&\sum_{j|(j,i)\in A}y_{ji}^{k}=\sum_{p\in P}w_{ip}^{k}\quad\forall\:i\in N-\{s,\:t\}\:\forall\:k \\
&\sum_{k}\:\sum_{p\in P}w_{ip}^{k}\leq1\quad\forall\:i\in N \\
&h_{k}=\sum_{(i,j)\in A}t(i,j)y_{ij}^{k}\:\forall\:k \\
&h_{k}\leq L_{mor}+L_{owr}\quad\forall\:k \\
&d_{i}\geq a_{i}+\sum_{k}\sum_{p}T(p)w_{ip}^{k}\quad\forall\:i\in N-\{s,\:t\} \\
&d_{s}\geq W_{1}^{start\:(day)} \\
&a_{j}\geq d_{i}+\sum_{k}t(i,j)y_{ij}^{k}\quad\forall\:(i,j)\in A \\
&d_{i}\geq W_{k+1}^{start(day)}+M(w_{i3}^{k}-1)\quad\forall\:i\in N\:\forall\:k \\
&a_{i}\geq W_{k}^{start(meal)}+M(w_{i2}^{k}-1)\quad\forall\:i\in N\:\forall\:k \\
&a_{i}\geq W_{k}^{end(meal)}+M(1-w_{i2}^{k})\quad\forall\:i\in N\:\forall\:k \\
&M\sum_{i\in N}w_{i2}^{k}\leq h_{k}\quad\forall\:k \\
&M\sum_{i\in N}w_{i3}^{k}\geq h_{k}\quad\forall\:k
\end{aligned}$$

(1) y ∈ {0, 1} v (i,j) ∈ A V k w ∈ [0, 1} i ∈ N V p V k Q; ≥0Vi ∈ N d; ≥0Vi ∈ N

------------------------------------------------------------------

$$h_{k}\geq0\quad\forall\:i\in N$$

This is a mixed integer programming formulation which is linear in parts due to the discontinuous nature of $\eta(h_{k})$ . Depending on the nature of the function $(d_5,a_t)$ , the problem can also be nonlinear. Because of the combinatorial nature of the feasible solution space, an analytical resolution for this mathematical programming formulation is not practical. The computational effort required in real-life situations, in which millions of integer variables and hundreds of thousands of restrictions are considered, is significant Please note that in the interest of exposition clarity, the above mathematical formulation is time-invariant. The time-dependent component is introduced in the next section

## 4. A state-space graph model

The problem described above is now modeled as a search problem in a directed graph that is progressively constructed. A graph is characterized by a set of nodes and a set of arcs that are ordered pairs of nodes. In this paper we use a state-space approach in which each node represents a unique stop situation and is uniquely and fully represented by a set of parameters forming the stoppage configuration. Arcs between nodes represent transitions from one state to another. In this formulation the whole graph is not known explicitly beforehand because evolving conditions lead to different viable stoppage configurations. As time advances only certair states within the state-space can feasibly be reached. We therefore define a feasible successor node generator (referred to herein as a successor operator) I. For each node, the successor operator I determines the set of feasible successor nodes. In other words, given a stoppage configuration the successor operator I develops a set of feasible subsequent stops along the route. The graph is built from its source through repeated applications of the successor node generator I. The cost-minimizing route and schedule is found through a shortest path search in the directed state-space graph thus generated, in which each node is a configuration of stoppages and each arc connects two different adjacent stoppage configurations. Characterization of this graph includes three elements: a set of nodes; a set of arcs that are ordered pairs of nodes; and costs associated to arcs. What follows is a description of each of these elements

### 4.1. Nodes, arcs, and the successor operator

Node: A node in the state-space graph, identified by $X_{n}$ ,is defined as an n-tuple containing all the information necessary to identify a stoppage configuration. This information completely defines the state, and includes the permitted location identifier; the type of stop (rest, meal, overnight, or required weekly rest); the travel day; the driving time durations since the last stop, since the morning, and since the beginning of the week; and the arrival and departure times. A node is represented by the following n-tuple?

$$x_{n}=(i_{n},p_{n},k_{n},h_{n}^{1},h_{n}^{2},h_{n}^{3},a_{n},d_{n},\delta_{n})$$

in which:

$i_{n}$ stoppage location identifier associated with node $X_{n}$

p,type of stop associated to node $X_{n}$ , where the value of $p_{n}\in\{1$ , 2, 3, 4} corresponds, respectively, to a short rest stop, a meal, an overnight stay, or the required weekly rest; $k_{n}$ current travel day in node $X_{n}$ , counted sequentially beginning in the departure from the origin (the first day corresponds tc

$k_{n}=1$ 牌$h_{n}^{1}$ $h_{n}^{2}$ drving time sine erevou rest tops

$h_{n}^{3}$ driving time that week, $a_{n}$ arrival time at node $X_{n}$ $d_{n}$ departure time from node $x_n$ $\delta_{n}$ signals whether the main meal of the day has happened ( $\delta_{n}=1$ ) or not $(\delta_{n}=0$

Arc: In a generic graph search problem, an arc represents an ordered link between two consecutive nodes, $X_{m}$ and $\Lambda_{\mathrm{R}}$ .Let $\iota\left(i_m,i_n,d_m\right)$ dm $d_{m}$ be the travel time between locations $i_{m}$ and $i_{n}$ given departure time $d_{m}$ , and consider that after stopping at $i_{rve}$ the driver will make a subsequent stop at $i_{n}$ and that this stop will be of type $P_n\in$ [1, 2, 3, 4}. The following equations are then valid

$$\begin{aligned}
&\text{k} \left.=\left\{\begin{matrix}{k_{m}}&{\mathrm{if}}&{p_{m}\in\{1,2}\\{k_{m}+1}&{\mathrm{if}}&{p_{m}=3}\\{k_{m}+2}&{\mathrm{if}}&{p_{m}=4}\\\end{matrix}\right.\right.  \\
&h_n^1 =t(i_{m},i_{n},d_{m})  \\
&h_{n}^{2} =\begin{cases}h_{m}^{2}+t\left(i_{m},\:i_{n},\:d_{m}\right)&\mathrm{if}\:p_{m}\in\{1,\:2\}\\t\left(i_{m},\:i_{n},\:d_{m}\right)&\mathrm{if}\:p_{m}\in\{3,\:4\}\end{cases}  \\
&h_n^3 =\begin{cases}h_{m}^{3}+t\left(i_{m},i_{n},d_{m}\right)&\mathrm{if}\quad p_{m}\in\{1,\:2,\:3\\t\left(i_{m},\:i_{n},\:d_{m}\right)&\mathrm{if}\quad p_{m}\in\{4\}\end{cases}  \\
&a_{n} =d_{m}+t(i_{m},i_{n},d_{m})
\end{aligned}$$

------------------------------------------------------------------

$$\left.d_{n}\geq\left\{\begin{array}{lll}a_{n}+T_{1}&\mathrm{if}&p_{m}\in\{1\}\\max\left[a_{n},W_{k_{n}}^{stan(meal)}\right]+T_{2}&\mathrm{if}&p_{m}\in\{2\}\\max\left[a_{n}+T_{3},W_{k_{n}+1}^{stanr(day)}\right]&\mathrm{if}&p_{m}\in\{3\}\\max\left[a_{n}+T_{4},W_{k_{n}+2}^{stanr(day)}\right]&\mathrm{if}&p_{m}\in\{4\}\end{array}\right.\right.$$

$$\delta_n=\begin{cases}0&\text{if}\quad p_n\in\{3,\:4\}\\\delta_m&\text{if}\quad p_n\in\{1\}\\1&\text{if}\quad p_n\in\{2\}\end{cases}$$

where $T_{\mathrm{i}}$ $T_{2}$ $T_{3}$ and $T_{4}$ are a required minimum length of time to a rest stop, a meal, an overnight stay, and a required weekly rest Eq. (23) determine the day in which a stop described by node $X_{n}$ occurs, counting from the beginning of the route. If the previous stop in the configuration, described by node $X_{m}$ , was a meal stop or a rest stop, the next stop, forming configuration $X_{n}$ will occur on the same day. If the previous stop was an overnight, the subsequent stop will occur the next day. Finally, if the previous stop was a weekly downtime stop, the subsequent stop will occur only after the driver remains at that stop at least for the required weekly rest time, usually at least one whole day, in which case it will be two days later. Eq. (24) requires that uninterrupted driving time be the elapsed time between two consecutive stop locations. Eq. (25) accumulate the elapsed time in the current workday, expressing it as the sum of the accumulated driving time in the day and the driving time between location stops if the previous stop was for rest or meal. If the previous stop was an overnight or weekly rest stop, the daily workday time count is reinitiated. Eq. (26) are analogous but refer to elapsed time in the current workweek, a count which reinitiates after a weekly downtime stop. Eq. (27) is necessary to determine the arrival time associated with the stoppage configuration described by node $X_{n}$ , considering that the driver left the previous stop location $i_{m}$ at the time $d_{na}$ and took $\iota(i_{ne}$ $i_{r}$ $d_{m}$ ) in transit until arriving at location $i_{n}$ . Eq. (28) are used to determine if the departure time from the stoppage configuration described by node $X_{n}$ is feasible, depending on the respective stop type and arrival times. If node $X_{n}$ refers to a rest stop $(p_{n}=1$ ), departure cannot occur earlier than $T_{1}$ units of time after arrival. If it refers to a meal stop $(p_{n}=2$ ), departure cannot occur earlier than an elapsed time $T_{2}$ for the meal. In addition, the earliest beginning time for meals at the $k_{\mathrm{н}}^{th}$ day cannot oceur before $W_{k_n}^{\text{slart( merat)}}$ In case $X_{n}$ is an overnight stop $(p_{n}=3$ ), the minimum rest period is given by $T_{3}$ ,and the following workday (i.e, driving) cannot begin before time $W_{k_n+1}^{\text{start }(\text{day})}$ If the stop is for the weekly downtime rest $(p_{n}=4$ ), the total minimum stoppage time is $T_{i}$ , and the following workweek (i.e., driving) cannot begin before time $W_{k_n+2}^{\text{sfarl (day)}}.$ Finally, Eq. (29) are used to update $\delta_{re}$ , the parameter that signals whether the driver has had the main meal of the day. The existence of an arc $(x_{m},x_{n})$ is conditioned to $h_{n}^{1}$ ， $h_{\mathrm{H}}^{2}$ and $h_{n}^{3}$ satisfying the driving time requirements set by regulations

including labor agreements:

$$\begin{aligned}&h_{n}^{1}\leq L_{dr\nu}\\&h_{n}^{2}\leq L_{nor}+L_{ovr}\\&h_{n}^{3}\leq L_{\mathrm{weck}}\end{aligned}$$

in which $L_{\mathrm{d}n}$ $L_{\mathrm{HO}}+L_{\mathrm{OW}}$ and $L_{\text{week}}$ are, respectively: the maximum allowed continuous driving period (i.e., without any rest stops); the maximum allowed driving time in a workday (normal plus allowed overtime labor hours); and the maximum allowed driving time in a workweek. In addition, the time of the main meal in the $k_n^{lh}$ workday needs to occur within the $[W_{k_n}^{\text{start (moul)}}]$ $W_{k_n}^{\mathrm{end}(\text{лаеаГ})}$I time window so a stop

configuration with $\delta_{n}=0$ on the $k_n^{m}$ workday is only feasible ifarrival occurs before $W_{k_n}^{\mathrm{end}(\text{mend})}$ ,that is:

$$a_{n}\leq W_{k_{n}}^{end(meal)}\quad\mathrm{if}\:\delta_{n}=0$$

Successor operator r: Any two stoppage configurations, ie., any two nodes in the graph described by $x_{m}= ( i_{m}$, $p_{m}$ ， $k_{m}$ $h_{m}^{1}$ $h_{m}^{2}$ $h_m^5$ $a_{m}$ $d_{m}$ $\partial_{m}$ ) and $x_{n}=(i_{n},p_{n}$ $k_{n}$ $h_{n}^{1}$ $h_n^2$ $h_n^3$ $a_{n}$ $d_{n}$ $\partial_n)$ , will be connected by an arc $(x_{m},x_{n})$ if and only if it is feasible for the driver to transition (relocate) from the state represented by the stoppage configuration described in node $X_{m}$ ,to the state represented by the stoppage configuration described in node $X_{p}$ , and there have a stop of type $P_{n}$ Eqs. (23)(33) determine the feasibility of each such transition. Consequently, from any node $X_{m}$ a set of feasible states, i.e., of feasible stoppage configurations represented by adjacent nodes $\{x_n$ [x $\{x_n,x_{n+1},x_{n+2}\}$ .], can be generated. Given the continuous nature of time-dependent elements or parameters that comprise a node's n-tuple (such as driving times as well as arrival and departure times), the state-space graph has an unlimited number of successor nodes. In order to limit the size of the state-space representation (i.e., the size of the graph), node pruning is used to generate only the most promising successor nodes during an expansion. Consequently the successor operator I generates the set of stoppage configurations by: (a) examining the Cartesian product of all

possible stoppage types $p\in\{1$ , 2, 3, 4} and locations $i_n$ which can be reached from $i_{m}$ in a time not greater than the regulated maximum uninterrupted driving time ( $.L_{\mathrm{d}rv}$, , considering as departure time only the minimum feasible value $d_{n}$ ; and (b) eliminating options that do not satisfy one or more of Eqs. (23)(33), ie., eliminating all infeasible candidates. The option of considering only the minimum feasible departure time stems from the fact that less stoppage time is better than more because there are significant costs that increase with the total duration of the trip, such as the opportunity cost of asset utilization, cost of capital applied to fixed assets and cost of parking, among others.

------------------------------------------------------------------

The application of the successor operator $\Gamma$ to a node $X_{m}$ is also referred to as the expansion of node $X_{m}$ . The condition in whicl $\{x_n,x_{n+1},x_{n+2},...\}$ are successors of $X_{m}$ and/or in which $X_{ne}$ is a predecessor of each node in $\{x_n$ [xn $\{x_n,x_{n+1},x_{n+2}$, ..), or in other words, the expansion of node $X_{m}$ results from the application of successor operator $\Gamma$ in a sequential process that builds out the graph Consequently, the following obtains:

$$\Gamma(x_m)=\{x_n,x_{n+1},x_{n+2},\:...\}$$

4.2.Determining the cost of an arc

In this formulation there is a cost associated to each arc $(x_{m},x_{n})$ that includes the cost of physical movement (relocation) from stoppage location $i_{m}$ to stoppage location $i_{n}$ and the cost of a stop of type p ∈ [1, 2, 3, 4} at location $i_n$ , among others. The following describes all such aggregate arc cost components:

a) driver compensation (including benefits), which is a function of hours on the job, hours of overtime driving, social security and other taxes, benefits such as health and life insurance, and other components b) truck travel costs, including fuel, other supplies such as lubricants, and maintenance expenses including tires, which are usually a

function of the time and/or distance covered:

c) vehicle fixed costs, such as depreciation, the cost of immobilized capital, taxes, insurance, which usually are proportional to the total elapsed time of each activity or trip leg

d) costs of services incurred in stoppage locations which are charged per unit of time (parking expenditures, etc.), costs which are a function of the elapsed time incurred;

e) costs of services incurred in stoppage locations which are not charged per unit of time (meals, overnight stays, etc.); f) opportunity cost for the allocation of the asset (the vehicle) to this particular assignment (trip), which is proportional to travel

time and represents the expected foregone operating income incurred for not assigning the particular truck to another job during the duration of the trip. From an accounting perspective this is not an operating cost, but rather an expected contribution to income from alternative asset utilization. As described in the previous section, this is a necessary consideration whenever two or more routes are compared: foregone operating income associated to additional travel time must be added when comparing two alternative routing/scheduling combinations. Lastly,

g) a potential penalty cost to express the need to arrive at the final destination before a deadline

Therefore, the cost $c(x_{m},x_{n})$ associated to an arc connecting configurations represented by nodes $X_{m}$ and $x_{n}\in\Gamma(x_{m})$ ,may be calculated as follows:

$$c(x_{m},x_{n})=c_{1}t(i_{m},i_{n},\:d_{m})+c_{2}[i_{n}](d_{n}-a_{n})+c_{3}(i_{n},\:p_{n})+\\c_{4}[a_{n}-d_{m}]+c_{9}max[0,\:a_{n}-max(T_{max},\:a_{m})]+c_{6}(h_{m}^{2},\:h_{m}^{2},\:p_{m})$$

in which:

$c_{1}$ is the cost of truck relocation per unit of time expressed as \$/hour which includes costs described above in (b) and (c); $c_{2}(i_{n})$ is the stoppage cost per unit of time in location $i_n$ , expressed as \$/hour which includes costs described in (c) and (d) above

$c_{3}(i_{n},p_{n})$ is the cost of non-time-dependent services incurred in stoppage location $i_n$ during a stop of type $P_{n}$ which includes costs described in (e) above; $C_{4}$ is, without loss of generality, the opportunity cost applied to the time incurred between departure from stoppage location $i_{m}$ and

arrival to stoppage location $i_n$ and described in (f) above, is considered to be linear in time; $Cs$ is the penalty cost per hour incurred if deadline $T_{max}$ is not respected; and

$c_{6}(h_{m}^{2},h_{n}^{2},p_{m})$ is the daily labor cost which includes costs described above in (a) calculated as

$$c_6(h_m^2,h_n^2,p_m)=\begin{cases}S(h_n^2)-S(h_m)&\text{if}\:p_m\in\{1,\:2\}\\\quad S(h_n^2)&\text{if}\:p_m\in\{3,\:4\}\end{cases}$$

where $S(h)$ is the driver cost for $k$ working hours in the respective day, given by

$$S\left(h\right)=\left\{\begin{matrix}S_{nor}L_{nor}&\mathrm{if}\quad h\leq L_{nor}\\S_{nor}L_{nor}+S_{nor}(h-L_{nor})&\mathrm{if}\quad L_{nor}<h\leq L_{nor}+L_{nor}\end{matrix}\right.$$

where $S_{\mathrm{mor}}$ and $S_{\mathrm{ovr}}$ correspond to the hourly labor driving costs (including benefits) in both normal and overtime and $L_{\mathrm{nov}}$ and $L_{007}$ are respectively the maximum permitted daily normal and overtime driving times In Eq. (36), the driver labor cost on arc $(x_{m},x_{n})$ is calculated in two different ways depending on the type of stoppage config

uration $X_{m}$ . If stoppage configuration $Xm$ corresponds to an overnight $(p_{m}=3$ ) or to a weekly rest $(p_{m}=4)$ , the labor cost on the respective arc will take into account only the driving time that day until stoppage configuration $X_{n}$ ,that is, $h_m^2$ . If configuration $X_{ne}$ corresponds to a rest $(P_{m}=1$ ) or meal $(p_{m}=2$ ) stop, labor driving costs on the respective arc through configuration $X_{n}$ should be calculated based on the day's driving time, $h_{n}^{2}$ , less the labor driving costs through the predecessor configuration.

------------------------------------------------------------------

## 5. The graph search algorithm

The previous section described the steps needed to create the graph of states (or stoppage configurations) between the origin and the destination of a full-load trucking route through the sequential node expansion process using the successor operator I. In this state-space graph the route and schedule of the lowest cost trip will correspond to the shortest path of stoppage configurations linking the initial state associated with the origin and a final state associated with arrival to the destination. It is important to note that although at first examination it may appear otherwise, the VRTDSPIS state-space graph may not be a tree: there may be more than one way to reach a given stoppage configuration

Dijkstra (1959) was one of the first to address the problem of finding a minimum cost path between an origin node $x_{\mathrm{s}}\in X$ and a destination node $x_{t}\in X$ ,where $X$ is the set of all nodes in a graph. Associated with each node $x_{n}\in X$ there is a label $[\hat{g}(x_n)$ ,pred $(x_n)].$ in which $\hat{g}(x_n)$ is the current lowest cost sequence of nodes that connects the origin $X_{x}$ to node $X_{n}$ , and pred $(x_n)$ is the predecessor (the preceding node) to $X_{n}$ in this sequence. Two subsets of nodes are defined in this algorithm: $X_{\mathrm{T}}\subseteq X$ is a subset labeled temporary and $X_{P}\subsetneq X$ is a subset labeled permanent. At each stage Dijkstra's algorithm selects node $Xm$ with lowest cost $\hat{g}\left(x_m\right)$ in the temporary subset, includes it in the permanent subset, and applies a successor operator I to this node to determine its successors, which are added to the temporary subset. All costs in the graph are non-negative so once a node $X_{\mathrm{H}}$ is selected, it represents the lowest cost alternative to that node, so it is excluded from the subset $X_{7}$ and included in the set $X_{\mathrm{P}}$ . This process is repeated until the destinatior node is selected as having the lowest value of $\hat{g}\left(x_m\right)$ among all the nodes labeled as temporary. When this occurs the lowest cost path between the origin node $x_{\mathrm{s}}\in X$ and the final destination node $x_{\mathrm{r}}\in X$ is determined as it will not be possible to reach the destination node $x_{\mathrm{r}}\in X$ at a cost lower than $\hat{g}\left(x_{t}\right)$ . The lowest cost path is recovered through the sequence of predecessor nodes

## 5.1. VRTDSPIS state-space graph properties influencing the algorithm

The actual physical road network consists of tens of thousands of road segments and stoppage locations (such as gas stations, rest areas, parking sites, road-side restaurants, road-side overnight sites, etc.) Although the driver is assumed to always choose the lowest cost route to relocate from any point to another, a given stoppage location can be reached through many different sequences of predecessor stoppage points, with the result that any location can be reached at different times, and therefore characterizing different stoppage configurations in the space of states. Because of the combinatorial nature of possible alternatives to arrive at a given stoppage location, the number of nodes in the graph is very high, and because of the continuous nature of the elapsed time dimension the number of feasible successors to a given node may be unlimited. As a result, we suggest a pruning criterion to eliminate routing and scheduling alternatives which are less promising, i.e., which are less likely to result in a route and schedule to reach the final destination at minimum cost. This proposed pruning criterion is based on the concept of weak dominance between nodes, as de veloped in this section

Definition 1:. Two nodes $X_{m}$ and $X_{n}$ are defined as similar in elements $(i,p)$ ,represented with the notation $x_{m}^{(t,p)}\equiv x_{n}^{(t,p)}$ ， $if$ and only if $i_{m}=i_{m}$ and $P_{\mathrm{m}}=P_{\mathrm{m}}$

In other words, two stoppage configurations are similar in elements $(i,p)$ , if the stop occurs in the same location with the same objective. Please note that nodes which are similar in elements (i, p) may (and likely will) have different arrival times and different costs ${\widehat g}\left(x\right)$,

Definition 2:. $X_{m}$ weakly dominates $X_{n}$ , (or, analogously, $X_{n}$ is weakly dominated by $X_{H}$ )if and only if $x_{m}^{(i,p)}\equiv x_{n}^{(i,p)}$ and ${\widehat{g}}\left(x_{m}\right)<{\widehat{g}}\left(x_{n}\right)$

Proposition:. Consider that $x_{\mathrm{H}}^{(\mathrm{i,p})}\equiv x_{n}^{(\mathrm{i,p})}$ . Then, if $X_{m}$ weakly dominates $X_{n\pi}$ i.e., $f$ ${\hat{g} }\left ( x_{m}\right ) < {\hat{g} }\left ( x_{n}\right )$ there is no evidence that the lowest cost path between the origin and the destination configurations includes node $X_{n}$ . Consequentiy, node $X_{n}$ can be pruned

Demonstration: Let $\hat{h}(x_m)$ and $\hat{\hbar}(x_n)$ be, respectively, cost estimates for the routes to be taken from nodes $X_{m}$ and $X_{p}$ to node 1. If $x_m^{(i,p)}\equiv x_n^{(i,p)}$ then $\hat{h}=\hat{\hbar}\left(x_{m}\right)\cong\hat{\hbar}\left(x_{n}\right)$ since $\hat{h}\left(x_m\right)$ and $\hat{h}\left(x_n\right)$ depends essentially on the stoppage location and type of $X_{m}$ and $X_{n}$ , which are the same. Thus, if $Xm$ weakly dominates $X_{n}$ , i.e., ${\widehat g}\left(x_{m}\right)<{\widehat g}\left(x_{n}\right)$ ,then $\hat{g}\left(x_{m}\right)+\hat{h}\left(x_{m}\right)<\hat{g}\left(x_{n}\right)+\hat{h}\left(x_{n}\right)$ . Therefore there is no evidence that the path containing $X_{n}$ is preferable to the path that contains $X_{ne}$

Pruning nodes in the graph is not without disadvantages as the guarantee of optimality is lost. Without pruning, the model itself remains unchanged but the resulting processing time increases dramatically because the time dimension in the state space graph is not discrete, but rather continuous, which generates an unlimited number of successors for any node. Therein lies the need for a rule of dominance between pairs of nodes, the basis for pruning

### 5.2.The algorithm

Let s, $l\in N$ be respectively the origin and destination of a trip and $x_{0}=(i_{0},p_{0}$ $k_{\mathrm{t}}$ $h_{0}^{1}$ $h_0^2$ $h_0^3$ $a_0$ d $d_0$ $d_0,\delta_0)$ $\delta_0$ be the initial state or stoppage configuration at the origin $i_{0}=s$ , i.e., the location in which the trip originates, as described in Section 4.1. We now turn to finding a low cost path in the pruned graph of states connecting the origin to the destination and propose an algorithm that uses a node elimination process based on the weak dominance concept described above. The search algorithm consists of the following steps: S1. Initialization: Set the initial node $x_{0}=(i_{0}=s$ $P_{0}$ kahghhg $a_{0}$ ， $d_{\mathrm{o}}$ $\delta_{\mathrm{r}}$ ) and destination location $\in N$ . Let $\hat{\mathbf{g}}\left(x_{0}\right)\leftarrow0$

$pred(x_0)\leftarrow nil$ ， $X_{\mathrm{T}}=\varnothing$ and $X_{\mathrm{P}}=\{x_{0}\}$ . Let $x_{m}=x_{0}$

------------------------------------------------------------------

S2. Graph expansion:For each node $x_n\in\Gamma(x_m)$ do a) if $\exists$ $x_{k}\in X_{P}| x_{k}^{( i, p) }\equiv x_{n}^{( 1, p) }$ , discard $X_{n}$ b) otherwise, calculate $\beta\leftarrow\widehat{g}(x_{m})+c(x_{m},x_{n})$ ,and

b.1) if 3 $x_{k}\in X_{\mathrm{T}}|x_{\mathrm{K}}^{(i,p)}\equiv x_{\mathrm{n}}^{(i,p)}$ and $\geq\hat{g}\left(x_{k}\right)$ , discard $X_{p}$ b.2) if 3 $x_{k}\in X_{T}|x_{k}^{(t,p)}\equiv x_{n}^{(i,p)}$ and $<\hat{g}\left(x_{k}\right)$ , set $X_{T}\leftarrow X_{T}\cup\{x_{n}\}-\{x_{k}\}$ and update $X_{n}$ 's label letting $\hat{\mathbf{g}}\left(x_{n}\right)\leftarrow\beta$ and prea $I(x_{n})\leftarrow x_{m}$ b.3) else let $X_{T}\leftarrow X_{T}\cup\{x_{n}\}$ and update $X_{n}$ 's label letting $\hat{\mathbf{g}}\left(x_{n}\right)\leftarrow\beta$ and $pred(x_{n})\leftarrow x_{m}$

S3. Node selection: If $X_{T}=\mathbb{Q}$ , there is no feasible sequence of stoppage configurations that satisfies all the conditions of the problem; exit with falure. Otherwise selet a configration $x_{m}\in X_{\mathrm{T}}$ such that ${\widehat{g}}\left(x_{m}\right)=min_{x\in X_{\Gamma}}{\widehat{g}}\left(x\right)$ Let $X_{\mathrm{T}}\leftarrow X_{\mathrm{T}}-\{x_{\mathrm{m}}\}$ and $X_{P}\leftarrow X_{P}\cup\{x_{m}\}$

S4. Termination test: If for configuration $X_{m}$ we have $i_{m}=0$ , then finalize with success: the sequence of stoppages is determined by the predecessors of the configuration ending in $Xm$ . Otherwise return to step S2

## 6.Evaluation of the economic impact of a policy change

## 6.1. Brazilian context and recent regulatory change

Brazil is a country with continental dimensions covering more almost half $(47.5\%)$ of South America and accounting for roughly half its inhabitants: it is the fifth country in the world both in size, with 8.5 million square kilometers, and in population, with an estimated 210 million inhabitants in 2019 (IBGE, 2019). It is a developing country with a 2017 GDP of over US\$ 2 trillion, ranking as the 9th largest economy in the world (World Bank, 2019). The average annual economic growth rate between 2000 and 2018 was $2.4\%$ , with the agricultural output growth far surpassing that rate. Brazil is currently the largest world exporter of coffee, sugar orange juice, and soy, among other commodities, and agribusiness exports grew by $328\%$ during that same period (Cepea, 2018) corresponding to an annual growth rate of $8.4\%$ .Given the country's dimensions and the lack of an integrated country-wide railroad system, long-haul trucking in all its forms is the main method of freight transportation. Despite continuing efforts to improve logistics infrastructure, periodic disruptions either during harvest as agribusiness products are transported from the interior to ports, or throughout the year due to unexpected events, are not uncommon In this context it is no surprise that professional truck driving is a stressful occupation that has statistically been at or near the top

of the road fatality rates every year between 2007 and 2016 (DNIT, 2019). Road accidents involving professional truck drivers have different causes but a large number is linked to the significant geographical distances leading to long trips, the difficulty in planning due to unexpected events and sparse infrastructure in some parts of the country, the pressure to deliver loads on time, and the long periods at the wheel with little or no rest leading to fatigue and slower reflexes, all of which have been found to contribute to lower road safety levels. In the first half of the decade societal pressure to implement public policies enhancing road safety and truck driver well-being increased, leading to a new set of regulations finally enacted into law in 2015. It is important to recognize that while the legislation is necessary to enhance road safety, the increased travel time due to longer and more frequent required rest stops impacts road freight operations and costs, especially for longer trips lasting more than one day. Therefore, careful planning of these trips is necessary and a clear understanding of the economic impact of policy changes is desirable. The current Brazilian regulations governing professional truck and bus driving activity result from law $n^{\circ}$ 13.103/2015, which

covers both passenger and freight transportation and was approved on March 2, 2015. Essentially this law aims to improve professional driver working conditions and to increase highway safety focusing on driver well-being by providing rest and recovery requirements during trips as well as mandating periodic drug tests to ensure compliance. This law adapted some stipulations contained in the Brazilian Consolidacdo das Leis do Trabalho (CLT) that aggregates federal labor laws, and the Codigo de Trainsito Brasileiro (CTB), the Brazilian traffic federal code to discipline professional drivers’ workdays driving time. This law also revoked some legal provisions in previous regulations governing the professional driving activity, namely law n° 12.619/2012, because this law ignored

Table 1 Professional driving requirements for Scenarios I and II

<table>
 <tbody>
  <tr>
   <th>Driving requirements</th>
   <th>Scenario I (before law)</th>
   <th>Scenario II (after law)</th>
  </tr>
  <tr>
   <td>Start time of work dav $(W_\mathrm{c}^{\text{slart}(duy)}y$</td>
   <td>06:00 am</td>
   <td>07{:}00 am</td>
  </tr>
  <tr>
   <td> </td>
   <td>8h</td>
   <td>8h</td>
  </tr>
  <tr>
   <td>$ff$</td>
   <td>6h</td>
   <td>4h</td>
  </tr>
  <tr>
   <td>rivin $\cdot ff$</td>
   <td>8h</td>
   <td>5.5 h</td>
  </tr>
  <tr>
   <td>Maximi Pekls drivine Lime $:(L$,</td>
   <td>84 h</td>
   <td>$72h$</td>
  </tr>
  <tr>
   <td>Start time for lunch $(W_k^{start(m\text{eu})}$to $W_k^{\mathrm{end}(m\text{ea}l)})$</td>
   <td>11:30 to 15:00</td>
   <td>12{:}00 to 14:00</td>
  </tr>
  <tr>
   <td>$\lim_{n\to\infty}\frac{1}{n^{2}}$ ripet 7 $(T_1)$</td>
   <td>no regulated</td>
   <td>15 min</td>
  </tr>
  <tr>
   <td>lunch (Tz)</td>
   <td>1h</td>
   <td>1h</td>
  </tr>
  <tr>
   <td>time $(T_{3})$</td>
   <td>$10h$</td>
   <td>$111h$</td>
  </tr>
  <tr>
   <td>time $(T_{4})$</td>
   <td>$35h$</td>
   <td>$35h$</td>
  </tr>
 </tbody>
</table>

------------------------------------------------------------------

Table2 Cost parameters.

<table>
 <tbody>
  <tr>
   <th>Cost Parameters</th>
   <th>Cast (RS/hour)</th>
  </tr>
  <tr>
   <td>(normal)</td>
   <td>15.91</td>
  </tr>
  <tr>
   <td>Prive hondw P 119 e (overtime)</td>
   <td>23.86</td>
  </tr>
  <tr>
   <td>Ferima l costs - truck</td>
   <td>5.05</td>
  </tr>
  <tr>
   <td>Fetimated hor maintenance</td>
   <td>90.30</td>
  </tr>
  <tr>
   <td>terims rating costs</td>
   <td>111.26</td>
  </tr>
  <tr>
   <td>tetimated F freicht rater</td>
   <td>147.00</td>
  </tr>
  <tr>
   <td>nitw rost</td>
   <td>35.74</td>
  </tr>
 </tbody>
</table>

some professional driver demands

Table 1 depicts the parameters for two different scenarios. Scenario II represents professional driving conditions required by law $\mathrm{n}^{\circ}13.103/2015$ and Scenario I represents the previous reality. The 2015 law changed prior practices by establishing specific limits to the driving activity, mainly in the following ways:

(a) by capping the number of daily overtime driving hours permitted during a trip to two hours, and exceptionally to four hours if specifically allowed by a union labor agreement (b) by capping uninterrupted continuous driving time at 5 h and 30 min; (c) by capping the total number of driving hours in a week; (d) by establishing a required stop in an appropriate rest area of at least fifteen minutes for every five-and-a-half hours of uninterrupted driving; (e) by establishing a minimum required rest time of eleven hours between consecutive driving days.

## 6.2. Operational costs and impact on one illustrative route

The operational costs related to each application of the successor operator as explained in Section 4.2 above, i.e., with each arc in the graph, are calculated through Eq. (35). Table 2 depicts the costs observed at the time of the approval of the legislation. In Table 2 normal and overtime pay rates include social security and other payroll charges required by law. Capital costs for the

truck are fixed monthly costs that include depreciation as well as vehicle taxes and fees also required by law. These monthly costs were allocated on an hourly basis to obtain the estimates in Table 2. Truck travel costs are costs that vary with distance travelled including fuel and maintenance costs such as oil, tires, filters, etc. These costs were allocated on an hourly basis to obtain the estimates in Table 2. The sum of the driver hourly pay rate, the estimated hourly truck capital costs, and the truck travel variable costs represents the total estimated hourly travel operating costs. Subtracting this value from the estimated hourly revenue given the freight rate at the time of the law and average distance travelled per hour, the estimated hourly operating income obtains. The opportunity cost refers to this hourly operating income, i.e., the average hourly contribution obtained from truck use in freight transportation. In other words, an additional hour the asset (the truck) needs to spend in any given trip through an alternative route implies not using this asset (the truck) in an another revenue-generating transportation job. As an illustrative example, consider a long-haul full-truckload trip between the cities of Brasilia and Uruguaiana, manned by one

driver. We consider two economic agents in long-haul transport, the driver and the owner of the truck, and in Brazil it is not uncommon for these two agents to be the same person (an independent trucker). Brasilia, the country's capital is located in the mid western region and Uruguaiana in the extreme south, at a distance of over 2,000 km (more than 1,250 miles). Tables 3 and 4 show results of the application of the algorithm to the two scenarios. The data base used to calculate these routes is the road transport network digitalized by the Brazilian national land transportation agency, the federal Agencia Nacional de Transportes Terrestre: (ANTT). For route calculation, support infrastructure for overnight, meals, fuel, and short rest stops were assumed to exist only in the proximity of towns or municipality seats, a situation that reflects the sparse support network existent in most of the country. In this example, there was a significant change in the trip, not only regarding the stoppage schedule,but also regarding the route

Table3 Route and scheduled stops for Brasilia-Uruguaiana trip considering the regulatory environment before enactment of law n 13.103/2015 (Scenario I).

<table>
 <tbody>
  <tr>
   <th>Local</th>
   <th>Stoppage type</th>
   <th>Arrive</th>
   <th>Departure</th>
   <th>Travel time (hours)</th>
   <th>Rest time (hours)</th>
   <th>Travel distance (km</th>
  </tr>
  <tr>
   <td>Brasilia</td>
   <td> </td>
   <td> </td>
   <td>Mon. 06:00</td>
   <td> </td>
   <td> </td>
   <td> </td>
  </tr>
  <tr>
   <td>Comendador Gomes</td>
   <td>lunch</td>
   <td>Mon. 13:50</td>
   <td>Mon. 14:50</td>
   <td>7.83</td>
   <td>1.00</td>
   <td>577.94</td>
  </tr>
  <tr>
   <td>Ocaucu</td>
   <td>overnight</td>
   <td>Mon. 19:55</td>
   <td>Tue. 06:00</td>
   <td>5.09</td>
   <td>10.07</td>
   <td>354.01</td>
  </tr>
  <tr>
   <td>Guamiranga</td>
   <td>lunch</td>
   <td>Tue. 13:05</td>
   <td>Tue. 14:05</td>
   <td>7.09</td>
   <td>1.00</td>
   <td>427.34</td>
  </tr>
  <tr>
   <td>Frederico Westphalen</td>
   <td>overnight</td>
   <td>$Tue.20:56$</td>
   <td>Wed.06:56</td>
   <td>6.85</td>
   <td>10.00</td>
   <td>455.14</td>
  </tr>
  <tr>
   <td>Sio Luiz Gonzaga</td>
   <td>lunch</td>
   <td>Wed.11:31</td>
   <td>Wed. 12:31</td>
   <td>4.59</td>
   <td>1.00</td>
   <td>276.47</td>
  </tr>
  <tr>
   <td>Uruguaiana</td>
   <td> </td>
   <td>Wed.16:52</td>
   <td> </td>
   <td>4.35</td>
   <td> </td>
   <td>286.79</td>
  </tr>
  <tr>
   <td>Total</td>
   <td> </td>
   <td>58.87 h</td>
   <td> </td>
   <td>35.80</td>
   <td>23.07</td>
   <td>2,377.69</td>
  </tr>
 </tbody>
</table>

------------------------------------------------------------------

Table 4 Route and scheduled stops for Brasilia-Uruguaiana trip considering the regulatory environment after enactment of law n’ 13.103/2015 (Scenario II)
<table>
 <tbody>
  <tr>
   <th>Local</th>
   <th>Stoppage type</th>
   <th>Arrive</th>
   <th>Departure</th>
   <th>Travel time(hours)</th>
   <th>Rest time (hours)</th>
   <th>Travel distance(km)</th>
  </tr>
  <tr>
   <td>Brasilia</td>
   <td> </td>
   <td> </td>
   <td>Mon. 07:00</td>
   <td> </td>
   <td> </td>
   <td> </td>
  </tr>
  <tr>
   <td>Campo Alegre de Goias</td>
   <td>quiek rest</td>
   <td>Mon. 10:51</td>
   <td>Mon. 11:06</td>
   <td>3.85</td>
   <td>0.25</td>
   <td>239.82</td>
  </tr>
  <tr>
   <td>Araguari</td>
   <td>lunch</td>
   <td>Mon. 13:30</td>
   <td>Mon. 14:30</td>
   <td>2.40</td>
   <td>1.00</td>
   <td>148.66</td>
  </tr>
  <tr>
   <td>Leme</td>
   <td>overnight</td>
   <td>Mon. 19:54</td>
   <td>$Tue.07{:}00$</td>
   <td>5.40</td>
   <td>11.10</td>
   <td>434.58</td>
  </tr>
  <tr>
   <td>Cajati</td>
   <td>lunch</td>
   <td>Tue. 11:49</td>
   <td>Tue. 13:00</td>
   <td>4.82</td>
   <td>1.18</td>
   <td>403.57</td>
  </tr>
  <tr>
   <td>Fazenda Rio Grande</td>
   <td>quiek rest</td>
   <td>Tue. 15:39</td>
   <td>Tue. 15:54</td>
   <td>2.65</td>
   <td>0.25</td>
   <td>205.75</td>
  </tr>
  <tr>
   <td>Sio Cristovăo do Sul</td>
   <td>overnight</td>
   <td>Tue. 19:28</td>
   <td>Wed. 07: 00</td>
   <td>3.57</td>
   <td>11.53</td>
   <td>268.62</td>
  </tr>
  <tr>
   <td>Sto. Antõnio do Planalto</td>
   <td>lunch</td>
   <td>Wed. 12: 03</td>
   <td>Wed. 13: 03</td>
   <td>5.05</td>
   <td>1.00</td>
   <td>382.24</td>
  </tr>
  <tr>
   <td>Bozano</td>
   <td>quiek rest</td>
   <td>Wed.14:33</td>
   <td>Wed. 14:48</td>
   <td>1.50</td>
   <td>0.25</td>
   <td>101.14</td>
  </tr>
  <tr>
   <td>Sio Borja</td>
   <td>overnicht</td>
   <td>Wed. 18:55</td>
   <td>Thu. 07:00</td>
   <td>4.12</td>
   <td>12.08</td>
   <td>242.86</td>
  </tr>
  <tr>
   <td>Uruguaiana</td>
   <td> </td>
   <td>Thu. 09:44</td>
   <td> </td>
   <td>2.73</td>
   <td> </td>
   <td>186.46</td>
  </tr>
  <tr>
   <td>T $0Lal$</td>
   <td> </td>
   <td>74.73 h</td>
   <td> </td>
   <td>36.09</td>
   <td>38.64</td>
   <td>2.613.70</td>
  </tr>
 </tbody>
</table>

itself, as can be observed in Fig. 1. Although there was a significant increase in distance traveled, from 2,377.69 km to 2,613.70 km the total driving time was approximately the same at roughly $36h$ . This occurred because the recent law is more restrictive and the algorithm picked roads with higher speed limits, closer to the coast, with a denser support network, all of which leads to more flexibility when selecting stoppage locations. On the other hand, the total elapsed time, which was slightly under 59 h before the law came into effect, went up to $74h$ and three quarters afterwards, a consequence of the need to stop more frequently and for longer periods as required by the 2015 law. Table 5 presents a summary of the costs in these two routes. Although actual driving time in both scenarios is very similar at $36h$

the added restrictions imposed by the 2015 legislation led to a reduction in overtime hours, which was compensated with more nonovertime driving hours, resulting in a small reduction in driver pay. However, it is important to note that because the total elapsed time is longer in Scenario II, the driver actually faces a reduction in income of $23.0\%$ during the elapsed time away. On the other hand, from the point of view of the owner of the truck, the total cost of the trip increases by R$ 712.25, from R$

4,385.17 to R$ 5,097.42, i.e., a $16.2\%$ increase.Part of this increase, a manageable RS 144.99, or 3.396 of the original operating costs, results from the recent legislation’s requirement for additional stops and resulting increase in paid services along the route. However. the component that contributes most to the total cost increase is foregone income associated with the increase in travel time, namely the excess opportunity cost of truck use, which rises by R$ 567.26 (from R$ 2,104.29 to R$ 2,671.55), i.e., due to longer truck time "at rest."

If it is not possible to pass along the increase in opportunity cost to the customer through higher freight pricing because of competition and/or other factors, the truck owner would need to regard this increase in costs as a reduction in the expectation of

![](https://storage.simpletex.cn/view/fGwGORMbF2bF40U9ZBAEEaFd3WTY6623D)

Fig. 1. Routes for travel from Brasilia to Uruguaiana applying the algorithm to Scenarios I and II (Google Maps).

------------------------------------------------------------------

Table 5 Evaluation of the economic impact of the two policies (Scenario I and Il), specifically for the Brasilia to Uruguaiana trip case
<table>
 <tbody>
  <tr>
   <th>Item description</th>
   <th>Unit</th>
   <th>Scenario I</th>
   <th>Scenario II</th>
   <th>Variation</th>
   <th> </th>
   <th>Impact</th>
  </tr>
  <tr>
   <td>Total travel time</td>
   <td>haurs</td>
   <td>58.88</td>
   <td>74.75</td>
   <td>15.87</td>
   <td>$27.0\%$</td>
   <td> </td>
  </tr>
  <tr>
   <td>$\cdot Rest$ time</td>
   <td>hours</td>
   <td>23.07</td>
   <td>38.63</td>
   <td>15.56</td>
   <td>67.496</td>
   <td>$26.4\%$</td>
  </tr>
  <tr>
   <td>$\cdot$Travel time</td>
   <td>hours</td>
   <td>35.81</td>
   <td>36.12</td>
   <td>0.31</td>
   <td>0.996</td>
   <td>$0.5\%$</td>
  </tr>
  <tr>
   <td>Driver normal working hours</td>
   <td>hours</td>
   <td>24.00</td>
   <td>26.75</td>
   <td>2.75</td>
   <td>$11.5\%$</td>
   <td>$4.7\%$</td>
  </tr>
  <tr>
   <td>Driver overtime hours</td>
   <td>hours</td>
   <td>11.81</td>
   <td>9.37</td>
   <td>2.44</td>
   <td>-20.796</td>
   <td>-4.196</td>
  </tr>
  <tr>
   <td>Travel cost</td>
   <td>$RS$</td>
   <td>4,385,17</td>
   <td>5,097.42</td>
   <td>712.25</td>
   <td>16.296</td>
   <td> </td>
  </tr>
  <tr>
   <td>$\cdot$Cost of services / stops</td>
   <td>$RS$</td>
   <td>190.51</td>
   <td>242.47</td>
   <td>51.96</td>
   <td>27.396</td>
   <td>1.296</td>
  </tr>
  <tr>
   <td>$\cdot$Driver's pay</td>
   <td>$RS$</td>
   <td>663.64</td>
   <td>649.04</td>
   <td>-14.60</td>
   <td>-2.296</td>
   <td>-0.396</td>
  </tr>
  <tr>
   <td>Driver's normal pay</td>
   <td>$RS$</td>
   <td>381.84</td>
   <td>425.59</td>
   <td>43.75</td>
   <td>$11.5\%$</td>
   <td>1.096</td>
  </tr>
  <tr>
   <td>Driver's overtime pay</td>
   <td>$RS$</td>
   <td>281.80</td>
   <td>223.45</td>
   <td>-58.35</td>
   <td>-20.796</td>
   <td>-1.396</td>
  </tr>
  <tr>
   <td>Driver's income in time away</td>
   <td>RS/haur</td>
   <td>11.27</td>
   <td>8.68</td>
   <td>-2.59</td>
   <td>-23.096</td>
   <td> </td>
  </tr>
  <tr>
   <td>$\cdot Vehiclecost$</td>
   <td>$RS$</td>
   <td>3.531.02</td>
   <td>3.638.65</td>
   <td>107.63</td>
   <td>3.096</td>
   <td>2.596</td>
  </tr>
  <tr>
   <td>Parked vehicle cost</td>
   <td>$RS$</td>
   <td>116.49</td>
   <td>195.11</td>
   <td>78.62</td>
   <td>67.596</td>
   <td>1.896</td>
  </tr>
  <tr>
   <td>Traveling vehicle cost</td>
   <td>$RS$</td>
   <td>3,414.53</td>
   <td>3,443.54</td>
   <td>29.01</td>
   <td>0.896</td>
   <td>$0.7\%$</td>
  </tr>
  <tr>
   <td>Excess travel time opportunity cost</td>
   <td>$RS$</td>
   <td> </td>
   <td>567.26</td>
   <td>567.26</td>
   <td> </td>
   <td>$12.9\%$</td>
  </tr>
  <tr>
   <td>Total travel distance</td>
   <td>km</td>
   <td>2,377.69</td>
   <td>2.613.70</td>
   <td>236.01</td>
   <td>9.996</td>
   <td> </td>
  </tr>
 </tbody>
</table>

contribution to profits from R$ 35.74 (see Table 2) per hour to a lower amount, which in effect represents a reduction in the truck's opportunity cost. The owner would need to deduct the aggregate increase in costs of stops, rest services, driver pay, and vehicle, i.e. R$ 144.99 (=51.96-14.60+107.63) ,from the expected contribution to profits. Should the freight price continue unaltered, this trip's contribution to profits would be reduced by R$ 144,99. In addition, this contribution to profits is diluted over a period of $74h$ and three quarters instead of the original $59h$ , which represents a reduction from RS 35.74 per hour to RS 26.21 per hour, i.e., a $26.7\%$ lower contribution to freight profits per unit of time.

6.3. An economic impact evaluation of the 2015 law governing Brazilian professional driving

In order to assess the economic impact of law No. 13.103/2015 on the Brazilian road freight market, the analysis performed in Section 6.2 was extended to a set of 151 trips made between eighteen different cities, distributed throughout Brazil, as follows: five cities located in the Midwest region (Brasilia, Campo Grande, Cuiaba, Palmas, and Sinop); two cities in the Northeast region (Recife and Salvador); three cities in the North region (Belem, Porto Velho, and Sao Luis); five cities in the Southeast region (Aracatuba, Belo Horizonte, Niter6i, Sao Jose do Rio Preto, and Sao Paulo); and three cities in the South region (Foz do Iguacu, Pelotas, and Uruguaiana). Table 6 presents aggregate results, i.e., the sum total for each line item, corresponding to a route grand total of ap proximately 313,500 km with point-to-point travel distances ranging from 160 to $4800km$ Comparing the two scenarios it is apparent that the same total distance that before the change in policy had been traveled by a

vehicle in 7,991.43 h is traveled in 9,224.98 h after the implementation of the new law. This represents a $15.4\%$ increase in truck allocation time. On the other hand, there was a $3.1\%$ reduction in total driver-earned income for this set of trips, from R$ 88,885.83 to R$ 86,093.80. Although there was no significant variation in total actual driving time, the total elapsed time for these routes increased from 7,991.43 h to 9,224.98 h , as mentioned above, and when accounting for the average hourly driver income during time away, a reduction of $16.1\%$ is observed, from 11.12 R$/hour to 9.33 RS/hour. Although this reduction in driver income per period is smaller than that reported for the trip between Brasilia and Uruguaiana in Section 6.2 above, it is still a significant amount.

Table 6 Evaluation of the economic impact of the two policies (Scenario I and Il), on a set of 151 different trips involving 18 Brazilian cities.

<table>
 <tbody>
  <tr>
   <th>Item description</th>
   <th>Unit</th>
   <th>Scenario I</th>
   <th>Scenario II</th>
   <th>Variation</th>
   <th> </th>
   <th>Impact</th>
  </tr>
  <tr>
   <td>Total travel time</td>
   <td>haurs</td>
   <td>7.991.43</td>
   <td>9.224.98</td>
   <td>1,233.55</td>
   <td>$15.4\%$</td>
   <td> </td>
  </tr>
  <tr>
   <td>$\cdot Resttime$</td>
   <td>haurs</td>
   <td>3,192.98</td>
   <td>4.424.07</td>
   <td>1,231.09</td>
   <td>$38.6\%$</td>
   <td>15.495</td>
  </tr>
  <tr>
   <td>·Travel time</td>
   <td>haurs</td>
   <td>4.798.45</td>
   <td>4.800.91</td>
   <td>2.46</td>
   <td>$0.1\%$</td>
   <td>0.095</td>
  </tr>
  <tr>
   <td>Driver normal working hours</td>
   <td>haurs</td>
   <td>3,220.92</td>
   <td>3.579.28</td>
   <td>358.36</td>
   <td>$11.1\%$</td>
   <td>4.595</td>
  </tr>
  <tr>
   <td>Driver overtime hours</td>
   <td>haurs</td>
   <td>1.577.53</td>
   <td>1,221.63</td>
   <td>-355.90</td>
   <td>$-22.6\%$</td>
   <td>-4.590</td>
  </tr>
  <tr>
   <td>Travel cost</td>
   <td>RS</td>
   <td>590.763.46</td>
   <td>603,796.50</td>
   <td>13,033.04</td>
   <td>$2.2\%$</td>
   <td> </td>
  </tr>
  <tr>
   <td>- Cost of services / stops</td>
   <td>RS</td>
   <td>28,964.27</td>
   <td>38,002.12</td>
   <td>9.037.85</td>
   <td>$31.2\%$</td>
   <td>$1.5\%$</td>
  </tr>
  <tr>
   <td>$\cdot$Driver"s pay</td>
   <td>RS</td>
   <td>88,885.83</td>
   <td>86,093.80</td>
   <td>-2,792.03</td>
   <td>-3.196</td>
   <td>-0.590</td>
  </tr>
  <tr>
   <td>Driver's normal pay</td>
   <td>RS</td>
   <td>51.245.25</td>
   <td>56,946.54</td>
   <td>5.701.29</td>
   <td>$11.1\%$</td>
   <td>1.0%</td>
  </tr>
  <tr>
   <td>Driver's overtime pay</td>
   <td>RS</td>
   <td>37,640.58</td>
   <td>29,147.26</td>
   <td>-8.493.32</td>
   <td>$-22.6\%$</td>
   <td>-1.490</td>
  </tr>
  <tr>
   <td>Driver's income in time away</td>
   <td>RS/hour</td>
   <td>11.12</td>
   <td>9.33</td>
   <td>-1.79</td>
   <td>-16.196</td>
   <td> </td>
  </tr>
  <tr>
   <td>$\cdot Vehiclecost$</td>
   <td>RS</td>
   <td>472,913.36</td>
   <td>479.700.58</td>
   <td>6.787.22</td>
   <td>1.496</td>
   <td>1.29</td>
  </tr>
  <tr>
   <td>Parked vehicle cost</td>
   <td>RS</td>
   <td>16,124.23</td>
   <td>22,341.65</td>
   <td>6.217.42</td>
   <td>$38.6\%$</td>
   <td>1.195</td>
  </tr>
  <tr>
   <td>Traveling vehicle cost</td>
   <td>RS</td>
   <td>456.789.13</td>
   <td>457,358.93</td>
   <td>569.80</td>
   <td>$0.1\%$</td>
   <td>0.195</td>
  </tr>
  <tr>
   <td>Aggregate excess opportunity cost</td>
   <td>RS</td>
   <td> </td>
   <td> </td>
   <td>44,215.10</td>
   <td> </td>
   <td>7.59</td>
  </tr>
  <tr>
   <td>Total travel distance</td>
   <td>km</td>
   <td>313.840.88</td>
   <td>313.495.74</td>
   <td>-345.14</td>
   <td>$-0.1\%$</td>
   <td> </td>
  </tr>
 </tbody>
</table>

------------------------------------------------------------------

Table 7 Economic impact of law $n^{*}$ 13.103/2015, per range of distance.
<table>
 <tbody>
  <tr>
   <th>From</th>
   <th>To</th>
   <th>% Increase in market fleet</th>
   <th>% Reduction in hourly driver's pay</th>
   <th>% Reduction in owner bourly income</th>
  </tr>
  <tr>
   <td>0 $km$</td>
   <td>800 km</td>
   <td>18.196</td>
   <td>$15.8\%$</td>
   <td>$20.8\%$</td>
  </tr>
  <tr>
   <td>km 800</td>
   <td>1,600 km</td>
   <td>19.096</td>
   <td>$18.3\%$</td>
   <td>$20.6\%$</td>
  </tr>
  <tr>
   <td>km 1,600</td>
   <td>2,400 km</td>
   <td>14.196</td>
   <td>$15.5\%$</td>
   <td>15.496</td>
  </tr>
  <tr>
   <td>km 2,400</td>
   <td>3,200 km</td>
   <td>15.096</td>
   <td>$16.3\%$</td>
   <td>$16.9\%$</td>
  </tr>
  <tr>
   <td>km 3,200</td>
   <td>4,000 km</td>
   <td>11.696</td>
   <td>$13.1\%$</td>
   <td>$13.5\%$</td>
  </tr>
  <tr>
   <td>km 4.000</td>
   <td>4,800 km</td>
   <td>20.396</td>
   <td>$18.5\%$</td>
   <td>$22.5\%$</td>
  </tr>
  <tr>
   <td>Overall</td>
   <td> </td>
   <td>15.496</td>
   <td>16.196</td>
   <td>17.496</td>
  </tr>
 </tbody>
</table>

Lastly, and directly affecting the truck owner's income, an increase in travel costs (including service/stop costs, driver payments and vehicle costs) is observed, as it rises by R\$ 13,033.04, from R\$ 590,763.46 to R\$ 603,796.50. If it turns out to be impossible to pass along that increase in costs to freight prices due to market competitive pressures or another reason, the contribution to profits (which had been RS 285,333.36 in the previous regime) will be reduced. In other words, the owner's hourly rate, i.e., the hourly contribution to the owner's profits, which under the previous regulatory regime had been R\$ 35.70 = = (=285,333.36 / 7,991.43) decreased to R\$ 29.52 = = (=(285,333.36-13,033.04)/9,224.98) after approval of the law, representing a $17.4\%$ reduction in the owner's expected hourly income for asset use. In order to assess the effect of the new law for different distances, Table 7 depicts the economic impact grouped by distance

traveled. Two different situations should be examined to understand the implications of these results for the long-haul point-to-point full

load trucking freight market in Brazil

a) that of medium- and large-scale trucking companies with fleets of hundreds of trucks; b) that of independent truckers (transportadores autonomos) who often own trucks and provide services as free-lancers without a sophisticated support infrastructure.

Medium- and large-scale trucking companies have efficient operating modus operandi and may be able to engage in driver relaying in some long trips through use of hubs for driver substitution and rest. This can allow truckers to fulfill regulatory overnight or weekend rest requirements at pre-determined locations and be relieved by fresh drivers upon arrival. Such relay systems result in a much more efficient asset utilization rate, as trucks do not stop for long rest periods. Conversely, when independent truckers conduct long-haul full-load travel, the asset's allocative efficiency (the truck's usage rate) is affected because the truck also stops when the driver rests. Independent trucking operators are less affected with double-teaming (i.e., if two drivers share the entire long-haul drive), but even in this case they are at a disadvantage when compared to the hub relay system for two reasons. First, the other driver may need to be paid for at least a portion of non-driving idle time. Second, Law $\mathbf{n}^{\circ}13.103$ imposes restrictions to continuous driving even in that situation (e.g., the requirement to stop for six hours of “overnight” every three days even when the relay driver goes with the main driver in the truck). In short, when compared to the previous reality, independent truckers and their vehicles experiment an increase in stoppage time and frequency for meals, rest, overnights, and weekly rest. Trucking companies are able to operate with lower hourly operational costs under the new regulatory framework and therefore can secure the larger transportation contracts perhaps even outsourcing other business to independent truckers. In turn, these independent truckers, when faced with higher operating costs, cannot offset them by increasing freight prices, so they run the risk of losing business to the more efficient freight companies their only other option is to accept lower margins by absorbing the increase in operating costs, which as illustrated in this section, are not insignificant

### 7.Conclusion

The research problem and resolution methods proposed in this paper were motivated by a very practical problem in Brazil and other emerging market countries with large territories where long-haul point-to-point trucking is an important (sometimes the predominant) transportation method, and regulatory frameworks are still being developed. The desirability of maintaining highway safety standards in the face of increasing traffic volume has led to increased and detailed trucking industry regulations through hours of service limits, driver working condition safeguards, and rest requirements. This paper provides a solution for the generic problem in a subset of the vehicle routing and driver scheduling models, the long-haul full-load vehicle routing and truck driver scheduling problem with intermediate stops for refueling and rest, subject to regulatory requirements. The paper contributes to the literature by characterizing the problem, suggesting a generic mathematical optimization formulation, modeling the problem as a graph in a state space of feasible stoppage configurations, presenting an algorithmic solution to find the lowest cost path in this graph, and providing an illustration of its use by evaluating the economic impact of a regulatory change in Brazil. In addition to the proposed solution method through a state-space graph with a Dijkstra-based algorithm, its use in policy analysis also is an important contribution. The methodology and algorithm proposed herein can be helpful for policy design both in the ex-ante planning stage by examining the economic impact of different regulatory scenarios and in the ex-post evaluation stage by comparing before and after conditions. The paper illustrates the algorithm’s applicability to policy design by evaluating the economic impact of the 2015 change in regulations

------------------------------------------------------------------

governing trucking in Brazil. When long-haul trucking is subject to additional constraints, such as reductions in maximum consecutive driving hours, increases in mandatory rest time frequency and length, and other safety-inducing requirements, longer elapsed travel time and higher costs are to be expected. It becomes important to examine these increases in travel time and costs to understand how different stakeholders are affected.

In the Brazilian example that illustrates the methodology, one main objective of the new law was to enhance driver well-being and highway safety. According to the World Health Organization, 1,350,000 people die each year as a result of traffic accidents, with a disproportionate number occurring in low-income countries, in which roughly one percent of the world's motor vehicles account for thirteen percent of the deaths (WHO, 2020). In Brazil road safety is a major issue, as traffic deaths are a leading cause of mortality, at an annual rate of 19.7 deaths per 100,000 inhabitants (WHO, 2020), higher than the average of middle-income countries in the Americas. Although there were 28.6 million automobiles and two million trucks circulating in Brazil as of the passing of Law $n^{\circ}$ 13.103 in 2015, trucks had been involved in 42 percent of fatal accidents while cars had been involved in 64.4 percent (some such deaths involved both cars and trucks) with fatalities occurring in fewer than five percent of accidents, but representing 35 percent of the total cost of accidents in the country (IPEA, 2015). Narciso and Mello (2017) had examined the impact of fatigue on professional drivers in Brazil comparing eight-hour, ten-hour, and twelve-hour work days with a limit of five hours and thirty minutes of uninterrupted driving time and found that the “fatigue index” increased from 18.8 to 27.1 to 37.8 respectively in each case. While enactment of Law n° 13.103 has contributed to increase highway safety in the country, several other road safety initiatives have been implemented in recent years as well, so the precise role and economic impact of that law in Brazil's highway safety is a suggestion for additional research that arises from this work. The main advantage of an algorithm such as the one developed and described in this paper is that potential increases in time and

costs can be quantified so policy-makers may have a clearer idea of the potential economic impact of regulatory changes, including how different stakeholders are affected. The illustration presented in Section 6 points to some interesting consequences of improved driver regulations in addition to increased highway safety. Both drivers and vehicle owners see their hourly income per trip decrease One immediate consequence is that because transportation fleets have more flexibility to adapt their operations, such as hiring permanent drivers based out of different cities, establishing relay teams in frequently traveled long-haul routes, and providing lower cost support within a trip, they will be better able to adapt to lower hourly income than independent operators. Long-haul freight prices are usually point-to-point and distance-based, but hourly returns for labor (driver) and capital (truck) will tend to go down. Besides being less able to absorb higher costs leading to lower returns, independent operators are almost always price-takers as they have very little bargaining power. Because of superior operations and higher bargaining power, transportation companies will be able to absorb more business, which may result in crowding-out of independent drivers, who sometimes but not always may be able to obtain jobs outsourced by companies who find themselves at capacity. It is interesting to note that in 2018 in Brazil there was a general strike of independent truckers, who among other demands requested a floor to freight prices. Lastly, it is important to note that the methodology described in this paper has embedded parametric flexibility that makes it

useful for other regulatory environments. Indeed, with only slight modifications, the mathematical formulation and the algorithmic solution presented herein are robust to all regulatory requirements the authors are aware of. In an era in which many countries need to improve road safety while also dealing with the economic pressure of ever-increasing costs, we believe that algorithmic tools such as the one developed in this research can be very helpful to policy-makers in both the planning and the evaluation stages of regulatory analysis.

### CRediT authorship contribution statement

Sergio Fernando Mayerle: Conceptualization, Methodology, Data curation, Writing - review & editing, Software, Validation Daiane Maria De Genaro Chiroli: Conceptualization, Methodology, Data curation, Writing - original draft, Writing - review & editing. Joao Neiva Figueiredo: Methodology, Data curation, Writing - original draft, Writing - review & editing. Hidelbrand Ferreira Rodrigues: Visualization, Investigation

Declaration of Competing Interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Appendix A. Supplementary material

Supplementary data to this article can be found online at https://doi.org/10.1016/j.tra.2020.07.021

References

Alcaraz, J., Caballero-Arnaldos, L., Vales-Alonso, J., 2019. Rich vehicle routing with last-mile outsourcing decisions. Transport Res E 129, 263286. ANTr, 2012. Agencia Nacional de Transportes Terrestres. Available at: http://www.antt.gov.br/. Accessed on 17 June 2014. BRASlL, 2015. From the Brazilian Diario Oficial da Uniao. 3 mar 2015. Law number 13.103 altering labor laws for truck drivers, i.e., altering law number 12.619, de 30 de abril de 2012. Available at http://www.planalto.gov.br/ccivil_03/Ato2015-2018/2015/Lei/L13103.htm and accessed on December 28 2018 Cepea (Centro de estudos avancados em economia aplicada, Esalq/USP), 2018. Indice de exportacao do agronegocio. https://www.cepea.esalq.usp.br/upload

------------------------------------------------------------------

kceditor/files/Cepea_ExportAgro_2018_.pdf, accessed on October 4, 2019. Cesell, A., Righini, G., Salani, M., 2009. A column generation algorithm for a rich vehicle-routing problem. Transp. Sci. 43 (1), 5669. https:/doi.org/10.1287/rsC 1080.0256 Chiroli, D.M.G., Rodrigues, H.F., Mayerle, S.F., 2016. Problem Truck driver scheduling and routing HOS: A study of scientific production. Espacios. 37 (04), 17. Dell'Amico, M., lori, M., Pretolani, D., 2008. Shortest paths in piecewise continuous time-dependent networks. Oper. Res. Lett. 36, 688691. Dijkstra, E.W., 1959. A note on two problems in connexion with graphs. Numer. Math. 1 (1), 269271. https://doi.org/10.1007/BF01386390. Eksioglu, B., Vural, A.V., Reisman, AL., 2009. The vehicle routing problem: A taxonomic review. Comput. Ind. Eng. 57, 14721483. Gendreau, M., Ghiani, G., Guerriero, E., 2015. Time-dependent routing problems: A review. Comput. Oper. Res. 64, 189197. Goel, A., 2009. Vehicle scheduling and routing with drivers" working hours. Transport Sci. 43, 1726. Goel, A., 2012a. The Canadian minimum duration truck driver scheduling problem. Comput. Oper. Res. 39, 23592367 Goel, A., 2012b. A mixed integer programming formulation and effective cuts for minimising schedule durations of Australian truck drivers. J. Sched. 15, 733741 Goel, A., 2018. Legal aspects in road transport optimization in Europe. Transport Res. E 114, 144-162 Goel, A., Archetti, C., Savelsbergh, M., 2011. Truck driver scheduling in Australia. Comput. Oper. Res. 39, 11221132 Goel, A., Irmich, S., 2017. An exact method for vehicle routing and truck driver scheduling problems. Transport Sci. 51 (2), 737754. https://doi.org/10.1287/trsc. 2016.0678 Goel, A., Kok, AL.L., 2011. Truck driver scheduling in the United States. Transport Sci. 46, 317326. Goel, A., Rousseau, L.M., 2011. Truck driver scheduling in Canada. J. Sched. 15, 783799 Goel, A., Vidal, T., 2014. Hours of service regulations in road freight transport: an optimization-based international assesment. Transport Sci. 48, 391412 Goel, A, Vidal, T., Kok, A.L., 2019. To team up or not Single versus team driving in European road freight transport. https://w1.cirrelt.ca/vidalt/papers/Team-vs Single.pdf accessed August 30, 2019. Tech. rep., PUCRio, Rio de Janeiro, Brasil. Hart, P, Nilsson, Nils J., Bertram, Raphael, 1968. A formal basis for the heuristic determination of minimum cost paths. IEEE Trans. Syst. Sci. Cyber. 4 (2), 100107. https://doi.0rg/10.1109/TS5C.1968.300136. IBGE (Instituto Brasileiro de Geografia e Estatistica), 2019. IBGE divulga as estimativas da populacao dos municipios para 2019. https://agenciadenoticias.ibge.gov. br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/25278-ibge-divulga-as-estimativas-da-populacao-dos-municipios-para-2019, accessed on October 2, 2019. IPEA, 2015 (Instituto de Pesquisa Economica Aplicada) Traffic accidents on Brazilian federal highways: characterization, trends and costs for society. http://re positorio.ipea.gov.br/bitstream/11058/7493/1/RP_Acidentes _2015.pdf. Koc, C, Jabali, O., Laporte, G., 2018. Long-haul vehicle routing and scheduling with idling options. J. Oper. Res. Soc. 69 (2), 235246. https:/doi.org/10.1057/ s41274-017-0202-y. Laporte, G., Gendreau, M., Ppotvin, J-Y., Semet, F., 2000. Classical and modem heuristies for the vehicle routing problem. Inl Trans. Op. Res. 7, 285300. Narciso, F.V., Mello, M.T., 2017. Seguranca e saide dos motoristas profissionais que trafegam nas rodovias do Brasil. Rev Saade Piblica 2017, 51126 Prescott-Gagnon, E., Desaulniers, G., Drexl, M, Rousseau, LM., 2010. European driver rules in vehicle routing with time windows. Transport Sci. 44, 455473. Savelsbergh, M, Sol, M., 1998. DRIVE: dynamic routing of independent vehicles. Oper. Res. 46, 474490. Schiffer, M., Schneider, M., Walther, G., Laporte, G., 2019. Vehicle routing and location routing with intermediate stops: A review. Transport Sci. 53 (2), 319343 https://doi.org/10.1287/trsc.2018.0836 Vidal, T., Crainic, T.G., Gendreau, M., Prins, C., 2015. Time-window relaxations in vehicle routing heuristies. J. Heuristies 21, 329358 Vidal, T., Laporte, G., Matl, P., 2019. A Concise Guide to Existing and Emerging Vehicle Routing Problem Variants. ArXiv:1906.06750 [Cs], June 16, 2019, http:// arxiv.org/abs/1906.06750. Wen, L., Catay, B., Eglese, R., 2014. Finding a minimum cost path between a pair of nodes in a time-varying road network with a congestion charge. Eur. J. Oper. Res. 236, 915923. WHO, 2020. World Health Organization. Global status report on road safety 2018. https://www.who.int/violence_injury_prevention/road safety status/2018/en/ World Bank, 2019. The World Bank in Brazil. https://data.worldbank.org/country/brazil accessed on October 2, 2019. Xu, H., Chen, Z., Rajagopal, S., Arunapuram, S., 2003. Solving a practical pickup and delivery problem. Transport Sci. 37, 347364.
