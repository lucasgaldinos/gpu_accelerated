TSPLIB 95
Gerhard Reinelt
Universität Heidelberg
Institut für Angewandte Mathematik
Im Neuenheimer Feld 294
D-69120 Heidelberg
Gerhard.Reinelt@IWR.Uni-Heidelberg.DE

TSPLIB is a library of sample instances for the TSP (and related problems) from various
sources and of various types. Instances of the following problem classes are available.
Symmetric traveling salesman problem (TSP)
Given a set of n nodes and distances for each pair of nodes, find a roundtrip of minimal
total length visiting each node exactly once. The distance from node i to node j is the
same as from node j to node i.
Hamiltonian cycle problem (HCP)
Given a graph, test if the graph contains a Hamiltonian cycle or not.
Asymmetric traveling salesman problem (ATSP)
Given a set of n nodes and distances for each pair of nodes, find a roundtrip of minimal
total length visiting each node exactly once. In this case, the distance from node i to node
j and the distance from node j to node i may be different.
Sequential ordering problem (SOP)
This problem is an asymmetric traveling salesman problem with additional constraints.
Given a set of n nodes and distances for each pair of nodes, find a Hamiltonian path from
node 1 to node n of minimal length which takes given precedence constraints into account.
Each precedence constraint requires that some node i has to be visited before some other
node j.
Capacitated vehicle routing problem (CVRP)
We are given n − 1 nodes, one depot and distances from the nodes to the depot, as well as
between nodes. All nodes have demands which can be satisfied by the depot. For delivery
to the nodes, trucks with identical capacities are available. The problem is to find tours for
the trucks of minimal total length that satisfy the node demands without violating truck
capacity constraint. The number of trucks is not specified. Each tour visits a subset of the
nodes and starts and terminates at the depot. (Remark: In some data files a collection of
alternate depots is given. A CVRP is then given by selecting one of these depots.)
Except, for the Hamiltonian cycle problems, all problems are defined on a complete graph
and, at present, all distances are integer numbers. There is a possibility to require that
certain edges appear in the solution of a problem.

11. The file format
Each file consists of a specification part and of a data part. The specification part
contains information on the file format and on its contents. The data part contains explicit
data.

1.1 The specification part
All entries in this section are of the form <keyword> : <value>, where <keyword> denotes an alphanumerical keyword and <value> denotes alphanumerical or numerical data.
The terms <string>, <integer> and <real> denote character string, integer or real data,
respectively. The order of specification of the keywords in the data file is arbitrary (in
principle), but must be consistent, i.e., whenever a keyword is specified, all necessary information for the correct interpretation of the keyword has to be known. Below we give a
list of all available keywords.
1.1.1

NAME : <string>

Identifies the data file.
1.1.2

TYPE : <string>

Specifies the type of the data. Possible types are
TSP
Data for a symmetric traveling salesman problem
ATSP
Data for an asymmetric traveling salesman problem
SOP
Data for a sequential ordering problem
HCP
Hamiltonian cycle problem data
CVRP
Capacitated vehicle routing problem data
TOUR
A collection of tours
1.1.3

COMMENT : <string>

Additional comments (usually the name of the contributor or creator of the problem instance is given here).
1.1.4

DIMENSION : <integer>

For a TSP or ATSP, the dimension is the number of its nodes. For a CVRP, it is the total
number of nodes and depots. For a TOUR file it is the dimension of the corresponding
problem.
1.1.5

CAPACITY : <integer>

Specifies the truck capacity in a CVRP.
1.1.6

EDGE WEIGHT TYPE : <string>

Specifies how the edge weights (or distances) are given. The values are
EXPLICIT
Weights are listed explicitly in the corresponding section
Weights are Euclidean distances in 2-D
EUC 2D
EUC 3D
Weights are Euclidean distances in 3-D
MAX 2D
MAX 3D
MAN 2D
MAN 3D
CEIL 2D
GEO
ATT
XRAY1
XRAY2
SPECIAL
1.1.7

Weights are maximum distances in 2-D
Weights are maximum distances in 3-D
Weights are Manhattan distances in 2-D
Weights are Manhattan distances in 3-D
Weights are Euclidean distances in 2-D rounded up
Weights are geographical distances
Special distance function for problems att48 and att532
Special distance function for crystallography problems (Version 1)
Special distance function for crystallography problems (Version 2)
There is a special distance function documented elsewhere

EDGE WEIGHT FORMAT : <string>

Describes the format of the edge weights if they are given explicitly. The values are
FUNCTION
Weights are given by a function (see above)
FULL MATRIX
Weights are given by a full matrix
UPPER ROW
Upper triangular matrix (row-wise without diagonal entries)
Lower triangular matrix (row-wise without diagonal entries)
LOWER ROW
UPPER DIAG ROW
Upper triangular matrix (row-wise including diagonal entries)
LOWER DIAG ROW
Lower triangular matrix (row-wise including diagonal entries)
Upper triangular matrix (column-wise without diagonal entries)
UPPER COL
LOWER COL
Lower triangular matrix (column-wise without diagonal entries)
Upper triangular matrix (column-wise including diagonal entries)
UPPER DIAG COL
LOWER DIAG COL
Lower triangular matrix (column-wise including diagonal entries)
1.1.7

EDGE DATA FORMAT : <string>

Describes the format in which the edges of a graph are given, if the graph is not complete.
The values are
The graph is given by an edge list
EDGE LIST
ADJ LIST
The graph is given as an adjacency list
1.1.9

NODE COORD TYPE : <string>

Specifies whether coordinates are associated with each node (which, for example may be
used for either graphical display or distance computations). The values are
TWOD COORDS
Nodes are specified by coordinates in 2-D
Nodes are specified by coordinates in 3-D
THREED COORDS
NO COORDS
The nodes do not have associated coordinates
The default value is NO COORDS.
1.1.10 DISPLAY DATA TYPE : <string>
Specifies how a graphical display of the nodes can be obtained. The values are
COORD DISPLAY
Display is generated from the node coordinates
Explicit coordinates in 2-D are given
TWOD DISPLAY
NO DISPLAY
No graphical display is possible
The default value is COORD DISPLAY if node coordinates are specified and NO DISPLAY
otherwise.
1.1.11 EOF :
Terminates the input data. This entry is optional.

1.2 The data part
Depending on the choice of specifications some additional data may be required. These
data are given in corresponding data sections following the specification part. Each data
section begins with the corresponding keyword. The length of the section is either implicitly
known from the format specification, or the section is terminated by an appropriate endof-section identifier.
1.2.1

NODE COORD SECTION :

Node coordinates are given in this section. Each line is of the form
<integer> <real> <real>
if NODE COORD TYPE is TWOD COORDS, or
<integer> <real> <real> <real>
if NODE COORD TYPE is THREED COORDS. The integers give the number of the respective
nodes. The real numbers give the associated coordinates.
1.2.2

DEPOT SECTION :

Contains a list of possible alternate depot nodes. This list is terminated by a −1.
1.2.3

DEMAND SECTION :

The demands of all nodes of a CVRP are given in the form (per line)
<integer> <integer>
The first integer specifies a node number, the second its demand. The depot nodes must
also occur in this section. Their demands are 0.
1.2.4

EDGE DATA SECTION :

Edges of a graph are specified in either of the two formats allowed in the EDGE DATA FORMAT
entry. If the type is EDGE LIST, then the edges are given as a sequence of lines of the form
<integer> <integer>
each entry giving the terminal nodes of some edge. The list is terminated by a −1.
If the type is ADJ LIST, the section consists of a list of adjacency lists for nodes. The
adjacency list of a node x is specified as
<integer> <integer> . . . <integer> −1
where the first integer gives the number of node x and the following integers (terminated
by −1 ) the numbers of nodes adjacent to x. The list of adjacency lists is terminated by
an additional −1.

1.2.5

FIXED EDGES SECTION :

In this section, edges are listed that are required to appear in each solution to the problem.
The edges to be fixed are given in the form (per line)
<integer> <integer>
meaning that the edge (arc) from the first node to the second node has to be contained in
a solution. This section is terminated by a −1.
1.2.6

DISPLAY DATA SECTION :

If DISPLAY DATA TYPE is TWOD DISPLAY, the 2-dimensional coordinates from which a display
can be generated are given in the form (per line)
<integer> <real> <real>
The integers specify the respective nodes and the real numbers give the associated coordinates.
1.2.7

TOUR SECTION :

A collection of tours is specified in this section. Each tour is given by a list of integers giving
the sequence in which the nodes are visited in this tour. Every such tour is terminated by
a −1. An additional −1 terminates this section.
1.2.8

EDGE WEIGHT SECTION :

The edge weights are given in the format specified by the EDGE WEIGHT FORMAT entry. At
present, all explicit data is integral and is given in one of the (self-explanatory) matrix
formats. with implicitly known lengths.
2. The distance functions
For the various choices of EGDE WEIGHT TYPE, we now describe the computations of the repsective distances. In each case we give a (simplified) C-implementation for computing the
distances from the input coordinates. All computations involving floating-point numbers
are carried out in double precision arithmetic. The integers are assumed to be represented
in 32-bit words. Since distances are required to be integral, we round to the nearest integer (in most cases). Below we have used the rounding function “nint” (“nint(x)” can be
replaced by “(int) (x+0.5)”).

2.1 Euclidean distance (L2 -metric)
For edge weight type EUC 2D and EUC 3D, floating point coordinates must be specified for
each node. Let x[i], y[i], and z[i] be the coordinates of node i.
In the 2-dimensional case the distance between two points i and j is computed as follows:
xd = x[i] - x[j];
yd = y[i] - y[j];
dij = nint( sqrt( xd*xd + yd*yd) );
In the 3-dimensional case we have:
xd = x[i] - x[j];
yd = y[i] - y[j];
zd = z[i] - z[j];
dij = nint( sqrt( xd*xd + yd*yd + zd*zd) );
where sqrt is the C square root function.

2.2 Manhattan distance (L1 -metric)
Distances are given
They are computed
2-dimensional case:
xd = abs( x[i]
yd = abs( y[i]
dij = nint( xd
3-dimensional case:
xd = abs( x[i]
yd = abs( y[i]
zd = abs( z[i]
dij = nint( xd

as Manhattan distances if the edge weight type is MAN 2D or MAN 3D.
as follows.
- x[j] );
- y[j] );
+ yd );
+

x[j]
y[j]
z[j]
yd +

);
);
);
zd );

2.3 Maximum distance (L∞ -metric)
Maximum distances are computed if the edge weight type is MAX 2D or MAX 3D.
2-dimensional case:
xd = abs( x[i] - x[j] );
yd = abs( y[i] - y[j] );
dij = max( nint( xd ), nint( yd ) ) );
3-dimensional case:
xd = abs( x[i] yd = abs( y[i] zd = abs( z[i] dij = max( nint(

x[j] );
y[j] );
z[j] );
xd ), nint( yd ), nint( zd ) );

2.4 Geographical distance
If the traveling salesman problem is a geographical problem, then the nodes correspond to
points on the earth and the distance between two points is their distance on the idealized
sphere with radius 6378.388 kilometers. The node coordinates give the geographical latitude and longitude of the corresponding point on the earth. Latitude and longitude are
given in the form DDD.MM where DDD are the degrees and MM the minutes. A positive latitude is assumed to be “North”, negative latitude means “South”. Positive longitude means
“East”, negative latitude is assumed to be “West”. For example, the input coordinates for
Augsburg are 48.23 and 10.53, meaning 48o 23´ North and 10o 53´ East.
Let x[i] and y[i] be coordinates for city i in the above format. First the input is converted
to geographical latitude and longitude given in radians.
PI = 3.141592;
deg = nint( x[i] );
min = x[i] - deg;
latitude[i] = PI * (deg + 5.0 * min / 3.0 ) / 180.0;
deg = nint( y[i] );
min = y[i] - deg;
longitude[i] = PI * (deg + 5.0 * min / 3.0 ) / 180.0;
The distance between two different nodes i and j in kilometers is then computed as follows:
RRR = 6378.388;
q1 = cos( longitude[i] - longitude[j] );
q2 = cos( latitude[i] - latitude[j] );
q3 = cos( latitude[i] + latitude[j] );
dij = (int) ( RRR * acos( 0.5*((1.0+q1)*q2 - (1.0-q1)*q3) ) + 1.0);
The function “acos” is the inverse of the cosine function.

2.5 Pseudo-Euclidean distance
The edge weight type ATT corresponds to a special “pseudo-Euclidean” distance function.
Let x[i] and y[i] be the coordinates of node i. The distance between two points i and j
is computed as follows:
xd = x[i] - x[j];
yd = y[i] - y[j];
rij = sqrt( (xd*xd + yd*yd) / 10.0 );
tij = nint( rij );
if (tij<rij) dij = tij + 1;
else dij = tij;
2.6 Ceiling of the Euclidean distance
The edge weight type CEIL 2D requires that the 2-dimensional Euclidean distances is
rounded up to the next integer.

2.7 Distance for crystallography problems
We have included into TSPLIB the crystallography problems as described in [1]. These
problems are not explicitly given but subroutines are provided to generate the 12 problems
mentioned in this reference and subproblems thereof (see section 3.2).
To compute distances for these problems the movement of three motors has to be taken into
consideration. There are two types of distance functions: one that assumes equal speed
of the motors (XRAY1) and one that uses different speeds (XRAY2). The corresponding
distance functions are given as FORTRAN implementations (files deq.f, resp. duneq.f) in
the distribution file.
For obtaining integer distances, we propose to multiply the distances computed by the
original subroutines by 100.0 and round to the nearest integer.
We list our modified distance function for the case of equal motor speeds in the FORTRAN
version below.
INTEGER FUNCTION ICOST(V,W)
INTEGER V,W
DOUBLE PRECISION DMIN1,DMAX1,DABS
DOUBLE PRECISION DISTP,DISTC,DISTT,COST
DISTP=DMIN1(DABS(PHI(V)-PHI(W)),DABS(DABS(PHI(V)-PHI(W))-360.0E+0))
DISTC=DABS(CHI(V)-CHI(W))
DISTT=DABS(TWOTH(V)-TWOTH(W))
COST=DMAX1(DISTP/1.00E+0,DISTC/1.0E+0,DISTT/1.00E+0)
C *** Make integral distances ***
ICOST=AINT(100.0E+0*COST+0.5E+0)
RETURN
END
The numbers PHI(), CHI(), and TWOTH() are the respective x-, y-, and z-coordinates of
the points in the generated traveling salesman problems. Note, that TSPLIB95 contains
only the original distance computation without the above modification.

2.7 Verification
To verify correctness of the distance function implementations we give the length of some
“canonical” tours 1, 2, 3, . . . , n.
The canonical tours for pcb442, gr666, and att532 have lengths 221 440, 423 710, and
309 636, respectively.
The canonical tour for the problem xray14012 (the 8th problem considered in [21]) with
distance XRAY1 has length 15 429 219. With distance XRAY2 it has the length 12 943 294.
3. Description of the library files
In this section we give a list of all problem instances that are currently available together
with information on the length of optimal tours or lower and upper bounds for this length
(if available).

3.1 Symmetric traveling salesman problems
The TSP instances are contained in directory tsp. Table 1 gives the problem names along
with number of cities, problem type, and known lower and upper bounds for the optimal
tour length (a single number indicating that the optimal length is known). The entry
MATRIX indicates that the data is given in one of the matrix formats of 1.1.7. The names
of the corresponding data files are obtained by appending the suffix “.tsp” to the problem
name. Some optimal tours are also provided. The corresponding files have names with
suffix “.opt.tour”.

Name
a280
ali535
att48
att532
bayg29
bays29
berlin52
bier127
brazil58
brd14051
brg180
burma14
ch130
ch150
d198
d493
d657
d1291
d1655
d2103
d15112
d18512
dantzig42
dsj1000
eil51
eil76
eil101

#cities
280
535
48
532
29
29
52
127
58
14051
180
14
130
150
198
493
657
1291
1655
2103
15112
18512
42
1000
51
76
101

Type
EUC 2D
GEO
ATT
ATT
GEO
GEO
EUC 2D
EUC 2D
MATRIX
EUC 2D
MATRIX
GEO
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
EUC 2D
MATRIX
CEIL 2D
EUC 2D
EUC 2D
EUC 2D

Bounds
2579
202310
10628
27686
1610
2020
7542
118282
25395
[468942,469445]
1950
3323
6110
6528
15780
35002
48912
50801
62128
[79952,80450]
[1564590,1573152]
[644650,645488]
699
18659688
426
538
629

Table 1 Symmetric traveling salesman problems (Part I)
Lang: eng
10
Table 1 Symmetric traveling salesman problems (Part II)
[141904862,142487006]
CEIL_2D
85900
 pla85900
[65913275,66116530]
CEIL_2D
33810
pla33810
23260728
CEIL_2D
7397
pla7397
137694
EUC_2D
3038
pcb3038
56892
EUC_2D
1173
pcb1173
50778
EUC_2D
442
pcb442
2763
MATRIX
561
pa561
34643
EUC_2D
654
p654
56638
EUC_2D
1379
nrw1379
41345
EUC_2D
318
linhp318
42029
EUC_2D
318
lin318
14379
EUC_2D
105
lin105
29437
EUC_2D
200
kroB200
29368
EUC_2D
200
kroA200
26130
EUC_2D
150
kroB150
26524
EUC_2D
150
kroA150
22068
EUC_2D
100
kroE100
21294
EUC_2D
100
kroD100
20749
EUC_2D
100
kroC100
22141
EUC_2D
100
kroB100
21282
EUC_2D
100
kroA100
11461
MATRIX
48
hk48
294358
GEO
666
gr666
171414
GEO
431
gr431
134602
GEO
229
gr229
40160
GEO
202
gr202
69853
GEO
137
gr137
6942
MATRIX
120
gr120
55209
GEO
96
gr96
5046
MATRIX
48
gr48
1272
MATRIX
24
gr24
2707
MATRIX
21
gr21
2085
MATRIX
17
gr17
2378
EUC_2D
262
gil262
937
MATRIX
26
fri26
182566
EUC_2D
4461
fn14461
[28723,28772]
EUC_2D
3795
f13795
[22204,22249]
EUC_2D
1577
f11577
20127
EUC_2D
1400
f11400
11861
EUC_2D
417
f1417
Bounds
Type
#cities
Name