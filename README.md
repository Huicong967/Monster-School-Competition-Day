git fetch origin
git checkout main
git reset --hard origin/main
bash scripts/fetch_assets.sh# Monster School — Competition Day

Interactive branching video where the audience chooses the story.

## Quick Overview

Follow three students — Flying Tiger, Max, and Sir Doggegg—as they head into Competition Day. Viewers vote at key moments; each choice branches the video and changes relationships, challenges, and endings.

Assets note
-----------
This project does not include large media files (videos and audio) in the Git repository.

To get the media files required to run the game after cloning:

1. Make sure the shared Google Drive folder contains the required files (`intro01..04.mp4`, `takeabreak.mp4`, and Tetris SFX).
2. Run:

```bash
bash scripts/fetch_assets.sh
```

If you want to use a different Drive folder link, run:

```bash
bash scripts/fetch_assets.sh "YOUR_DRIVE_FOLDER_URL"
```

3. Then create and activate a Python virtualenv and install requirements:

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

A fullscreen, side-scrolling shooter mini game. You move Max, shoot flying wood, and try to reach a target score before time runs out.

### Quick start (Windows)

1. Install the only dependency:

```powershell
python -m pip install pygame
```

2. Run the game (from the repo root):

```powershell
python "Max_mini_game/Max Mini Game.py"
```

If you’re using this repo’s venv:

```powershell
& .venv/Scripts/python.exe "Max_mini_game/Max Mini Game.py"
```

### Required files (assets)

The game loads images from `Max_mini_game/Max_assets/`. If a required PNG is missing, it will stop and print the missing filename.

Required PNGs:
- Background / menu: `Max_minigame_bg.png`, `Whiteboard.png`, `Max_full.png`, `start_button.png`
- Player / shooting: `Max_game_ready_pose.png`, `Max_game_ready_shotpose.png`, `Laser_shot.png`
- Woods: `wood.png`, `star_wood.png`, `moon_wood.png`, `around_wood.png`
- End screen: `replay_button.png`, `home_button.png`

Optional files:
- SFX (used if present): `laser_gun.wav`, `Collect_wood.wav`, `Got_hit.wav`
- `invitation.png` (if present and you win, it’s shown on the end screen)

### Controls

- Menu: Click Start (or the whiteboard), or press `Enter`
- Move: `WASD` or Arrow keys
- Shoot: `Space`
- Quit immediately: `Esc`

End screen:
- Replay: play again
- Home: exit the mini game
- If `invitation.png` is shown (win screen), click or press `Enter` to continue

### Win + scoring (simple rules)

- Time limit: **60 seconds**
- Win condition: **Marks ≥ 30**
- Shoot an unhit wood (first hit): **+1** and it transforms
- Touch transformed wood: **+1** (collect)
- Touch unhit `wood.png`: **-1**
- Unhit `wood.png` leaving the left edge: **-1**

## Contribute

**Assets: Uploading & Auto-Download (English / 繁體中文 / 简体中文)**

English
- Upload large media files (intro videos and SFX) into a single Google Drive folder.
  - Suggested structure inside the Drive folder:
    - `menu&map/intro_video/intro01.mp4` ... `intro04.mp4`
    - `tetris_game/takeabreak.mp4`
    - `tetris_game/button_clicking_soun_#3-1776674335806.mp3`
    - `tetris_game/tetris_line_clear_so_#4-1776674161372.mp3`
    - `tetris_game/tetris_puzzle_drop_s_#1-1776674215861.mp3`
  - Set folder sharing to **Anyone with the link can view**.
- How it works: we provide `scripts/fetch_assets.sh` which uses `gdown` to download the whole Drive folder and place files into the correct local folders (`menu&map/intro_video` and `tetris_game`).
- Quick steps for classmates after cloning the repo:
  ```bash
  git clone <your-repo-url>
  cd Monster-College
  bash scripts/fetch_assets.sh               # downloads assets from the configured Drive folder
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python Monster_College.py
  ```
- If you prefer a different Drive folder, run:
  ```bash
  bash scripts/fetch_assets.sh "YOUR_DRIVE_FOLDER_URL"
  ```

繁體中文（說明）
- 將大型媒體檔（intro 影片、音效）上傳到同一個 Google 雲端硬碟資料夾中。
  - 建議在雲端資料夾中維持下列結構／檔名：
    - `menu&map/intro_video/intro01.mp4` ... `intro04.mp4`
    - `tetris_game/takeabreak.mp4`
    - `tetris_game/button_clicking_soun_#3-1776674335806.mp3`
    - `tetris_game/tetris_line_clear_so_#4-1776674161372.mp3`
    - `tetris_game/tetris_puzzle_drop_s_#1-1776674215861.mp3`
  - 權限請設定為「取得連結的任何人皆可檢視」。
- 原理：專案內的 `scripts/fetch_assets.sh` 會使用 `gdown` 下載整個 Drive 資料夾，並依檔名自動放到專案的 `menu&map/intro_video` 與 `tetris_game` 目錄。
- 給同學的快速指令：
  ```bash
  git clone <your-repo-url>
  cd Monster-College
  bash scripts/fetch_assets.sh               # 會自動下載並放好檔案
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python Monster_College.py
  ```
- 要使用不同的 Drive 連結：
  ```bash
  bash scripts/fetch_assets.sh "你的Drive資料夾連結"
  ```

简体中文（说明）
- 将大型媒体文件（intro 视频、音效）上传到同一个 Google Drive 文件夹。
  - 建议在云端文件夹中保持以下结构/文件名：
    - `menu&map/intro_video/intro01.mp4` ... `intro04.mp4`
    - `tetris_game/takeabreak.mp4`
    - `tetris_game/button_clicking_soun_#3-1776674335806.mp3`
    - `tetris_game/tetris_line_clear_so_#4-1776674161372.mp3`
    - `tetris_game/tetris_puzzle_drop_s_#1-1776674215861.mp3`
  - 权限请设置为“任何拥有链接的人均可查看”。
- 原理：项目里的 `scripts/fetch_assets.sh` 会用 `gdown` 下载整个 Drive 文件夹，并根据文件名自动放到项目的 `menu&map/intro_video` 和 `tetris_game` 目录。
- 给同学的快速命令：
  ```bash
  git clone <your-repo-url>
  cd Monster-College
  bash scripts/fetch_assets.sh               # 自动下载并放置文件
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  python Monster_College.py
  ```
- 如果想使用不同的 Drive 链接：
  ```bash
  bash scripts/fetch_assets.sh "你的Drive文件夹链接"
  ```

Troubleshooting / Notes
- If `bash scripts/fetch_assets.sh` fails because `gdown` is not installed, the script will try to install it into the project virtualenv. If that also fails, run manually:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install gdown
  bash scripts/fetch_assets.sh
  ```
- Make sure file names on Drive match the expected names in the script. If you rename files on Drive, update the script or provide a different Drive folder URL that contains the correctly named files.
- We intentionally do not keep large media files in Git history. This keeps the repo small and avoids push failures.

