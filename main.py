"""
Wild West Runner
================

A pixel-art endless runner set in a Wild West desert, built with Pygame.

Roll the terracotta ball across the sand and jump over cacti and
tumbleweeds. The longer you survive, the faster the desert scrolls by.

Controls
--------
SPACE / UP     Jump
DOWN           Drop faster while in the air
R / SPACE      Restart after Game Over
ESC            Quit

Every graphic (scenery, sprites, even the font) is drawn in code,
so the game runs without any external asset files.
"""

import math
import random
import sys

import pygame


# ===========================================================================
# Configuration
# ===========================================================================

# --- Display ---------------------------------------------------------------
# The scene is drawn on a small virtual canvas and scaled up with
# nearest-neighbour filtering. That is what gives it the crisp pixel look.
CANVAS_WIDTH = 320
CANVAS_HEIGHT = 180
PIXEL_SCALE = 3
SCREEN_WIDTH = CANVAS_WIDTH * PIXEL_SCALE    # 960
SCREEN_HEIGHT = CANVAS_HEIGHT * PIXEL_SCALE  # 540
FPS = 60
TITLE = "Wild West Runner"

# Top edge of the desert floor, in canvas pixels.
GROUND_Y = 150

# --- Player & physics (canvas pixels, per frame) ----------------------------
PLAYER_X = 48               # Horizontal centre of the ball
PLAYER_RADIUS = 7
HITBOX_RADIUS = 6           # Slightly forgiving collision circle
GRAVITY = 0.32
JUMP_VELOCITY = -5.4        # Peak jump height is roughly 45 px
FAST_FALL_BOOST = 0.45      # Extra gravity while holding DOWN in the air
ROLL_SPEED = 0.35           # Radians of ball spin per frame

# --- Difficulty & scoring ----------------------------------------------------
BASE_SPEED = 2.6            # Starting scroll speed
MAX_SPEED = 7.0             # Speed cap
SPEED_GAIN_PER_FRAME = 0.0008
SCORE_PER_PIXEL = 0.06      # Score earned per pixel travelled
RESTART_DELAY_FRAMES = 20   # Stops an accidental instant restart
FIRST_OBSTACLE_OFFSET = 160 # Extra breathing room before the first obstacle

# --- Obstacles ---------------------------------------------------------------
# kind: (width, height, spawn weight)
OBSTACLE_TYPES = {
    "small_cactus": (10, 18, 35),
    "tall_cactus": (12, 26, 25),
    "double_cactus": (22, 20, 20),
    "tumbleweed": (14, 14, 20),
}
TUMBLEWEED_HOP = 6          # Max bounce height of a tumbleweed
GAP_RANDOM_EXTRA = 160      # Random spacing added on top of the minimum gap


def rgb(hex_code):
    """Convert '#RRGGBB' into an (r, g, b) tuple."""
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


# --- Palette -----------------------------------------------------------------
COLOR_SAND = rgb("#E6C280")          # Main background
COLOR_SKY_TOP = rgb("#F2DCA6")
COLOR_SKY_MID = rgb("#ECCF92")
COLOR_SUN_GLOW = rgb("#EFD69B")
COLOR_SUN = rgb("#F8E2A4")
COLOR_SUN_CORE = rgb("#FFF2CC")
COLOR_CLOUD = rgb("#F5E4BC")
COLOR_CLOUD_SHADE = rgb("#EBD3A0")

COLOR_MESA = rgb("#CF9764")
COLOR_MESA_LIGHT = rgb("#DDAA78")
COLOR_MESA_SHADOW = rgb("#BC8455")
COLOR_DUNE = rgb("#D8A865")
COLOR_DUNE_SHADE = rgb("#C99657")
COLOR_DUNE_CACTUS = rgb("#B4885A")

COLOR_GROUND = rgb("#8A5A36")        # Desert floor
COLOR_GROUND_LIGHT = rgb("#A8754A")
COLOR_GROUND_DARK = rgb("#6E4529")
COLOR_PEBBLE = rgb("#B3845A")
COLOR_BONE = rgb("#EFE3C8")

COLOR_CACTUS = rgb("#2A6F40")        # Cacti
COLOR_CACTUS_LIGHT = rgb("#3F8C57")
COLOR_CACTUS_DARK = rgb("#1C4F2D")
COLOR_CACTUS_SPINE = rgb("#CFE0A0")

COLOR_TUMBLE = rgb("#A27848")
COLOR_TUMBLE_LIGHT = rgb("#C29A62")
COLOR_TUMBLE_DARK = rgb("#7A5532")

COLOR_PLAYER = rgb("#C05A3E")        # Terracotta ball
COLOR_PLAYER_DARK = rgb("#8E3F2B")
COLOR_PLAYER_LIGHT = rgb("#E28A6B")
COLOR_PLAYER_OUTLINE = rgb("#5E2A1D")
COLOR_SHADOW = rgb("#6E4529")
COLOR_DUST = rgb("#C9A36C")

COLOR_TEXT_DARK = rgb("#4A2E1A")
COLOR_TEXT_MID = rgb("#8A5A36")
COLOR_TEXT_LIGHT = rgb("#FBEFC8")
COLOR_TEXT_GOLD = rgb("#F6C453")
COLOR_WOOD = rgb("#9A6A40")
COLOR_WOOD_DARK = rgb("#6B4426")
COLOR_WOOD_LIGHT = rgb("#B5814F")
COLOR_NAIL = rgb("#3A2416")


# ===========================================================================
# Pixel font (5x7 glyphs, so no font files are needed)
# ===========================================================================

PIXEL_FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
}
GLYPH_WIDTH = 5
GLYPH_HEIGHT = 7

_text_cache = {}


def render_pixel_text(text, color, scale=1):
    """Render text with the built-in 5x7 pixel font onto a new surface."""
    key = (text, color, scale)
    if key in _text_cache:
        return _text_cache[key]

    advance = (GLYPH_WIDTH + 1) * scale
    width = max(1, len(text) * advance - scale)
    surface = pygame.Surface((width, GLYPH_HEIGHT * scale), pygame.SRCALPHA)

    for index, char in enumerate(text.upper()):
        glyph = PIXEL_FONT.get(char, PIXEL_FONT["?"])
        origin_x = index * advance
        for row, line in enumerate(glyph):
            for col, cell in enumerate(line):
                if cell == "#":
                    surface.fill(color, (origin_x + col * scale, row * scale, scale, scale))

    _text_cache[key] = surface
    return surface


def draw_text(screen, text, x, y, color, scale=1, align="left", shadow=None):
    """Draw pixel text aligned 'left', 'center' or 'right' at x, with optional drop shadow."""
    surface = render_pixel_text(text, color, scale)
    if align == "center":
        x -= surface.get_width() // 2
    elif align == "right":
        x -= surface.get_width()

    if shadow is not None:
        screen.blit(render_pixel_text(text, shadow, scale), (x + scale, y + scale))
    screen.blit(surface, (x, y))


# ===========================================================================
# Setup
# ===========================================================================

def init_game():
    """Initialise Pygame, the window, the clock and the starting game variables.

    Returns:
        (screen, canvas, clock, state, high_score)
    """
    pygame.init()
    pygame.display.set_caption(TITLE)
    pygame.display.set_icon(_make_window_icon())

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
    clock = pygame.time.Clock()

    state = reset_game()
    high_score = 0
    return screen, canvas, clock, state, high_score


def reset_game():
    """Return a fresh game state: score, player position, speed and obstacles."""
    player_rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    player_rect.midbottom = (PLAYER_X, GROUND_Y)

    # The first obstacle starts off-screen to give the player a moment to settle.
    first_obstacle = _create_obstacle(BASE_SPEED, CANVAS_WIDTH + FIRST_OBSTACLE_OFFSET)

    return {
        "player_rect": player_rect,
        "velocity_y": 0.0,
        "is_jumping": False,
        "scroll_speed": BASE_SPEED,
        "distance": 0.0,
        "score": 0.0,
        "frame": 0,
        "obstacles": [first_obstacle],
        "game_over": False,
        "game_over_timer": 0,
        "new_high_score": False,
    }


def _make_window_icon():
    """Build a small ball icon for the window title bar."""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, COLOR_PLAYER_OUTLINE, (16, 16), 15)
    pygame.draw.circle(icon, COLOR_PLAYER, (15, 15), 13)
    pygame.draw.line(icon, COLOR_PLAYER_DARK, (6, 22), (24, 8), 3)
    icon.fill(COLOR_PLAYER_LIGHT, (9, 8, 4, 4))
    return icon


# ===========================================================================
# Input & physics
# ===========================================================================

def handle_input(player_rect, is_jumping, velocity_y):
    """Read the keyboard and start a jump (or speed up a fall).

    Returns:
        (is_jumping, velocity_y)
    """
    keys = pygame.key.get_pressed()
    jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP]
    on_ground = player_rect.bottom >= GROUND_Y

    if jump_pressed and on_ground and not is_jumping:
        velocity_y = JUMP_VELOCITY
        is_jumping = True
    elif is_jumping and keys[pygame.K_DOWN]:
        velocity_y += FAST_FALL_BOOST

    return is_jumping, velocity_y


def update_physics(player_rect, velocity_y):
    """Apply gravity, move the ball and land it on the ground.

    Moves player_rect in place.

    Returns:
        (velocity_y, is_jumping)
    """
    velocity_y += GRAVITY
    player_rect.y += round(velocity_y)

    if player_rect.bottom >= GROUND_Y:
        player_rect.bottom = GROUND_Y
        return 0.0, False

    return velocity_y, True


# ===========================================================================
# Obstacles
# ===========================================================================

def _create_obstacle(scroll_speed, x=None):
    """Create a random obstacle just past the right edge of the canvas.

    Each obstacle stores the gap to leave before the next one spawns. The
    minimum gap grows with speed so there is always room to land and jump again.
    """
    kinds = list(OBSTACLE_TYPES)
    weights = [OBSTACLE_TYPES[kind][2] for kind in kinds]
    kind = random.choices(kinds, weights=weights)[0]
    width, height, _ = OBSTACLE_TYPES[kind]

    if x is None:
        x = CANVAS_WIDTH + 8

    airtime_frames = 2 * abs(JUMP_VELOCITY) / GRAVITY
    min_gap = scroll_speed * airtime_frames * 1.1 + 24

    return {
        "kind": kind,
        "x": float(x),
        "rect": pygame.Rect(int(x), GROUND_Y - height, width, height),
        "gap": min_gap + random.uniform(0, GAP_RANDOM_EXTRA),
        "angle": 0.0,                           # Tumbleweed spin
        "phase": random.uniform(0, math.pi),    # Tumbleweed bounce timing
    }


def spawn_and_update_obstacles(obstacles, scroll_speed):
    """Move obstacles left, remove those off-screen, and spawn new ones.

    Returns:
        The updated list of obstacles.
    """
    for obstacle in obstacles:
        obstacle["x"] -= scroll_speed
        obstacle["rect"].x = round(obstacle["x"])

        if obstacle["kind"] == "tumbleweed":
            radius = obstacle["rect"].width / 2
            obstacle["angle"] -= scroll_speed / radius   # Rolls toward the player
            obstacle["phase"] += 0.10 + scroll_speed * 0.012
            hop = abs(math.sin(obstacle["phase"])) * TUMBLEWEED_HOP
            obstacle["rect"].bottom = GROUND_Y - round(hop)

    obstacles = [ob for ob in obstacles if ob["rect"].right > -4]

    if not obstacles:
        obstacles.append(_create_obstacle(scroll_speed))
    else:
        last = obstacles[-1]
        if CANVAS_WIDTH - last["rect"].right >= last["gap"]:
            obstacles.append(_create_obstacle(scroll_speed))

    return obstacles


def _cactus_parts(obstacle):
    """Break a cactus obstacle into rectangles (trunks and arms).

    Used for both drawing and collision, so the hitbox always matches the art.
    """
    rect = obstacle["rect"]
    if obstacle["kind"] == "double_cactus":
        return (_saguaro_parts(rect.x, rect.bottom, 10, 20)
                + _saguaro_parts(rect.x + 12, rect.bottom, 10, 14))
    return _saguaro_parts(rect.x, rect.bottom, rect.width, rect.height)


def _saguaro_parts(x, bottom, width, height):
    """Return [trunk, left_elbow, left_arm, right_elbow, right_arm] rects of one saguaro."""
    top = bottom - height
    trunk_width = 4
    trunk_x = x + (width - trunk_width) // 2
    trunk = pygame.Rect(trunk_x, top, trunk_width, height)

    left_y = bottom - int(height * 0.45)
    left_len = max(4, height // 4)
    left_elbow = pygame.Rect(x, left_y, trunk_x - x, 2)
    left_arm = pygame.Rect(x, left_y - left_len, 2, left_len + 2)

    right_y = bottom - int(height * 0.6)
    right_len = max(3, height // 5)
    right_start = trunk_x + trunk_width
    right_elbow = pygame.Rect(right_start, right_y, x + width - right_start, 2)
    right_arm = pygame.Rect(x + width - 2, right_y - right_len, 2, right_len + 2)

    return [trunk, left_elbow, left_arm, right_elbow, right_arm]


def _circle_hits_rect(cx, cy, radius, rect):
    """True if a circle overlaps an axis-aligned rectangle."""
    nearest_x = max(rect.left, min(cx, rect.right - 1))
    nearest_y = max(rect.top, min(cy, rect.bottom - 1))
    return (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2 < radius ** 2


def check_collision(player_rect, obstacles):
    """Check the ball (as a circle) against every obstacle.

    Cacti are tested part by part; tumbleweeds are treated as circles.
    """
    cx, cy = player_rect.center

    for obstacle in obstacles:
        if obstacle["kind"] == "tumbleweed":
            ox, oy = obstacle["rect"].center
            reach = HITBOX_RADIUS + obstacle["rect"].width / 2 - 1
            if (cx - ox) ** 2 + (cy - oy) ** 2 < reach ** 2:
                return True
        else:
            if not player_rect.colliderect(obstacle["rect"]):
                continue
            for part in _cactus_parts(obstacle):
                if _circle_hits_rect(cx, cy, HITBOX_RADIUS, part):
                    return True

    return False


# ===========================================================================
# Background (pre-rendered layers, scrolled with parallax)
# ===========================================================================

_background_layers = {}


def _get_background_layers():
    """Build the scenery layers once, then reuse them every frame."""
    if not _background_layers:
        rng = random.Random(1849)  # Fixed seed: same desert every run
        _background_layers["sky"] = _build_sky_layer()
        _background_layers["clouds"] = _build_cloud_layer(rng)
        _background_layers["mesas"] = _build_mesa_layer(rng)
        _background_layers["dunes"] = _build_dune_layer(rng)
        _background_layers["ground"] = _build_ground_layer(rng)
    return _background_layers


def _build_sky_layer():
    """Sky gradient in dithered bands, plus a pixel sun."""
    sky = pygame.Surface((CANVAS_WIDTH, GROUND_Y))
    sky.fill(COLOR_SAND)

    bands = [(0, 24, COLOR_SKY_TOP), (24, 50, COLOR_SKY_MID)]
    for start, end, color in bands:
        sky.fill(color, (0, start, CANVAS_WIDTH, end - start))

    # Dither each band edge so the gradient looks hand-pixelled.
    edges = [(24, COLOR_SKY_TOP), (50, COLOR_SKY_MID)]
    for edge_y, upper_color in edges:
        for x in range(0, CANVAS_WIDTH, 2):
            sky.fill(upper_color, (x, edge_y, 1, 1))
        for x in range(1, CANVAS_WIDTH, 4):
            sky.fill(upper_color, (x, edge_y + 1, 1, 1))

    sun_center = (262, 40)
    pygame.draw.circle(sky, COLOR_SUN_GLOW, sun_center, 19)
    pygame.draw.circle(sky, COLOR_SUN, sun_center, 14)
    pygame.draw.circle(sky, COLOR_SUN_CORE, sun_center, 10)
    return sky


def _build_cloud_layer(rng):
    """A few flat pixel clouds on a wide transparent strip."""
    width = CANVAS_WIDTH * 2
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)

    for i in range(5):
        cloud_w = rng.randint(22, 40)
        x = i * width // 5 + rng.randint(0, 50)
        y = rng.randint(12, 58)
        for dx in (-width, 0, width):  # Wrap so the strip tiles seamlessly
            left = x + dx
            layer.fill(COLOR_CLOUD, (left, y, cloud_w, 4))
            layer.fill(COLOR_CLOUD, (left + 4, y - 3, cloud_w // 2, 3))
            layer.fill(COLOR_CLOUD, (left + cloud_w // 2, y - 5, cloud_w // 3, 5))
            layer.fill(COLOR_CLOUD_SHADE, (left + 2, y + 4, cloud_w - 4, 1))
    return layer


def _build_mesa_layer(rng):
    """Distant flat-topped mesas and buttes."""
    width = CANVAS_WIDTH * 2
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)
    base_y = GROUND_Y - 4  # Dunes hide the very bottom

    x = 0
    while x < width - 40:
        if rng.random() < 0.35:
            mesa_w, mesa_h = rng.randint(18, 26), rng.randint(32, 46)  # Butte
        else:
            mesa_w, mesa_h = rng.randint(44, 90), rng.randint(20, 38)  # Mesa
        for dx in (-width, 0, width):
            _draw_mesa(layer, x + dx, base_y, mesa_w, mesa_h)
        x += mesa_w + rng.randint(10, 60)
    return layer


def _draw_mesa(surface, x, base_y, width, height):
    """Draw one mesa row by row: sloped base, sheer cliffs, striped rock."""
    talus = max(4, height // 3)
    for row in range(height):
        y = base_y - row
        inset = row // 2 if row < talus else talus // 2 + 2
        inset = min(inset, (width - 10) // 2)  # Keep the flat top at least 10 px wide
        row_w = width - inset * 2
        if row_w <= 0:
            continue
        left = x + inset
        is_cap = row >= height - 2
        is_stripe = row >= talus and (row - talus) % 7 == 3

        color = COLOR_MESA_LIGHT if is_cap else COLOR_MESA_SHADOW if is_stripe else COLOR_MESA
        surface.fill(color, (left, y, row_w, 1))
        if not is_cap:
            # Shaded right face (the sun is high on the right, so keep it narrow).
            shade_w = max(2, row_w // 4)
            surface.fill(COLOR_MESA_SHADOW, (left + row_w - shade_w, y, shade_w, 1))


def _build_dune_layer(rng):
    """Rolling sand dunes with tiny far-off cactus silhouettes."""
    width = CANVAS_WIDTH
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)

    def dune_height(px):
        # Whole-number frequencies so the layer tiles without a seam.
        t = 2 * math.pi * px / width
        return 12 + 5 * math.sin(2 * t) + 3 * math.sin(5 * t + 1.3)

    for px in range(width):
        top = GROUND_Y - round(dune_height(px))
        layer.fill(COLOR_DUNE, (px, top, 1, GROUND_Y - top))
        if dune_height(px + 1) < dune_height(px):  # Slope facing away from the sun
            layer.fill(COLOR_DUNE_SHADE, (px, top, 1, 2))

    for _ in range(4):
        px = rng.randint(4, width - 4)
        top = GROUND_Y - round(dune_height(px))
        layer.fill(COLOR_DUNE_CACTUS, (px, top - 7, 2, 8))
        layer.fill(COLOR_DUNE_CACTUS, (px - 2, top - 4, 2, 1))
        layer.fill(COLOR_DUNE_CACTUS, (px - 2, top - 6, 1, 2))
        layer.fill(COLOR_DUNE_CACTUS, (px + 2, top - 5, 2, 1))
        layer.fill(COLOR_DUNE_CACTUS, (px + 3, top - 7, 1, 2))
    return layer


def _build_ground_layer(rng):
    """Desert floor tile: lit edge, rock strata, pebbles and the odd bone."""
    width = CANVAS_WIDTH
    height = CANVAS_HEIGHT - GROUND_Y
    layer = pygame.Surface((width, height))
    layer.fill(COLOR_GROUND)

    layer.fill(COLOR_GROUND_LIGHT, (0, 0, width, 1))
    for x in range(0, width, 2):
        layer.fill(COLOR_GROUND_LIGHT, (x, 1, 1, 1))

    for _ in range(14):  # Strata streaks
        layer.fill(COLOR_GROUND_DARK, (rng.randint(0, width - 20), rng.randint(6, height - 3),
                                       rng.randint(6, 20), 1))
    for _ in range(45):  # Pebbles
        color = COLOR_PEBBLE if rng.random() < 0.5 else COLOR_GROUND_DARK
        layer.fill(color, (rng.randint(0, width - 2), rng.randint(3, height - 2),
                           rng.choice((1, 2)), 1))

    for _ in range(2):  # Bleached bones
        bx, by = rng.randint(10, width - 20), rng.randint(9, height - 6)
        layer.fill(COLOR_BONE, (bx + 1, by + 1, 5, 1))
        for knob_x in (bx, bx + 6):
            layer.fill(COLOR_BONE, (knob_x, by, 1, 1))
            layer.fill(COLOR_BONE, (knob_x, by + 2, 1, 1))
    return layer


def _blit_parallax(screen, layer, offset, y):
    """Blit a horizontally repeating layer scrolled left by `offset` pixels."""
    layer_width = layer.get_width()
    x = -(int(offset) % layer_width)
    while x < screen.get_width():
        screen.blit(layer, (x, y))
        x += layer_width


def draw_western_background(screen, camera_offset):
    """Draw sun and sky, clouds, mesas, dunes and the ground with parallax.

    camera_offset is the total distance travelled; farther layers scroll slower.
    """
    layers = _get_background_layers()
    screen.blit(layers["sky"], (0, 0))
    _blit_parallax(screen, layers["clouds"], camera_offset * 0.05, 0)
    _blit_parallax(screen, layers["mesas"], camera_offset * 0.15, 0)
    _blit_parallax(screen, layers["dunes"], camera_offset * 0.4, 0)
    _blit_parallax(screen, layers["ground"], camera_offset, GROUND_Y)


# ===========================================================================
# Sprites
# ===========================================================================

def draw_obstacles(screen, obstacles):
    """Draw every obstacle."""
    for obstacle in obstacles:
        if obstacle["kind"] == "tumbleweed":
            _draw_tumbleweed(screen, obstacle)
        else:
            _draw_cactus(screen, obstacle)


def _draw_cactus(screen, obstacle):
    """Draw a cactus with a dark outline, lit edge and little spines."""
    parts = _cactus_parts(obstacle)

    for part in parts:  # Outline first, so the fills sit on top of it
        screen.fill(COLOR_CACTUS_DARK, part.inflate(2, 2))
    for part in parts:
        screen.fill(COLOR_CACTUS, part)

    # Saguaros come in groups of five parts; the first part is the trunk.
    for trunk in parts[::5]:
        screen.fill(COLOR_CACTUS_LIGHT, (trunk.x + 1, trunk.y + 1, 1, trunk.height - 1))
        screen.fill(COLOR_CACTUS_DARK, (trunk.right - 1, trunk.y + 2, 1, trunk.height - 2))
        for spine_y in range(trunk.y + 3, trunk.bottom - 2, 4):
            screen.fill(COLOR_CACTUS_SPINE, (trunk.x + 2, spine_y, 1, 1))


def _draw_tumbleweed(screen, obstacle):
    """Draw a spinning, bouncing tumbleweed and its ground shadow."""
    rect = obstacle["rect"]
    cx, cy = rect.center
    radius = rect.width // 2
    angle = obstacle["angle"]

    hop_height = GROUND_Y - rect.bottom
    shadow_w = 11 - hop_height // 2  # Shrinks while the tumbleweed is airborne
    pygame.draw.ellipse(screen, COLOR_SHADOW, (cx - shadow_w // 2, GROUND_Y - 1, shadow_w, 3))

    pygame.draw.circle(screen, COLOR_TUMBLE_DARK, (cx, cy), radius, 1)
    pygame.draw.circle(screen, COLOR_TUMBLE_LIGHT, (cx, cy), radius - 3, 1)
    for k in range(3):  # Spinning twigs through the middle
        a = angle + k * math.pi / 3
        dx, dy = math.cos(a) * (radius - 1), math.sin(a) * (radius - 1)
        pygame.draw.line(screen, COLOR_TUMBLE,
                         (round(cx - dx), round(cy - dy)), (round(cx + dx), round(cy + dy)))
    for k in range(5):  # Stray twigs poking out
        a = angle + k * 2 * math.pi / 5
        tx, ty = round(cx + math.cos(a) * (radius + 1)), round(cy + math.sin(a) * (radius + 1))
        screen.fill(COLOR_TUMBLE_DARK, (tx, ty, 1, 1))


def draw_player(screen, player_rect, frame_count):
    """Draw the rolling ball, its ground shadow and kicked-up dust."""
    cx, cy = player_rect.center
    radius = PLAYER_RADIUS
    height_above_ground = GROUND_Y - player_rect.bottom
    on_ground = height_above_ground <= 0

    # Shadow shrinks as the ball rises.
    shadow_w = max(4, 14 - height_above_ground // 4)
    pygame.draw.ellipse(screen, COLOR_SHADOW, (cx - shadow_w // 2, GROUND_Y - 1, shadow_w, 3))

    # Little dust puffs trail behind the ball while it rolls.
    if on_ground:
        for i in range(3):
            age = (frame_count + i * 4) % 12
            size = 2 if age < 6 else 1
            screen.fill(COLOR_DUST, (player_rect.left - 1 - age, GROUND_Y - 2 - age // 4, size, size))

    # Body: dark outline, shaded lower-right, lit upper-left.
    pygame.draw.circle(screen, COLOR_PLAYER_OUTLINE, (cx, cy), radius)
    pygame.draw.circle(screen, COLOR_PLAYER_DARK, (cx, cy), radius - 1)
    pygame.draw.circle(screen, COLOR_PLAYER, (cx - 1, cy - 1), radius - 2)

    # Rolling detail: a band and a dot spin clockwise around the centre.
    angle = frame_count * ROLL_SPEED
    band_dx = math.cos(angle) * (radius - 2)
    band_dy = math.sin(angle) * (radius - 2)
    pygame.draw.line(screen, COLOR_PLAYER_DARK,
                     (round(cx - band_dx), round(cy - band_dy)),
                     (round(cx + band_dx), round(cy + band_dy)))
    dot_x = round(cx + math.cos(angle + math.pi / 2) * 3)
    dot_y = round(cy + math.sin(angle + math.pi / 2) * 3)
    screen.fill(COLOR_PLAYER_LIGHT, (dot_x, dot_y, 1, 1))

    # Fixed highlight so the ball reads as round.
    screen.fill(COLOR_PLAYER_LIGHT, (cx - 4, cy - 4, 2, 2))


# ===========================================================================
# HUD & overlays
# ===========================================================================

def draw_hud(screen, score, high_score):
    """Draw the score, the session high score and a quick hint at the start."""
    score_value = int(score)

    # Every 100 points the score blinks, Chrome-dino style.
    milestone = score_value >= 100 and score_value % 100 < 12
    shown_score = score_value // 100 * 100 if milestone else score_value
    blink_hidden = milestone and (score_value // 3) % 2 == 1

    right_edge = CANVAS_WIDTH - 8
    score_text = f"{shown_score:05d}"
    if not blink_hidden:
        draw_text(screen, score_text, right_edge, 8, COLOR_TEXT_DARK, align="right",
                  shadow=COLOR_SKY_TOP)

    score_width = render_pixel_text(score_text, COLOR_TEXT_DARK).get_width()
    draw_text(screen, f"HI {int(high_score):05d}", right_edge - score_width - 12, 8,
              COLOR_TEXT_MID, align="right")

    draw_text(screen, TITLE.upper(), 8, 8, COLOR_TEXT_MID)

    if score_value < 25:
        draw_text(screen, "SPACE OR UP TO JUMP", CANVAS_WIDTH // 2, 74, COLOR_TEXT_DARK,
                  align="center", shadow=COLOR_SKY_TOP)


def draw_game_over(screen, final_score, is_new_high_score=False):
    """Darken the scene and show a hanging wooden sign with the result."""
    overlay = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
    overlay.fill((58, 36, 22, 110))
    screen.blit(overlay, (0, 0))

    board = pygame.Rect(0, 0, 200, 88)
    board.center = (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 2)

    # Ropes the sign hangs from.
    for rope_x in (board.left + 50, board.right - 51):  # Clear of the HUD text
        screen.fill(COLOR_WOOD_DARK, (rope_x, 0, 1, board.top))

    # Planks with a dark frame.
    screen.fill(COLOR_WOOD_DARK, board.inflate(4, 4))
    screen.fill(COLOR_WOOD, board)
    for seam_y in (board.top + 28, board.top + 60):
        screen.fill(COLOR_WOOD_DARK, (board.left, seam_y, board.width, 1))
        screen.fill(COLOR_WOOD_LIGHT, (board.left, seam_y + 1, board.width, 1))
    for nail_x, nail_y in ((board.left + 3, board.top + 3), (board.right - 5, board.top + 3),
                           (board.left + 3, board.bottom - 5), (board.right - 5, board.bottom - 5)):
        screen.fill(COLOR_NAIL, (nail_x, nail_y, 2, 2))

    center_x = board.centerx
    draw_text(screen, "GAME OVER", center_x, board.top + 8, COLOR_TEXT_LIGHT, scale=2,
              align="center", shadow=COLOR_TEXT_DARK)
    draw_text(screen, f"SCORE {int(final_score):05d}", center_x, board.top + 34,
              COLOR_TEXT_LIGHT, align="center", shadow=COLOR_TEXT_DARK)
    if is_new_high_score:
        draw_text(screen, "NEW HIGH SCORE!", center_x, board.top + 47, COLOR_TEXT_GOLD,
                  align="center", shadow=COLOR_TEXT_DARK)
    draw_text(screen, "PRESS R OR SPACE TO RESTART", center_x, board.top + 70,
              COLOR_TEXT_LIGHT, align="center", shadow=COLOR_TEXT_DARK)


# ===========================================================================
# Main loop
# ===========================================================================

def main():
    """Run the game until the window is closed or ESC is pressed."""
    screen, canvas, clock, state, high_score = init_game()
    running = True

    while running:
        # --- Events ----------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif (state["game_over"]
                      and event.key in (pygame.K_r, pygame.K_SPACE)
                      and state["game_over_timer"] >= RESTART_DELAY_FRAMES):
                    state = reset_game()

        # --- Update ----------------------------------------------------------
        if state["game_over"]:
            state["game_over_timer"] += 1
        else:
            state["frame"] += 1
            state["scroll_speed"] = min(MAX_SPEED,
                                        BASE_SPEED + state["frame"] * SPEED_GAIN_PER_FRAME)

            state["is_jumping"], state["velocity_y"] = handle_input(
                state["player_rect"], state["is_jumping"], state["velocity_y"])
            state["velocity_y"], state["is_jumping"] = update_physics(
                state["player_rect"], state["velocity_y"])
            state["obstacles"] = spawn_and_update_obstacles(
                state["obstacles"], state["scroll_speed"])

            state["distance"] += state["scroll_speed"]
            state["score"] += state["scroll_speed"] * SCORE_PER_PIXEL

            if check_collision(state["player_rect"], state["obstacles"]):
                state["game_over"] = True
                if state["score"] > high_score:
                    state["new_high_score"] = high_score > 0
                    high_score = state["score"]

        # --- Draw ------------------------------------------------------------
        draw_western_background(canvas, state["distance"])
        draw_obstacles(canvas, state["obstacles"])
        draw_player(canvas, state["player_rect"], state["frame"])
        draw_hud(canvas, state["score"], high_score)
        if state["game_over"]:
            draw_game_over(canvas, state["score"], state["new_high_score"])

        pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
    sys.exit()
