import pygame
from pygame.locals import *
import math


class Map:
    def __init__(self, map_list: list[list]):
        self.map = map_list
        self.tile_size = 64
        self.screen_x_offset = 0
        self.screen_y_offset = 0
        self.map_coordinates = self._get_map_coordinates()
        self.rect_map = self._create_rects()
        self.colors = {0: 'black', 1: 'white', 2: 'magenta'}

    def _create_rects(self):
        import copy
        rect_map = copy.deepcopy(self.map)
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                rect_map[row_idx][col_idx] = Rect(
                    [col_idx * self.tile_size + self.tile_size * self.screen_x_offset, row_idx * self.tile_size + self.tile_size * self.screen_y_offset,
                     self.tile_size - 1, self.tile_size - 1])
        return rect_map

    def draw(self, surface):
        for row_idx, row in enumerate(self.map):
            for col_idx, cell_color in enumerate(row):
                pygame.draw.rect(surface, self.colors[cell_color], self.rect_map[row_idx][col_idx])

    def _get_map_coordinates(self):
        c = dict()
        c['x1'] = self.screen_x_offset * self.tile_size
        c['y1'] = self.screen_y_offset * self.tile_size
        c['x2'] = c['x1'] + len(self.map) * self.tile_size
        c['y2'] = c['y1'] + len(self.map[0]) * self.tile_size

        return c


def clamp_to_range(c, r1, r2):
    if c < r1:
        return r1
    elif c >= r2:
        return r2 - 1
    else:
        return c


class Player:
    def __init__(self, x, y, level_map: Map):
        self.level_map = level_map
        self.screen_x_offset = level_map.tile_size * level_map.screen_x_offset
        self.screen_y_offset = level_map.tile_size * level_map.screen_y_offset
        self.x = x + self.screen_x_offset
        self.y = y + self.screen_y_offset
        self.color = "yellow"
        self.size = 10
        self.rect = Rect([self.x - self.size // 2, self.y - self.size // 2, self.size, self.size])
        self.rotation = 0
        self.dx = math.cos(math.radians(self.rotation))
        # dy is negative sin since screen y coordinates increase downward, unlike Cartesian
        self.dy = -math.sin(math.radians(self.rotation))
        self.pov_line = self._calc_view_line()
        self.fov = 60

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.line(surface, self.color, [self.x, self.y], self.pov_line, 2)

    def move(self, direction):
        speed = 5
        org_x = self.x
        org_y = self.y

        if direction == 'forward':
            self.x += self.dx * speed
            self.y += self.dy * speed
        else:
            self.x -= self.dx * speed
            self.y -= self.dy * speed

        self._wall_collision(org_x, org_y)

        self.rect.update(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        self.pov_line = self._calc_view_line()

    def _wall_collision(self, org_x, org_y):
        org_map_x, org_map_y = self._map_location(org_x, org_y)
        new_map_x, new_map_y = self._map_location(self.x, self.y)

        # Collision detection
        if self.level_map.map[new_map_y][new_map_x] != 0:  # is new position colliding with a wall?
            # Enable wall gliding
            if org_map_x != new_map_x and org_map_y != new_map_y:  # Trying to move between tiles on both x and y
                test_x, test_y = self._map_location(org_x, self.y)  # Can we move on the y-axis?
                if self.level_map.map[test_y][test_x] != 0:
                    self.y = org_y  # If not, keep y position
                test_x, test_y = self._map_location(self.x, org_y)  # Can we move on the x-axis?
                if self.level_map.map[test_y][test_x] != 0:
                    self.x = org_x  # If not, keep x position
            elif org_map_x != new_map_x:  # Colliding move between tiles on x-axis
                self.x = org_x  # so hold x position
            elif org_map_y != new_map_y:  # Colliding move between tiles on y-axis
                self.y = org_y  # so hold y position

    def rotate(self, n):
        speed = 1
        self.rotation = (self.rotation + n * speed) % 360
        self.dx = math.cos(math.radians(self.rotation))
        self.dy = -math.sin(math.radians(self.rotation))
        self.pov_line = self._calc_view_line()

    def _calc_view_line(self):
        line_length = 20
        dx = self.x + self.dx * line_length
        dy = self.y + self.dy * line_length

        return dx, dy

    def _map_location(self, x, y):
        map_x = abs(int((x - self.screen_x_offset) // self.level_map.tile_size))
        map_y = abs(int((y - self.screen_y_offset) // self.level_map.tile_size))
        return min(map_x, len(self.level_map.map[0]) - 1), min(map_y, len(self.level_map.map) - 1)

    def strafe(self, direction):
        speed = 2
        org_x = self.x
        org_y = self.y
        if direction == 'left':
            angle = 90
        else:
            angle = -90
        self.x += math.cos(math.radians(self.rotation + angle)) * speed
        self.y += -math.sin(math.radians(self.rotation + angle)) * speed
        self._wall_collision(org_x, org_y)

        self.rect.update(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        self.pov_line = self._calc_view_line()

    def draw_ray(self, surface):
        for r in range(-30,30):
            ray_angle = (self.rotation + r) % 360
            ray_slope = math.tan(math.radians(ray_angle))
            if ray_slope == 0:
                ray_slope = 0.000001
            ray_to_x_step = math.sqrt(self.level_map.tile_size ** 2 + ray_slope ** 2)
            ray_to_y_step = math.sqrt(self.level_map.tile_size ** 2 + 1 / ray_slope ** 2)
            test_to_x_x, test_to_x_y, test_to_y_y, test_to_y_x = None, None, None, None

            # Cast ray to next tile
            ax = (self.x / self.level_map.tile_size) % 1
            ay = (self.y / self.level_map.tile_size) % 1
            # Check Vertical (x-axis) tiles
            if 270 <= ray_angle < 360 or 0 <= ray_angle < 90:  # looking right
                ray_to_x_x = self.x + (1 - ax) * ray_to_x_step
                ray_to_x_y = self.y - ray_slope * ray_to_x_step * (1 - ax)
            elif 90 <= ray_angle <= 270:  # looking left
                ray_to_x_x = self.x - ax * ray_to_x_step
                ray_to_x_y = self.y + ray_slope * ray_to_x_step * ax

            # Check Horizontal (y-axis) tiles
            if 0 <= ray_angle <= 180:  # looking up
                ray_to_y_x = self.x + 1 / ray_slope * ray_to_y_step * ay
                ray_to_y_y = self.y - ay * ray_to_y_step
            elif 180 <= ray_angle < 360:  # looking down
                ray_to_y_x = self.x - 1 / ray_slope * ray_to_y_step * (1 - ay)
                ray_to_y_y = self.y + (1 - ay) * ray_to_y_step

            # # Check vertical tiles
            # x_step = 1
            # while True:
            #     if 270 < ray_angle < 360 or 0 <= ray_angle < 90:  # looking right
            #         ray_to_x_x = self.rect.centerx + self.level_map.tile_size * x_step
            #         ray_to_x_y = self.rect.centery - ray_slope * ray_to_x_step * x_step
            #         # print("looking right")
            #
            #     elif 90 < ray_angle < 270:  # looking left
            #         ray_to_x_x = self.rect.centerx - self.level_map.tile_size * x_step
            #         ray_to_x_y = self.rect.centery + ray_slope * ray_to_x_step * x_step
            #         # print("looking left")
            #     else:
            #         ray_to_x_x = self.rect.centerx * x_step
            #         ray_to_x_y = self.rect.centery * x_step
            #         # print("looking vertical")
            #         break
            #     # print(ray_to_x_x, ray_to_x_y)
            #     # ray_to_x_x = clamp_to_range(ray_to_x_x, self.level_map.map_coordinates['x1'], self.level_map.map_coordinates['x2'])
            #     # ray_to_x_y = clamp_to_range(ray_to_x_y, self.level_map.map_coordinates['y1'], self.level_map.map_coordinates['y2'])
            #
            #     test_to_x_x, test_to_x_y = self._map_location(ray_to_x_x, ray_to_x_y)
            #     # print("angle: ", self.rotation, ray_angle)
            #     #
            #     # print(self.level_map.map_coordinates)
            #     # print(ray_to_x_x, ray_to_x_y)
            #     # print(self._map_location(ray_to_x_x, ray_to_x_y))
            #     # print(self.level_map.map[test_y][test_x])
            #     if self.level_map.map[test_to_x_y][test_to_x_x] == 0:
            #         x_step += 1
            #     else:
            #         break
            #
            # # Checking Horizontal tiles
            # y_step = 1
            # while True:
            #     if 0 < ray_angle < 180:  # looking up
            #         ray_to_y_y = self.rect.centery - self.level_map.tile_size * y_step
            #         ray_to_y_x = self.rect.centerx + 1 / ray_slope * ray_to_y_step * y_step
            #     elif 180 < ray_angle < 360:  # looking down
            #         ray_to_y_y = self.rect.centery + self.level_map.tile_size * y_step
            #         ray_to_y_x = self.rect.centerx - 1 / ray_slope * ray_to_y_step * y_step
            #     else:
            #         ray_to_y_y = self.rect.centery
            #         ray_to_y_x = self.rect.centerx
            #         break
            #
            #     test_to_y_x, test_to_y_y = self._map_location(ray_to_y_x, ray_to_y_y)
            #     if self.level_map.map[test_to_y_y][test_to_y_x] == 0:
            #         y_step += 1
            #     else:
            #         break
            #
            #     # ray_to_y_x = clamp_to_range(ray_to_y_x, self.level_map.map_coordinates['x1'], self.level_map.map_coordinates['x2'])
            #     # ray_to_y_y = clamp_to_range(ray_to_y_y, self.level_map.map_coordinates['y1'], self.level_map.map_coordinates['y2'])
            #     # print("rotation:", self.rotation,
            #     #       "r value:", r,
            #     #       "ray angle:", ray_angle,
            #     #       "ray slope:", ray_slope,
            #     #       "ray x, y:", ray_to_x_x, ray_to_x_y)
            #
            # # Check which ray is shorter
            ray_to_x_total_distance = math.sqrt((ray_to_x_x - self.rect.centerx) ** 2 + (ray_to_x_y - self.rect.centery) ** 2)
            ray_to_y_total_distance = math.sqrt((ray_to_y_x - self.rect.centerx) ** 2 + (ray_to_y_y - self.rect.centery) ** 2)
            #
            # # print(ray_to_x_total_distance, ray_to_y_total_distance)
            # print("To x:", test_to_x_x, test_to_x_y,"To y:", test_to_y_x, test_to_y_y)
            if ray_to_x_total_distance < ray_to_y_total_distance:
                ray_x, ray_y = ray_to_x_x, ray_to_x_y
                # pygame.draw.line(surface, 'green', self.rect.center, (ray_to_x_x, ray_to_x_y), 5)
            else:
                ray_x, ray_y = ray_to_y_x, ray_to_y_y
                # pygame.draw.line(surface, 'red', self.rect.center, (ray_to_y_x, ray_to_y_y), 2)
            pygame.draw.line(surface, 'green', self.rect.center, (ray_x, ray_y), 3)


class App:
    def __init__(self, width, height, caption):
        self._running = True
        self.screen = None
        self._caption = caption
        self.size = self.width, self.height = width, height
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.map = Map([
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ])
        self.player = Player(x=self.map.tile_size * 3 + self.map.tile_size // 3, y=self.map.tile_size * 5 + self.map.tile_size // 3, level_map=self.map)

    def on_init(self):
        pygame.init()
        pygame.display.set_caption(self._caption)
        self.screen = pygame.display.set_mode(self.size, HWSURFACE | DOUBLEBUF)

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            if keys[K_LALT]:
                self.player.strafe('left')
            else:
                self.player.rotate(+1)
        if keys[K_RIGHT]:
            if keys[K_LALT]:
                self.player.strafe('right')
            else:
                self.player.rotate(-1)
        if keys[K_UP]:
            self.player.move('forward')
        if keys[K_DOWN]:
            self.player.move('backward')

    def on_render(self):
        self.screen.fill("gray")
        self.map.draw(self.screen)
        self.player.draw_ray(self.screen)
        self.player.draw(self.screen)

        pygame.display.flip()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):
        self.on_init()
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(self.fps)
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App(width=1024, height=512, caption="RayCast")
    theApp.on_execute()
