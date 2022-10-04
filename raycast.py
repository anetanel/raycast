import pygame
from pygame.locals import *
import math


class Player:
    def __init__(self, x, y):
        self.color = "yellow"
        self.size = 10
        self.rect = Rect([x - self.size // 2, y - self.size // 2, self.size, self.size])
        self.rotation = 45
        self.dx = math.cos(math.radians(self.rotation))
        # dy is negative sin since screen y coordinates increase downward, unlike Cartesian
        self.dy = -math.sin(math.radians(self.rotation))
        self.view_line = self._calc_view_line()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.line(surface, self.color, self.rect.center, self.view_line, 5)

    def move(self, d):
        speed = 5
        if d > 0:
            x = self.dx
            y = self.dy
        else:
            x = -self.dx
            y = -self.dy
        self.rect = self.rect.move(x * speed, y * speed)
        self.view_line = self._calc_view_line()

    def rotate(self, n):
        speed = 2
        self.rotation = (self.rotation + n * speed) % 360
        # print(self.rotation)
        self.dx = math.cos(math.radians(self.rotation))
        self.dy = -math.sin(math.radians(self.rotation))
        self.view_line = self._calc_view_line()

    def _calc_view_line(self):
        line_length = 50
        dx = self.rect.centerx + self.dx * line_length
        dy = self.rect.centery + self.dy * line_length
        # print(dx, dy, self.rotation)

        return dx, dy

    def strafe(self, d):

        speed = 2
        if d == 'left':
            angle = 90
        else:
            angle = -90
        x = math.cos(math.radians(self.rotation + angle))
        y = -math.sin(math.radians(self.rotation + angle))
        # print("rotation ", self.rotation, self.rotation+angle)
        print("pos ", self.rect.center)
        print("move by ", x * speed, y * speed)

        self.rect = self.rect.move(round(x * speed), round(y * speed))
        print("new pos ", self.rect.center)
        self.view_line = self._calc_view_line()


class Map:
    def __init__(self, map_list: list[list]):
        self.map = map_list
        self.cube_size = 64
        self.rect_map = self._create_rects()
        self.colors = {0: 'black', 1: 'white'}

    def _create_rects(self):
        import copy
        rect_map = copy.deepcopy(self.map)
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                rect_map[row_idx][col_idx] = Rect(
                    [col_idx * self.cube_size, row_idx * self.cube_size, self.cube_size - 1, self.cube_size - 1])
        return rect_map

    def draw(self, surface):
        for row_idx, row in enumerate(self.map):
            for col_idx, cell_color in enumerate(row):
                pygame.draw.rect(surface, self.colors[cell_color], self.rect_map[row_idx][col_idx])


class App:
    def __init__(self, width, height, caption):
        self._running = True
        self.screen = None
        self._caption = caption
        self.size = self.width, self.height = width, height
        self.player = Player(width // 3, height // 2)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.map = Map([
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ])

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
            self.player.move(+1)
        if keys[K_DOWN]:
            self.player.move(-1)

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
