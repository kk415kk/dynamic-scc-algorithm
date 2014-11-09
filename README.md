Author
----
Kevin Kao


Fully Dynamic SCC Maintenance Algorithm
----
Research in-progress as part of prototyping work for [LogicBlox](http://www.logicblox.com), based off of [Roditty and Zwick's paper](http://dl.acm.org/citation.cfm?id=1007387&dl=ACM&coll=DL&CFID=446154922&CFTOKEN=78521305). Some of the explanations below may be drawn directly from the paper.


Overview
---
Disclaimer: the terms "component" and "strongly connected component" will be used interchangeably in the description below. Note that they both refer to a strongly connected component (SCC).

The algorithm maintains the strongly connected components of a sequence of graphs G<sub>1</sub>, ..., G<sub>t</sub>, where `t` is the number of insert operations performed so far. Basically, G<sub>i</sub> = (V,E<sub>i</sub>) is the graph created by the i<sup>th</sup> insert operation. Assume that G<sub>0</sub> = (V, E<sub>0</sub>), the initial graph, is a graph with no edges, i.e., E<sub>0</sub> is the empty set.

For the graph sequence G<sub>0</sub>, ..., G<sub>t</sub>, each of the corresponding set of edges edges E<sub>0</sub>, ..., E<sub>t</sub> are subsets of each other, in that sequence, i.e. E<sub>0</sub> is a strict subset of E<sub>1</sub>. Hence, each component of G<sub>i</sub> is either a component of G<sub>i-1</sub> or a union of some subset of components of G<u>i-1</u> (remember, single nodes are their own strongly connected components). 

The components of the sequence of versions of graphs can naturally be represented in a hierarchy, as a forest. Each node in the forest will represent a strongly connected component of the graph, with no duplications. The leaves of the forest are the vertices of the graph, which are components of the empty graph G<sub>0</sub>. The parent of a component `w` in the forest is the smallest component that strictly contains `w`. For each component `w`, we assign a version number that corresponds to the index `i` of the first graph G<sub>i</sub> in the sequence in which `w` is found to be a component.

Supported Operations (in general terms):

* `Insert(E')` - Create a new version of the graph, initially identical to the latest version of the graph, and add the set of edges `E'` to it
* `Delete(E')` - Delete the set of edges `E'` from <i>all</i> versions of the graph
* `Query(u, v, i)` - Check if `u, v` are in the same SCC of the i<sup>th</sup> version of the graph


Notes
---
Developed in Python.


