#!/usr/bin/python
import pydot
import graph as LB

# Draw the graph and generate
def draw_graph(G, name='output_graph'):
  graph = pydot.Dot('Forest')
  for node in G.edges:
    for s_node in G.edges[node]:
      edge = pydot.Edge(str(node), str(s_node))
      graph.add_edge(edge)
  graph.write_png(name + '.png')

def draw_scc_graph(G, name='scc_graph'):
  graph = pydot.Dot('Forest')
  visited = set()
  for component in G.components:
    if component not in visited:
      nodes = G.components[component]
      f_node = LB.Node(nodes)
      graph.add_node(pydot.Node(str(f_node)))
      print nodes
      for node in nodes:
        if node in G.edges:
          for s_node in G.edges[node]:
            if s_node not in nodes:
              edge = pydot.Edge(str(f_node), str(s_node))
              graph.add_edge(edge)
  graph.write_png(name + '.png')


# Build a graph
G = LB.Graph()
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

G.add_edges(edge_set)
G.add_edges(set([e5]))
G.add_edges(set([e6]))
G.add_edges(set([e7]))
G.add_edges(set([e8]))
G.add_edges(set([e9]))
G.compute_scc()

#LB.print_graph(G)
#print "----------------------------------------"
#G.delete(set([e6]))
#LB.print_graph(G)
draw_graph(G)
draw_scc_graph(G)
