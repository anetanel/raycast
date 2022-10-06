import pygame
from pygame.locals import *
import math


class Map:
    def __init__(self, map_list: list[list]):
        self.map = map_list
        self.tile_size = 64
        self.rect_map = self._create_rects()
        self.colors = {0: 'black', 1: 'white', 2: 'magenta'}

    def _create_rects(self):
        import copy
        rect_map = copy.deepcopy(self.map)
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                rect_map[row_idx][col_idx] = Rect(
                    [col_idx * self.tile_size, row_idx * self.tile_size, self.tile_size - 1, self.tile_size - 1])
        return rect_map

    def draw(self, surface):
        for row_idx, row in enumerate(self.map):
            for col_idx, cell_color in enumerate(row):
                pygame.draw.rect(surface, self.colors[cell_color], self.rect_map[row_idx][col_idx])


class Player:
    def __init__(self, x, y, level_map: Map):
        self.x = x
        self.y = y
        self.color = "yellow"
        self.size = 5
        self.rect = Rect([self.x, self.y, self.size, self.size])
        self.rotation = 0
        self.dx = math.cos(math.radians(self.rotation))
        # dy is negative sin since screen y coordinates increase downward, unlike Cartesian
        self.dy = -math.sin(math.radians(self.rotation))
        self.view_line = self._calc_view_line()
        self.level_map = level_map

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.line(surface, self.color, self.rect.center, self.view_line, 2)

    def move(self, direction):
        speed = 5
        org_x = self.x
        org_y = self.y
        org_map_x, org_map_y = self._map_location(org_x, org_y)
        if direction == 'forward':
            self.x += self.dx * speed
            self.y += self.dy * speed
        else:
            self.x -= self.dx * speed
            self.y -= self.dy * speed

        new_map_x, new_map_y = self._map_location(self.x, self.y)

        # Collision detection
        if self.level_map.map[new_map_y][new_map_x] != 0:   # is new position colliding with a wall?
            # Enable wall gliding
            if org_map_x != new_map_x and org_map_y != new_map_y:   # Trying to move between tiles on both x and y
                test_x, test_y = self._map_location(org_x, self.y)  # Can we move on the y-axis?
                if self.level_map.map[test_y][test_x] != 0:
                    self.y = org_y                                  # If not, keep y position
                test_x, test_y = self._map_location(self.x, org_y)  # Can we move on the x-axis?
                if self.level_map.map[test_y][test_x] != 0:
                    self.x = org_x                                  # If not, keep x position
            elif org_map_x != new_map_x:                            # Colliding move between tiles on x-axis
                self.x = org_x                                      # so hold x position
            elif org_map_y != new_map_y:                            # Colliding move between tiles on y-axis
                self.y = org_y                                      # so hold y position

        self.rect.update(self.x, self.y, self.size, self.size)
        self.view_line = self._calc_view_line()

    def rotate(self, n):
        speed = 4
        self.rotation = (self.rotation + n * speed) % 360
        self.dx = math.cos(math.radians(self.rotation))
        self.dy = -math.sin(math.radians(self.rotation))
        self.view_line = self._calc_view_line()

    def _calc_view_line(self):
        line_length = 20
        dx = self.rect.centerx + self.dx * line_length
        dy = self.rect.centery + self.dy * line_length

        return dx, dy

    def _map_location(self, x, y):
        map_x = int(x // self.level_map.tile_size)
        map_y = int(y // self.level_map.tile_size)
        return map_x, map_y

    def strafe(self, direction):
        speed = 2
        if direction == 'left':
            angle = 90
        else:
            angle = -90
        self.x += math.cos(math.radians(self.rotation + angle)) * speed
        self.y += -math.sin(math.radians(self.rotation + angle)) * speed

        self.rect.update(self.x, self.y, self.size, self.size)
        self.view_line = self._calc_view_line()


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
        self.player = Player(x=64, y=128, level_map=self.map)

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
