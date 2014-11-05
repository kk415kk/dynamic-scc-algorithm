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

class Graph:
  """
  Class to represent a DIRECTED graph using linear space
  """
  def __init__(self):
    self.edges = {}				# Maps node to list of neighbors
    self.nodes = set()		# Set of all nodes in graph
    self.components = {}	# Strong components of graph

  def add_edge(self, edge):
    """
    O(1) time to add nodes to a set
    O(1) time to add node to a set inside a map (dictionary)
    """
    print edge
    print edge.nodes
    s_node, e_node = edge.nodes
    self.nodes.add(s_node)
    self.nodes.add(e_node)

    if s_node not in self.edges:
      self.edges[s_node] = set()
      self.edges[s_node].add(e_node)

  def remove_edge(self, edge):
    """
    O(1) time to remove node from a set inside a map
    O(1) time to remove node from a map (dictionary)
    """
    if s_node in self.edges and e_node in self.edges[s_node]:
      self.edges[s_node].remove(e_node)
      if len(self.edges[s_node]) == 0:
        del self.edges[s_node]

a = Node('A')
b = Node('B')
e1 = Edge(a,b)
G = Graph()
G.add_edge(e1)


