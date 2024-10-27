import math

import pygame
import sys
from typing import List, Tuple

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
MAP_SIZE = 16
TILE_SIZE = 32
FOV = 900  # 90 degrees in tenths of a degree
HALF_FOV = FOV // 2
NUM_RAYS = SCREEN_WIDTH // 2
SCALE = SCREEN_WIDTH // NUM_RAYS
MAX_DEPTH = 16
MOVE_SPEED = 5
ROTATE_SPEED = 50  # 5 degrees in tenths of a degree

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game map
game_map: List[List[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class Player:
    def __init__(self, x: int, y: int, angle: int):
        self.x = x
        self.y = y
        self.angle = angle

    def move(self, dx: int, dy: int):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < MAP_SIZE * TILE_SIZE and 0 <= new_y < MAP_SIZE * TILE_SIZE:
            if game_map[new_y // TILE_SIZE][new_x // TILE_SIZE] == 0:
                self.x = new_x
                self.y = new_y

    def rotate(self, da: int):
        self.angle = (self.angle + da) % 3600

def deg_to_rad(deg: int) -> int:
    return (deg * 31416) // 1800

def cast_ray(player: Player, angle: int) -> Tuple[int, int, int]:
    sin_a = sin_table[angle]
    cos_a = cos_table[angle]

    x, y = player.x, player.y
    x_map, y_map = x // TILE_SIZE, y // TILE_SIZE

    ray_cos = cos_a if cos_a else 1
    ray_sin = sin_a if sin_a else 1

    y_step = TILE_SIZE if sin_a > 0 else -TILE_SIZE
    x_step = TILE_SIZE if cos_a > 0 else -TILE_SIZE

    y_tilt = y % TILE_SIZE
    if sin_a < 0:
        y_tilt = TILE_SIZE - y_tilt

    x_tilt = x % TILE_SIZE
    if cos_a < 0:
        x_tilt = TILE_SIZE - x_tilt

    y_dist = (y_tilt * ray_cos) // ray_sin if ray_sin else 1000000
    x_dist = (x_tilt * ray_sin) // ray_cos if ray_cos else 1000000

    for _ in range(MAX_DEPTH):
        if x_dist < y_dist:
            x_map += 1 if cos_a > 0 else -1
            dist = x_dist
            x_dist += TILE_SIZE * ray_sin // ray_cos
        else:
            y_map += 1 if sin_a > 0 else -1
            dist = y_dist
            y_dist += TILE_SIZE * ray_cos // ray_sin

        if 0 <= x_map < MAP_SIZE and 0 <= y_map < MAP_SIZE and game_map[y_map][x_map]:
            return max(dist, 1), x_map, y_map

        if game_map[y_map][x_map]:
            return dist, x_map, y_map

    return MAX_DEPTH * TILE_SIZE, x_map, y_map

def draw_minimap(screen: pygame.Surface, player: Player):
    mini_map_surface = pygame.Surface((MAP_SIZE * TILE_SIZE, MAP_SIZE * TILE_SIZE))
    mini_map_surface.fill(BLACK)

    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x]:
                pygame.draw.rect(mini_map_surface, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1))

    pygame.draw.circle(mini_map_surface, RED, (player.x, player.y), 5)

    for ray in range(-HALF_FOV, HALF_FOV, FOV // NUM_RAYS):
        angle = (player.angle + ray) % 3600
        dist, _, _ = cast_ray(player, angle)
        ex = player.x + (dist * cos_table[angle]) // 1000
        ey = player.y + (dist * sin_table[angle]) // 1000
        pygame.draw.line(mini_map_surface, GREEN, (player.x, player.y), (ex, ey))

    screen.blit(mini_map_surface, (SCREEN_WIDTH // 2, 0))

def draw_3d_view(screen: pygame.Surface, player: Player):
    half_height = SCREEN_HEIGHT // 2
    for ray in range(NUM_RAYS):
        angle = (player.angle - HALF_FOV + ray * (FOV // NUM_RAYS)) % 3600
        dist, _, _ = cast_ray(player, angle)
        dist = max(dist * cos_table[(player.angle - angle) % 3600] // 1000, 1)
        wall_height = (TILE_SIZE * SCREEN_HEIGHT) // (dist + 1)
        color_intensity = min(255, max(0, 255 - (dist * 255) // (MAP_SIZE * TILE_SIZE)))
        color = (color_intensity, color_intensity, color_intensity)
        pygame.draw.rect(screen, color, (ray * SCALE, half_height - wall_height // 2, SCALE, wall_height))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rotate(-ROTATE_SPEED)
        if keys[pygame.K_RIGHT]:
            player.rotate(ROTATE_SPEED)
        if keys[pygame.K_UP]:
            dx = (MOVE_SPEED * cos_table[player.angle]) // 1000
            dy = (MOVE_SPEED * sin_table[player.angle]) // 1000
            player.move(dx, dy)
        if keys[pygame.K_DOWN]:
            dx = (-MOVE_SPEED * cos_table[player.angle]) // 1000
            dy = (-MOVE_SPEED * sin_table[player.angle]) // 1000
            player.move(dx, dy)

        screen.fill((50, 50, 50))
        draw_3d_view(screen, player)
        draw_minimap(screen, player)

        pygame.display.flip()
        clock.tick(60)

# Pre-compute sine and cosine tables
sin_table = [int(1000 * math.sin(deg_to_rad(i))) for i in range(3600)]
cos_table = [int(1000 * math.cos(deg_to_rad(i))) for i in range(3600)]

if __name__ == "__main__":
    main()