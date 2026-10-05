# Endless Runner

A minimal Google Dino style endless runner built with Python and pygame.
You are a ball; jump over the red blocks for as long as you can.

## How to run

Requires Python 3.

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Controls:

| Key | Action |
| --- | --- |
| `SPACE` | Jump (while playing) / restart (on game over) |
| `R` | Restart (on game over) |
| `ESC` | Quit |

## What you made better

_TODO: this is the base version. List the improvements made on top of it here
(e.g. increasing speed over time, random obstacle sizes, high score saving)._

## How it works

- **Game loop** (`main`): each frame it handles input, updates the game if
  still playing, draws everything, and caps the speed at 60 FPS.
- **State** (`reset_game`): all game data lives in one dictionary (player,
  obstacles, score, spawn timer, game-over flag). Restarting just creates a
  fresh one.
- **Physics** (`update_physics`, `jump`): the player has a vertical velocity.
  Jumping sets it to a negative value (up); gravity is added every frame to
  pull it back down, and the ground stops it.
- **Obstacles** (`update_game`, `update_obstacles`): a timer spawns a red
  rectangle off the right edge every `SPAWN_INTERVAL` frames. Obstacles move
  left each frame and are removed once off-screen.
- **Collision** (`check_collision`): finds the point on the rectangle closest
  to the circle's centre; if that point is closer than the radius, they touch.
- **Score** (`draw_hud`): increases by 1 every frame survived.
- **Tuning**: all the numbers (gravity, jump strength, speed, sizes) are
  constants at the top of `main.py`.

## One undo

_TODO: describe one change you tried and reverted, and why._
