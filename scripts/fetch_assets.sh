#!/usr/bin/env bash
set -euo pipefail

# fetch_assets.sh
# Simple downloader for large media assets used by Monster-College.
# Replace the placeholder URLs with the actual links where you upload the files (GitHub Release / Drive / CDN).

# Ensure asset dirs exist
mkdir -p "menu&map/intro_video" "tetris_game"

# Example downloads — REPLACE these URLs with your uploaded file links
curl -L -o "menu&map/intro_video/intro01.mp4" "<INTRO01_URL>"
curl -L -o "menu&map/intro_video/intro02.mp4" "<INTRO02_URL>"
curl -L -o "menu&map/intro_video/intro03.mp4" "<INTRO03_URL>"
curl -L -o "menu&map/intro_video/intro04.mp4" "<INTRO04_URL>"

# Tetris SFX
curl -L -o "tetris_game/button_clicking_soun_#3-1776674335806.mp3" "<BUTTON_CLICK_URL>"
curl -L -o "tetris_game/tetris_line_clear_so_#4-1776674161372.mp3" "<LINE_CLEAR_URL>"
curl -L -o "tetris_game/tetris_puzzle_drop_s_#1-1776674215861.mp3" "<PUZZLE_DROP_URL>"

echo "Download complete."
