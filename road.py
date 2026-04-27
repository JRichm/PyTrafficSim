from vec2 import Vector2





class Node:
    def __init__(self, position: Vector2, neighbor_nodes: list["Node"] = None):
        self._position = position
        self.neighbors = neighbor_nodes


    @property
    def position(self) -> Vector2:
        return self._position


    @property
    def neighbors(self) -> list["Node"]:
        return self._neighbors
    

    @neighbors.setter
    def neighbors(self, nodes: list["Node"]):
        if nodes is None:
            self._neighbors = []
            return

        non_nodes = [n for n in nodes if not isinstance(n, Node)]
        if non_nodes:
            raise ValueError(f"Cannot add non-Node type ({type(non_nodes[0])}) to neighbors")

        # add self to other neighbor nodes
        for node in nodes:
            if self not in node.neighbors:
                node.add_neighbor(self)

        self._neighbors = nodes


    def add_neighbor(self, node: "Node"):
        if not isinstance(node, Node):
            raise TypeError(f"Cannot add non-Node type ({type(node)}) to neighbors")

        self._neighbors.append(node)



class Road:
    def __init__(
        self, 
        node_a: Node,
        node_b: Node,
        num_lanes: int = 2,
    ):
        self._node_a = node_a
        self._node_b = node_b
        self._num_lanes = num_lanes


    @property
    def node_a(self) -> Node:
        return self._node_a


    @property
    def node_b(self) -> Node:
        return self._node_b


    @property
    def num_lanes(self):
        return self._num_lanes


    @property
    def direction(self):
        return (self._node_b.position - self._node_a.position).normalized
    


class Network:
    def __init__(self, nodes: list[Node], num_lanes: int = 1):
        self.nodes: list[Node] = nodes
        self.num_lanes = num_lanes
        self.roads = []
        self.terminals = []
        self.intersections = []

        self._build(num_lanes)


    def _build(self, num_lanes):
        seen_edges: set[frozenset] = set()

        for node in self.nodes:
            if len(node.neighbors) == 1:
                self.terminals.append(node)
            if len(node.neighbors) > 2:
                self.intersections.append(node)

            for neighbor in node.neighbors:
                edge = frozenset([id(node), id(neighbor)])
                if edge not in seen_edges:
                    seen_edges.add(edge)
                    self.roads.append(Road(node, neighbor, num_lanes))