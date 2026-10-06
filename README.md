# Wild West Runner

A pixel-art endless runner set in the Wild West, built with Python and Pygame.
Roll a stitched leather ball across the desert, jump over cacti, skull rocks
and tumbleweeds, grab power-ups, and see how far you can get as the pace
keeps picking up.

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
| `SPACE` / `UP` | Jump (press again in mid-air with a Winged Horseshoe) |
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

### Power-ups

| Item | Effect |
| --- | --- |
| Winged Horseshoe | **Double jump** for 10 seconds: press `SPACE` / `UP` again in mid-air |
| Golden Star | **Invincible** for 5 seconds: smash straight through obstacles (+20 each) |
| Coin Bag | **+100 bonus points** right away |

Items float on the ground (roll into them) or in the air (jump for them).
Grabbing an item you already have restarts its timer.

## What you made better

### Power-up system

- **Three Western items drawn as pixel art:** a Winged Horseshoe, a
  Golden Star and a Coin Bag with a gold `$`. Each one has a dark outline so
  it stands out against the sand and sky.
- **Floating pickups:** items bob up and down, pulse with a coloured glow,
  have a sparkle circling them and cast a shadow that shrinks with height.
- **Fair placement:** a new item appears every 6–11 seconds (the first after
  4), always in the empty stretch between two obstacles and at least 28 px
  from both, so an item never sits on a hazard. Heights vary: on the
  ground (roll into it), low (caught over most of a jump), or high (near the
  top of a jump).
- **Pickup feedback:** a sparkle burst in the item's colours, and a pop-up
  text that rises and fades ("DOUBLE JUMP ACTIVE!", "INVINCIBLE!",
  "+100 BONUS!"). Pop-ups stack when they appear together and stay on
  screen near the edges.

### Double jump

- While the Winged Horseshoe is active, a fresh press of `SPACE` / `UP` in
  mid-air gives a second, slightly smaller jump. A full double jump reaches
  about 73 px, compared with about 43 px for a single jump.
- Only one extra jump per trip through the air, and landing refills it.
  Holding the key down doesn't use it up, and neither does the press that
  starts a normal jump.
- Small white wings flap beside the ball while the double jump is ready.
  Using it plays the takeoff stretch and puffs out white feathers.

### Invincibility

- The Golden Star makes the ball invulnerable for 5 seconds.
- **Aura:** a pulsing golden glow with a rainbow ring and four rainbow
  sparkles circling the ball. The ball itself flashes gold and leaves a gold
  motion trail.
- **Smashing:** obstacles you run into burst into debris in their own
  colours (green for cacti, grey for rock, brown for tumbleweeds). Each one
  gives +20 points, shows a "SMASH +20" pop-up and shakes the screen a
  little.
- The aura blinks for the last 1.5 seconds so the end never comes as a
  surprise.

### Active power-up HUD

- In the top-left corner, each timed effect gets a row: its icon, a bar
  that empties as time runs out, and the seconds left. The bar blinks during
  the last 1.5 seconds.

### Fixes along the way

- **Obstacle spacing at top speed:** an obstacle that had scrolled off the
  left edge used to be removed before the next one was due. With nothing
  left to measure from, the next obstacle appeared straight away, making
  gaps at top speed shorter than intended. The newest obstacle is now kept
  until the next one spawns, so every gap is honoured. Power-up placement
  relies on this.
- Smashed obstacles are hidden and harmless but stay in the list for the
  same reason.

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
| `create_player()` | Builds the player: position, motion, animation and active power-ups |
| `handle_input(player_rect, is_jumping, velocity_y)` | Reads the jump and fast-fall keys |
| `try_double_jump(player)` | Mid-air jump when a Winged Horseshoe is active and unused |
| `update_physics(player_rect, velocity_y)` | Applies gravity and landing |
| `update_squash_and_stretch(squash, velocity_y, is_jumping)` | Springs the ball's shape toward its target |
| `spawn_and_update_obstacles(obstacles, scroll_speed)` | Moves, removes and spawns obstacles |
| `check_collision(player_rect, obstacles)` | Tests the ball's circle against each obstacle |
| `spawn_powerup(powerups, current_time, obstacles)` | Places an item in a safe gap and returns when the next is due |
| `check_item_collisions(player, powerups)` | Returns (and removes) the items the ball touches |
| `apply_powerup_effect(player, powerup_type)` | Starts the effect and returns bonus points and pop-up text |
| `smash_obstacle(state, obstacle)` | Destroys an obstacle hit while invincible |
| `add_floating_text(...)` / `draw_floating_texts(...)` | Rising, fading pop-up text |
| `update_particles(particles, dt)` | Moves, settles and expires dust particles |
| `update_motion_trail(...)` / `draw_motion_trails(screen, trail_history)` | Records and draws the afterimages |
| `draw_western_background(screen, camera_offset)` | Draws the sky, sun and parallax layers |
| `draw_player_with_squash(screen, player_rect, squash_x, squash_y, rotation_angle)` | Draws the rolling, squashing ball |
| `draw_invincibility_aura(...)` / `draw_double_jump_wings(...)` | Power-up visuals on the ball |
| `draw_hud(screen, score, high_score)` | Draws the score and high score |
| `draw_active_powerup_hud(screen, active_effects)` | Draws the icon, timer bar and seconds left for each active effect |
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
- `POWERUP_TYPES`: each item's duration, spawn weight, pop-up text and colours
- `POWERUP_INTERVAL`, `FIRST_POWERUP_TIME`, `POWERUP_HEIGHTS`: how often items appear and at what heights
- `DOUBLE_JUMP_VELOCITY`, `SCORE_BOOST_POINTS`, `SMASH_POINTS`: strength of each power-up
- `OBSTACLE_TYPES`: obstacle sizes and how often each one appears
- `PARALLAX_LAYERS`: the scroll speed of each background layer
- `PIXEL_SCALE`: window size (the game draws at 320×180 and scales up by this factor)
- `COLOR_*`: the color palette

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`**: make sure the virtual
  environment is active, then run `pip install -r requirements.txt` again.
- **No Pygame wheel for a brand-new Python version**: try `pip install --upgrade pip`
  first, or use a Python version Pygame publishes wheels for.
