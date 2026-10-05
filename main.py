"""Endless Runner - a minimal Google Dino style game built with pygame.

Controls:
    SPACE      - jump (while playing) / restart (on game over)
    R          - restart (on game over)
    ESC        - quit
"""

import sys

import pygame

# --- Settings ---------------------------------------------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

GROUND_Y = 320               # y-coordinate of the ground line
GRAVITY = 0.8                # downward acceleration per frame
JUMP_STRENGTH = -15          # initial upward velocity when jumping

PLAYER_X = 100
PLAYER_RADIUS = 20

OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 50
OBSTACLE_SPEED = 6
SPAWN_INTERVAL = 90          # frames between obstacle spawns

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (120, 120, 120)
BLUE = (50, 120, 220)
RED = (220, 50, 50)


# --- Game setup -------------------------------------------------------------
def create_player():
    """Return a new player dict resting on the ground."""
    return {
        "x": PLAYER_X,
        "y": GROUND_Y - PLAYER_RADIUS,
        "vel_y": 0,
        "radius": PLAYER_RADIUS,
        "on_ground": True,
    }


def create_obstacle():
    """Return a new obstacle rect just off the right edge of the screen."""
    return pygame.Rect(SCREEN_WIDTH, GROUND_Y - OBSTACLE_HEIGHT,
                       OBSTACLE_WIDTH, OBSTACLE_HEIGHT)


def reset_game():
    """Return a fresh game state dictionary."""
    return {
        "player": create_player(),
        "obstacles": [],
        "score": 0,
        "spawn_timer": 0,
        "game_over": False,
    }


# --- Game logic -------------------------------------------------------------
def jump(player):
    """Make the player jump, but only if standing on the ground."""
    if player["on_ground"]:
        player["vel_y"] = JUMP_STRENGTH
        player["on_ground"] = False


def update_physics(player, gravity):
    """Apply gravity to the player and stop them at the ground."""
    player["vel_y"] += gravity
    player["y"] += player["vel_y"]

    floor = GROUND_Y - player["radius"]
    if player["y"] >= floor:
        player["y"] = floor
        player["vel_y"] = 0
        player["on_ground"] = True


def update_obstacles(obstacles):
    """Move obstacles left and remove the ones that left the screen."""
    for obstacle in obstacles:
        obstacle.x -= OBSTACLE_SPEED
    obstacles[:] = [o for o in obstacles if o.right > 0]


def check_collision(player, obstacle):
    """Return True if the player's circle overlaps the obstacle rectangle."""
    # Find the point on the rectangle closest to the circle's center
    closest_x = max(obstacle.left, min(player["x"], obstacle.right))
    closest_y = max(obstacle.top, min(player["y"], obstacle.bottom))
    dx = player["x"] - closest_x
    dy = player["y"] - closest_y
    return dx * dx + dy * dy < player["radius"] ** 2


def update_game(state):
    """Advance the game by one frame while playing."""
    update_physics(state["player"], GRAVITY)

    state["spawn_timer"] += 1
    if state["spawn_timer"] >= SPAWN_INTERVAL:
        state["obstacles"].append(create_obstacle())
        state["spawn_timer"] = 0

    update_obstacles(state["obstacles"])

    for obstacle in state["obstacles"]:
        if check_collision(state["player"], obstacle):
            state["game_over"] = True
            return

    state["score"] += 1


# --- Drawing ----------------------------------------------------------------
def draw_world(screen, state):
    """Draw the ground, player and obstacles."""
    screen.fill(WHITE)
    pygame.draw.line(screen, GRAY, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)

    player = state["player"]
    pygame.draw.circle(screen, BLUE, (int(player["x"]), int(player["y"])),
                       player["radius"])

    for obstacle in state["obstacles"]:
        pygame.draw.rect(screen, RED, obstacle)


def draw_hud(screen, score, font):
    """Draw the current score in the top-right corner."""
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH - text.get_width() - 20, 20))


def draw_game_over(screen, score, big_font, font):
    """Draw the game over message with the final score."""
    lines = [
        (big_font, "GAME OVER"),
        (font, f"Final score: {score}"),
        (font, "Press R or SPACE to restart"),
    ]
    y = 110
    for line_font, message in lines:
        text = line_font.render(message, True, BLACK)
        screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, y))
        y += text.get_height() + 15


# --- Main loop --------------------------------------------------------------
def handle_events(state):
    """Process input. Returns the (possibly new) state, or None to quit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return None
            if state["game_over"]:
                if event.key in (pygame.K_r, pygame.K_SPACE):
                    return reset_game()
            elif event.key == pygame.K_SPACE:
                jump(state["player"])
    return state


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Endless Runner")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)

    state = reset_game()

    while True:
        state = handle_events(state)
        if state is None:
            break

        if not state["game_over"]:
            update_game(state)

        draw_world(screen, state)
        draw_hud(screen, state["score"], font)
        if state["game_over"]:
            draw_game_over(screen, state["score"], big_font, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
