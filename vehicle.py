from math import sqrt

from vec2 import Vector2
from road import Node

IDM_TIME_HEADWAY = 1.5
IDM_MIN_GAP = 10
IDM_ACCEL_EXPONENT = 4
MAX_DECEL = 50
MAX_ACCEL = 20

WAYPOINT_REACH_DIST = 15

class Vehicle:
    def __init__(
        self,
        position: Vector2,
        color: str,
        size: Vector2,
        desired_speed: float = 100.0,
    ):
        self.position = position
        self.color = color
        self.size = size
        self.velocity = Vector2.zero
        self.desired_speed = desired_speed
        self.lane_offset: float = 0

        self._origin: Node = None

        self.path: list[Node] = []

        self._heading: Vector2 = Vector2.up


    @property
    def current_target(self) -> Node:
        return self.path[0] if self.path else None
    

    def _advance_path(self):
        if self.path:
            self._origin = self.path[0]
            self.path.pop(0)


    def _idm_acceleration(self, speed: float, delta_v: float, gap: float) -> float:
        gap = max(gap, 0.1)

        s_star = (IDM_MIN_GAP + max(0.0, speed * IDM_TIME_HEADWAY + speed * delta_v / (2 * sqrt(MAX_ACCEL * MAX_DECEL))))

        free_road_term = (speed / max(self.desired_speed, 0.1)) ** IDM_ACCEL_EXPONENT

        interaction_term = (s_star / gap) ** 2

        return MAX_ACCEL * (1 - free_road_term - interaction_term)


    def move(self, dt: float, all_vehicles: list["Vehicle"], traffic_lights: dict):
        
        target = self.current_target

        if target is not None:
            to_target = target.position - self.position
            dist_to_target = to_target.magnitude

            if dist_to_target < WAYPOINT_REACH_DIST:
                self._advance_path()
                target = self.current_target

            if target is not None:
                if self._origin is not None:
                    self._heading = (target.position - self._origin.position).normalized
                else:
                    self._heading = (target.position - self.position).normalized

        speed = self.velocity.magnitude

        gap, leader_speed = self._find_leader(all_vehicles, traffic_lights)

        if target is None:
            accel = -MAX_DECEL if speed > 0 else 0.0

        else:
            delta_v = speed - leader_speed
            accel = self._idm_acceleration(speed, delta_v, gap)

        accel = max(-MAX_DECEL, min(MAX_ACCEL, accel))

        new_speed = max(0.0, speed + accel * dt)
        self.velocity = self._heading * new_speed
        self.position = self.position + self.velocity * dt


    def _find_leader(
        self,
        all_vehicles: list["Vehicle"],
        traffic_lights: dict,
    ) -> tuple[float, float]:
        LOOK_AHEAD = 300
        LATERAL_TOL = 20

        best_gap = LOOK_AHEAD
        best_speed = self.desired_speed

        heading = self._heading
        my_length = self.size.y

        for other in all_vehicles:
            if other is self:
                continue

            rel = other.position - self.position

            # skip oncoming vehicles
            dot = other._heading.x * heading.x + other._heading.y * heading.y
            if dot < -0.5:
                continue

            lon = rel.x * heading.x + rel.y * heading.y
            if lon <= 0:
                continue # behind

            lat = abs(-rel.x * heading.y + rel.y * heading.x)
            if lat > LATERAL_TOL:
                continue # not in our lane

            gap = lon - other.size.y / 2 - my_length / 2
            if gap < best_gap:
                best_gap = gap
                best_speed = other.velocity.magnitude


        for node, light in traffic_lights.items():

            if node not in self.path:
                continue


            path_idx = self.path.index(node)
            if path_idx == 0:
                approaching_from = self._origin
            else:
                approaching_from = self.path[path_idx - 1]

            if approaching_from is None:
                continue

            if light.is_green_for(approaching_from):
                continue

            stop_pos = node.position
            rel = stop_pos - self.position
            lon = rel.x * heading.x + rel.y * heading.y
            if lon <= 0:
                continue

            gap = lon - light.stop_distance - my_length / 2
            if gap < best_gap:
                best_gap = gap
                best_speed = 0.0

        return best_gap, best_speed


class Car(Vehicle):
    def __init__(
        self,
        position: Vector2 = Vector2.zero,
        color: str = "red",
        size: Vector2 = Vector2(15, 30),
        desired_speed: float = 80.0,
    ):
        super().__init__(position, color, size, desired_speed)



class Truck(Vehicle):
    def __init__(
        self,
        position: Vector2 = Vector2.zero,
        color: str = "grey",
        size: Vector2 = Vector2(15, 60),
        cargo: int = 0,
        desired_speed: float = 55.0,
    ):
        super().__init__(position, color, size, desired_speed)



class Bus(Vehicle):
    def __init__(
        self,
        position: Vector2 = Vector2.zero,
        color: str = "yellow",
        size: Vector2 = Vector2(15, 70),
        stops: list = [],
        desired_speed: float = 60.0,
    ):
        super().__init__(position, color, size, desired_speed)

        self._next_stop = None
        self._is_stopped = False



class PoliceCar(Car):
    def __init__(
        self,
        position: Vector2 = Vector2.zero,
        color: str = "white",
        size: Vector2 = Vector2(15, 70),
    ):
        super().__init__(position, color, size)

        self._lights_on = False