from vec2 import Vector2
from road import Node, Network

GREEN_DURATION = 5.0
YELLOW_DURATION = 1.5
STOP_DISTANCE = 55

class TrafficLight:

    PHASE_GREEN = "green"
    PHASE_YELLOW = "yellow"

    def __init__(self, node: Node):
        self.node = node

        self._neighbours = list(node.neighbors)
        self._phase_index = 0

        self._phase = self.PHASE_GREEN
        self._timer = GREEN_DURATION


    def update(self, dt: float):
        self._timer -= dt
        if self._timer <= 0:
            if self._phase == self.PHASE_GREEN:
                self._phase = self.PHASE_YELLOW
                self._timer = YELLOW_DURATION

            else:
                self._phase_index = (self._phase_index + 1) % len(self._neighbours)
                self._phase = self.PHASE_GREEN
                self._timer = GREEN_DURATION



    def is_green_for(self, approaching_from: Node) -> bool:

        if self._phase == self.PHASE_YELLOW:
            return False
    
        return self._neighbours[self._phase_index] == approaching_from
    

    @property
    def current_color(self) -> tuple:
        if self._phase == self.PHASE_GREEN:
            return (0, 220, 0)
        
        return (220, 180, 0)
    

    @property
    def stop_distance(self) -> float:
        return STOP_DISTANCE
    

def build_traffic_lights(network: Network) -> dict[Node, "TrafficLight"]:
    lights: dict[Node, TrafficLight] = {}

    for node in network.intersections:
        lights[node] = TrafficLight(node)

    return lights