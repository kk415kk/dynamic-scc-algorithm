#!/usr/bin/python
import pydot
import graph as LB
import random

def hex_color():
  r = lambda: random.randint(0,255)
  return '#%02X%02X%02X' % (r(),r(),r())

# Draw the graph and generate
def draw_graph(G, name='output_graph'):
  graph = pydot.Dot('Forest')
  scc_colors = {}
  visited_nodes = {}

  for node in G.edges:
    col = hex_color()
    while col in scc_colors:
      col = hex_color()
    scc = G.inverse_components[node]
    if scc in scc_colors:
      col = scc_colors[scc]
    scc_colors[scc] = col

    if node not in visited_nodes:
      pydot_snode = pydot.Node(str(node), style="filled", fillcolor=col)
      visited_nodes[node] = pydot_snode
      graph.add_node(pydot_snode)

    for e_node in G.edges[node]:
      if e_node not in visited_nodes:
        col = hex_color()
        while col in scc_colors:
          col = hex_color()
        scc = G.inverse_components[e_node]
        if scc in scc_colors:
          col = scc_colors[scc]
        scc_colors[scc] = col

        pydot_enode = pydot.Node(str(e_node), style="filled", fillcolor=col)
        edge = pydot.Edge(pydot_snode, pydot_enode)
      else:
        edge = pydot.Edge(pydot_snode, visited_nodes[e_node])
      graph.add_edge(edge)
  graph.write_png(name + '.png')

def print_edges(edges):
  for s_node in edges:
    for e_node in edges[s_node]:
      print LB.Edge(s_node, e_node)

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
G.optimized_remove_edges(set([e8, e9]))


# print "INTRA-EDGES"
# print "-----------------"
# print_edges(G.intra_edges)
# print "END"
# print ""

# print "INTER-EDGES"
# print "-----------------"
# print_edges(G.inter_edges)
# print "END"
# print ""

# print "INVERSE-COMPONENTS"
# print "--------------------"
# for node in G.inverse_components:
#   print node

# print "COMPONENTS"
# print "-----------"
# for scc in G.components:
#   print "----SCC----"
#   for node in G.components[scc]:
#     print node

#LB.print_graph(G)
#print "----------------------------------------"
#G.delete(set([e6]))
#LB.print_graph(G)
draw_graph(G)
