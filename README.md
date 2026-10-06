# Wild West Runner

A pixel-art endless runner set in the Wild West, built with Python and Pygame.
Roll a stitched leather ball across the desert, jump over cacti, skull rocks
and tumbleweeds, and see how far you can get as the pace keeps picking up.

All graphics, including the font, are drawn in code, so there are no asset
files to download.

## Requirements

- Python 3.9 or newer
- Pygame 2.5.0 or newer (installed from `requirements.txt`)

## Setup

Create and activate a virtual environment, then install the dependencies.

**macOS / Linux**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (Command Prompt)**

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

> On some systems the command is `python3` instead of `python`.

## Run

```bash
python main.py
```

## Controls

| Key            | Action                          |
| -------------- | ------------------------------- |
| `SPACE` / `UP` | Jump                            |
| `DOWN`         | Drop faster while in the air    |
| `R` / `SPACE`  | Restart after Game Over         |
| `ESC`          | Quit                            |

## How it plays

- The ball rolls on its own; you only decide when to jump.
- Hazards: small, tall and giant saguaros, double cactus clusters, boulders
  topped with a cow skull, and bouncing tumbleweeds.
- Your score goes up with the distance you cover, and the scroll speed rises
  the longer you survive.
- The high score is kept for the current session.

## What you made better

### Western pixel-art style

- **New palette:** a warm cream-to-gold sky (`#FDF5E6` → `#E9C46A`) drawn in
  dithered bands, and sandy soil (`#D2B48C` / `#C19A6B`) under a Chrome
  Dino-style horizon line with small bumps.
- **Retro sunset:** a low sun with horizontal stripes cut through it.
- **Four parallax layers**, each scrolling at its own speed:
  - clouds and a craggy mountain range in the far distance (slowest),
  - mesas and buttes in the middle distance,
  - rolling dunes with tiny cactus silhouettes (medium),
  - the ground, which moves with the obstacles (fastest).
- **Desert hazards drawn in code:** saguaros in four sizes, some with a
  flower on top; a weathered boulder with a bleached cow skull; and a
  spinning, bouncing tumbleweed. Each one casts a shadow on the ground.
- **Leather ball player:** an S-shaped seam with laced stitches and rivets.
  The pattern rotates while the light and highlight stay fixed, so the ball
  reads as round.
- **Rolling tied to speed:** the ball turns by `scroll_speed / radius` each
  frame, so it never looks like it is sliding, even at top speed.

### Squash & stretch physics

- **Takeoff:** the ball snaps to a tall, thin shape (scale Y 1.35, scale X 0.72).
- **In the air:** the stretch follows vertical speed, so the ball is long
  while rising or falling fast and round at the top of the arc.
- **Landing:** the ball flattens (scale Y down to 0.62, scale X up to 1.30).
  Harder landings flatten it more, and a full jump gives the deepest squash.
- **Recovery:** a damped spring brings the ball back to round with a small
  wobble. The sprite is scaled with nearest-neighbour filtering and anchored
  at its base, so it stays crisp and on the ground.
- Squash and stretch are visual only; the hitbox doesn't change, so
  collisions stay fair.

### Motion trails & particles

- **Afterimages:** see-through ghost outlines of the ball are recorded every
  other frame during jumps and at high ground speed. They fade with age and
  slide away with the ground, so they spread out into a trail.
- **Dust particles:**
  - specks kicked up behind the ball while it rolls (more at higher speed),
  - a puff on takeoff,
  - a burst on landing that grows with impact.

  Particles fall with gravity, settle on the ground and shrink as they fade.
- **Crash effects:** a burst of dust and leather scraps, plus a short screen
  shake that fades out.

### Code structure

- Separate helpers for each system: `update_squash_and_stretch`,
  `update_particles(particles, dt)`, `update_motion_trail`,
  `draw_motion_trails(screen, trail_history)`,
  `draw_player_with_squash(screen, player_rect, squash_x, squash_y, rotation_angle)`.
- The main loop is now four short steps: `update_running_game`,
  `update_effects`, `draw_scene` and `present`.
- Obstacle shapes come from one function that both drawing and collision
  use, so what you see is exactly what you hit.

## Project structure

```
.
├── main.py           # The whole game
├── requirements.txt  # Python dependencies
└── README.md
```

Main functions in `main.py`:

| Function | Purpose |
| --- | --- |
| `init_game()` | Starts Pygame and creates the window, clock and starting state |
| `reset_game()` | Resets score, player, speed, obstacles and effects |
| `handle_input(player_rect, is_jumping, velocity_y)` | Reads the jump and fast-fall keys |
| `update_physics(player_rect, velocity_y)` | Applies gravity and landing |
| `update_squash_and_stretch(squash, velocity_y, is_jumping)` | Springs the ball's shape toward its target |
| `spawn_and_update_obstacles(obstacles, scroll_speed)` | Moves, removes and spawns obstacles |
| `check_collision(player_rect, obstacles)` | Tests the ball's circle against each obstacle |
| `update_particles(particles, dt)` | Moves, settles and expires dust particles |
| `update_motion_trail(...)` / `draw_motion_trails(screen, trail_history)` | Records and draws the afterimages |
| `draw_western_background(screen, camera_offset)` | Draws the sky, sun and parallax layers |
| `draw_player_with_squash(screen, player_rect, squash_x, squash_y, rotation_angle)` | Draws the rolling, squashing ball |
| `draw_hud(screen, score, high_score)` | Draws the score and high score |
| `draw_game_over(screen, final_score)` | Draws the Game Over sign |
| `main()` | Runs the game loop |

## Tweaking the game

The constants at the top of `main.py` control the feel of the game:

- `BASE_SPEED`, `MAX_SPEED`, `SPEED_GAIN_PER_FRAME`: how fast it starts and how quickly it speeds up
- `GRAVITY`, `JUMP_VELOCITY`: jump height and hang time
- `TAKEOFF_STRETCH`, `LANDING_SQUASH`, `SQUASH_STIFFNESS`, `SQUASH_DAMPING`: how rubbery the ball feels
- `TRAIL_LENGTH`, `TRAIL_SPEED_THRESHOLD`, `TRAIL_MAX_ALPHA`: afterimage length, when they appear and how strong they are
- `MAX_PARTICLES`, `PARTICLE_GRAVITY`: dust amount and weight
- `SHAKE_FRAMES`, `SHAKE_STRENGTH`: crash screen shake
- `OBSTACLE_TYPES`: obstacle sizes and how often each one appears
- `PARALLAX_LAYERS`: the scroll speed of each background layer
- `PIXEL_SCALE`: window size (the game draws at 320×180 and scales up by this factor)
- `COLOR_*`: the color palette

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`**: make sure the virtual
  environment is active, then run `pip install -r requirements.txt` again.
- **No Pygame wheel for a brand-new Python version**: try `pip install --upgrade pip`
  first, or use a Python version Pygame publishes wheels for.
