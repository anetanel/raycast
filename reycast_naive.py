import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1024
HEIGHT = 512
HALF_WIDTH = WIDTH // 2
TILE_SIZE = 64
MAP_WIDTH = 8
MAP_HEIGHT = 8
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = int(MAP_WIDTH * TILE_SIZE)

# Colors
colors = {0: "black", 1: "white", 2: "yellow"}

# Player settings
player_x = 300
player_y = 300
player_angle = math.pi
PLAYER_SPEED = 5
PLAYER_SIZE = 16  # Size of the player's collision box

# Simple map (1 represents a wall, 0 represents empty space)
map_grid = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 2, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]



# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycasting POC")

number_of_checks = 0

def draw_map():
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            square = row * MAP_WIDTH + col
            pygame.draw.rect(
                screen,
                colors[map_grid[row][col]],
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
            )


def draw_player():
    # Draw player
    pygame.draw.circle(screen, "red", (int(player_x), int(player_y)), 8)
    # Draw player direction
    pygame.draw.line(screen, "red", (player_x, player_y),
                     (player_x - math.sin(player_angle) * 50,
                      player_y + math.cos(player_angle) * 50), 3)


def cast_rays():
    start_angle = player_angle - HALF_FOV
    global number_of_checks
    number_of_checks = 0

    for ray in range(CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)

            # Increase checks per frame counter
            number_of_checks += 1

            # Check if ray is out of bounds
            if col < 0 or col >= MAP_WIDTH or row < 0 or row >= MAP_HEIGHT:
                break

            # draw a circle in each grid intersection check
            # pygame.draw.circle(screen, "blue", (target_x, target_y), 1)

            # Check wall collision
            if map_grid[row][col] != 0:
                # Draw ray
                pygame.draw.line(screen, "green", (player_x, player_y), (target_x, target_y))

                # 3D wall drawing
                # brightness_factor = int(255 / (1 + depth * depth * 0.0001))
                # brightness = pygame.Color(brightness_factor, brightness_factor, brightness_factor)

                if map_grid[row][col] == 1:
                    wall_color = "red"
                elif map_grid[row][col] == 2:
                    wall_color = "yellow"
                else:
                    wall_color = "black"

                # Check if the ray is hitting a grid intersection
                if math.isclose(target_x / TILE_SIZE, round(target_x / TILE_SIZE), abs_tol=0.03) and math.isclose(target_y / TILE_SIZE,round(target_y / TILE_SIZE), abs_tol=0.03):
                    wall_color = "blue"

                depth *= math.cos(player_angle - start_angle)
                wall_height = 21000 / (depth + 0.0001)

                if wall_height > HEIGHT:
                    wall_height = HEIGHT

                wall_width = HALF_WIDTH / CASTED_RAYS
                wall_x = HALF_WIDTH + ray * wall_width

                pygame.draw.rect(screen, wall_color,
                                 (wall_x, (HEIGHT - wall_height) / 2,
                                  wall_width + 1, wall_height))
                break

        start_angle += STEP_ANGLE

def is_collision(x, y):
    # Check if the given coordinates collide with a wall
    grid_x = int(x / TILE_SIZE)
    grid_y = int(y / TILE_SIZE)

    # Check the four corners of the player's collision box
    for offset_x, offset_y in [(0, 0), (PLAYER_SIZE, 0), (0, PLAYER_SIZE), (PLAYER_SIZE, PLAYER_SIZE)]:
        check_x = int((x + offset_x) / TILE_SIZE)
        check_y = int((y + offset_y) / TILE_SIZE)
        if map_grid[check_y][check_x] == 1:
            return True
    return False

def move_player():
    global player_x, player_y, player_angle

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_angle -= 0.03
    if keys[pygame.K_RIGHT]:
        player_angle += 0.03

    # Calculate movement vector
    dx = -math.sin(player_angle) * PLAYER_SPEED
    dy = math.cos(player_angle) * PLAYER_SPEED

    if keys[pygame.K_UP]:
        new_x = player_x + dx
        new_y = player_y + dy
        if not is_collision(new_x, player_y):
            player_x = new_x
        if not is_collision(player_x, new_y):
            player_y = new_y
    if keys[pygame.K_DOWN]:
        new_x = player_x - dx
        new_y = player_y - dy
        if not is_collision(new_x, player_y):
            player_x = new_x
        if not is_collision(player_x, new_y):
            player_y = new_y

    # Keep angle between 0 and 2*pi
    player_angle %= 2 * math.pi

# Game loop
running = True
clock = pygame.time.Clock()
TARGET_FPS = 60
frame_times = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    screen.fill("gray50", (HALF_WIDTH, HEIGHT//2, WIDTH, HEIGHT)) # floor
    screen.fill("gray20", (HALF_WIDTH, 0, WIDTH, HEIGHT//2)) # ceiling

    move_player()
    draw_map()
    cast_rays()
    draw_player()

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

    pygame.display.flip()

    # Limit the frame rate to TARGET_FPS
    clock.tick(TARGET_FPS)

pygame.quit()