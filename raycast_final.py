import pygame
import math

# Initialize Pygame
pygame.init()
use_dda = False
show_blobs = False
casted_rays = 120
grayscale = True
font = pygame.Font(None, 55)

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
MAP_WIDTH = 8
MAP_HEIGHT = 8
TILE_SIZE = 64
START_3D_VIEW = MAP_WIDTH * TILE_SIZE
VIEWABLE_WIDTH = SCREEN_WIDTH - START_3D_VIEW
FOV = math.pi / 3
MAX_DEPTH = max(MAP_WIDTH, MAP_HEIGHT) * TILE_SIZE
TARGET_FPS = 60

# Player initial position and angle
player_x = 300
player_y = 300
player_angle = 0
PLAYER_SPEED = 5
PLAYER_ROTATION_SPEED = 0.03
PLAYER_SIZE = 16  # Size of the player's collision box

# STEP_ANGLE = FOV / casted_rays
# SCALE = (SCREEN_WIDTH - START_3D_VIEW) / casted_rays
# Map
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
map_colors = {0: "black", 1: "white", 2: "yellow"}

# Number of checks in each frame
number_of_checks = 0

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def draw_map():
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            pygame.draw.rect(
                screen,
                map_colors[map_grid[row][col]],
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
            )


def draw_player():
    # Draw player
    pygame.draw.circle(screen, "red", (int(player_x), int(player_y)), 8)
    # Draw player direction
    if use_dda:
        x = player_x + math.cos(player_angle) * 50
        y = player_y + math.sin(player_angle) * 50
    else:
        x = player_x - math.sin(player_angle) * 50
        y = player_y + math.cos(player_angle) * 50
    pygame.draw.line(screen, "red", (player_x, player_y), (x, y), 2)


def toggle_blobs(target_x, target_y):
    pygame.draw.circle(screen, "green", (target_x, target_y), 3)


def draw_ray(player_x, player_y, target_x, target_y):
    pygame.draw.line(screen, "yellow", (player_x, player_y), (target_x, target_y))


def cast_ray_naive(start_angle, step_angle, wall_width_scale):
    global number_of_checks
    for ray in range(casted_rays):
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

            # draw a circle in each place a wall hit is checked
            if show_blobs and ray % 20 == 0:
                toggle_blobs(target_x, target_y)

            # Check wall collision
            if map_grid[row][col] != 0:
                # Draw ray
                if ray % 20 == 0:
                    draw_ray(player_x, player_y, target_x, target_y)

                # 3D wall drawing

                # Color the wall based on depth
                if grayscale:
                    brightness_factor = int(255 / (1 + depth * depth * 0.0001))
                    wall_color = pygame.Color(brightness_factor, brightness_factor, brightness_factor)
                else:
                    # Check if the ray is hitting a grid intersection to color walls boundary
                    if math.isclose(target_x / TILE_SIZE, round(target_x / TILE_SIZE), abs_tol=0.03) and math.isclose(
                            target_y / TILE_SIZE, round(target_y / TILE_SIZE), abs_tol=0.03):
                        wall_color = "black"
                    else:
                        wall_color = map_colors[map_grid[row][col]]

                depth *= math.cos(player_angle - start_angle)
                wall_height = 30000 / (depth + 0.0001)

                if wall_height > SCREEN_HEIGHT:
                    wall_height = SCREEN_HEIGHT

                wall_width = wall_width_scale
                wall_x = START_3D_VIEW + ray * wall_width

                pygame.draw.rect(screen, wall_color,
                                 (wall_x, (SCREEN_HEIGHT - wall_height) / 2,
                                  wall_width + 1, wall_height))
                break
        start_angle += step_angle


def cast_rays():
    start_angle = player_angle - FOV / 2
    step_angle = FOV / casted_rays
    wall_width_scale = VIEWABLE_WIDTH / casted_rays
    global number_of_checks
    number_of_checks = 0
    if use_dda:
        cast_rays_dda(start_angle, step_angle, wall_width_scale)
    else:
        cast_ray_naive(start_angle, step_angle, wall_width_scale)


def cast_rays_dda(start_angle, step_angle, wall_width_scale):
    global number_of_checks
    number_of_checks = 0

    for ray in range(casted_rays):
        ray_angle = start_angle + ray * step_angle

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

        while not hit and math.sqrt((map_x - player_tile_x) ** 2 + (map_y - player_tile_y) ** 2) < MAX_DEPTH:
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
            if show_blobs and ray % 20 == 0:
                if side == 0:
                    wall_distance = (map_x - player_tile_x + (1 - step_x) / 2) / ray_dir_x
                else:
                    wall_distance = (map_y - player_tile_y + (1 - step_y) / 2) / ray_dir_y
                end_x = player_x + ray_dir_x * wall_distance * TILE_SIZE
                end_y = player_y + ray_dir_y * wall_distance * TILE_SIZE
                toggle_blobs(int(end_x), int(end_y))

            # Check if ray has hit a wall
            if map_x < MAP_WIDTH and map_y < MAP_HEIGHT and map_grid[map_y][map_x] == 1:
                hit = True

        if hit:
            # Calculate distance to the wall
            if side == 0:
                wall_distance = (map_x - player_tile_x + (1 - step_x) / 2) / ray_dir_x
            else:
                wall_distance = (map_y - player_tile_y + (1 - step_y) / 2) / ray_dir_y

            # Fisheye correction
            correct_dist = wall_distance * math.cos(ray_angle - player_angle)

            # Calculate wall height
            wall_height = int(SCREEN_HEIGHT / correct_dist)

            # Calculate wall color based on distance
            color = max(255 - int(correct_dist * TILE_SIZE), 0)

            # Draw 2D ray
            if ray % 20 == 0:
                end_x = player_x + ray_dir_x * wall_distance * TILE_SIZE
                end_y = player_y + ray_dir_y * wall_distance * TILE_SIZE
                pygame.draw.line(screen, "yellow", (player_x, player_y), (end_x, end_y))

            # Draw 3D projection
            pygame.draw.rect(screen, (color, color, color),
                             (START_3D_VIEW + ray * wall_width_scale, (SCREEN_HEIGHT - wall_height) // 2,
                              wall_width_scale + 1, wall_height))

    # start_angle += STEP_ANGLE


# Game loop
running = True
clock = pygame.time.Clock()
frame_times = []


def draw_bg():
    # Clear the screen
    screen.fill("black")  # Background color
    # Draw ceiling and floor
    pygame.draw.rect(screen, "gray30", (START_3D_VIEW, 0, VIEWABLE_WIDTH, SCREEN_HEIGHT // 2))  # Ceiling
    pygame.draw.rect(screen, "gray50", (START_3D_VIEW, SCREEN_HEIGHT // 2, VIEWABLE_WIDTH, SCREEN_HEIGHT // 2))  # Floor


def is_collision(x, y):
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
        player_angle -= PLAYER_ROTATION_SPEED
    elif keys[pygame.K_RIGHT]:
        player_angle += PLAYER_ROTATION_SPEED
    # Keep angle between 0 and 2*pi
    player_angle %= 2 * math.pi

    if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        # Calculate movement vector
        if use_dda:
            dx = math.cos(player_angle) * PLAYER_SPEED
            dy = math.sin(player_angle) * PLAYER_SPEED
        else:
            dx = -math.sin(player_angle) * PLAYER_SPEED
            dy = math.cos(player_angle) * PLAYER_SPEED

    if keys[pygame.K_UP]:
        new_x = player_x + dx
        new_y = player_y + dy
        if not is_collision(new_x, player_y):
            player_x = new_x
        if not is_collision(player_x, new_y):
            player_y = new_y
    elif keys[pygame.K_DOWN]:
        new_x = player_x - dx
        new_y = player_y - dy
        if not is_collision(new_x, player_y):
            player_x = new_x
        if not is_collision(player_x, new_y):
            player_y = new_y


def calc_fps():
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
    return locked_fps, theoretical_fps


def handle_events():
    global use_dda, show_blobs, running, casted_rays, grayscale
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                use_dda = not use_dda

            if event.key == pygame.K_b:
                show_blobs = not show_blobs

            if event.key == pygame.K_r:
                if casted_rays == VIEWABLE_WIDTH:
                    casted_rays = 120
                else:
                    casted_rays *= 2
                    if casted_rays > VIEWABLE_WIDTH:
                        casted_rays = VIEWABLE_WIDTH

            if event.key == pygame.K_g:
                grayscale = not grayscale

            if event.key == pygame.K_ESCAPE:
                running = False


def update_text():
    text = f"""
FPS: {locked_fps}
Theoretical FPS: {theoretical_fps}
Checks per Frame: {number_of_checks}
Rays: {casted_rays}

DDA: {use_dda}
"""
    text_surface = font.render(text, True, "yellow2")
    screen.blit(text_surface, dest=(0, SCREEN_HEIGHT // 2))
    pygame.display.set_caption(
        f"FPS: {locked_fps}, Theoretical FPS: {theoretical_fps}, Checks per Frame: {number_of_checks}, DDA: {use_dda}, Rays: {casted_rays}")




while running:
    handle_events()
    draw_bg()
    move_player()
    draw_map()
    cast_rays()
    draw_player()
    locked_fps, theoretical_fps = calc_fps()
    update_text()

    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()