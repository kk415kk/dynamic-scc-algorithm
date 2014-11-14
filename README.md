Author
----
Kevin Kao


Fully Dynamic SCC Maintenance Algorithm
----
Research in-progress as part of prototyping work for [LogicBlox](http://www.logicblox.com), based off of [Roditty and Zwick's paper](http://dl.acm.org/citation.cfm?id=1007387&dl=ACM&coll=DL&CFID=446154922&CFTOKEN=78521305). Some of the explanations below may be drawn directly from the paper.

Documentation
---
__Class `Node`__<br>
A class to represent a node in a graph.
* `__init__(self, value=None)`
  * `@param value`: any object

__Class `Edge`__<br>
A class to represent an edge in a graph.
* `__init__(self, s_node, e_node)`
  * `@param s_node`: the start node of the edge (the tail)
  * `@param e_node`: the end node of the edge (the head)

__Class `Graph`__<br>
A class to represent a directed graph. The graph maintains reverse edges as well, so it can easily be used to represent an undirected graph. Contains the ability to calculate the strong components of the graph.
* `__init__(self, edges=[])`
  * `@param edges`: [optional] a set of edges to instantiate the graph with
* `add_edge(self, edge)`
  * `@param edge`: an `Edge` object
* `removed_edge(self, edge)`
  * `@param edge`: an `Edge` object
* `get_nodes(self)`
  * `@return` a set of `Node` objects
* `compute_scc(self)`
  * `@return` a dictionary mapping SCC numbers to a set of nodes in the SCC

__Class `DynamicGraph`__<br>
A more complex version of a graph, with a vastly different implementation. This graph supports optimized SCC computations under dynamic edge additions/deletions.

`O(n)` space to represent a graph:
  * At most 2n-1 nodes in the forest representation of the graph
  * A linear size array for every node in the forest to map nodes to parents
  * A linear size array for every node in the forest to map nodes to graph versions
  * A node holds pointers to its "child" nodes in its component tree (linear size overall)

`compute_scc` runs in `O(|V|)` time, since it follows pointers down the component trees only from the root node.

* `__init__(self)`
* `insert(self, edge_set)`
  * `@param edge_set`: a <u>set</u> of `Edge` objects
* `delete(self, edge_set)`
  * `@param edge_set`: a <u>set</u> of `Edge` objects
* `get_nodes(self)`
  * `@return` a set of `Node` objects
* `query(self, u, v, i)`
  * `@param u, v`: two nodes to query
  * `@param i`: the version of the graph to query (or Graph.t for the latest graph)
  * `@return True if u, v are in the same SCC, False otherwise`
* `compute_scc(self)`:
  * `@return` a list of sets of nodes that are in the same component

Visualize
---
Run `sudo pip install pydot` to install the Python dot interface for visualizing the graph. 

Overview
---
Disclaimer: the terms "component" and "strongly connected component" will be used interchangeably in the description below. Note that they both refer to a strongly connected component (SCC).

The algorithm maintains the strongly connected components of a sequence of graphs G<sub>1</sub>, ..., G<sub>t</sub>, where `t` is the number of insert operations performed so far. Basically, G<sub>i</sub> = (V,E<sub>i</sub>) is the graph created by the i<sup>th</sup> insert operation. Assume that G<sub>0</sub> = (V, E<sub>0</sub>), the initial graph, is a graph with no edges, i.e., E<sub>0</sub> is the empty set.

For the graph sequence G<sub>0</sub>, ..., G<sub>t</sub>, each of the corresponding set of edges edges E<sub>0</sub>, ..., E<sub>t</sub> are subsets of each other, in that sequence, i.e. E<sub>0</sub> is a strict subset of E<sub>1</sub>. Hence, each component of G<sub>i</sub> is either a component of G<sub>i-1</sub> or a union of some subset of components of G<u>i-1</u> (remember, single nodes are their own strongly connected components). 

The components of the sequence of versions of graphs can naturally be represented in a hierarchy, as a <b>forest</b>. Each node in the forest will represent a strongly connected component of the graph, with no duplications. The leaves of the forest are the vertices of the graph, which are components of the empty graph G<sub>0</sub>. The parent of a component `w` in the forest is the smallest component that strictly contains `w`. For each component `w`, we assign a version number that corresponds to the index `i` of the first graph G<sub>i</sub> in the sequence in which `w` is found to be a component.

The algorithm maintains the component forest of the sequence of versions of graphs. Strong connectivity queries can be reduced to LCA queries on the forest (the LCA of any two leaf nodes will determine the smallest SCC they are both in, or if they're not in the same component).


Supported Operations (in general terms):

* `Insert(E')` - Create a new version of the graph, initially identical to the latest version of the graph, and add the set of edges `E'` to it
* `Delete(E')` - Delete the set of edges `E'` from <i>all</i> versions of the graph
* `Query(u, v, i)` - Check if `u, v` are in the same SCC of the i<sup>th</sup> version of the graph

Implementation Details
---
To maintain the component forest, we define the following partition of the edge sets E<sub>0</sub> &sube; E<sub>1</sub> &sube; ... &sube; E<sub>t</sub>:

<b>Definition (Dynamic Edge Partitioning):</b> The dynamic edge set H<sub>i</sub> of G<sub>i</sub> is a set of edges `(u,v)` in G<sub>i</sub> that satisfies <u>all</u> of the following:
* The nodes `u` and `v` are in the same component of the current version of the graph G<sub>i</sub>, i.e. `query(u, v, i)` does not return `None`.
* The edge `(u,v)` was present in the previous version of the graph, but the nodes `u` and `v` were <b>NOT</b> in the same component in the previous version of the graph (G<sub>i-1</sub>) <b><u>OR</u></b> the edge `(u,v)` was not in the set of edges in the previous version of the graph G<sub>i-1</sub>, i.e., `(u,v)` &nsube; E<sub>i-1</sub>.

<b>tl;dr:</b> H<sub>i</sub> represents the set of edges `(u,v)` in G<sub>i</sub> where `(u,v)` is part of the same SCC in G<sub>i</sub> AND is either 1) existed in the G<sub>i-1</sub> but was not part of the same component, or 2) newly added during the transition from G<sub>i-1</sub> to G<sub>i</sub> (the edge was part of the i<sup>th</sup> current insertion of edges).

Another way to think of it is that H<sub>i</sub> is composed from all edges that are inter-component edges in G<sub>i-1</sub> (used to only bridge two components in ONE direction but needed an edge in the opposite direction to create a new super-component; after the i<sup>th</sup> `insert(E')`, one of the edges in E' must have helped to create a new super-component), or are not present in G<sub>i-1</sub> (so now, it's part of H<sub>i</sub> because it was the edge that helped create a new super-component), and are intra-component edges in G<sub>i</sub> (because these edges in H<sub>i</sub> helped create a new super-component that didn't exist in the previous version of the graph, and are now part of that new super-component in G<sub>i</sub>). 

Example:
<pre>
  Graph G1
  Edges E1: (A,B), (B,C), (C,A), (B,D)
  A ----------> B ----> D
   \-- C ------/

  Suppose an insert(E') occurs, where E' = {(D,C)}. Note that all edges are directed.

  Graph G2
  Edges E1: (A,B), (B,C), (C,A), (B,D), (D,C)
  A --------> B ----> D
   \--- C ---/       /
        \-----------/

  The edge (B,D) bridged the component {A, B, C} to the component {D} and was an inter-
  component edge in G1. (D,C) was an inserted edge and was not present in G1. The insertion
  of (D,C) created a new super-component {A, B, C, D}. Therefore, the dynamic edge set H2 
  is {(B,D), (D,C)}, satisfying the criteria discussed above.
</pre>

Notes
---
Developed in Python.


