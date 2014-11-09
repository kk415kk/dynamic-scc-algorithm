Author: Kevin Kao

Fully Dynamic SCC Maintenance Algorithm
----
Research in-progress as part of prototyping work for [LogicBlox](http://www.logicblox.com), based off of [Roditty and Zwick's paper](http://dl.acm.org/citation.cfm?id=1007387&dl=ACM&coll=DL&CFID=446154922&CFTOKEN=78521305)


Overview
---
Supported Operations:

* <code>Insert(E')</code> - Create a new version of the graph, initially identical to the latest version of the graph, and add the set of edges <code>E'</code> to it
* <code>Delete(E')</code> - Delete the set of edges <code>E'</code> from <i>all</i> versions of the graph
* <code>Query(u, v, i)</code> - Check if <code>u, v</code> are in the same SCC of the <i>i</i>th version of the graph

Notes
---


