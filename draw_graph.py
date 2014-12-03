#!/usr/bin/python
import pydot
from graph import graph as LB
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
        col2 = hex_color()
        while col in scc_colors:
          col2 = hex_color()
        scc = G.inverse_components[e_node]
       
        if scc in scc_colors:
          col2 = scc_colors[scc]
        scc_colors[scc] = col2

        pydot_enode = pydot.Node(str(e_node), style="filled", fillcolor=col2)
        edge = pydot.Edge(pydot_snode, pydot_enode)
      else:
        edge = pydot.Edge(pydot_snode, visited_nodes[e_node])
      graph.add_edge(edge)
  graph.write_png(name + '.png')

def print_edges(edges):
  """
  @param edges: the edges to print out
  """
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
h = LB.Node('H')
i = LB.Node('I')
j = LB.Node('J')
k = LB.Node('K')
l = LB.Node('L')
m = LB.Node('M')
n = LB.Node('N')
o = LB.Node('O')
p = LB.Node('P')
q = LB.Node('Q')

# Test Case #1
# e1 = LB.Edge(a,b)
# e2 = LB.Edge(a,c)
# e3 = LB.Edge(c,a)
# e4 = LB.Edge(b,c)
# e5 = LB.Edge(c,d)
# e6 = LB.Edge(d,c)
# e7 = LB.Edge(e,f)
# e8 = LB.Edge(f,e)
# e9 = LB.Edge(c,g)
# e10 = LB.Edge(h,g)
# e11 = LB.Edge(g,i)
# G.add_edges(set([e1, e2, e3, e4]))
# G.add_edges(set([e5, e6, e7]))
# G.add_edges(set([e8, e11]))
# G.add_edges(set([e9, e10]))
# G.optimized_remove_edges(set([e8, e9]))
# G.optimized_remove_edges(set([e7, e5]))

# # Test Case #2
e12 = LB.Edge(j,k)
e13 = LB.Edge(k,l)
e14 = LB.Edge(l,m)
e15 = LB.Edge(m,j)
e16 = LB.Edge(k,o)
e17 = LB.Edge(o,p)
e18 = LB.Edge(p,q)
e19 = LB.Edge(q,o)
e20 = LB.Edge(q,l)
G.add_edges(set([e12, e13, e14, e15, e16, e17, e18, e19, e20]))
G.optimized_remove_edges(set([e13, e16]))

# Test Case #3
# e21 = LB.Edge(a,b)
# e22 = LB.Edge(b,c)
# e23 = LB.Edge(c,d)
# e24 = LB.Edge(e,f)
# e25 = LB.Edge(a,c)
# e26 = LB.Edge(d,e)
# e27 = LB.Edge(f,a)
# G.optimized_add_edges(set([e21, e24]))
# G.optimized_add_edges(set([e22, e23]))
# G.optimized_add_edges(set([e25, e26, e27]))


print "INTRA-EDGES"
print "-----------------"
print_edges(G.intra_edges)
print "END"
print ""

print "INTER-EDGES"
print "-----------------"
print_edges(G.inter_edges)
print "END"
print ""

print "INVERSE-COMPONENTS"
print "--------------------"
for node in G.inverse_components:
  print node
print ""

print "COMPONENTS"
print "-----------"
for scc in G.components:
  print "----SCC----"
  for node in G.components[scc]:
    print node

#LB.print_graph(G)
#print "----------------------------------------"
#G.delete(set([e6]))
#LB.print_graph(G)
draw_graph(G)
