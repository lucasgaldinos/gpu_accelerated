'''Code implementation'''

# Importing necessary libraries
import numpy as np
import numba as nb

'''
Variables aare given by:
$k$ - day

$i$ - location $i$ as an index.

$j$ - location $j$ as an index.

$index\ s$ - origin 

$index\ t$ - destination


$y^{k}_{i,j}$ - _decision_y_ is a decision variable indicating whether travel between 
a given pair of locations $i$ and $j$ occurs on the k th day with travel time 
$t(i, j)$ and cost $c(i, j)$, where $y^k_{i,j}$ is one if the driver 
decides to go from $i$ to $j$ on day $k$, and 0 otherwise.

$W^{k}_{i,p}$ - $\in {0, 1}$ is a decision variable indicating whether location $i$ is used for a
stop of type $p \in P$ on day $k$, where $p \in {1, 2, 3, 4}$ represent different stop modes, respectively
rest, meal, overnight, and weekend downtime, where $W^k_{i,p}$ is one if the
driver decides to stop at location $i$ for reason $p$ on day $k$, and 0 otherwise.

$h_k$ - continuous decision variable representing the number of hours the driver works on day $k$.

$a_i$ - arrival time in location $i$

$d_i$ - departure time in location $i$

$c(i,j)$ - travel cost

$p$ - stop mode $p \in \{1, 2, 3, 4\}$

$d(i,p)$ - stoppage costs of type $p$ in location $i$

$\ni(h_k)$ - number of hours driven in the $k^{th}$ day

$\phi(d_s, a_t)$ - opportunity cost of having a truck in use. This cost is a function of time each truck is 
not in use, namely the difference between departure time $d_i$ from a stoppage $i$ and arrival 
time $a_j$ at the next location $j$

$d_s$ - departure time from the origin

$t(i,j)$ - travel time

$x_t$ - final_destination

$x$ - node

'''

location_i_n = location_i
stop_reason = (1, 2, 3, 4)
node_xn = (
    location_i_n,
)

def connect_database():
    """
    Connect to a database, change as needed.
    """
    connection = ...
    return connection


    

class state_space_model:
    def __init__(self) -> None:
        self.k = None
        self.d_s = None
        
        ...

    @staticmethod
    @njit
    def cost_function(self, days, location_i, location_j, travel_cost, stoppage_costs, stop_reason, driver_cost, cost_penalty):
        '''
        function given by $$\min{Z} = \sum_{k}\sum_{(i,j)\in A}c(i,j)y^{k}_{i,j} 
        + \sum_{k}\sum_{i\in N}\sum_{p\in P}d(i,p)W^{k}_{i,p} + \sum_{k}\eta(h_k) + \phi(d_s, a_t)$$
        
        This cost function is called to calculate the total cost of the problem. 
        
        Parameters:
        day: list of days
        location_i: list of locations i
        location_j: list of locations j
        travel_cost: list of travel costs
        decision_y: list of decision variables y
        stoppage_costs: list of stoppage costs
        stop_reason: list of stop reasons
        decision_W: list of decision variables W
        driver_cost: list of driver costs
        hours_worked: list of hours worked
        
        $$
        \phi(d_s, a_t) = 
        $$
        '''
        
        phi = phi()
        
        decision_y = decision_y(day, location_i, location_j)
        decision_W = decision_W(location_i, stop_reason)
        hours_worked = hours_worked(day, ...)
        arrival_time = arrival_time(location_i, ...)
        departure_time = departure_time(location_i, ...)
        
        
        for day in range(len(days)):
            
            ...
        
        # self.node_cost = np.sum()
        
        ...
        
        def physical_constrains_calculation(days):
            """
            Here lies the constrains of the problem
            
            eq_1: $\sum_k \sum_{j|(i,j)\in A} 
            """
            
            decision_y
            def constraint_1(i, j, k):
            
                
                    for i, j in day:
                        
                        assert decision_y[i, j, k] == decision_y[j, i, k]
                        ...
            
            def constraint_2(i, j):
                decision_y_start = 1
                return decision_y_start
        
        def phi_calculation(d):
            """"""
            ...
        
        def y_calculation(i, j, k):
            """
            """
            
    
    # @staticmethod
    # @njit
    # def phi_cost_function