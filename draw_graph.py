#!/usr/bin/python
import pydot
import graph as LB

# Build a graph
G = LB.DynamicGraph()
a = LB.Node('A')
b = LB.Node('B')
c = LB.Node('C')
d = LB.Node('D')
e1 = LB.Edge(a,b)
e2 = LB.Edge(a,c)
e3 = LB.Edge(c,a)
e4 = LB.Edge(b,c)
e5 = LB.Edge(c,d)
e6 = LB.Edge(d,c)
edge_set = set([e1, e2, e3])
G.insert(edge_set)
G.insert(set([e4]))
G.insert(set([e5]))
G.insert(set([e6]))

# Draw the graph and generate
graph = pydot.Dot('Forest')
for node in G.parent:
  f_node = str(G.parent[node]) + " - " + str(G.version[G.parent[node]])
  s_node = str(node) + " - " + str(G.version[node])
  edge = pydot.Edge(f_node, s_node)
  graph.add_edge(edge)
graph.write_png('graph.png')

