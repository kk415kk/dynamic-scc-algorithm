# See https://wiki.python.org/moin/TimeComplexity for running times
class Node:
  """
  Class to represent a node
  """
  def __init__(self, value=None):
    self.value = value

  def __eq__(self, other):
    return self is other

  def __repr__(self):
    return '<Node %s @%s>' % (str(self.value), str(hex(id(self))))

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

  def __repr__(self):
    return '[%s %s @%s]' % (str(self.nodes[0]), str(self.nodes[1]), str(hex(id(self))))

  def __hash__(self):
    return hash(repr(self))

  def __str__(self):
    return '[%s %s]' % (str(self.nodes[0]), str(self.nodes[1]))

class Graph:
  """
  Class to represent a DIRECTED graph using linear space
  """
  def __init__(self, edges=[]):
    """
    @param edges: optional input set or list of edges to be inserted
    """
    self.edges = {}	        # Maps node to list of forward neighbors
    self.rev_edges = {}         # Maps node to list of backwards neighbors
    self.components = {}	# Strong components of graph

    # Initialize graph, if desired
    for edge in edges:
      self.add_edge(edge)

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
    @return a dictionary mapping component number to component nodes
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

class DynamicGraph():
  """
  An implementation of a graph that uses Roditty and Zwick's dynamic SCC algorithm
  to maintain the components of the graph.

  Maintain the components forest of the graph as a disjoint set, where the rank of
  a node is the version of the graph the node first appears in.
  """
  def __init__(self):
    """
    Note: all nodes will be a key in self.parent and self.version
    """
    self.t = 0              # t represents the version of the graph that is most recently represented
    self.dynamic_set = { 0: set(), 1: set() }   # H (dynamic edge set), where the i-th set is H_i
    self.parent = {}        # (key, val) -> (node, parent)
    self.version = {}       # The graph version where each node first appeared
    self.nodes = set()      # The nodes in the original graph, NOT SCC nodes

  def __str__(self):
    graph_str = ""
    for time_set in self.dynamic_set.values():
      for edge in time_set:
        s_node, e_node = edge.nodes
        graph_str += "[%s %s]\n" % (str(s_node), str(e_node))
    return graph_str if graph_str != "" else "Empty graph"

  def insert(self, edge_set):
    """
    @param edge_set: a set of edges to be inserted
    If there are new nodes, they must be added to every version of the graph.
    """
    self.nodes = self.nodes | self.__edge_set_nodes(edge_set)
    self.t += 1
    self.__populate_nodes(edge_set)
    self.dynamic_set[self.t] = self.dynamic_set[self.t] | edge_set
    self.__find_scc(self.dynamic_set[self.t])
    self.dynamic_set[self.t+1] = set()
    self.__shift(self.dynamic_set[self.t], self.dynamic_set[self.t+1])
    # TODO: Pre-process for LCA queries

  def delete(self, edge_set):
    """
    @param edge_set: a set of edges to be deleted
    """
    #self.parent = dict((node, node) for node in self.parent)  # Set all parent nodes to themselves
    self.parent = dict((node, node) for node in self.nodes)

    # Recompute the strong components using our dynamic edge partitions
    for i in xrange(1, self.t+1):
      self.dynamic_set[i] = self.dynamic_set[i] - edge_set
      self.__find_scc(self.dynamic_set[i])
      self.__shift(self.dynamic_set[i], self.dynamic_set[i+1])

    self.dynamic_set[self.t+1] = self.dynamic_set[self.t+1] - edge_set
    self.version = dict((node, version) for node, version in self.version.items() \
      if node in self.parent.keys())
    # TODO: Pre-process for LCA queries

  def compute_scc(self):
    """
    @return a dictionary of the strong components of the graph
    """
    pass

  def query(self, u, v, i):
    """
    Currently takes O(h) time, where h = max(height(tree(u)), height(tree(v)))
    @param u, v: two nodes
    @param i: the version of the graph to query
    @return True if u, v are in the same SCC in version i of the graph
    """
    lca_node = self.__lca(u, v)
    return self.version[lca_node] <= i if lca_node in self.version else False

  def get_nodes(self):
    """
    @return a set of all the nodes in the graph
    """
    return self.nodes

  def __lca(self, u, v):
    """
    Finds the LCA of the two nodes u and v
    @param u, v: the two nodes to find the LCA of
    @return None if the two nodes are not connected; else return a Node
    """
    traversed = set([u])
    while self.parent[u] != u:
      u = self.parent[u]
      traversed.add(u)

    while self.parent[v] != v:
      v = self.parent[v]
      if v in traversed:
        return v
    return None if v not in traversed else v

  def __find_scc(self, dynamic_edge_set):
    """
    1. Create a temporary dynamic edge set using the component nodes instead
        of the actual nodes
    2. Construct a subgraph using these new edges and find their SCCs
    3. Add pointers from the component nodes to their new SCC node(s)
    4. Pre-process the new graph for fast LCA queries
    @param dynamic_edge_set: a dynamic edge set of the current time step
    """
    # Create a temporary dynamic edge set
    temp_dynamic_edge_set = set()
    for edge in dynamic_edge_set:
      s_node, e_node = edge.nodes
      temp_edge = Edge(self.__find(s_node), self.__find(e_node))
      temp_dynamic_edge_set.add(temp_edge)

    # Construct a subgraph out of the edges in the dynamic edge set and find SCCs
    subgraph = self.__construct_subgraph(temp_dynamic_edge_set)
    components = subgraph.compute_scc()
    for scc in components:
      component_nodes = components[scc]
      component_values = [node.value for node in component_nodes]
      if len(component_nodes) > 1:
        scc_node = Node(component_values)
        self.parent[scc_node] = scc_node
        self.version[scc_node] = self.t
        for node in component_nodes:
          # union step here?
          self.parent[node] = scc_node

  def __construct_subgraph(self, edge_set):
    """
    Builds a graph out of the set of edges and returns it
    @param edge_set
    @return a Graph object
    """
    return Graph(edge_set)

  def __shift(self, dynamic_edge_set_1, dynamic_edge_set_2):
    """
    Essentially, we want to move the edges in the first edge set into the second
    if the edge's nodes are not part of the same SCC (an inter-component edge)
    @param dynamic_edge_set_1: the dynamic edge set for the current time step
    @param dynamic_edge_set_2: the dynamic edge set for the next time step
    """
    edges_to_remove = set()
    for edge_1 in dynamic_edge_set_1:
      s_node, e_node = edge_1.nodes
      if self.__find(s_node) != self.__find(e_node):
        edges_to_remove.add(edge_1)
        dynamic_edge_set_2.add(edge_1)
    for edge in edges_to_remove:
      dynamic_edge_set_1.remove(edge)

  def __populate_nodes(self, edge_set):
    """
    Used for keeping track of nodes that were not previously in the graph
    @param edge_set: the set of edges to look at for nodes to add to dictionaries
    """
    for edge in edge_set:
      s_node, e_node = edge.nodes
      if s_node not in self.parent:
        self.parent[s_node] = s_node
        self.version[s_node] = self.t
      if e_node not in self.parent:
        self.parent[e_node] = e_node
        self.version[e_node] = self.t

  def __find(self, node):
    """
    Path compression optimization is not used because we need to keep the structure of trees
    @param u: a node in the forest
    @return the root node of the tree that node u is part of
    """
    parent = self.parent[node]
    return parent if parent == node else self.__find(parent)

  def __edge_set_nodes(self, edge_set):
    nodes = set()
    for edge in edge_set:
      nodes.add(edge.nodes[0])
      nodes.add(edge.nodes[1])
    return nodes

def print_graph(G):
  print str(G)
  print "Parents: %s\n" % G.parent
  print "Versions: %s\n" % G.version
  print "H: %s\n" % G.dynamic_set

def test_dynamic_graph():
  G = DynamicGraph()
  a = Node('A')
  b = Node('B')
  c = Node('C')
  e1 = Edge(a,b)
  e2 = Edge(a,c)
  e3 = Edge(c,a)
  e4 = Edge(b,c)
  edge_set = set([e1, e2, e3])
  G.insert(edge_set)
  print_graph(G)
  G.insert(set([e4]))
  print_graph(G)

def test_graph():
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
