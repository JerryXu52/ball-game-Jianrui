# Wild West Runner

A pixel-art endless runner set in the Wild West, built with Python and Pygame.
Roll a terracotta ball across the desert, jump over cacti and tumbleweeds, and
see how far you can get as the pace keeps picking up.

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
- Cacti come in small, tall and double sizes. Tumbleweeds bounce as they roll.
- Your score goes up with the distance you cover, and the scroll speed rises
  the longer you survive.
- The high score is kept for the current session.

## Project structure

```
.
├── main.py           # The whole game
├── requirements.txt  # Python dependencies
└── README.md
```

`main.py` is split into small functions:

| Function | Purpose |
| --- | --- |
| `init_game()` | Starts Pygame and creates the window, clock and starting state |
| `reset_game()` | Resets score, player, speed and obstacles |
| `handle_input(player_rect, is_jumping, velocity_y)` | Reads the jump and fast-fall keys |
| `update_physics(player_rect, velocity_y)` | Applies gravity and landing |
| `spawn_and_update_obstacles(obstacles, scroll_speed)` | Moves, removes and spawns obstacles |
| `check_collision(player_rect, obstacles)` | Tests the ball's circle against each obstacle |
| `draw_western_background(screen, camera_offset)` | Draws sky, sun, mesas, dunes and ground with parallax |
| `draw_player(screen, player_rect, frame_count)` | Draws the rolling ball with shadow and dust |
| `draw_hud(screen, score, high_score)` | Draws the score and high score |
| `draw_game_over(screen, final_score)` | Draws the Game Over sign |
| `main()` | Runs the game loop |

## Tweaking the game

The constants at the top of `main.py` control the feel of the game:

- `BASE_SPEED`, `MAX_SPEED`, `SPEED_GAIN_PER_FRAME`: how fast it starts and how quickly it speeds up
- `GRAVITY`, `JUMP_VELOCITY`: jump height and hang time
- `OBSTACLE_TYPES`: obstacle sizes and how often each one appears
- `PIXEL_SCALE`: window size (the game draws at 320×180 and scales up by this factor)
- `COLOR_*`: the color palette

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`**: make sure the virtual
  environment is active, then run `pip install -r requirements.txt` again.
- **No Pygame wheel for a brand-new Python version**: try `pip install --upgrade pip`
  first, or use a Python version Pygame publishes wheels for.
