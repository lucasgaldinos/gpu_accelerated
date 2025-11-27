# Insights from Articles

## Vehicle Routing and Job Scheduling: What's the difference?

Beck, J. & Prosser, Patrick & Selensky, E.. (2003). Vehicle Routing and Job Shop Scheduling: What's the difference?.

The CVRPTW is a problem where m identical vehicles initially located at a depot must deliver a discrete quantity of goods for n customers. The tour start at a depot, visits a subset of customers and return to depot. time windows define the interval for each customer to be visited. A solution is a set of tours for a subset of vehicles, such that all customers are served only once and the tw anc capacity constraints are respected.  
The objective is to minimize the distance traveled, sometimes reducing the number of resources (vehicles) used for the deliveries. It's an NP-hard and NP-complete problem

An $n{\times}m$ job scheduling problem (JSP) consists of n jobs and m resources, where each job is a set of m completely ordered activities and each activity has a duration for which must it execute and a resource which it must execute on. The total ordering defines a set of precedence constraints, meaning no activity can be started before the previous is finished. Each $m$ activities in a single job requires exclusive use of one of the $m$ resources defined in the problem. If they require the same resource, they must not overlap. Once an activity start, it must be executed during its entire duration. Its also NP-complete.

Now, why
