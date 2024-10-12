import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MAP_SIZE = 8
TILE_SIZE = 64
FOV = math.pi / 3
CASTED_RAYS = 300
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = 20
SCALE = (SCREEN_WIDTH - (MAP_SIZE * TILE_SIZE)) // CASTED_RAYS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
player_x = 300
player_y = 300
player_angle = 0

# Map
world_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wolfenstein 3D-style Raycaster")

number_of_checks = 0

def draw_map():
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            pygame.draw.rect(
                screen,
                WHITE if world_map[row][col] else BLACK,
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
            )

    # Draw player on 2D map
    pygame.draw.circle(screen, RED, (int(player_x), int(player_y)), 8)
    pygame.draw.line(screen, RED, (player_x, player_y),
                     (player_x + math.cos(player_angle) * 50,
                      player_y + math.sin(player_angle) * 50), 3)

def cast_rays():
    start_angle = player_angle - FOV / 2
    global number_of_checks
    number_of_checks = 0

    for ray in range(CASTED_RAYS):
        ray_angle = start_angle + ray * STEP_ANGLE

        # Player's position in tile coordinates
        player_tile_x, player_tile_y = player_x / TILE_SIZE, player_y / TILE_SIZE

        # Calculate ray direction vector
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        # Calculate step size and initial step
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1

        # Calculate distance to next x or y intersection
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        # Calculate initial side_dist
        if ray_dir_x < 0:
            side_dist_x = (player_tile_x - int(player_tile_x)) * delta_dist_x
        else:
            side_dist_x = (int(player_tile_x) + 1 - player_tile_x) * delta_dist_x

        if ray_dir_y < 0:
            side_dist_y = (player_tile_y - int(player_tile_y)) * delta_dist_y
        else:
            side_dist_y = (int(player_tile_y) + 1 - player_tile_y) * delta_dist_y

        # Perform DDA
        hit = False
        side = 0  # 0 for x-side, 1 for y-side
        map_x, map_y = int(player_tile_x), int(player_tile_y)

        while not hit and math.sqrt((map_x - player_tile_x)**2 + (map_y - player_tile_y)**2) < MAX_DEPTH:
            # Increase checks per frame counter
            number_of_checks += 1

            # Jump to next square
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            # Draw balls on the map
            if ray %10 == 0:
                if side == 0:
                    perp_wall_dist = (map_x - player_tile_x + (1 - step_x) / 2) / ray_dir_x
                else:
                    perp_wall_dist = (map_y - player_tile_y + (1 - step_y) / 2) / ray_dir_y
                end_x = player_x + ray_dir_x * perp_wall_dist * TILE_SIZE
                end_y = player_y + ray_dir_y * perp_wall_dist * TILE_SIZE
                pygame.draw.circle(screen, "green", (int(end_x), int(end_y)), 3)

            # Check if ray has hit a wall
            if map_x < MAP_SIZE and map_y < MAP_SIZE and world_map[map_y][map_x] == 1:
                hit = True

        if hit:
            # Calculate distance to the wall
            if side == 0:
                perp_wall_dist = (map_x - player_tile_x + (1 - step_x) / 2) / ray_dir_x
            else:
                perp_wall_dist = (map_y - player_tile_y + (1 - step_y) / 2) / ray_dir_y

            # Fisheye correction
            correct_dist = perp_wall_dist * math.cos(ray_angle - player_angle)

            # Calculate wall height
            wall_height = int(SCREEN_HEIGHT / correct_dist)

            # Calculate wall color based on distance
            color = max(255 - int(correct_dist * TILE_SIZE), 0)

            # Draw 2D ray
            if ray % 10 == 0:
                end_x = player_x + ray_dir_x * perp_wall_dist * TILE_SIZE
                end_y = player_y + ray_dir_y * perp_wall_dist * TILE_SIZE
                pygame.draw.line(screen, YELLOW, (player_x, player_y), (end_x, end_y))

            # Draw 3D projection
            pygame.draw.rect(screen, (color, color, color),
                             (MAP_SIZE * TILE_SIZE + ray * SCALE, (SCREEN_HEIGHT - wall_height) // 2,
                              SCALE + 1, wall_height))

    start_angle += STEP_ANGLE

# Game loop
clock = pygame.time.Clock()
running = True
TARGET_FPS = 60
frame_times = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill("black")  # Floor color
    pygame.draw.rect(screen, "gray30", (MAP_SIZE * TILE_SIZE, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))  # Ceiling color
    pygame.draw.rect(screen, "gray50", (MAP_SIZE* TILE_SIZE, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT))  # Floor color

    # Draw the 2D map
    draw_map()

    # Cast rays and draw 3D view
    cast_rays()

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_angle -= 0.1
    if keys[pygame.K_RIGHT]:
        player_angle += 0.1
    if keys[pygame.K_UP]:
        player_x += math.cos(player_angle) * 5
        player_y += math.sin(player_angle) * 5
    if keys[pygame.K_DOWN]:
        player_x -= math.cos(player_angle) * 5
        player_y -= math.sin(player_angle) * 5

    # Get the time this frame took (in milliseconds)
    frame_time = clock.get_rawtime() / 1000.0  # Convert to seconds
    frame_times.append(frame_time)

    # Keep only the last 60 frame times
    if len(frame_times) > 60:
        frame_times.pop(0)

    # Calculate average frame time and theoretical FPS
    avg_frame_time = sum(frame_times) / len(frame_times)
    theoretical_fps = int(1 / avg_frame_time) if avg_frame_time > 0 else 0

    # Update FPS counter
    locked_fps = int(clock.get_fps())
    pygame.display.set_caption(f"Raycasting POC - Locked FPS: {locked_fps}, Theoretical FPS: {theoretical_fps}, Number of checks: {number_of_checks}")

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()