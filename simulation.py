import random
import pandas as pd
import pygame as pg

from vec2 import Vector2
from road import Node, Network

# from road import Road, Intersection
from display import Display, ROAD_WIDTH
from vehicle import Vehicle, Car
from traffic_light import TrafficLight, build_traffic_lights


LANE_WIDTH = 5
ROAD_LENGTH = 20
SPAWN_INTERVAL = 3


class TrafficSim:
    def __init__(self, screen_width: int = 800, screen_height: int = 600, fps: int = 30):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # initialize display
        self.display = Display(self.screen_width, self.screen_height)

        # # initialize roads
        self._build_network()

        self.traffic_lights: dict[Node, TrafficLight] = build_traffic_lights(self.network)

        # initialize vehicle spawners
        self.vehicles = []
        self._spawn_timer = 0.0

        for _ in range(4):
            self._spawn_vehicle()

        self.clock = pg.time.Clock()
        self.fps = fps


    def start(self):
        '''Start the main loop of the simulation'''
        self.running = True
        self.display.bake_road_network(self.network)

        # main loop, 1 iteration = 1 frame
        while self.running:
            dt = self.clock.tick(self.fps) / 1000

            # handle user input
            self.handle_pg_events()

            # update traffic lights
            for light in self.traffic_lights.values():
                light.update(dt)


            self._spawn_timer -= dt
            if self._spawn_timer <= 0:
                self._spawn_vehicle()
                self._spawn_timer = SPAWN_INTERVAL

            dead = []
            for vehicle in self.vehicles:
                vehicle.move(dt, self.vehicles, self.traffic_lights)

                if not vehicle.path and vehicle.velocity.magnitude < 0.5:
                    dead.append(vehicle)

            for v in dead:
                self.vehicles.remove(v)
        
            # draw simulaiton
            self.display.draw(self.vehicles, self.traffic_lights, self.network)

            # flip display
            pg.display.flip()

            # wait for next frame
            # self.clock.tick(self.fps)


    def stop(self):
        '''Stop the simulation and close the window'''
        self.running = False
        self.display.close()


    def _spawn_vehicle(self):
        terminals = self.network.terminals
        if len(terminals) < 2:
            return
        
        origin, dest = random.choice(self._straight_pairs)

        path_nodes = self._find_path(origin, dest)
        if not path_nodes:
            return
        
        start_pos = origin.position

        colors = ["red", "blue", "orange", "purple", "cyan", "white"]
        vehicle = Car(
            position=start_pos,
            color=random.choice(colors),
            desired_speed=random.uniform(60, 100)
        )
        vehicle._origin = origin

        vehicle.path = path_nodes
        if vehicle.path:
            vehicle._heading = (vehicle.path[0].position - vehicle.position).normalized
            perp = Vector2(vehicle._heading.y, -vehicle._heading.x)
            vehicle.lane_offset = ROAD_WIDTH / 2 * 0.5

        self.vehicles.append(vehicle)

    
    def _find_path(self, origin: Node, dest: Node) -> list[Node]:
        from collections import deque
        queue = deque([[origin]])
        visited = {origin}

        while queue:
            path = queue.popleft()
            node = path[-1]
            if node is dest:
                return path[1:]
            
            for neighbor in node.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []


    def _register_vehicle(self, vehicle: Vehicle):
        pass


    def _remove_vehicle(self, vehicle: Vehicle):
        pass


    def handle_pg_events(self):
        '''Handles all interactions between User and Simulation'''

        for event in self.display.poll_events():
            # handle close window
            if event.type == pg.QUIT:
                self.stop()

            # handle window resize
            if event.type == pg.WINDOWRESIZED:
                new_width = event.dict.get("x")
                new_height = event.dict.get("y")
                self.display.screen_size = Vector2(new_width, new_height)

            # handle camera zoom 
            if event.type == pg.MOUSEWHEEL:
                direction = event.dict.get("y")
                self.display.zoom(direction)

        # get user key presses
        keys = pg.key.get_pressed()

        # handle WASD camera movement
        direction = Vector2.zero
        if keys[pg.K_w]:
            direction = direction + Vector2.up
        if keys[pg.K_s]:
            direction = direction + Vector2.down
        if keys[pg.K_a]:
            direction = direction + Vector2.left
        if keys[pg.K_d]:
            direction = direction + Vector2.right
        if direction != Vector2.zero: 
            # move camera
            self.display.move_camera(direction)


    def _build_network(self):
        # outer nodes
        n_node = Node(Vector2(    0,  500))
        e_node = Node(Vector2( 500,     0))
        s_node = Node(Vector2(    0, -500))
        w_node = Node(Vector2(-500,     0))

        # intersection node
        i_node = Node(
            # centered at world origin
            Vector2(0, 0),

            # add neighbors
            [
                n_node,
                e_node,
                s_node,
                w_node,
            ]
        )

        self.network = Network([i_node, n_node, e_node, s_node, w_node], num_lanes=2)
        
        self._straight_pairs = [
            (n_node, s_node),
            (s_node, n_node),
            (e_node, w_node),
            (w_node, e_node),
        ]