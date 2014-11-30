# See https://wiki.python.org/moin/TimeComplexity for running times
class Node:
  """
  Class to represent a node. A node represents its own strongly connected component;
  its children are nodes that are part of the SCC that it represents.
  """
  def __init__(self, value=None):
    self.value = value
    self.component_edges = {}

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
  def __init__(self, s_node, e_node, scc_edge=False):
    self.nodes = (s_node, e_node)
    self.scc_edge = scc_edge

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
    self.edges = {}               # Maps node to list of forward neighbors
    self.rev_edges = {}           # Maps node to list of backwards neighbors
    self.components = {}          # Strong components of graph
    self.inverse_components = {}  # Maps each node to its component in the graph
    self.scc_num = 0              # Next available component number

    self.intra_edges = {}         # Stores the intra-SCC edges, mapping node to list of forward neighbors
    self.inter_edges = {}         # Stores the inter-SCC edges, mapping node to list of forward neighbors

    # Initialize graph, if desired
    for edge in edges:
      self.add_edge(edge)
    self.compute_scc()

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

  def add_edges(self, edge_set):
    """
    Add multiple edges, one at a time

    NOTE: Must call compute_scc() after this operation to maintain SCCs
    """
    for edge in edge_set:
      self.add_edge(edge)

  def remove_edge(self, edge):
    """
    O(1) time to remove node from a set inside a map
    O(1) time to remove node from a map (dictionary)
    """
    s_node, e_node = edge.nodes

    if s_node in self.edges and e_node in self.edges[s_node]:
      self.edges[s_node].remove(e_node)
      self.rev_edges[e_node].remove(s_node)

      # Update edge partitions
      if s_node in self.intra_edges and e_node in self.intra_edges[s_node]: 
        self.intra_edges[s_node].remove(e_node)
        if len(self.intra_edges[s_node]) == 0:
          del self.intra_edges[s_node]

      if s_node in self.inter_edges and e_node in self.inter_edges[s_node]: 
        self.inter_edges[s_node].remove(e_node)
        if len(self.inter_edges[s_node]) == 0:
          del self.inter_edges[s_node]

      # If there are no outgoing edges from the start node, del it
      if len(self.edges[s_node]) == 0:
        del self.edges[s_node]
        
        # If there are no incoming edges to the start node, del it
        if s_node in self.rev_edges and len(self.rev_edges[s_node]) == 0:
          del self.rev_edges[s_node]
          # Maintain inverse components mapping
          self.__clear_component_node(e_node)

        elif s_node not in self.rev_edges:
          # Maintain inverse components mapping
          self.__clear_component_node(snode)

      # If there are no incoming edges to the end node, del it
      if len(self.rev_edges[e_node]) == 0:
        del self.rev_edges[e_node]

        # If there are no outgoing edges from the end node, del it
        if e_node in self.edges and len(self.edges[e_node]) == 0:
          del self.edges[e_node]
          # Maintain inverse components mapping
          self.__clear_component_node(e_node)
        elif e_node not in self.edges:
          # Maintain inverse components mapping
          self.__clear_component_node(e_node)

  def __clear_component_node(self, node):
    scc = self.inverse_components[node]
    del self.inverse_components[node]
    self.components[scc].remove(node)
    if len(self.components[scc]) == 0:
      del self.components[scc]

  def remove_edges(self, edges):
    """
    Remove multiple edges, one at a time

    NOTE: Must remove this from public API - improper use will result in error
    """
    for edge in edges:
      self.remove_edge(edge)

  def optimized_remove_edges(self, edges):
    """
    Optimized bulk removal of edges
    @param edges: a set of edges to be removed
    """
    check_scc = set()
    for edge in edges:
      s_node, e_node = edge.nodes
      if self.inverse_components[s_node] == self.inverse_components[e_node]:
        scc = self.inverse_components[s_node]
        check_scc.add(scc)
      self.remove_edge(edge)

    for scc in check_scc:
      nodes = self.components[scc]
      components, inverse_components = self.compute_partial_scc(nodes)

      # If the component got split up, we need to merge the results in
      # 1. Delete the scc from self.components
      # 2. Merge in the new components
      # 3. Update all the nodes in self.inverse_components
      # NOTE: We can re-use the number "scc" by replacing the max number of 
      #       components with "scc", then going through all of inverse_comp
      #       to reset those nodes to "scc"
      if len(components) > 1:
        del self.components[scc]
        self.components.update(components)
        self.inverse_components.update(inverse_components)
        self.__partial_partition_edges(components, inverse_components, op='del')

  def __partial_partition_edges(self, components, inverse_components, op):
    """
    Different optimizations can be made depending on if the operation
    that was just run was a deletion or insertion.
    @param components: the partial components that were computed
    @param inverse_components
    @param op: 'del' or 'add', depending on which operation was run
    """
    if op == 'del':
      self.__delete_partial_partition_edges(components, inverse_components)
    elif op == 'add':
      # TODO
      self.__partition_edges()
    else:
      return

  def __delete_partial_partition_edges(self, components, inverse_components):
    """
    Computes a partial recompute of the edge partitions.
    For a deletion, SCCs can only be broken, not created, so only 
    update the nodes that are no longer part of an SCC. For these,
    just move all of the node's intra-SCC edges to inter-SCC ones.
    """
    for node in inverse_components:
      scc = inverse_components[node]
      if len(components[scc]) == 1 and node in self.intra_edges:
        if node not in self.inter_edges:
          self.inter_edges[node] = set()
        self.inter_edges[node] = self.inter_edges[node] & self.intra_edges[node]
        del self.intra_edges[node]
      else:
        # The node was part of an SCC, is still now part of an SCC, 
        # so its edge is still part of an SCC and no changes need to be made.
        continue

  def get_nodes(self):
    """
    O(|V|) time to retrieve all nodes in the graph
    """
    return set(self.edges.keys()) | set(self.rev_edges.keys())

  def compute_partial_scc(self, nodes):
    """
    Computes the SCCs of the graph from traversing just the nodes in question,
    considering only intra-SCC edges

    NOTE: The partial SCC compute does NOT partition the edges, so those need to
          be updated by the calling method.

    @return a dictionary mapping component number to a set of component nodes, 
            and a reverse dictionary mapping a node to the component number
    """
    lowlinks, indices, index = {}, {}, [self.scc_num]
    components, inverse_components = {}, {}
    visited = []
    for node in nodes:
      if node not in indices:
        self.__partial_traverse(node, lowlinks, indices, index, components, inverse_components, visited, nodes)
    self.scc_num = index[0]
    return components, inverse_components

  def compute_scc(self):
    """
    Full compute of the SCCs of this graph
    O(|V|+|E|) time, based on Tarjan's algorithm
    @return a dictionary mapping component number to a set of component nodes, 
            and a reverse dictionary mapping a node to the component number
    """
    s_nodes = self.edges.keys()
    lowlinks, indices, index = {}, {}, [0]
    components, inverse_components = {}, {}
    visited = []
    for s_node in s_nodes:
      if s_node not in indices:
        self.__traverse(s_node, lowlinks, indices, index, components, inverse_components, visited)
    self.scc_num = index[0]
    self.components = components
    self.inverse_components = inverse_components
    self.__partition_edges()
    return components, inverse_components

  #######################
  ### PRIVATE METHODS ###
  #######################
  def __partial_traverse(self, node, lowlinks, indices, index, components, inverse_components, visited, nodes):
    """
    Private helper function to perform DFS and compute components
    of graph (final components in lowlinks)

    The partial version ONLY considers the nodes passed in as the 
    last argument. Any edges that lead to a node not in that set will
    be ignored.
    """
    indices[node], lowlinks[node] = index[0], index[0]
    index[0] = index[0] + 1
    visited.append(node)
    if node in self.edges:
      for e_node in self.edges[node]:
        if e_node not in nodes:
          continue
        if e_node not in indices:
          self.__traverse(e_node, lowlinks, indices, index, components, inverse_components, visited)
          lowlinks[node] = min(lowlinks[node], lowlinks[e_node])
        else:
          lowlinks[node] = min(lowlinks[node], indices[e_node])

    lowlink = lowlinks[node]
    if lowlink == indices[node] and len(visited) > 0:
      components[lowlink] = set()
      c_node = None 
      while len(visited) > 0 and c_node != node:
        c_node = visited.pop()
        inverse_components[c_node] = lowlink
        components[lowlink].add(c_node)

  def __traverse(self, node, lowlinks, indices, index, components, inverse_components, visited):
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
          self.__traverse(e_node, lowlinks, indices, index, components, inverse_components, visited)
          lowlinks[node] = min(lowlinks[node], lowlinks[e_node])
        else:
          lowlinks[node] = min(lowlinks[node], indices[e_node])

    lowlink = lowlinks[node]
    if lowlink == indices[node] and len(visited) > 0:
      components[lowlink] = set()
      c_node = None 
      while len(visited) > 0 and c_node != node:
        c_node = visited.pop()
        inverse_components[c_node] = lowlink
        components[lowlink].add(c_node)

  def __partition_edges(self):
    """
    Partitions the edges of the graph into "intra" or "inter"-SCC edges.
    """
    intra_edges, inter_edges = {}, {}
    for s_node in self.edges:
      intra_edges[s_node] = set()
      inter_edges[s_node] = set()
      e_nodes = self.edges[s_node]

      for e_node in e_nodes:
        if self.inverse_components[s_node] == self.inverse_components[e_node]:
          intra_edges[s_node].add(e_node)
        else:
          inter_edges[s_node].add(e_node)
    self.intra_edges, self.inter_edges = intra_edges, inter_edges

  def __str__(self):
    graph_str = ""
    for s_node in self.edges:
      neighbors = self.edges[s_node]
      for n in neighbors:
        graph_str += ("[%s %s]\n" % (str(s_node), str(n)))
    return graph_str

def print_graph(G):
  print str(G)
  print "Parents: %s\n" % G.parent
  print "Versions: %s\n" % G.version
  print "H: %s\n" % G.dynamic_set

a = Node('A')
b = Node('B')
c = Node('C')
d = Node('D')
e = Node('E')
f = Node('F')
g = Node('G')

e1 = Edge(a,b)
e2 = Edge(a,c)
e3 = Edge(c,a)
e4 = Edge(b,c)
e5 = Edge(c,d)
e6 = Edge(d,c)
e7 = Edge(e,f)
e8 = Edge(f,e)
e9 = Edge(c,g)
e10 = Edge(b,a)
e11 = Edge(g,c)

edge_set1 = set([e1, e2, e3, e4])
edge_set2 = set([e5])
edge_set3 = set([e6])
edge_set4 = set([e7])
edge_set5 = set([e8, e9])
edge_set6 = set([e10, e11])
edge_sets = [edge_set1, edge_set2, edge_set3, edge_set4, edge_set5, edge_set6]

def benchmark(edge_set_list):
  with Timer() as t:
    G1 = Graph()
    for edge_set in edge_set_list:
      for edge in edge_set:
        G1.add_edge(edge)
  fsecs = float(t.secs)

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
