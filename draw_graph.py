#!/usr/bin/python
import pydot
import rz_graph as LB

# Draw the graph and generate
def draw_graph(G, name='output_graph'):
  graph = pydot.Dot('Forest')
  for node in G.parent:
    f_node = str(G.parent[node]) + " - " + str(G.version[G.parent[node]])
    s_node = str(node) + " - " + str(G.version[node])
    edge = pydot.Edge(f_node, s_node)
    graph.add_edge(edge)
  graph.write_png(name + '.png')

# Build a graph
G = LB.DynamicGraph()
a = LB.Node('A')
b = LB.Node('B')
c = LB.Node('C')
d = LB.Node('D')
e = LB.Node('E')
f = LB.Node('F')
g = LB.Node('G')

e1 = LB.Edge(a,b)
e2 = LB.Edge(a,c)
e3 = LB.Edge(c,a)
e4 = LB.Edge(b,c)
e5 = LB.Edge(c,d)
e6 = LB.Edge(d,c)
e7 = LB.Edge(e,f)
e8 = LB.Edge(f,e)
e9 = LB.Edge(c,g)

edge_set = set([e1, e2, e3, e4])

G.insert(edge_set)
G.insert(set([e5]))
G.insert(set([e6]))
G.insert(set([e7]))
G.insert(set([e8]))
G.insert(set([e9]))

print G.compute_scc()

#LB.print_graph(G)
#print "----------------------------------------"
#G.delete(set([e6]))
#LB.print_graph(G)
draw_graph(G)
