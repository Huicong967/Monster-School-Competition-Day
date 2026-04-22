import os
import pygame
import subprocess
import sys
import importlib.util
import numpy as np
import tempfile
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips


# Initialize Pygame
pygame.init()

# Set up the display in full screen mode (copied from Max Mini Game.py)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Main Menu")

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

ASSET_DIR = os.path.join(os.path.dirname(__file__), "menu&map")
BG_PATH = os.path.join(ASSET_DIR, "cloud.png")

if not os.path.exists(BG_PATH):
    raise FileNotFoundError(f"Missing background image: {BG_PATH}. Put cloud.png in the menu&map folder.")

_bg_raw = pygame.image.load(BG_PATH).convert()
_bg_w, _bg_h = _bg_raw.get_size()

# Scale background to fill the screen while preserving aspect ratio
scale = max(SCREEN_WIDTH / _bg_w, SCREEN_HEIGHT / _bg_h)
_bg = pygame.transform.smoothscale(_bg_raw, (int(_bg_w * scale), int(_bg_h * scale)))

# Load menu assets
LOGO_PATH = os.path.join(ASSET_DIR, "logo.png")
START_BTN_PATH = os.path.join(ASSET_DIR, "start_button.png")
INTRO_VIDEO_DIR = os.path.join(ASSET_DIR, "intro_video")
INTRO_VIDEO_NAMES = ["intro01.mp4", "intro02.mp4", "intro03.mp4", "intro04.mp4"]

for _p in (LOGO_PATH, START_BTN_PATH):
    if not os.path.exists(_p):
        raise FileNotFoundError(f"Missing menu asset: {_p}.")

_logo_raw = pygame.image.load(LOGO_PATH).convert_alpha()
_start_raw = pygame.image.load(START_BTN_PATH).convert_alpha()

# Scale logo + buttons relative to screen height
# Make the logo larger and the buttons larger as requested
LOGO_SCALE_MULT = 3.5
BTN_SCALE_MULT = 1.8
LOGO_TARGET_H = int(SCREEN_HEIGHT * 0.18 * LOGO_SCALE_MULT)
BTN_TARGET_H = int(SCREEN_HEIGHT * 0.12 * BTN_SCALE_MULT)

def _scale_to_height(img: pygame.Surface, target_h: int) -> pygame.Surface:
    target_h = max(1, int(target_h))
    w, h = img.get_size()
    if h <= 0:
        return img
    scale = target_h / h
    return pygame.transform.smoothscale(img, (max(1, int(w * scale)), target_h))

_logo_img = _scale_to_height(_logo_raw, LOGO_TARGET_H)
_start_img = _scale_to_height(_start_raw, BTN_TARGET_H)


def main() -> None:
    clock = pygame.time.Clock()
    running = True
    pressed_button = None

    # Pre-render simple instruction text
    font = pygame.font.Font(None, 48)
    instr_s = font.render("Press ENTER to play — ESC to quit", True, (255, 255, 255))

    while running:
        dt = clock.tick(60) / 1000.0

        # Compute centered layout for logo + buttons before handling events
        spacing_top = 10
        logo_h = _logo_img.get_height()
        start_h = _start_img.get_height()
        total_h = logo_h + spacing_top + start_h
        # Center the group vertically (moved higher than previous lower-offset layout)
        top_y = int((SCREEN_HEIGHT - total_h) / 2)

        bg_x = (SCREEN_WIDTH - _bg.get_width()) // 2
        bg_y = (SCREEN_HEIGHT - _bg.get_height()) // 2

        logo_rect = _logo_img.get_rect(midtop=(SCREEN_WIDTH // 2, top_y))
        start_rect = _start_img.get_rect(midtop=(SCREEN_WIDTH // 2, logo_rect.bottom + spacing_top))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Play video when Enter pressed
                            play_video()
                            show_map()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # record which button was pressed
                if start_rect.collidepoint(event.pos):
                    pressed_button = "start"
                else:
                    pressed_button = None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # trigger click if press started and ended on same button
                if pressed_button == "start" and start_rect.collidepoint(event.pos):
                    # Play the video when Start is clicked
                    play_video()
                    show_map()
                pressed_button = None

        # Draw background centered
        screen.blit(_bg, (bg_x, bg_y))

        # Draw logo and buttons (centered group)
        screen.blit(_logo_img, logo_rect)

        mx, my = pygame.mouse.get_pos()

        # Simple hover/press visual: slight scale but no glow
        def _maybe_draw_button(img: pygame.Surface, rect: pygame.Rect, hovered: bool, pressed: bool) -> None:
            if pressed:
                scale_mult = 0.96
            elif hovered:
                scale_mult = 1.06
            else:
                scale_mult = 1.0
            w = max(1, int(img.get_width() * scale_mult))
            h = max(1, int(img.get_height() * scale_mult))
            scaled = pygame.transform.smoothscale(img, (w, h))
            srect = scaled.get_rect(center=rect.center)
            screen.blit(scaled, srect)

        hovered = start_rect.collidepoint((mx, my))
        pressed = pressed_button == "start" and pygame.mouse.get_pressed()[0]
        _maybe_draw_button(_start_img, start_rect, hovered, pressed)

        # Draw instructions at bottom center
        instr_rect = instr_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        # Draw a subtle shadow for readability
        shadow = font.render("Press ENTER to play — ESC to quit", True, (0, 0, 0))
        shadow_rect = instr_rect.copy()
        shadow_rect.move_ip(2, 2)
        screen.blit(shadow, shadow_rect)
        screen.blit(instr_s, instr_rect)

        pygame.display.flip()

    pygame.quit()


def play_video_in_pygame(path: str) -> str:
    """Play the given video file inside the existing Pygame `screen`.

    This uses MoviePy to decode frames and blits them into the Pygame surface.
    Audio is ignored to keep implementation simple and reliable across platforms.
    """
    clip = VideoFileClip(path)
    fps = clip.fps if clip.fps and clip.fps > 0 else 30
    clock = pygame.time.Clock()

    # Prepare optional on-screen instruction (styled like the start screen)
    font = pygame.font.Font(None, 48)
    base = os.path.basename(path).lower()
    skip_allowed = base.startswith("intro")
    instr_s = None
    shadow = None
    instr_rect = None
    shadow_rect = None
    if skip_allowed:
        instr_text = "Use TAB to skip video"
        instr_s = font.render(instr_text, True, (255, 255, 255))
        shadow = font.render(instr_text, True, (0, 0, 0))
        instr_rect = instr_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        shadow_rect = instr_rect.copy()
        shadow_rect.move_ip(2, 2)

    audio_temp = None
    try:
        # extract and play audio if present
        try:
            if hasattr(clip, "audio") and clip.audio is not None:
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp_name = tmp.name
                tmp.close()
                clip.audio.write_audiofile(tmp_name, logger=None)
                audio_temp = tmp_name
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    pygame.mixer.music.load(audio_temp)
                    pygame.mixer.music.play()
                except Exception as e:
                    print("Warning: failed to play audio via pygame.mixer:", e)
        except Exception as e:
            print("Warning: failed to extract/play audio:", e)

        for frame in clip.iter_frames(fps=fps, dtype="uint8"):
            # handle quit / escape / tab events while playing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                    except Exception:
                        pass
                    clip.close()
                    if audio_temp is not None:
                        try:
                            os.remove(audio_temp)
                        except Exception:
                            pass
                    return "stopped"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        try:
                            if pygame.mixer.get_init():
                                pygame.mixer.music.stop()
                        except Exception:
                            pass
                        clip.close()
                        if audio_temp is not None:
                            try:
                                os.remove(audio_temp)
                            except Exception:
                                pass
                        return "stopped"
                    if event.key == pygame.K_TAB and skip_allowed:
                        try:
                            if pygame.mixer.get_init():
                                pygame.mixer.music.stop()
                        except Exception:
                            pass
                        clip.close()
                        if audio_temp is not None:
                            try:
                                os.remove(audio_temp)
                            except Exception:
                                pass
                        return "skipped"

            # frame is HxWx3 RGB
            h, w = frame.shape[0], frame.shape[1]
            # create a surface from the frame bytes
            surf = pygame.image.frombuffer(frame.tobytes(), (w, h), "RGB")
            # scale to fullscreen while preserving aspect
            surf = pygame.transform.smoothscale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(surf, (0, 0))

            # Draw the optional instruction over the video
            if instr_s is not None:
                screen.blit(shadow, shadow_rect)
                screen.blit(instr_s, instr_rect)

            pygame.display.flip()
            clock.tick(fps)
        return "done"
    finally:
        try:
            clip.close()
        except Exception:
            pass
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        if audio_temp is not None:
            try:
                os.remove(audio_temp)
            except Exception:
                pass


def play_video() -> None:
    """Play intro01-04 as one continuous intro sequence.

    TAB skips the entire sequence.
    """
    intro_paths = [os.path.join(INTRO_VIDEO_DIR, name) for name in INTRO_VIDEO_NAMES]
    existing_paths = [p for p in intro_paths if os.path.exists(p)]

    if not existing_paths:
        print(f"No intro videos found in: {INTRO_VIDEO_DIR}")
        return

    clips = []
    combined = None
    audio_temp = None
    try:
        for path in existing_paths:
            clips.append(VideoFileClip(path))

        # Concatenate into one stream so intro01-04 behaves like one continuous video.
        combined = concatenate_videoclips(clips, method="chain")
        fps = combined.fps if combined.fps and combined.fps > 0 else 30
        clock = pygame.time.Clock()

        # Play one continuous audio track for the combined intro.
        try:
            if hasattr(combined, "audio") and combined.audio is not None:
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp_name = tmp.name
                tmp.close()
                combined.audio.write_audiofile(tmp_name, logger=None)
                audio_temp = tmp_name
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(audio_temp)
                pygame.mixer.music.play()
        except Exception as e:
            print("Warning: failed to extract/play intro audio:", e)

        # One shared skip hint for the entire intro block.
        font = pygame.font.Font(None, 48)
        instr_text = "Use TAB to skip intro"
        instr_s = font.render(instr_text, True, (255, 255, 255))
        shadow = font.render(instr_text, True, (0, 0, 0))
        instr_rect = instr_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        shadow_rect = instr_rect.copy()
        shadow_rect.move_ip(2, 2)

        for frame in combined.iter_frames(fps=fps, dtype="uint8"):
            stop_sequence = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_sequence = True
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                        stop_sequence = True
            if stop_sequence:
                break

            h, w = frame.shape[0], frame.shape[1]
            surf = pygame.image.frombuffer(frame.tobytes(), (w, h), "RGB")
            surf = pygame.transform.smoothscale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(surf, (0, 0))
            screen.blit(shadow, shadow_rect)
            screen.blit(instr_s, instr_rect)
            pygame.display.flip()
            clock.tick(fps)
    except Exception as e:
        print("Intro sequence playback failed:", e)
        # Fallback: open first available clip with system player.
        first_path = existing_paths[0]
        try:
            print(f"Falling back to system player for: {first_path}")
            sys.stdout.flush()
            if sys.platform == "darwin":
                subprocess.Popen(["open", first_path])
            elif sys.platform.startswith("win"):
                os.startfile(first_path)
            else:
                subprocess.Popen(["xdg-open", first_path])
        except Exception as fb_err:
            print("Fallback open failed:", fb_err)
            print("Unable to open intro videos. Check files and system defaults.")
    finally:
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass
        if audio_temp is not None:
            try:
                os.remove(audio_temp)
            except Exception:
                pass
        if combined is not None:
            try:
                combined.close()
            except Exception:
                pass
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass


def show_map() -> None:
    """Display the map image fullscreen and wait until the user quits or presses BACKSPACE to return."""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT
    MAP_PATH = os.path.join(ASSET_DIR, "map.png")
    if not os.path.exists(MAP_PATH):
        print(f"Missing map image: {MAP_PATH}. Put map.png in the menu&map folder.")
        return

    try:
        map_raw = pygame.image.load(MAP_PATH).convert()
    except Exception as e:
        print("Failed to load map image:", e)
        return

    mw, mh = map_raw.get_size()
    scale = max(SCREEN_WIDTH / mw, SCREEN_HEIGHT / mh)
    map_surf = pygame.transform.smoothscale(map_raw, (int(mw * scale), int(mh * scale)))
    map_x = (SCREEN_WIDTH - map_surf.get_width()) // 2
    map_y = (SCREEN_HEIGHT - map_surf.get_height()) // 2

    clock = pygame.time.Clock()
    showing = True
    # Load button assets for map screen
    def _load_btn(n):
        p = os.path.join(ASSET_DIR, n)
        return pygame.image.load(p).convert_alpha() if os.path.exists(p) else None

    robot_normal = _load_btn("robot01.png")
    robot_hover = _load_btn("robot02.png")
    tiger_normal = _load_btn("tigerlogo1.png")
    tiger_hover = _load_btn("tigerlogo2.png")
    dog_normal = _load_btn("doggegg001.png")
    dog_hover = _load_btn("doggegg002.png")

    # Scale buttons relative to screen height (made larger per request)
    BTN_TARGET_H = int(SCREEN_HEIGHT * 0.18)
    def _scale_opt(img):
        if img is None:
            return None
        return _scale_to_height(img, BTN_TARGET_H)

    # Make robot button a bit larger than the others for emphasis
    robot_img = _scale_to_height(robot_normal, int(BTN_TARGET_H * 1.35)) if robot_normal is not None else None
    robot_img_hov = _scale_to_height(robot_hover, int(BTN_TARGET_H * 1.35)) if robot_hover is not None else None
    tiger_img = _scale_opt(tiger_normal)
    tiger_img_hov = _scale_opt(tiger_hover)
    dog_img = _scale_opt(dog_normal)
    dog_img_hov = _scale_opt(dog_hover)

    def _to_disabled(img):
        if img is None:
            return None
        disabled = img.copy()
        # Dim and desaturate feel for a locked button state.
        disabled.fill((120, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return disabled

    dog_img_locked = _to_disabled(dog_img)
    dog_img_hov_locked = _to_disabled(dog_img_hov)

    # Compute button positions (left, right, top-center for dog egg)
    left_pos = (int(SCREEN_WIDTH * 0.18), int(SCREEN_HEIGHT * 0.5))
    right_pos = (int(SCREEN_WIDTH * 0.82), int(SCREEN_HEIGHT * 0.5))
    top_pos = (int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.22))

    # Build rects if images exist
    robot_rect = robot_img.get_rect(center=left_pos) if robot_img is not None else None
    tiger_rect = tiger_img.get_rect(center=right_pos) if tiger_img is not None else None
    dog_rect = dog_img.get_rect(center=top_pos) if dog_img is not None else None

    pressed_btn = None
    max_won = False
    tiger_won = False
    # Prepare bottom instruction like the start screen
    font = pygame.font.Font(None, 48)
    esc_text = "ESC to close game"
    instr_s = font.render(esc_text, True, (255, 255, 255))
    shadow = font.render(esc_text, True, (0, 0, 0))
    instr_rect = instr_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
    shadow_rect = instr_rect.copy()
    shadow_rect.move_ip(2, 2)
    lock_font = pygame.font.Font(None, 42)

    while showing:
        launch_mini_game = False
        launch_tiger_game = False
        launch_dog_game = False

        mx, my = pygame.mouse.get_pos()
        hovered_robot = robot_rect.collidepoint((mx, my)) if robot_rect is not None else False
        hovered_tiger = tiger_rect.collidepoint((mx, my)) if tiger_rect is not None else False
        hovered_dog = dog_rect.collidepoint((mx, my)) if dog_rect is not None else False
        dog_unlocked = max_won and tiger_won

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_BACKSPACE:
                    # Return to main menu loop
                    showing = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_robot:
                    pressed_btn = "robot"
                elif hovered_tiger:
                    pressed_btn = "tiger"
                elif hovered_dog:
                    pressed_btn = "dog"
                else:
                    pressed_btn = None
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if pressed_btn == "robot" and hovered_robot:
                    # Launch Max Mini Game (smooth: keep this frame on-screen; don't tear down the display).
                    launch_mini_game = True
                elif pressed_btn == "tiger" and hovered_tiger:
                    # Launch Tiger Game with the same embedded-jump behavior as Max Mini Game.
                    launch_tiger_game = True
                elif pressed_btn == "dog" and hovered_dog:
                    # Lock Sir Doggegg until both Max and Tiger are won.
                    if dog_unlocked:
                        launch_dog_game = True
                    else:
                        print("Sir Doggegg is locked. Win Max and Tiger first.")
                pressed_btn = None

        # Draw map
        screen.blit(map_surf, (map_x, map_y))

        # Draw buttons with hover/pressed visuals
        def _draw_btn(normal, hov, rect, hovered, pressed):
            if rect is None or normal is None:
                return
            img = hov if (hovered or pressed) and hov is not None else normal
            screen.blit(img, img.get_rect(center=rect.center))

        _draw_btn(robot_img, robot_img_hov, robot_rect, hovered_robot, pressed_btn == "robot")
        _draw_btn(tiger_img, tiger_img_hov, tiger_rect, hovered_tiger, pressed_btn == "tiger")
        if dog_unlocked:
            _draw_btn(dog_img, dog_img_hov, dog_rect, hovered_dog, pressed_btn == "dog")
        else:
            _draw_btn(dog_img_locked, dog_img_hov_locked, dog_rect, hovered_dog, pressed_btn == "dog")

            lock_msg = "Finish Max and Tiger first to unlock Sir Doggegg"
            lock_s = lock_font.render(lock_msg, True, (235, 235, 235))
            lock_shadow = lock_font.render(lock_msg, True, (0, 0, 0))
            if dog_rect is not None:
                lock_rect = lock_s.get_rect(center=(SCREEN_WIDTH // 2, dog_rect.bottom + 28))
            else:
                lock_rect = lock_s.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.30)))
            lock_shadow_rect = lock_rect.copy()
            lock_shadow_rect.move_ip(2, 2)
            screen.blit(lock_shadow, lock_shadow_rect)
            screen.blit(lock_s, lock_rect)

        # Draw bottom instruction
        screen.blit(shadow, shadow_rect)
        screen.blit(instr_s, instr_rect)
        pygame.display.flip()
        clock.tick(30)

        if launch_mini_game:
            mini_path = os.path.join(os.path.dirname(__file__), "Max_mini_game", "Max Mini Game.py")
            if not os.path.exists(mini_path):
                print("Max Mini Game script not found at", mini_path)
                continue

            # Run the mini game inside the same Pygame window (no subprocess).
            try:
                spec = importlib.util.spec_from_file_location("max_mini_game", mini_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError("Unable to load Max Mini Game module")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                if hasattr(mod, "run"):
                    max_result = mod.run(screen)
                elif hasattr(mod, "main"):
                    max_result = mod.main()
                else:
                    raise RuntimeError("Max Mini Game does not define run() or main()")

                max_won = bool(max_result)

                # Clear any queued events from the mini game so the map doesn't instantly react.
                try:
                    pygame.event.clear()
                except Exception:
                    pass
            except Exception as e:
                print("Failed to run Max Mini Game:", e)

        if launch_tiger_game:
            tiger_path = os.path.join(os.path.dirname(__file__), "tiger-game", "main.py")
            if not os.path.exists(tiger_path):
                print("Tiger game script not found at", tiger_path)
                continue

            # Run tiger game inside the same Pygame window (no subprocess).
            try:
                spec = importlib.util.spec_from_file_location("tiger_game", tiger_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError("Unable to load Tiger Game module")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                if hasattr(mod, "run"):
                    tiger_result = mod.run(screen)
                elif hasattr(mod, "main"):
                    mod.main(screen)
                    tiger_result = None
                else:
                    raise RuntimeError("Tiger Game does not define run() or main()")

                tiger_won = bool(tiger_result)

                # Clear any queued events from the tiger game so the map doesn't instantly react.
                try:
                    pygame.event.clear()
                except Exception:
                    pass
            except Exception as e:
                print("Failed to run Tiger Game:", e)

        if launch_dog_game:
            base_dir = os.path.join(os.path.dirname(__file__), "sir_doggegg_nap_break")
            dog_candidates = [
                os.path.join(base_dir, "sir_doggegg_nap_break.py"),
                os.path.join(base_dir, "tetris_game.py"),
            ]
            dog_path = next((p for p in dog_candidates if os.path.exists(p)), None)
            if dog_path is None:
                print("Sir Doggegg game script not found. Checked:", ", ".join(dog_candidates))
                continue

            try:
                spec = importlib.util.spec_from_file_location("sir_doggegg_nap_break_game", dog_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError("Unable to load Sir Doggegg module")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                if hasattr(mod, "run"):
                    mod.run(screen)
                elif hasattr(mod, "main"):
                    mod.main(screen)
                else:
                    raise RuntimeError("Sir Doggegg game does not define run() or main()")

                try:
                    pygame.event.clear()
                except Exception:
                    pass
            except Exception as e:
                print("Failed to run Sir Doggegg game:", e)


if __name__ == "__main__":
    main()
