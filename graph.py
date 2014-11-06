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
    return '<Node %s>' % str(self.value)

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

        # Mirrors above
        if len(self.rev_edges[e_node]) == 0:
          del self.rev_edges[e_node]
          if len(self.rev_edges[e_node]) == 0:
            del self.edges[e_node]
            if e_node in self.edges and len(self.edges[e_node]) == 0:
              del self.edges[e_node]

  def get_nodes(self):
    return set(self.edges.keys()) | set(self.rev_edges.keys())

  def __str__(self):
    graph_str = ""
    for s_node in self.edges:
      neighbors = self.edges[s_node]
      for n in neighbors:
        graph_str += ("[%s %s]\n" % (s_node, n))
    return graph_str

def test():
  a = Node('A')
  b = Node('B')
  c = Node('C')
  b2 = Node('B')
  e1 = Edge(a,b)
  e2 = Edge(a,c)
  G = Graph()
  print "Adding edge %s" % str(e1)
  G.add_edge(e1)
  print "Adding edge %s" % str(e2)
  G.add_edge(e2)
  print "Graph: "
  print G
  print "Removing edge %s" % str(e2)
  G.remove_edge(e2)
  print "Graph: "
  print G

