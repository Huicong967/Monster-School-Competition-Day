# Monster School — Competition Day

Interactive branching video where the audience chooses the story.

## Quick Overview

Follow three students — Flying Tiger, Max, and Sir Doggegg—as they head into Competition Day. Viewers vote at key moments; each choice branches the video and changes relationships, challenges, and endings.

Assets note
-----------
This project does not include large media files (videos and audio) in the Git repository.

To get the media files required to run the game after cloning:

1. Upload the media files (intro videos and SFX) to a public location you control (GitHub Release, Google Drive, or other CDN) and copy the direct download URLs.
2. Edit `scripts/fetch_assets.sh` and replace the `<INTRO01_URL>` etc. placeholders with the real URLs.
3. Run:

```bash
bash scripts/fetch_assets.sh
```

4. Then create and activate a Python virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python Monster_College.py
```

If you prefer not to maintain external downloads, consider using Git LFS to track large files.

## How It Works (short)

- Scenes play as short clips with decision prompts.
- Choices load the next branch; branches may reconverge or lead to unique outcomes.

## Max Mini Game (Pygame)

A fullscreen, side-scrolling shooter mini game with a simple menu screen.

### What you need in the folder

- Game script: `Max_mini_game/Max Mini Game.py`
- Assets folder: `Max_mini_game/Max_assets/` with these PNGs:
  - Background / menu:
    - `Max_minigame_bg.png`
    - `Whiteboard.png`
    - `Max_full.png`
    - `start_button.png`
  - Player / shooting:
    - `Max_game_ready_pose.png`
    - `Max_game_ready_shotpose.png`
    - `Laser_shot.png`
  - Woods:
    - `wood.png`, `star_wood.png`, `moon_wood.png`, `around_wood.png`
  - End screen buttons:
    - `replay_button.png`
    - `home_button.png`

If any file is missing, the game will stop and tell you which image is missing.

### Install (one time)

```powershell
python -m pip install pygame
```

If you use this repo’s venv, you can also do:

```powershell
& .venv/Scripts/python.exe -m pip install pygame
```

### Run

From the repository root (Windows PowerShell):

```powershell
& .venv/Scripts/python.exe "Max_mini_game/Max Mini Game.py"
```

Or with your system Python:

```powershell
python "Max_mini_game/Max Mini Game.py"
```

### Controls

- Menu:
  - Click `start_button.png` (or click the whiteboard) to start
  - `Enter`: start
  - `Esc`: quit
- In-game:
  - `W` / `S` or `↑` / `↓`: move up / down
  - `A` / `D` or `←` / `→`: move left / right
  - `Space`: shoot
  - `Esc`: quit
- End screen:
  - Click Replay to play again
  - Click Home to exit to desktop

### Scoring (easy rules)

- You play for **60 seconds**.
- You win if your marks are **30 or more** ($\text{Marks} \ge 30$).
- Laser hits:
  - When your laser hits an **unhit** wood for the first time: **+1 mark** and it transforms.
- Touching wood with Max:
  - Touch a **hit / transformed** wood: **+1 mark** (collect it).
  - Touch an **unhit** `wood.png`: **-1 mark**.
- Missed wood:
  - If an **unhit** `wood.png` flies off the **left edge**: **-1 mark**.

## Contribute

