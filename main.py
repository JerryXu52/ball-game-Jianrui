"""
Wild West Runner
================

A pixel-art endless runner set in a Wild West desert, built with Pygame.

Roll a stitched leather ball across the sand and jump over cacti, skull
rocks and tumbleweeds. The longer you survive, the faster the desert
scrolls by.

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
FRAME_TIME = 1.0 / FPS      # Fixed time step (seconds) used for particles
TITLE = "Wild West Runner"

# Top edge of the desert floor (the horizon line), in canvas pixels.
GROUND_Y = 150

# --- Player & physics (canvas pixels, per frame) ----------------------------
PLAYER_X = 48               # Horizontal centre of the ball
PLAYER_RADIUS = 7
BALL_SIZE = PLAYER_RADIUS * 2 + 1
HITBOX_RADIUS = 6           # Slightly forgiving collision circle
GRAVITY = 0.32
JUMP_VELOCITY = -5.4        # Peak jump height is roughly 43 px
FAST_FALL_BOOST = 0.45      # Extra gravity while holding DOWN in the air

# --- Squash & stretch ----------------------------------------------------------
# scale_y > 1 stretches the ball tall and thin; scale_y < 1 squashes it flat.
TAKEOFF_STRETCH = 1.35      # scale_y the instant the ball leaves the ground
LANDING_SQUASH = 0.62       # scale_y after the hardest possible landing
AIR_STRETCH_PER_SPEED = 0.045
AIR_STRETCH_MAX = 1.22      # Most the ball stretches from falling speed alone
WIDTH_PER_SQUASH = 0.8      # How much the width bulges as the height squashes
SQUASH_STIFFNESS = 0.28     # Spring pull back toward the target shape
SQUASH_DAMPING = 0.68       # Lower = more wobble after a landing

# --- Motion trails -------------------------------------------------------------
TRAIL_LENGTH = 7            # Ghost images kept at once
TRAIL_SAMPLE_EVERY = 2      # Record a ghost every N frames
TRAIL_SPEED_THRESHOLD = 5.0 # Ground speed at which trails appear on the ground
TRAIL_MAX_ALPHA = 130

# --- Particles ---------------------------------------------------------------
MAX_PARTICLES = 160
PARTICLE_GRAVITY = 160.0    # px / s^2

# --- Difficulty & scoring ----------------------------------------------------
BASE_SPEED = 2.6            # Starting scroll speed
MAX_SPEED = 7.0             # Speed cap
SPEED_GAIN_PER_FRAME = 0.0008
SCORE_PER_PIXEL = 0.06      # Score earned per pixel travelled
RESTART_DELAY_FRAMES = 20   # Stops an accidental instant restart
FIRST_OBSTACLE_OFFSET = 160 # Extra breathing room before the first obstacle
SHAKE_FRAMES = 14           # Screen shake length after a crash
SHAKE_STRENGTH = 3          # Max shake offset in canvas pixels

# --- Obstacles ---------------------------------------------------------------
# kind: (width, height, spawn weight)
OBSTACLE_TYPES = {
    "small_cactus": (10, 18, 24),
    "tall_cactus": (12, 26, 20),
    "giant_cactus": (14, 31, 10),
    "double_cactus": (22, 20, 14),
    "skull_rock": (20, 14, 16),
    "tumbleweed": (14, 14, 16),
}
TUMBLEWEED_HOP = 6          # Max bounce height of a tumbleweed
GAP_RANDOM_EXTRA = 160      # Random spacing added on top of the minimum gap


def rgb(hex_code):
    """Convert '#RRGGBB' into an (r, g, b) tuple."""
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def lerp_color(color_a, color_b, t):
    """Blend two colours; t=0 gives color_a, t=1 gives color_b."""
    return tuple(round(a + (b - a) * t) for a, b in zip(color_a, color_b))


# --- Palette -----------------------------------------------------------------
COLOR_SKY_TOP = rgb("#FDF5E6")       # Warm cream
COLOR_SKY_BOTTOM = rgb("#E9C46A")    # Desert gold at the horizon
COLOR_SUN = rgb("#FFF8E1")
COLOR_SUN_RING = rgb("#F9E6B0")
COLOR_CLOUD = rgb("#FFF9EC")
COLOR_CLOUD_SHADE = rgb("#F0DDB6")

COLOR_MOUNTAIN = rgb("#D6A877")      # Far mountain silhouettes
COLOR_MOUNTAIN_LIT = rgb("#E2BA8C")
COLOR_MESA = rgb("#BF8A5E")
COLOR_MESA_LIGHT = rgb("#CF9E70")
COLOR_MESA_SHADOW = rgb("#A8754D")
COLOR_DUNE = rgb("#DDBB86")
COLOR_DUNE_LIGHT = rgb("#E8CC9C")
COLOR_DUNE_SHADE = rgb("#CBA36D")
COLOR_DUNE_CACTUS = rgb("#B48D60")

COLOR_SOIL_TOP = rgb("#D2B48C")      # Sandy soil
COLOR_SOIL = rgb("#C19A6B")
COLOR_SOIL_DARK = rgb("#A47E54")
COLOR_HORIZON = rgb("#7A5A3C")
COLOR_PEBBLE_LIGHT = rgb("#E3CDA6")
COLOR_BONE = rgb("#F4ECD8")
COLOR_SHADOW = rgb("#A88760")

COLOR_CACTUS = rgb("#2A6F40")
COLOR_CACTUS_LIGHT = rgb("#3F8C57")
COLOR_CACTUS_DARK = rgb("#1C4F2D")
COLOR_CACTUS_SPINE = rgb("#CFE0A0")
COLOR_FLOWER = rgb("#E2708A")

COLOR_ROCK = rgb("#8E7B66")
COLOR_ROCK_LIGHT = rgb("#AE9C84")
COLOR_ROCK_DARK = rgb("#5E5044")
COLOR_SKULL_EYE = rgb("#3A2A1E")

COLOR_TUMBLE = rgb("#A27848")
COLOR_TUMBLE_LIGHT = rgb("#C29A62")
COLOR_TUMBLE_DARK = rgb("#7A5532")

COLOR_LEATHER = rgb("#C05A3E")       # Terracotta leather ball
COLOR_LEATHER_DARK = rgb("#8E3F2B")
COLOR_LEATHER_LIGHT = rgb("#E28A6B")
COLOR_LEATHER_OUTLINE = rgb("#4E2418")
COLOR_STITCH = rgb("#F4E3C3")

DUST_COLORS = [rgb("#E3CDA6"), rgb("#D2B48C"), rgb("#F3E6CC"), rgb("#C9AA7E")]
CRASH_COLORS = DUST_COLORS + [COLOR_LEATHER, COLOR_LEATHER_DARK]

COLOR_TEXT_DARK = rgb("#4A2E1A")
COLOR_TEXT_MID = rgb("#8A6440")
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
    """Return a fresh game state: score, player, speed, obstacles and effects."""
    player_rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    player_rect.midbottom = (PLAYER_X, GROUND_Y)

    # The first obstacle starts off-screen to give the player a moment to settle.
    first_obstacle = _create_obstacle(BASE_SPEED, CANVAS_WIDTH + FIRST_OBSTACLE_OFFSET)

    return {
        # Player
        "player_rect": player_rect,
        "velocity_y": 0.0,
        "is_jumping": False,
        "roll_angle": 0.0,
        "squash": {"y": 1.0, "velocity": 0.0},
        "squash_x": 1.0,
        "squash_y": 1.0,
        # World
        "scroll_speed": BASE_SPEED,
        "distance": 0.0,
        "obstacles": [first_obstacle],
        # Effects
        "particles": [],
        "trail": [],
        "shake": 0,
        # Progress
        "score": 0.0,
        "frame": 0,
        "game_over": False,
        "game_over_timer": 0,
        "new_high_score": False,
    }


def _make_window_icon():
    """Build a small leather-ball icon for the window title bar."""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, COLOR_LEATHER_OUTLINE, (16, 16), 15)
    pygame.draw.circle(icon, COLOR_LEATHER, (15, 15), 13)
    pygame.draw.line(icon, COLOR_LEATHER_DARK, (6, 22), (24, 8), 3)
    for i in range(4):
        icon.fill(COLOR_STITCH, (9 + i * 4, 18 - i * 4, 2, 2))
    icon.fill(COLOR_LEATHER_LIGHT, (9, 8, 4, 4))
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
# Squash & stretch
# ===========================================================================

def trigger_takeoff_stretch(squash):
    """Snap the ball tall and thin the moment it leaves the ground."""
    squash["y"] = TAKEOFF_STRETCH
    squash["velocity"] = 0.0


def trigger_landing_squash(squash, impact_speed):
    """Flatten the ball on landing; harder landings squash it more."""
    strength = min(1.0, abs(impact_speed) / abs(JUMP_VELOCITY))
    squash["y"] = 1.0 - (1.0 - LANDING_SQUASH) * strength
    squash["velocity"] = 0.0


def update_squash_and_stretch(squash, velocity_y, is_jumping):
    """Spring the ball's height scale back toward its resting shape.

    In the air the target stretches with vertical speed (thin and fast,
    round at the top of the arc). On the ground the target is 1.0, and the
    damped spring gives a small wobble after a landing.

    Returns:
        (squash_x, squash_y)
    """
    if is_jumping:
        target = 1.0 + min(AIR_STRETCH_MAX - 1.0, abs(velocity_y) * AIR_STRETCH_PER_SPEED)
    else:
        target = 1.0

    squash["velocity"] += (target - squash["y"]) * SQUASH_STIFFNESS
    squash["velocity"] *= SQUASH_DAMPING
    squash["y"] = max(0.5, min(1.5, squash["y"] + squash["velocity"]))

    squash_y = squash["y"]
    squash_x = 1.0 + (1.0 - squash_y) * WIDTH_PER_SQUASH  # Bulge out when flattened
    return squash_x, squash_y


# ===========================================================================
# Particles
# ===========================================================================

def emit_particles(particles, x, y, count, velocity_x, velocity_y, lifetime,
                   sizes=(1, 2), colors=DUST_COLORS):
    """Add up to `count` particles at (x, y).

    velocity_x, velocity_y and lifetime are (min, max) ranges in px/s and seconds.
    """
    for _ in range(count):
        if len(particles) >= MAX_PARTICLES:
            return
        life = random.uniform(*lifetime)
        particles.append({
            "x": x + random.uniform(-2, 2),
            "y": y - random.uniform(0, 2),
            "vx": random.uniform(*velocity_x),
            "vy": random.uniform(*velocity_y),
            "life": life,
            "max_life": life,
            "size": random.choice(sizes),
            "color": random.choice(colors),
        })


def emit_running_dust(particles, player_rect, scroll_speed):
    """Kick up a few dust specks behind the ball while it rolls."""
    if random.random() > min(0.9, 0.2 + scroll_speed * 0.1):
        return
    ground_speed = scroll_speed * FPS  # px/s, the speed the ground moves left
    emit_particles(particles, player_rect.left + 3, GROUND_Y - 1, 1,
                   velocity_x=(-ground_speed * 0.9, -ground_speed * 0.5),
                   velocity_y=(-30, -8), lifetime=(0.2, 0.45), sizes=(1, 1, 2))


def emit_landing_dust(particles, player_rect, scroll_speed, impact_speed):
    """Burst of dust to both sides of the ball when it lands."""
    strength = min(1.0, abs(impact_speed) / abs(JUMP_VELOCITY))
    drift = -scroll_speed * FPS * 0.4
    emit_particles(particles, player_rect.centerx, GROUND_Y - 1, 8 + int(strength * 10),
                   velocity_x=(drift - 70, drift + 70), velocity_y=(-75 * strength - 15, -15),
                   lifetime=(0.3, 0.65), sizes=(1, 2, 2, 3))


def emit_takeoff_dust(particles, player_rect, scroll_speed):
    """Small puff from the ground when the ball jumps."""
    drift = -scroll_speed * FPS * 0.5
    emit_particles(particles, player_rect.centerx, GROUND_Y - 1, 6,
                   velocity_x=(drift - 40, drift + 15), velocity_y=(-35, -5),
                   lifetime=(0.2, 0.4), sizes=(1, 2))


def emit_crash_burst(particles, player_rect):
    """Dust and leather scraps flying off on a crash."""
    emit_particles(particles, player_rect.right - 2, player_rect.centery, 22,
                   velocity_x=(-110, 60), velocity_y=(-120, -20),
                   lifetime=(0.4, 0.9), sizes=(1, 2, 2, 3), colors=CRASH_COLORS)


def update_particles(particles, dt):
    """Move particles with gravity, let them settle on the ground, drop expired ones.

    Args:
        particles: list of particle dicts.
        dt: time step in seconds.

    Returns:
        The list of particles still alive.
    """
    alive = []
    for particle in particles:
        particle["life"] -= dt
        if particle["life"] <= 0:
            continue
        particle["vy"] += PARTICLE_GRAVITY * dt
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        if particle["y"] >= GROUND_Y + 1:  # Settle on the ground
            particle["y"] = GROUND_Y + 1
            particle["vy"] = 0.0
            particle["vx"] *= 0.85
        alive.append(particle)
    return alive


def draw_particles(screen, particles):
    """Draw particles as square pixels that shrink as they fade out."""
    for particle in particles:
        remaining = particle["life"] / particle["max_life"]
        size = max(1, round(particle["size"] * (0.4 + 0.6 * remaining)))
        screen.fill(particle["color"],
                    (round(particle["x"]), round(particle["y"]) - size + 1, size, size))


# ===========================================================================
# Motion trails
# ===========================================================================

def update_motion_trail(trail_history, player_rect, squash_x, squash_y, scroll_speed,
                        active, frame):
    """Record afterimages of the ball and scroll old ones with the world.

    Ghosts are anchored to the ground, so they drift left at scroll speed and
    spread out behind the ball. When inactive, one ghost fades per frame.

    Returns:
        The updated trail history (oldest first).
    """
    for ghost in trail_history:
        ghost["x"] -= scroll_speed

    if active:
        if frame % TRAIL_SAMPLE_EVERY == 0:
            trail_history.append({
                "x": float(player_rect.centerx),
                "bottom": player_rect.bottom,
                "squash_x": squash_x,
                "squash_y": squash_y,
            })
    elif trail_history:
        trail_history.pop(0)

    while len(trail_history) > TRAIL_LENGTH:
        trail_history.pop(0)
    return trail_history


def draw_motion_trails(screen, trail_history):
    """Draw fading, semi-transparent ghost outlines of recent ball positions."""
    count = len(trail_history)
    for index, ghost in enumerate(trail_history):
        strength = (index + 1) / (count + 1)        # Older ghosts are fainter
        alpha = int(TRAIL_MAX_ALPHA * strength)
        width = max(2, round(BALL_SIZE * ghost["squash_x"]))
        height = max(2, round(BALL_SIZE * ghost["squash_y"]))

        image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(image, (*COLOR_LEATHER, alpha // 2), image.get_rect())
        pygame.draw.ellipse(image, (*COLOR_STITCH, alpha), image.get_rect(), 1)
        screen.blit(image, (round(ghost["x"]) - width // 2, ghost["bottom"] + 1 - height))


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
        "flower": random.random() < 0.35,       # Some cacti are in bloom
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


def _obstacle_parts(obstacle):
    """Break a solid obstacle into rectangles.

    Used for both drawing and collision, so the hitbox always matches the art.
    """
    rect = obstacle["rect"]
    if obstacle["kind"] == "double_cactus":
        return (_saguaro_parts(rect.x, rect.bottom, 10, 20)
                + _saguaro_parts(rect.x + 12, rect.bottom, 10, 14))
    if obstacle["kind"] == "skull_rock":
        return _skull_rock_parts(rect)
    return _saguaro_parts(rect.x, rect.bottom, rect.width, rect.height)


def _saguaro_parts(x, bottom, width, height):
    """Return [trunk, left_elbow, left_arm, right_elbow, right_arm] rects of one saguaro."""
    top = bottom - height
    trunk_width = 6 if width >= 14 else 4
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


def _skull_rock_parts(rect):
    """Return [boulder, boulder_top, skull] rects for a skull rock."""
    x, bottom = rect.x, rect.bottom
    return [
        pygame.Rect(x, bottom - 9, rect.width, 9),
        pygame.Rect(x + 3, bottom - 11, rect.width - 6, 2),
        pygame.Rect(x + 6, bottom - 14, 8, 3),
    ]


def _circle_hits_rect(cx, cy, radius, rect):
    """True if a circle overlaps an axis-aligned rectangle."""
    nearest_x = max(rect.left, min(cx, rect.right - 1))
    nearest_y = max(rect.top, min(cy, rect.bottom - 1))
    return (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2 < radius ** 2


def check_collision(player_rect, obstacles):
    """Check the ball (as a circle) against every obstacle.

    Cacti and skull rocks are tested part by part; tumbleweeds are circles.
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
            for part in _obstacle_parts(obstacle):
                if _circle_hits_rect(cx, cy, HITBOX_RADIUS, part):
                    return True

    return False


# ===========================================================================
# Background (pre-rendered layers, scrolled with parallax)
# ===========================================================================

# (layer name, scroll factor, y position). Farther layers scroll slower.
PARALLAX_LAYERS = [
    ("clouds", 0.04, 0),
    ("mountains", 0.08, 0),
    ("mesas", 0.18, 0),
    ("dunes", 0.45, 0),
    ("ground", 1.0, GROUND_Y - 2),
]

_background_layers = {}


def _get_background_layers():
    """Build the scenery layers once, then reuse them every frame."""
    if not _background_layers:
        rng = random.Random(1849)  # Fixed seed: same desert every run
        _background_layers["sky"] = _build_sky_layer()
        _background_layers["clouds"] = _build_cloud_layer(rng)
        _background_layers["mountains"] = _build_mountain_layer(rng)
        _background_layers["mesas"] = _build_mesa_layer(rng)
        _background_layers["dunes"] = _build_dune_layer(rng)
        _background_layers["ground"] = _build_ground_layer(rng)
    return _background_layers


def _build_sky_layer():
    """Cream-to-gold sky in dithered bands, with a striped retro sun."""
    sky = pygame.Surface((CANVAS_WIDTH, GROUND_Y))
    band_count = 6
    band_height = GROUND_Y / band_count
    band_colors = [lerp_color(COLOR_SKY_TOP, COLOR_SKY_BOTTOM, i / (band_count - 1))
                   for i in range(band_count)]

    for i, color in enumerate(band_colors):
        top = int(i * band_height)
        sky.fill(color, (0, top, CANVAS_WIDTH, int((i + 1) * band_height) - top))

    # Dither each band edge so the gradient looks hand-pixelled.
    for i in range(1, band_count):
        edge_y = int(i * band_height)
        for x in range(0, CANVAS_WIDTH, 2):
            sky.fill(band_colors[i], (x, edge_y - 1, 1, 1))
        for x in range(1, CANVAS_WIDTH, 4):
            sky.fill(band_colors[i], (x, edge_y - 2, 1, 1))

    # Low sun with horizontal cut-outs (a classic retro sunset touch).
    sun_x, sun_y = 238, 74
    pygame.draw.circle(sky, COLOR_SUN_RING, (sun_x, sun_y), 22)
    pygame.draw.circle(sky, COLOR_SUN, (sun_x, sun_y), 18)
    for cut_y, cut_h in ((sun_y + 6, 1), (sun_y + 11, 2), (sun_y + 16, 2)):
        row_color = sky.get_at((2, cut_y))
        sky.fill(row_color, (sun_x - 23, cut_y, 47, cut_h))
    return sky


def _build_cloud_layer(rng):
    """A few flat pixel clouds on a wide transparent strip."""
    width = CANVAS_WIDTH * 2
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)

    for i in range(5):
        cloud_w = rng.randint(22, 42)
        x = i * width // 5 + rng.randint(0, 50)
        y = rng.randint(28, 66)
        for dx in (-width, 0, width):  # Wrap so the strip tiles seamlessly
            left = x + dx
            layer.fill(COLOR_CLOUD, (left, y, cloud_w, 4))
            layer.fill(COLOR_CLOUD, (left + 4, y - 3, cloud_w // 2, 3))
            layer.fill(COLOR_CLOUD, (left + cloud_w // 2, y - 5, cloud_w // 3, 5))
            layer.fill(COLOR_CLOUD_SHADE, (left + 2, y + 4, cloud_w - 4, 1))
    return layer


def _build_mountain_layer(rng):
    """Jagged far-off mountain range with two-tone, stair-stepped faces."""
    width = CANVAS_WIDTH * 2
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)

    # A broad rolling ridgeline (whole-number sine cycles so it tiles) with
    # random jitter on closely spaced points for a rugged, craggy silhouette.
    points = []
    x = 0
    while x < width:
        t = 2 * math.pi * x / width
        ridge = 36 + 12 * math.sin(3 * t + 0.7) + 7 * math.sin(7 * t + 2.1)
        points.append((x, max(8, ridge + rng.uniform(-7, 7))))
        x += rng.randint(7, 16)
    points.append((width, points[0][1]))  # Close the loop for seamless tiling

    heights = [0] * (width + 1)
    for (x0, h0), (x1, h1) in zip(points, points[1:]):
        for px in range(x0, x1 + 1):
            heights[px] = h0 + (h1 - h0) * (px - x0) / (x1 - x0)

    for px in range(width):
        height = int(heights[px]) // 2 * 2  # Quantise for a stepped pixel edge
        lit = heights[px + 1] < heights[px]  # Slopes facing the sun (on the right)
        color = COLOR_MOUNTAIN_LIT if lit else COLOR_MOUNTAIN
        layer.fill(color, (px, GROUND_Y - height, 1, height))
    return layer


def _build_mesa_layer(rng):
    """Mid-distance flat-topped mesas and buttes."""
    width = CANVAS_WIDTH * 2
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)
    base_y = GROUND_Y - 6  # Dunes hide the very bottom

    x = rng.randint(0, 40)
    while x < width - 40:
        if rng.random() < 0.4:
            mesa_w, mesa_h = rng.randint(18, 26), rng.randint(28, 40)  # Butte
        else:
            mesa_w, mesa_h = rng.randint(44, 80), rng.randint(18, 30)  # Mesa
        for dx in (-width, 0, width):
            _draw_mesa(layer, x + dx, base_y, mesa_w, mesa_h)
        x += mesa_w + rng.randint(50, 150)
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
            shade_w = max(2, row_w // 4)
            surface.fill(COLOR_MESA_SHADOW, (left, y, shade_w, 1))  # Shaded side away from sun


def _build_dune_layer(rng):
    """Rolling sand dunes with sunlit crests and tiny far-off cacti."""
    width = CANVAS_WIDTH
    layer = pygame.Surface((width, GROUND_Y), pygame.SRCALPHA)

    def dune_height(px):
        # Whole-number frequencies so the layer tiles without a seam.
        t = 2 * math.pi * px / width
        return 12 + 5 * math.sin(2 * t) + 3 * math.sin(5 * t + 1.3)

    for px in range(width):
        top = GROUND_Y - round(dune_height(px))
        layer.fill(COLOR_DUNE, (px, top, 1, GROUND_Y - top))
        if dune_height(px + 1) < dune_height(px):   # Facing the sun
            layer.fill(COLOR_DUNE_LIGHT, (px, top, 1, 1))
        else:
            layer.fill(COLOR_DUNE_SHADE, (px, top, 1, 2))

    for _ in range(4):
        px = rng.randint(4, width - 6)
        top = GROUND_Y - round(dune_height(px))
        layer.fill(COLOR_DUNE_CACTUS, (px, top - 7, 2, 8))
        layer.fill(COLOR_DUNE_CACTUS, (px - 2, top - 4, 2, 1))
        layer.fill(COLOR_DUNE_CACTUS, (px - 2, top - 6, 1, 2))
        layer.fill(COLOR_DUNE_CACTUS, (px + 2, top - 5, 2, 1))
        layer.fill(COLOR_DUNE_CACTUS, (px + 3, top - 7, 1, 2))
    return layer


def _build_ground_layer(rng):
    """Desert floor tile: Dino-style horizon line with bumps, sandy soil, pebbles, bones.

    The tile starts 2 px above GROUND_Y so the bumps can poke above the line.
    """
    width = CANVAS_WIDTH
    height = CANVAS_HEIGHT - GROUND_Y + 2
    layer = pygame.Surface((width, height), pygame.SRCALPHA)
    line_y = 2

    layer.fill(COLOR_SOIL_TOP, (0, line_y, width, 9))
    layer.fill(COLOR_SOIL, (0, line_y + 9, width, height - line_y - 9))
    for x in range(0, width, 2):  # Dither between the two soil tones
        layer.fill(COLOR_SOIL, (x, line_y + 8, 1, 1))
    for x in range(1, width, 4):
        layer.fill(COLOR_SOIL, (x, line_y + 7, 1, 1))

    layer.fill(COLOR_HORIZON, (0, line_y, width, 1))
    for _ in range(10):  # Bumps along the horizon line
        bump_x = rng.randint(0, width - 6)
        layer.fill(COLOR_HORIZON, (bump_x, line_y - 1, rng.randint(2, 5), 1))
    for _ in range(3):
        layer.fill(COLOR_HORIZON, (rng.randint(0, width - 2), line_y - 2, 1, 1))

    for _ in range(26):  # Specks in the top band
        layer.fill(COLOR_SOIL_DARK, (rng.randint(0, width - 3), rng.randint(line_y + 2, line_y + 7),
                                     rng.randint(1, 3), 1))
    for _ in range(12):  # Strata streaks
        layer.fill(COLOR_SOIL_DARK, (rng.randint(0, width - 20), rng.randint(line_y + 11, height - 3),
                                     rng.randint(6, 20), 1))
    for _ in range(40):  # Pebbles
        color = COLOR_PEBBLE_LIGHT if rng.random() < 0.5 else COLOR_SOIL_DARK
        layer.fill(color, (rng.randint(0, width - 2), rng.randint(line_y + 10, height - 2),
                           rng.choice((1, 2)), 1))

    for _ in range(2):  # Bleached bones
        bx, by = rng.randint(10, width - 20), rng.randint(line_y + 13, height - 6)
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
    """Draw the sky and sun, then each parallax layer from far to near.

    camera_offset is the total distance travelled. Distant clouds and
    mountains crawl, dunes move at medium pace, the ground keeps pace
    with the obstacles.
    """
    layers = _get_background_layers()
    screen.blit(layers["sky"], (0, 0))
    for name, factor, y in PARALLAX_LAYERS:
        _blit_parallax(screen, layers[name], camera_offset * factor, y)


# ===========================================================================
# Sprites
# ===========================================================================

def draw_obstacles(screen, obstacles):
    """Draw every obstacle."""
    for obstacle in obstacles:
        kind = obstacle["kind"]
        if kind == "tumbleweed":
            _draw_tumbleweed(screen, obstacle)
        elif kind == "skull_rock":
            _draw_skull_rock(screen, obstacle)
        else:
            _draw_cactus(screen, obstacle)


def _draw_ground_shadow(screen, center_x, width):
    """Flat oval shadow on the soil just below the horizon line."""
    width = max(2, int(width))
    pygame.draw.ellipse(screen, COLOR_SHADOW, (center_x - width // 2, GROUND_Y + 1, width, 3))


def _draw_cactus(screen, obstacle):
    """Draw a cactus with a dark outline, lit edge, spines and maybe a flower."""
    parts = _obstacle_parts(obstacle)
    _draw_ground_shadow(screen, obstacle["rect"].centerx + 2, obstacle["rect"].width + 4)

    for part in parts:  # Outline first, so the fills sit on top of it
        screen.fill(COLOR_CACTUS_DARK, part.inflate(2, 2))
    for part in parts:
        screen.fill(COLOR_CACTUS, part)

    # Saguaros come in groups of five parts; the first part is the trunk.
    for trunk in parts[::5]:
        screen.fill(COLOR_CACTUS_LIGHT, (trunk.x + 1, trunk.y + 1, 1, trunk.height - 1))
        screen.fill(COLOR_CACTUS_DARK, (trunk.right - 1, trunk.y + 2, 1, trunk.height - 2))
        spine_columns = (trunk.x + 2, trunk.x + 4) if trunk.width >= 6 else (trunk.x + 2,)
        for column, spine_x in enumerate(spine_columns):
            for spine_y in range(trunk.y + 3 + column * 2, trunk.bottom - 2, 4):
                screen.fill(COLOR_CACTUS_SPINE, (spine_x, spine_y, 1, 1))

    if obstacle["flower"]:
        trunk = parts[0]
        screen.fill(COLOR_FLOWER, (trunk.centerx - 1, trunk.y - 1, 2, 2))
        screen.fill(COLOR_TEXT_GOLD, (trunk.centerx - 1, trunk.y - 1, 1, 1))


SKULL_PIXELS = [
    "#..........#",
    ".##.####.##.",
    "...#o##o#...",
    "....####....",
    "....#oo#....",
]


def _draw_skull_rock(screen, obstacle):
    """Draw a weathered boulder with a bleached cow skull on top."""
    boulder, boulder_top, _skull_box = _obstacle_parts(obstacle)
    rect = obstacle["rect"]
    _draw_ground_shadow(screen, rect.centerx + 2, rect.width + 6)

    for part in (boulder, boulder_top):
        screen.fill(COLOR_ROCK_DARK, part.inflate(2, 2))
    for part in (boulder, boulder_top):
        screen.fill(COLOR_ROCK, part)

    # Round off the corners, light the top-left, shade the right.
    for corner_x in (boulder.left, boulder.right - 1):
        screen.fill(COLOR_ROCK_DARK, (corner_x, boulder.top, 1, 1))
    screen.fill(COLOR_ROCK_LIGHT, (boulder_top.x + 1, boulder_top.y, boulder_top.width - 5, 1))
    screen.fill(COLOR_ROCK_LIGHT, (boulder.x + 1, boulder.y + 1, 3, 1))
    screen.fill(COLOR_ROCK_DARK, (boulder.right - 3, boulder.y + 2, 2, boulder.height - 2))
    for crack_x, crack_y in ((5, 4), (6, 5), (12, 3), (12, 4), (13, 6)):  # Cracks
        screen.fill(COLOR_ROCK_DARK, (boulder.x + crack_x, boulder.y + crack_y, 1, 1))

    skull_x, skull_y = rect.x + 4, rect.bottom - 15
    for row, line in enumerate(SKULL_PIXELS):
        for col, cell in enumerate(line):
            if cell == "#":
                screen.fill(COLOR_BONE, (skull_x + col, skull_y + row, 1, 1))
            elif cell == "o":
                screen.fill(COLOR_SKULL_EYE, (skull_x + col, skull_y + row, 1, 1))


def _draw_tumbleweed(screen, obstacle):
    """Draw a spinning, bouncing tumbleweed and its ground shadow."""
    rect = obstacle["rect"]
    cx, cy = rect.center
    radius = rect.width // 2
    angle = obstacle["angle"]

    hop_height = GROUND_Y - rect.bottom
    _draw_ground_shadow(screen, cx, 11 - hop_height // 2)  # Shrinks while airborne

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


def _render_ball_sprite(rotation_angle):
    """Draw the leather ball, with its seam rotated, onto a small transparent surface.

    Shading and highlight stay fixed (the light doesn't spin); only the
    stitched seam and rivets turn with the ball.
    """
    size = BALL_SIZE
    c = PLAYER_RADIUS
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(sprite, COLOR_LEATHER_OUTLINE, (c, c), c)
    pygame.draw.circle(sprite, COLOR_LEATHER_DARK, (c, c), c - 1)
    pygame.draw.circle(sprite, COLOR_LEATHER, (c - 1, c - 1), c - 2)

    cos_a, sin_a = math.cos(rotation_angle), math.sin(rotation_angle)

    def to_sprite(u, v):
        """Rotate a point in ball space into sprite pixel coordinates."""
        return round(c + u * cos_a - v * sin_a), round(c + u * sin_a + v * cos_a)

    # S-shaped seam across the ball, laced with pairs of stitches.
    seam_reach = c - 2
    seam_points = []
    for i in range(11):
        t = -1.0 + i * 0.2
        u, v = t * seam_reach, math.sin(t * math.pi) * 1.8
        seam_points.append(to_sprite(u, v))
        if i in (2, 5, 8):  # Stitches first, so the seam line stays unbroken on top
            for side in (-1.6, 1.6):
                sprite.fill(COLOR_STITCH, (*to_sprite(u, v + side), 1, 1))
    pygame.draw.lines(sprite, COLOR_LEATHER_OUTLINE, False, seam_points)

    # Two rivets on the panels either side of the seam.
    for v in (-3.6, 3.6):
        sprite.fill(COLOR_STITCH, (*to_sprite(0, v), 1, 1))

    sprite.fill(COLOR_LEATHER_LIGHT, (c - 4, c - 4, 2, 2))  # Fixed highlight
    sprite.fill(COLOR_LEATHER_LIGHT, (c - 2, c - 5, 2, 1))
    return sprite


def draw_player_shadow(screen, player_rect, squash_x):
    """Shadow under the ball: shrinks as it rises, widens when squashed."""
    height_above_ground = GROUND_Y - player_rect.bottom
    width = (BALL_SIZE - height_above_ground // 4) * squash_x
    _draw_ground_shadow(screen, player_rect.centerx, max(4, width))


def draw_player_with_squash(screen, player_rect, squash_x, squash_y, rotation_angle):
    """Draw the rolling leather ball scaled by squash_x / squash_y.

    The sprite is scaled with nearest-neighbour filtering so it stays pixel
    crisp, and anchored at its bottom centre so squashing keeps it on the ground.
    """
    sprite = _render_ball_sprite(rotation_angle)
    width = max(2, round(BALL_SIZE * squash_x))
    height = max(2, round(BALL_SIZE * squash_y))
    if (width, height) != sprite.get_size():
        sprite = pygame.transform.scale(sprite, (width, height))
    screen.blit(sprite, (player_rect.centerx - width // 2, player_rect.bottom + 1 - height))


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
        draw_text(screen, "SPACE OR UP TO JUMP", CANVAS_WIDTH // 2, 100, COLOR_TEXT_DARK,
                  align="center", shadow=COLOR_SKY_TOP)


def draw_game_over(screen, final_score, is_new_high_score=False):
    """Darken the scene and show a hanging wooden sign with the result."""
    overlay = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
    overlay.fill((60, 40, 25, 110))
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
# Game loop helpers
# ===========================================================================

def update_running_game(state, high_score):
    """Advance one frame of play: input, physics, obstacles, score, collisions.

    Returns:
        The (possibly updated) session high score.
    """
    state["frame"] += 1
    state["scroll_speed"] = min(MAX_SPEED, BASE_SPEED + state["frame"] * SPEED_GAIN_PER_FRAME)
    speed = state["scroll_speed"]
    player_rect = state["player_rect"]
    particles = state["particles"]

    # Input -> takeoff
    was_airborne = state["is_jumping"]
    is_jumping, velocity_y = handle_input(player_rect, was_airborne, state["velocity_y"])
    if is_jumping and not was_airborne:
        trigger_takeoff_stretch(state["squash"])
        emit_takeoff_dust(particles, player_rect, speed)

    # Physics -> landing
    impact_speed = velocity_y + GRAVITY
    velocity_y, landed_airborne = update_physics(player_rect, velocity_y)
    if is_jumping and not landed_airborne:
        trigger_landing_squash(state["squash"], impact_speed)
        emit_landing_dust(particles, player_rect, speed, impact_speed)
    state["velocity_y"], state["is_jumping"] = velocity_y, landed_airborne

    if not state["is_jumping"]:
        emit_running_dust(particles, player_rect, speed)

    # The ball spins exactly as fast as the ground moves under it.
    state["roll_angle"] += speed / PLAYER_RADIUS

    state["obstacles"] = spawn_and_update_obstacles(state["obstacles"], speed)
    state["distance"] += speed
    state["score"] += speed * SCORE_PER_PIXEL

    if check_collision(player_rect, state["obstacles"]):
        state["game_over"] = True
        state["shake"] = SHAKE_FRAMES
        emit_crash_burst(particles, player_rect)
        if state["score"] > high_score:
            state["new_high_score"] = high_score > 0
            high_score = state["score"]

    return high_score


def update_effects(state):
    """Advance squash & stretch, motion trails and particles (also after a crash)."""
    running = not state["game_over"]
    state["squash_x"], state["squash_y"] = update_squash_and_stretch(
        state["squash"], state["velocity_y"], state["is_jumping"])

    trail_active = running and (state["is_jumping"]
                                or state["scroll_speed"] >= TRAIL_SPEED_THRESHOLD)
    state["trail"] = update_motion_trail(
        state["trail"], state["player_rect"], state["squash_x"], state["squash_y"],
        state["scroll_speed"] if running else 0.0, trail_active, state["frame"])

    state["particles"] = update_particles(state["particles"], FRAME_TIME)
    if state["shake"] > 0:
        state["shake"] -= 1


def draw_scene(canvas, state, high_score):
    """Draw one complete frame onto the low-resolution canvas."""
    draw_western_background(canvas, state["distance"])
    draw_obstacles(canvas, state["obstacles"])
    draw_motion_trails(canvas, state["trail"])
    draw_player_shadow(canvas, state["player_rect"], state["squash_x"])
    draw_particles(canvas, state["particles"])
    draw_player_with_squash(canvas, state["player_rect"], state["squash_x"],
                            state["squash_y"], state["roll_angle"])
    draw_hud(canvas, state["score"], high_score)
    if state["game_over"]:
        draw_game_over(canvas, state["score"], state["new_high_score"])


def present(screen, canvas, shake_frames):
    """Scale the canvas up to the window, adding screen shake after a crash."""
    pygame.transform.scale(canvas, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
    if shake_frames > 0:
        strength = SHAKE_STRENGTH * shake_frames / SHAKE_FRAMES
        offset_x = round(random.uniform(-strength, strength)) * PIXEL_SCALE
        offset_y = round(random.uniform(-strength, strength)) * PIXEL_SCALE
        screen.scroll(offset_x, offset_y)
    pygame.display.flip()


# ===========================================================================
# Main loop
# ===========================================================================

def main():
    """Run the game until the window is closed or ESC is pressed."""
    screen, canvas, clock, state, high_score = init_game()
    running = True

    while running:
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

        if state["game_over"]:
            state["game_over_timer"] += 1
        else:
            high_score = update_running_game(state, high_score)

        update_effects(state)
        draw_scene(canvas, state, high_score)
        present(screen, canvas, state["shake"])
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
    sys.exit()
