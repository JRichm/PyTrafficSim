import math
import pygame as pg

from vec2 import *
from road import Network


pg.init()


TEST_BG_SIZE = 2000
CAMERA_SPEED = 1
ROAD_COLOR = (100, 100, 100)
ROAD_WIDTH = 50

# WORLD_SCALE = 5
TL_RADIUS = 10
TL_OFFSET = 60


class Display:
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self._window: pg.Surface = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
        self._screen_size = Vector2(screen_width, screen_height)

        self._camera_pos: Vector2[float, float] = Vector2(0, 0) # world position
        self._camera_zoom: int = 1 # min: 1, max = 10

        self._bg = self._test_bg_sprite()
        self._scale_background()

        self._road_surface: pg.Surface = None
        self._road_surface_zoom = None

        self._draw_surface = pg.Surface((self.screen_size.x, self.screen_size.y))

        self._road_min = None
        self._road_max = None


    @property
    def screen_size(self) -> Vector2:
        return self._screen_size
    

    @screen_size.setter
    def screen_size(self, new_size: Vector2):
        self._screen_size = new_size
        self._draw_surface = pg.Surface((self.screen_size.x, self.screen_size.y))


    def zoom(self, direction: int = None):
        if not direction:
            return

        # zoom direction must be 1 or -1
        if abs(direction) != 1:
            return
        
        new_zoom = self._camera_zoom + direction

        # make sure new zoom level is valid
        # min: 1, max = 10
        if new_zoom < 1 or new_zoom > 10:
            return
        
        self._camera_zoom = new_zoom
        self._scale_background()


    def poll_events(self) -> list[pg.event.Event]:
        # return pygame events
        return pg.event.get()


    def _world_to_screen_cords(self, world_pos: Vector2) -> tuple:
        screen_x = (world_pos.x - self._camera_pos.x) * self._camera_zoom + self._screen_size.x / 2
        screen_y = -(world_pos.y - self._camera_pos.y) * self._camera_zoom + self._screen_size.y / 2
        return (int(screen_x), int(screen_y))
    

    def world_to_screen_size(self, world_size) -> tuple[int, int]:
        return (
            int(world_size.x * self._camera_zoom),
            int(world_size.y * self._camera_zoom)
        )
        

    def _world_to_surface_cords(self, world_pos: Vector2) -> tuple:
        x = int(world_pos.x - self._road_min.x)
        y = int(-(world_pos.y - self._road_max.y))
        return (x, y)


    def draw(self, vehicles: list, traffic_lights: dict, network):
        '''Main draw function that draws the entire simulation

        Creates a blank surface then adds details layer by layer, giving a sense of depth:
            1) background
            2) roads
            3) vehicles
            4) police lights
            5) traffic lights
        '''

        # initialize a new black surface to blit to
        self._draw_surface.fill((0, 0, 0))

        # draw background
        self.draw_background()

        # draw roads
        self._update_road_surface()
        top_left_world = Vector2(self._road_min.x, self._road_max.y)
        blit_pos = self._world_to_screen_cords(top_left_world)
        self._draw_surface.blit(self._road_surface, blit_pos)

        for node, light in traffic_lights.items():
            self.draw_traffic_light(node, light, network)

        # draw vehicles
        for vehicle in vehicles:
            self.draw_vehicle(vehicle)

        # draw police lights

        # draw traffic lights

        # finally blits draw surface to the main window
        self._window.blit(self._draw_surface, (0, 0))



    def move_camera(self, direction: Vector2):
        '''Updates camera position based on a given direction, camera speed, and current zoom level'''
        self._camera_pos = self._camera_pos + direction * CAMERA_SPEED * (10 / self._camera_zoom)


    def _scale_background(self):
        size = int(TEST_BG_SIZE * self._camera_zoom)
        self._bg_scaled = pg.transform.scale(self._bg_base, (size, size))


    def draw_background(self):
        origin = self._world_to_screen_cords(Vector2(0, 0))
        blit_pos = (
            origin[0] - (TEST_BG_SIZE * self._camera_zoom) // 2,
            origin[1] - (TEST_BG_SIZE * self._camera_zoom) // 2
        )
        self._draw_surface.blit(self._bg_scaled, blit_pos)
            

    def draw_vehicle(self, vehicle):

        sw, sh = self.world_to_screen_size(vehicle.size)
        sw = max(sw, 2)
        sh = max(sh, 2)
 
        surf = pg.Surface((sw, sh), pg.SRCALPHA)
        pg.draw.rect(surf, vehicle.color, (0, 0, sw, sh))

        pg.draw.rect(surf, (30, 30, 30), (0, 0, sw, max(2, sh // 5)))
 
        hx = vehicle._heading.x
        hy = vehicle._heading.y
        angle_rad = math.atan2(hx, hy)
        angle_deg = math.degrees(angle_rad)
 
        rotated = pg.transform.rotate(surf, angle_deg)
 
        perp = Vector2(vehicle._heading.y, -vehicle._heading.x)
        draw_pos = Vector2(
            vehicle.position.x + perp.x * vehicle.lane_offset,
            vehicle.position.y + perp.y * vehicle.lane_offset,
        )
        screen_pos = self._world_to_screen_cords(draw_pos)
        rect = rotated.get_rect(center=screen_pos)
        self._draw_surface.blit(rotated, rect.topleft)


    def draw_police_lights(self, police_car):
        pass


    def draw_traffic_light(self, node, light, network):
        color = light.current_color

        for neighbor in node.neighbors:

            diff = neighbor.position - node.position
            mag = diff.magnitude

            if mag == 0:
                continue

            indicator_world = Vector2(
                node.position.x + diff.x / mag * TL_OFFSET,
                node.position.y + diff.y / mag * TL_OFFSET
            )

            arm_color = light.current_color if light.is_green_for(neighbor) else (220, 0, 0)

            screen_pos = self._world_to_screen_cords(indicator_world)
            r = max(4, int(TL_RADIUS * self._camera_zoom))
            pg.draw.circle(self._draw_surface, arm_color, screen_pos, r)
            pg.draw.circle(self._draw_surface, (255, 255, 255), screen_pos, r, 2)


    def bake_road_network(self, network: Network):
        all_x = [node.position.x for node in network.nodes]
        all_y = [node.position.y for node in network.nodes]

        self._road_min = Vector2(min(all_x), min(all_y))
        self._road_max = Vector2(max(all_x), max(all_y))

        width  = int(self._road_max.x - self._road_min.x)
        height = int(self._road_max.y - self._road_min.y)

        self._road_surface_base = pg.Surface((width, height), pg.SRCALPHA)

        # draw roads and lane markings
        for road in network.roads:
            self._bake_road(road)

        # blit empty square to cover lane markings inside intersections
        for node in network.intersections:
            self._bake_intersection(node, network)

        self._road_surface = self._road_surface_base
        self._road_surface_zoom = self._camera_zoom


    def _bake_road(self, road):

        # get world positions of road start and end
        start = self._world_to_surface_cords(road.node_a.position)
        end = self._world_to_surface_cords(road.node_b.position)

        # get width of road based on number of lanes
        # num_lanes = number of lanes on EACH side of the road
        total_width = road.num_lanes * ROAD_WIDTH

        # draw road base
        pg.draw.line(self._road_surface_base, ROAD_COLOR, start, end, width=total_width)

        # perpendicular vector
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(1, (dx**2 + dy**2) ** 0.5)
        perp = (-dy / length, dx / length)

        lane_width = ROAD_WIDTH / 2

        # draw yellow center line
        self._draw_marking_line(start, end, perp, offset=0, color="yellow", line_width=2)

        # dashed lane dividers, drawn on each side of lane
        for lane in range(1, road.num_lanes):
            offset = lane * lane_width
            self._draw_marking_line(start, end, perp, offset=offset, color="white", line_width=2, dashed=True)
            self._draw_marking_line(start, end, perp, offset=-offset, color="white", line_width=2, dashed=True)


    def _bake_intersection(self, node, network):
        # get size of widest road
        connected_roads = [r for r in network.roads if r.node_a == node or r.node_b == node]
        max_width = max(r.num_lanes * ROAD_WIDTH for r in connected_roads)

        # get world position of intersection
        center = self._world_to_surface_cords(node.position)
        rect = pg.Rect(
            center[0] - max_width // 2,
            center[1] - max_width // 2,
            max_width,
            max_width
        )

        # blit rect to road surface
        pg.draw.rect(self._road_surface_base, ROAD_COLOR, rect)


    def _draw_marking_line(self, start, end, perp, offset, color, line_width, dashed=False):
        s = (start[0] + perp[0] * offset, start[1] + perp[1] * offset)
        e = (end[0]   + perp[0] * offset, end[1]   + perp[1] * offset)

        # if solid, draw line and return
        if not dashed:
            pg.draw.line(self._road_surface_base, color, s, e, width=line_width)
            return

        dash_length = 20
        gap_length  = 20
        total = ((e[0]-s[0])**2 + (e[1]-s[1])**2) ** 0.5
        if total == 0:
            return

        ux = (e[0] - s[0]) / total
        uy = (e[1] - s[1]) / total

        pos = 0
        drawing = True
        while pos < total:
            seg = dash_length if drawing else gap_length
            next_pos = min(pos + seg, total)

            if drawing:
                p1 = (s[0] + ux * pos,      s[1] + uy * pos)
                p2 = (s[0] + ux * next_pos, s[1] + uy * next_pos)
                pg.draw.line(self._road_surface_base, color, p1, p2, width=line_width)

            pos = next_pos
            drawing = not drawing


    def _update_road_surface(self):
        if self._road_surface_zoom != self._camera_zoom:
            scaled_size = (
                int(self._road_surface_base.get_width()  * self._camera_zoom),
                int(self._road_surface_base.get_height() * self._camera_zoom)
            )
            self._road_surface = pg.transform.scale(self._road_surface_base, scaled_size)
            self._road_surface_zoom = self._camera_zoom


    def close(self):
        pg.quit()


    def _test_bg_sprite(self) -> pg.Surface:
        # just a checkerboard surface generator to test camera movement 
        sqr_size = 50
        
        bg = pg.Surface((TEST_BG_SIZE, TEST_BG_SIZE))

        x_squares = (TEST_BG_SIZE // sqr_size) + 1
        y_squares = (TEST_BG_SIZE // sqr_size) + 1

        for x in range(x_squares):
            for y in range(y_squares):
                sqr = pg.Surface((sqr_size, sqr_size))
                if (x + y) % 2 == 0:
                    sqr.fill((50, 50, 50))
                else:
                    sqr.fill((30, 30, 30))

                bg.blit(sqr, (x * sqr_size, y * sqr_size))

        self._bg_base = bg
        self._bg_scaled = bg

        return bg

