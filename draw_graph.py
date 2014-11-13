#!/usr/bin/python
import pydot
import graph as LB

# Build a graph
G = LB.DynamicGraph()
a = LB.Node('A')
b = LB.Node('B')
c = LB.Node('C')
e1 = LB.Edge(a,b)
e2 = LB.Edge(a,c)
e3 = LB.Edge(c,a)
e4 = LB.Edge(b,c)
edge_set = set([e1, e2, e3])
G.insert(edge_set)
G.insert(set([e4]))

# Draw the graph and generate
graph = pydot.Dot('Forest')
for node in G.parent:
  if node != G.parent[node]:
    edge = pydot.Edge(str(G.parent[node]), str(node))
    graph.add_edge(edge)
graph.write_png('graph.png')

