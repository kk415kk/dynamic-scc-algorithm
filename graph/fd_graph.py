# See https://wiki.python.org/moin/TimeComplexity for running times
### FULLY DYNAMIC GRAPH, with optimized bulk insertions/deletions ###

class Node:
  """
  Class to represent a node. A node represents its own strongly connected component;
  its children are nodes that are part of the SCC that it represents.
  """
  def __init__(self, value=None):
    self.value = value
  def __eq__(self, other):
    return self is other
  def __repr__(self):
    return '<Node "%s" @%s>' % (str(self.value), str(hex(id(self))))
  def __hash__(self):
    return hash(repr(self))
  def __str__(self):
    return '<Node "%s" @%s>' % (str(self.value), str(hex(id(self))))

class Edge:
  """
  Class to represent an edge
  """
  def __init__(self, s_node, e_node, scc_edge=False):
    self.nodes, self.scc_edge = (s_node, e_node), scc_edge
  def __eq__(self, other):
    return self.nodes[0] == other.nodes[0] and self.nodes[1] == other.nodes[1]
  def __repr__(self):
    return '[Edge: %s %s @%s]' % (str(self.nodes[0]), str(self.nodes[1]), str(hex(id(self))))
  def __hash__(self):
    return hash(repr(self))
  def __str__(self):
    return '[Edge: %s %s]' % (str(self.nodes[0]), str(self.nodes[1]))

class Graph:
  """
  Class to represent a DIRECTED graph using linear space
  """
  def __init__(self, edges=set()):
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
    self.add_edges(edges)
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
    Add multiple edges, one at a time.
    Computes the SCCs at the end to ensure graph structures are maintained.
    @param edge_set: the edges to be added to the graph
    """
    for edge in edge_set:
      self.add_edge(edge)
    if len(edge_set) > 0:
      self.compute_scc()

  def optimized_add_edges(self, edge_set):
    """
    An optimized bulk edge insertion method.
    @param edge_set: a set of edges to be added to the graph
    """
    check_scc = set()
    for edge in edge_set:
      s_node, e_node = edge.nodes
      self.add_edge(edge)

      # First 3 cases are just adding inter-SCC edges, since one or more of the nodes
      # were not part of the graph to begin with
      if s_node not in self.inverse_components or e_node not in self.inverse_components:
        self.add_edge(edge)
        if s_node not in self.inter_edges:
          self.inter_edges[s_node] = set()
        self.inter_edges[s_node].add(e_node)

      # First 3 cases as noted above
      if s_node not in self.inverse_components and e_node not in self.inverse_components:
        self.inverse_components[s_node] = self.scc_num
        self.inverse_components[e_node] = self.scc_num + 1
        self.components[self.scc_num] = set([s_node])
        self.components[self.scc_num+1] = set([e_node])
        self.scc_num += 2
      elif s_node not in self.inverse_components:
        self.inverse_components[s_node] = self.scc_num
        self.components[self.scc_num] = set([s_node])
        self.scc_num += 1
      elif e_node not in self.inverse_components:
        self.inverse_components[e_node] = self.scc_num
        self.components[self.scc_num] = set([e_node])
        self.scc_num += 1
      elif self.inverse_components[s_node] == self.inverse_components[e_node]:
        self.add(edge)
        if s_node not in self.intra_edges:
          self.intra_edges[s_node] = set()
        self.intra_edges[s_node].add(e_node)
      else:
        check_scc.add(edge)

    # If there are any edges that we need to check, let's run maintenance on them
    if len(check_scc) > 0:
      self.__run_add_maintenance(check_scc)

  def remove_edge(self, edge):
    """
    Removes an edge from the graph's internal maintenance structures
    O(1) time to remove node from a set inside a map
    O(1) time to remove node from a map (dictionary)
    NOTE: Should be removed from public API
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
          self.__clear_component_node(s_node)
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

  def remove_edges(self, edge_set):
    """
    Remove multiple edges, one at a time
    Computes the SCCs at the end to ensure graph structures are maintained.
    @param edge_set: a set of edges to be removed
    """
    for edge in edge_set:
      self.remove_edge(edge)
    if len(edge_set) > 0:
      self.compute_scc()

  def optimized_remove_edges(self, edge_set):
    """
    Optimized bulk removal of edges
    @param edges: a set of edges to be removed
    """
    check_scc = set()
    for edge in edge_set:
      s_node, e_node = edge.nodes
      if self.inverse_components[s_node] == self.inverse_components[e_node]:
        scc = self.inverse_components[s_node]
        check_scc.add(scc)
      self.remove_edge(edge)

    for scc in check_scc:
      # Check if the SCC still exists; could be taken care of by cleanup
      # code already
      if scc in self.components:
        nodes = self.components[scc]
        components, inverse_components = self.__compute_partial_scc_deletion(nodes)

        # If the component got split up, we need to merge the results in
        # 1. Delete the scc from self.components
        # 2. Merge in the new components
        # 3. Update all the nodes in self.inverse_components
        # NOTE: We can re-use the number "scc" by replacing the max number of 
        #       components with "scc", then going through all of inverse_comp
        #       to reset those nodes to "scc". Currently NOT implemented.
        if len(components) > 1:
          del self.components[scc]
          self.components.update(components)
          self.inverse_components.update(inverse_components)
          self.__delete_partial_partition_edges(components, inverse_components)

  def get_nodes(self):
    """
    O(|V|) time to retrieve all nodes in the graph
    """
    return set(self.edges.keys()) | set(self.rev_edges.keys())

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

  def __str__(self):
    """
    Returns a text representation of the graph.
    """
    graph_str = ""
    for s_node in self.edges:
      neighbors = self.edges[s_node]
      for n in neighbors:
        graph_str += ("[%s %s]\n" % (str(s_node), str(n)))
    return graph_str

  #######################
  ### PRIVATE METHODS ###
  #######################

  ### FULL SCC COMPUTE METHODS ###
  def __traverse(self, node, lowlinks, indices, index, components, inverse_components, visited):
    """
    Private helper function to perform DFS and compute components
    of graph (final components in lowlinks)
    @param node: a Node object to start traversing from
    @param lowlinks, indices: numbers used to track when a node was traversed
    @param index: the current unused index number
    @param components: the forward components mapping of SCC number to node
    @param inverse_components: the inverse index on components
    @param visited: the visited nodes
    """
    indices[node], lowlinks[node] = index[0], index[0]
    index[0] = index[0] + 1
    visited.append(node)
    if node in self.edges:
      for e_node in self.edges[node]:
        if e_node not in indices:
          self.__traverse(e_node, lowlinks, indices, index, components, inverse_components, visited)
          lowlinks[node] = min(lowlinks[node], lowlinks[e_node])
        elif e_node in visited:
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
    Partitions all current edges of the graph into intra-SCC or inter-SCC
    edges.
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

  ### PARTIAL SCC COMPUTE METHODS: ADDITION ###
  def __run_add_maintenance(self, check_scc):
    """
    Traverse collapsed nodes instead.
    """
    # TEST: Add all the edges to inter_edges for now
    for edge in check_scc:
      s_node, e_node = edge.nodes
      if s_node not in self.inter_edges:
        self.inter_edges[s_node] = set()
      self.inter_edges[s_node].add(e_node)

    # Modified Tarjan's algorithm on the DAG of the graph
    components, inverse_components = self.__compute_partial_scc_addition(check_scc)

    # Check for each edge in check_scc whether any SCCs have been joined
    affected_sccs = self.__merge_components(components, inverse_components)

    # Partition the edges into intra_edges if necessary
    self.__add_partial_partition_edges(affected_sccs)

  def __merge_components(self, components, inverse_components):
    """
    Merges the relevant components based on the partially traversed collapsed DAG
    of the graph.
    @param components
    @param inverse_components
    @return the affected SCCs (the ones that are merged - returns the number of the
      SCC that everything was merged into)
    """
    affected_sccs = set()
    for scc_group in components:
      if len(components[scc_group]) > 1:
        sccs = components[scc_group]
        keep_scc = next(iter(sccs))
        affected_sccs.add(keep_scc)
        merged_nodes = set([node for scc in sccs for node in self.components[scc]])

        self.components[keep_scc] = merged_nodes

        for scc in (sccs - set([keep_scc])):
          del self.components[scc]
        for node in merged_nodes:
          self.inverse_components[node] = keep_scc
    return affected_sccs

  def __compute_partial_scc_addition(self, check_scc):
    """
    Computes the SCCs of the graph from traversing just the nodes in question,
    considering only intra-SCC edges

    NOTE: The partial SCC compute does NOT partition the edges, so those need to
          be updated by the calling method.

    @param check_scc: the edges that need to be checked
    @return a dictionary mapping component number to a set of component nodes, 
            and a reverse dictionary mapping a node to the component number,
            and the traversed edges
    """
    index, lowlinks, indices, components, inverse_components, visited = [self.scc_num], {}, {}, {}, {}, []
    for edge in check_scc:
      s_node, e_node = edge.nodes
      scc = self.inverse_components[s_node]
      if scc not in indices:
        self.__partial_addition_traverse(scc, lowlinks, indices, index, components, inverse_components, visited)
    return components, inverse_components

  def __partial_addition_traverse(self, scc, lowlinks, indices, index, components, inverse_components, visited):
    """
    Traverses the collapsed DAG of the graph instead of the individual nodes. The components map 
    and inverse index reflects the SCC numbers rather than the individual nodes in the SCC.

    Private helper function to perform DFS and compute components
    of graph (final components in lowlinks)

    The partial version ONLY considers the nodes passed in as the 
    last argument. Any edges that lead to a node not in that set will
    be ignored. This is for the ADDITION case.
    @param scc: the SCC we're currently on
    @param lowlinks, indices: numbers used to track when a node was traversed
    @param index: the current unused index number
    @param components: the forward components mapping of SCC number to node
    @param inverse_components: the inverse index on components
    @param visited: the visited nodes
    """
    inter_edges = dict((node, self.inter_edges[node]) for node in self.components[scc] if node in self.inter_edges)

    indices[scc], lowlinks[scc] = index[0], index[0]
    index[0] = index[0] + 1
    visited.append(scc)

    next_sccs = [self.inverse_components[e_node] for node in inter_edges for e_node in inter_edges[node]]

    for n_scc in next_sccs:
      if n_scc not in indices:
        self.__partial_addition_traverse(n_scc, lowlinks, indices, index, components, inverse_components, visited)
        lowlinks[scc] = min(lowlinks[scc], lowlinks[n_scc])
      elif scc in visited:
        lowlinks[scc] = min(lowlinks[scc], indices[n_scc])        

    lowlink = lowlinks[scc]
    if lowlink == indices[scc] and len(visited) > 0:
      components[lowlink] = set()
      c_scc = None 
      while len(visited) > 0 and c_scc != scc:
        c_scc = visited.pop()
        inverse_components[c_scc] = lowlink
        components[lowlink].add(c_scc)

  def __add_partial_partition_edges(self, affected_sccs):
    """
    Maintain the edge partitions after an insertion operation.
    @param affected_sccs: the SCCs whose edges need to be re-partitioned
    """
    # Update edge partitioning
    for scc in affected_sccs:
      nodes = self.components[scc]
      for node in nodes:
        remove_nodes = {}
        for e_node in self.inter_edges.get(node, set()):
          if self.inverse_components[node] == self.inverse_components[e_node]:
            if node not in self.intra_edges:
              self.intra_edges[node] = set()
            self.intra_edges[node].add(e_node)

            # Nodes for removal (cannot remove during iteration)
            if node not in remove_nodes:
              remove_nodes[node] = set()
            remove_nodes[node].add(e_node)

        for r_node in remove_nodes:
          self.inter_edges[r_node] -= remove_nodes[r_node]
          if len(self.inter_edges[r_node]) == 0:
            del self.inter_edges[r_node]

  ### PARTIAL SCC COMPUTE METHODS: DELETION ###
  def __compute_partial_scc_deletion(self, nodes):
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
        self.__partial_deletion_traverse(node, lowlinks, indices, index, components, inverse_components, visited, nodes)
    self.scc_num = index[0]
    return components, inverse_components

  def __partial_deletion_traverse(self, node, lowlinks, indices, index, components, inverse_components, visited, nodes):
    """
    Private helper function to perform DFS and compute components
    of graph (final components in lowlinks)

    The partial version ONLY considers the nodes passed in as the 
    last argument. Any edges that lead to a node not in that set will
    be ignored. This is for the DELETION case.
    @param node: a Node object to start traversing from
    @param lowlinks, indices: numbers used to track when a node was traversed
    @param index: the current unused index number
    @param components: the forward components mapping of SCC number to node
    @param inverse_components: the inverse index on components
    @param visited: the visited nodes
    """
    indices[node], lowlinks[node] = index[0], index[0]
    index[0] = index[0] + 1
    visited.append(node)
    if node in self.edges:
      for e_node in self.edges[node]:
        if e_node not in nodes:
          continue
        if e_node not in indices:
          self.__partial_deletion_traverse(e_node, lowlinks, indices, index, components, inverse_components, visited, nodes)
          lowlinks[node] = min(lowlinks[node], lowlinks[e_node])
        elif e_node in visited:
          lowlinks[node] = min(lowlinks[node], indices[e_node])

    lowlink = lowlinks[node]
    if lowlink == indices[node] and len(visited) > 0:
      components[lowlink] = set()
      c_node = None 
      while len(visited) > 0 and c_node != node:
        c_node = visited.pop()
        inverse_components[c_node] = lowlink
        components[lowlink].add(c_node)

  def __delete_partial_partition_edges(self, components, inverse_components):
    """
    Computes a partial recompute of the edge partitions.
    For a deletion, SCCs can only be broken, not created, so only 
    update the nodes that are no longer part of an SCC. For these,
    just move all of the node's intra-SCC edges to inter-SCC ones.
    @param components: the partial components that were re-computed
    @param inverse_components: the inverse index on the partial components
    """
    for node in inverse_components:
      scc = inverse_components[node]
      if len(components[scc]) == 1 and node in self.intra_edges:
        if node not in self.inter_edges:
          self.inter_edges[node] = set()
        self.inter_edges[node] = self.inter_edges[node] | self.intra_edges[node]
        del self.intra_edges[node]
      else:
        # The node was part of an SCC, is still now part of an SCC, 
        # so its edge is still part of an SCC and no changes need to be made.
        continue
        
  def __clear_component_node(self, node):
    """
    Clears the node from the inverse components map and the forward 
    components map.
    @param node: a Node object
    """
    scc = self.inverse_components[node]
    del self.inverse_components[node]
    self.components[scc].remove(node)
    if len(self.components[scc]) == 0:
      del self.components[scc]

#######################
### TESTING METHODS ###
#######################
def print_graph(G):
  print str(G)
  print "Parents: %s\n" % G.parent
  print "Versions: %s\n" % G.version
  print "H: %s\n" % G.dynamic_set

def benchmark(edge_set_list):
  with Timer() as t:
    G1 = Graph()
    for edge_set in edge_set_list:
      for edge in edge_set:
        G1.add_edge(edge)
  fsecs = float(t.secs)
