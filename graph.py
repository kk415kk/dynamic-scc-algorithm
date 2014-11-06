# See https://wiki.python.org/moin/TimeComplexity for running times
class Node:
  """
  Class to represent a node
  """
  def __init__(self, value):
    self.value = value

  def __eq__(self, other):
    return self is other

  def __hash__(self):
    return hash(repr(self))

  def __str__(self):
    return '<Node %s @%s>' % (str(self.value), str(hex(id(self))))

class Edge:
  """
  Class to represent an edge
  """
  def __init__(self, s_node, e_node):
    self.nodes = (s_node, e_node)

  def __eq__(self, other):
    return self.nodes[0] == other.nodes[0] and self.nodes[1] == other.nodes[1]

  def __hash__(self):
    return hash(repr(self))

  def __str__(self):
    return '[%s %s]' % (str(self.nodes[0]), str(self.nodes[1]))

class Graph:
  """
  Class to represent a DIRECTED graph using linear space
  """
  def __init__(self):
    self.edges = {}	        # Maps node to list of forward neighbors
    self.rev_edges = {}         # Maps node to list of backwards neighbors
    self.components = {}	# Strong components of graph

  def add_edge(self, edge):
    """
    O(1) time to add node to a set inside a map (dictionary)
    """
    s_node, e_node = edge.nodes

    if s_node not in self.edges:
      self.edges[s_node] = set()
    if e_node not in self.rev_edges:
      self.rev_edges[e_node] = set()
    self.edges[s_node].add(e_node)
    self.rev_edges[e_node].add(s_node)
    

  def remove_edge(self, edge):
    """
    O(1) time to remove node from a set inside a map
    O(1) time to remove node from a map (dictionary)
    """
    s_node, e_node = edge.nodes
    if s_node in self.edges and e_node in self.edges[s_node]:
      self.edges[s_node].remove(e_node)
      self.rev_edges[e_node].remove(s_node)

      # If there are no outgoing edges from the start node, del it
      if len(self.edges[s_node]) == 0:
        del self.edges[s_node]
        
        # If there are no incoming edges to the start node, del it
        if s_node in self.rev_edges and len(self.rev_edges[s_node]) == 0:
          del self.rev_edges[s_node]

      # If there are no outgoing edges from the end node, del it
      if len(self.rev_edges[e_node]) == 0:
        del self.rev_edges[e_node]

        # If there are no incoming edges to the end node, del it
        if e_node in self.edges and len(self.edges[e_node]) == 0:
          del self.edges[e_node]

  def get_nodes(self):
    """
    O(|V|) time to retrieve all nodes in the graph
    """
    return set(self.edges.keys()) | set(self.rev_edges.keys())

  def compute_scc(self):
    """
    Computes the SCCs of this graph
    O(|E|) time to iterate through each edge
    """
    s_nodes = self.edges.keys()
    lowlinks, indices, index = {}, {}, [0]
    components = {}
    visited = []
    for s_node in s_nodes:
      if s_node not in indices:
        self.__traverse(s_node, lowlinks, indices, index, components, visited)
    return components

  def __traverse(self, node, lowlinks, indices, index, components, visited):
    """
    Private helper function to perform DFS and compute components
    of graph (final components in lowlinks)
    """
    indices[node], lowlinks[node] = index[0], index[0]
    index[0] = index[0] + 1
    visited.append(node)
    if node in self.edges:
      for e_node in self.edges[node]:
        if e_node not in indices:
          self.__traverse(e_node, lowlinks, indices, index, components, visited)
          lowlinks[node] = min(lowlinks[node], lowlinks[e_node])
        else:
          lowlinks[node] = min(lowlinks[node], indices[e_node])

    lowlink = lowlinks[node]
    if lowlink == indices[node] and len(visited) > 0:
      components[lowlink] = set()
      c_node = None 
      while len(visited) > 0 and c_node != node:
        c_node = visited.pop()
        components[lowlink].add(c_node)


  def __str__(self):
    graph_str = ""
    for s_node in self.edges:
      neighbors = self.edges[s_node]
      for n in neighbors:
        graph_str += ("[%s %s]\n" % (str(s_node), str(n)))
    return graph_str

def test():
  a = Node('A')
  b = Node('B')
  c = Node('C')
  e1 = Edge(a,b)
  e2 = Edge(a,c)
  e3 = Edge(c,a)
  G = Graph()
  print "Adding edge %s" % str(e1)
  G.add_edge(e1)
  print "Adding edge %s" % str(e2)
  G.add_edge(e2)
  print "Graph: "
  print G
  print ""
  print "Removing edge %s" % str(e2)
  G.remove_edge(e2)
  print "Adding edge %s" % str(e2)
  G.add_edge(e2)
  print "Adding edge %s" % str(e3)
  G.add_edge(e3)
  print "Graph: "
  print G
  print ""
  print "SCCs:"
  print dict((str(node), i) for node, i in G.compute_scc().items())
