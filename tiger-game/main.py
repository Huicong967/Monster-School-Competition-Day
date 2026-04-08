import os
import sys
import random
import math
import pygame
from PIL import Image
import shutil
from PIL import Image

# Simple pygame game:
import shutil

# Simple pygame game:
# - Load background PNG whose filename contains '背景'
# - Load player GIF (animated) and animate frames
# - Load ball PNGs (filename contains 'ball' or '球') and spawn randomly
# - Background scrolls left in an infinite loop
# - Player GIF moves steadily to the right; player controls vertical movement with UP/DOWN
# - On collision with a ball: play sound and score++ (displayed top-left)

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_SPEED = 2           # background scrolling speed (pixels/frame)
PLAYER_SPEED_X = 1.5   # player's automatic rightward speed (pixels/frame)
PLAYER_SPEED_Y = 4     # player's up/down speed when pressing keys
BALL_SPAWN_INTERVAL = 900  # milliseconds (shorter so balls appear more often)
BALL_SPEED = BG_SPEED  # balls move left at background speed so they appear to approach
TARGET_SCORE = 30
PLAYER_SCALE_FACTOR = math.sqrt(0.1 / 6.0)  # base scale used previously
# reduce area to 2/3 of current displayed area: multiply linear scale by sqrt(2/3)
PLAYER_SCALE_FACTOR = PLAYER_SCALE_FACTOR * math.sqrt(2.0/3.0)
# increase collision shrink so touch must be closer (more negative inflate)
COLLISION_MARGIN = 12  # pixels to shrink collision rect on each side to account for transparent padding

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

def organize_assets():
    """Move game asset files from the project folder into the assets/ directory.
    Files moved: background PNGs containing '背景', any GIF, ball PNGs (containing 'ball' or '球'), and common audio files.
    This uses shutil.move so the original file is removed from its source location.
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    moved = []
    for fn in os.listdir(BASE_DIR):
        fpath = os.path.join(BASE_DIR, fn)
        # skip directories and the assets folder itself
        if not os.path.isfile(fpath) or os.path.abspath(os.path.dirname(fpath)) == os.path.abspath(ASSETS_DIR):
            continue
        low = fn.lower()
        should_move = False
        if '背景' in fn and low.endswith('.png'):
            should_move = True
        elif low.endswith('.gif'):
            should_move = True
        elif ("ball" in low or '球' in fn) and low.endswith('.png'):
            should_move = True
        elif low.endswith(('.wav', '.ogg', '.mp3')):
            should_move = True
        if should_move:
            try:
                target = os.path.join(ASSETS_DIR, fn)
                # if a file with same name exists in assets, avoid overwrite by renaming
                if os.path.exists(target):
                    base, ext = os.path.splitext(fn)
                    i = 1
                    while True:
                        new_name = f"{base}_{i}{ext}"
                        new_target = os.path.join(ASSETS_DIR, new_name)
                        if not os.path.exists(new_target):
                            target = new_target
                            break
                        i += 1
                shutil.move(fpath, target)
                moved.append(fn)
            except Exception as e:
                print('Failed to move', fpath, e)
    if moved:
        print('Moved files to assets:', moved)
    else:
        print('No files moved.')

# Helpers
def load_background():
    if not os.path.isdir(ASSETS_DIR):
        print('Assets folder not found:', ASSETS_DIR)
        return None
    for fn in os.listdir(ASSETS_DIR):
        if '背景' in fn and fn.lower().endswith('.png'):
            path = os.path.join(ASSETS_DIR, fn)
            try:
                img = pygame.image.load(path).convert_alpha()
                return img
            except Exception as e:
                print('Failed to load background', path, e)
    print('No background PNG with "背景" in filename found in assets.')
    return None

def pil_image_to_surface(pil_img):
    mode = pil_img.mode
    size = pil_img.size
    data = pil_img.tobytes()
    return pygame.image.fromstring(data, size, mode).convert_alpha()

def load_gif_frames(path):
    frames = []
    try:
        img = Image.open(path)
    except Exception as e:
        print('Failed to open GIF', path, e)
        return frames
    try:
        n = getattr(img, 'n_frames', 1)
        for frame_index in range(0, n):
            img.seek(frame_index)
            frame = img.convert('RGBA')
            surf = pil_image_to_surface(frame)
            # 缩小到原面积的四分之一 -> 线性尺寸缩小 50%
            w, h = surf.get_width(), surf.get_height()
            new_w = max(1, int(w * PLAYER_SCALE_FACTOR))
            new_h = max(1, int(h * PLAYER_SCALE_FACTOR))
            try:
                surf = pygame.transform.smoothscale(surf, (new_w, new_h))
            except Exception:
                surf = pygame.transform.scale(surf, (new_w, new_h))
            frames.append(surf)
    except EOFError:
        pass
    return frames

def find_player_gif():
    if not os.path.isdir(ASSETS_DIR):
        return None
    for fn in os.listdir(ASSETS_DIR):
        if fn.lower().endswith('.gif'):
            return os.path.join(ASSETS_DIR, fn)
    print('No GIF found in assets for player.')
    return None

def find_ball_images():
    out = []
    if not os.path.isdir(ASSETS_DIR):
        return out
    for fn in os.listdir(ASSETS_DIR):
        low = fn.lower()
        if ("ball" in low or '球' in fn) and low.endswith('.png'):
            out.append(os.path.join(ASSETS_DIR, fn))
    return out

def find_sound():
    if not os.path.isdir(ASSETS_DIR):
        return None
    for fn in os.listdir(ASSETS_DIR):
        if fn.lower().endswith(('.wav', '.ogg', '.mp3')) and ('hit' in fn.lower() or '碰' in fn or 'sound' in fn.lower() or 'audio' in fn.lower()):
            return os.path.join(ASSETS_DIR, fn)
    # fallback: any wav/ogg
    for fn in os.listdir(ASSETS_DIR):
        if fn.lower().endswith(('.wav', '.ogg', '.mp3')):
            return os.path.join(ASSETS_DIR, fn)
    return None

def find_victory_sound():
    if not os.path.isdir(ASSETS_DIR):
        return None
    for fn in os.listdir(ASSETS_DIR):
        low = fn.lower()
        if low.endswith(('.wav', '.ogg', '.mp3')) and ('win' in low or 'victory' in low or '胜利' in fn or 'vict' in low):
            return os.path.join(ASSETS_DIR, fn)
    return find_sound()

def find_ding_sound():
    if not os.path.isdir(ASSETS_DIR):
        return None
    for fn in os.listdir(ASSETS_DIR):
        low = fn.lower()
        if low.endswith(('.wav', '.ogg', '.mp3')) and ('ding' in low or '叮' in fn or 'ding' in low):
            return os.path.join(ASSETS_DIR, fn)
    return None

def find_end_image():
    if not os.path.isdir(ASSETS_DIR):
        return None
    for fn in os.listdir(ASSETS_DIR):
        low = fn.lower()
        if low.endswith('.png') and ('end' in low or '结束' in fn or 'gameover' in low or 'over' in low):
            return os.path.join(ASSETS_DIR, fn)
    return None

def find_player_png_frames():
    """Return list of up to two player PNG paths named like 'tiger*' in assets."""
    out = []
    if not os.path.isdir(ASSETS_DIR):
        return out
    cand = []
    for fn in os.listdir(ASSETS_DIR):
        if fn.lower().endswith('.png') and 'tiger' in fn.lower():
            cand.append(os.path.join(ASSETS_DIR, fn))
    cand.sort()
    # take first two if available
    return cand[:2]

# Game objects
class Player:
    def __init__(self, frames, x=50, y=SCREEN_HEIGHT//2):
        self.frames = frames or []
        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_interval = 100  # ms per frame
        self.x = x
        self.y = y
        self.w = frames[0].get_width() if frames else 50
        self.h = frames[0].get_height() if frames else 50

    def update(self, dt, up=False, down=False):
        # animate
        self.anim_timer += dt
        if self.anim_timer >= self.anim_interval:
            self.anim_timer -= self.anim_interval
            self.frame_idx = (self.frame_idx + 1) % max(1, len(self.frames))
        # player stays horizontally fixed (visual movement comes from background/balls)
        # move up/down by input; accept boolean flags for robustness
        if up:
            self.y -= PLAYER_SPEED_Y
        if down:
            self.y += PLAYER_SPEED_Y
        # clamp
        self.y = max(0, min(SCREEN_HEIGHT - self.h, self.y))

    def draw(self, surface, offset_x=0):
        if self.frames:
            surf = self.frames[self.frame_idx]
            surface.blit(surf, (self.x + offset_x, self.y))
        else:
            pygame.draw.rect(surface, (255,0,0), (self.x+offset_x, self.y, 50, 50))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Ball:
    def __init__(self, surf, x, y):
        self.surf = surf
        self.x = x
        self.y = y
        self.w = surf.get_width()
        self.h = surf.get_height()

    def update(self, dt):
        self.x -= BALL_SPEED

    def draw(self, surface, offset_x=0):
        surface.blit(self.surf, (self.x + offset_x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

# Main
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flying Tiger Game')
    clock = pygame.time.Clock()

    # organize assets into assets/ directory
    organize_assets()

    # load assets
    bg_img = load_background()
    # Prefer tiger PNG frames (tiger1/tiger2) for transparent player; fallback to GIF
    player_frames = []
    png_paths = find_player_png_frames()
    if png_paths:
        for p in png_paths:
            try:
                img = pygame.image.load(p).convert_alpha()
                # scale player frames so area becomes ~1/10, preserving aspect
                bw, bh = img.get_width(), img.get_height()
                new_w = max(1, int(bw * PLAYER_SCALE_FACTOR))
                new_h = max(1, int(bh * PLAYER_SCALE_FACTOR))
                try:
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                except Exception:
                    img = pygame.transform.scale(img, (new_w, new_h))
                player_frames.append(img)
            except Exception as e:
                print('Failed to load player png', p, e)
    else:
        player_gif_path = find_player_gif()
        if player_gif_path:
            player_frames = load_gif_frames(player_gif_path)
    ball_imgs = []
    for p in find_ball_images():
        try:
            img = pygame.image.load(p).convert_alpha()
            # 如果球图片过大，按比例缩小以便在屏幕上可见
            max_dim = 80
            bw, bh = img.get_width(), img.get_height()
            if bw > max_dim or bh > max_dim:
                scale = min(max_dim / bw, max_dim / bh)
                new_size = (max(1, int(bw * scale)), max(1, int(bh * scale)))
                try:
                    img = pygame.transform.smoothscale(img, new_size)
                except Exception:
                    img = pygame.transform.scale(img, new_size)
            ball_imgs.append(img)
        except Exception as e:
            print('Failed to load ball image', p, e)
        hit_sound_path = find_sound()
        hit_sound = None
        if hit_sound_path:
            try:
                hit_sound = pygame.mixer.Sound(hit_sound_path)
            except Exception as e:
                print('Failed to load sound', hit_sound_path, e)
        # prefer a ding sound for scoring feedback
        ding_sound_path = find_ding_sound()
        ding_sound = None
        if ding_sound_path:
            try:
                ding_sound = pygame.mixer.Sound(ding_sound_path)
            except Exception as e:
                print('Failed to load ding sound', ding_sound_path, e)
    # prefer a ding sound for per-ball scoring if available
    ding_sound_path = find_ding_sound()
    ding_sound = None
    if ding_sound_path:
        try:
            ding_sound = pygame.mixer.Sound(ding_sound_path)
        except Exception as e:
            print('Failed to load ding sound', ding_sound_path, e)
    # set reasonable volumes
    try:
        if ding_sound:
            ding_sound.set_volume(0.6)
        if hit_sound:
            hit_sound.set_volume(0.6)
    except Exception:
        pass
    victory_sound_path = find_victory_sound()
    victory_sound = None
    if victory_sound_path:
        try:
            victory_sound = pygame.mixer.Sound(victory_sound_path)
            try:
                victory_sound.set_volume(0.9)
            except Exception:
                pass
        except Exception as e:
            print('Failed to load victory sound', victory_sound_path, e)

    # background tiling variables
    if bg_img:
        bg_w = bg_img.get_width()
        bg_h = bg_img.get_height()
        scale = max(SCREEN_WIDTH / bg_w, SCREEN_HEIGHT / bg_h)
        if scale != 1:
            bg_img = pygame.transform.smoothscale(bg_img, (int(bg_w*scale), int(bg_h*scale)))
            bg_w = bg_img.get_width()
            bg_h = bg_img.get_height()
    else:
        # fallback solid color
        bg_w = SCREEN_WIDTH
        bg_h = SCREEN_HEIGHT

    bg_offset = 0

    # create player
    if player_frames:
        pf_w = player_frames[0].get_width()
        start_x = SCREEN_WIDTH // 2 - pf_w // 2
        player = Player(player_frames, x=start_x, y=SCREEN_HEIGHT//2)
    else:
        # create a red square if no GIF
        surf = pygame.Surface((50,50), pygame.SRCALPHA)
        surf.fill((255,0,0))
        start_x = SCREEN_WIDTH // 2 - 50 // 2
        player = Player([surf], x=start_x, y=SCREEN_HEIGHT//2)

    # balls list
    balls = []
    # 让界面一开始就有一些球，避免右侧空白或等待过久
    if ball_imgs:
        for i in range(4):
            surf = random.choice(ball_imgs)
            # 不要在玩家左侧生成球，确保初始球位于玩家右侧或屏幕右半区
            player_right_x = player.x + player.w
            min_x = max(player_right_x + 20, SCREEN_WIDTH // 2)
            max_x = max(min_x, SCREEN_WIDTH - surf.get_width())
            if min_x <= max_x:
                x = random.randint(min_x, max_x)
            else:
                x = SCREEN_WIDTH + random.randint(50, 400)
            max_y = max(0, SCREEN_HEIGHT - surf.get_height())
            y = random.randint(0, max_y)
            balls.append(Ball(surf, x, y))
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, BALL_SPAWN_INTERVAL)

    score = 0
    font = pygame.font.Font(None, 36)
    won = False
    end_surface = None
    end_start = None

    running = True
    move_up = False
    move_down = False
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_EVENT:
                # spawn a ball at random y and x beyond right edge
                if ball_imgs:
                    surf = random.choice(ball_imgs)
                    x = SCREEN_WIDTH + random.randint(50, 400)
                    max_y = max(0, SCREEN_HEIGHT - surf.get_height())
                    y = random.randint(0, max_y)
                    balls.append(Ball(surf, x, y))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_up = True
                elif event.key == pygame.K_DOWN:
                    move_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    move_up = False
                elif event.key == pygame.K_DOWN:
                    move_down = False

        keys = pygame.key.get_pressed()
        # Combine get_pressed and explicit key events to be robust
        effective_up = keys[pygame.K_UP] or move_up
        effective_down = keys[pygame.K_DOWN] or move_down
        player.update(dt, effective_up, effective_down)

        # update background offset
        bg_offset = (bg_offset + BG_SPEED) % (bg_w if bg_img else SCREEN_WIDTH)

        # update balls
        for b in balls:
            b.update(dt)
        # remove off-screen balls
        balls = [b for b in balls if b.x + b.w > -100]

        # check collisions (player vs balls)
        p_rect = player.get_rect()
        collided = []
        for b in balls:
            # shrink both rects to avoid transparent-edge false collisions
            try:
                pr = p_rect.inflate(-2*COLLISION_MARGIN, -2*COLLISION_MARGIN)
            except Exception:
                pr = p_rect
            br = b.get_rect()
            try:
                br = br.inflate(-2*COLLISION_MARGIN, -2*COLLISION_MARGIN)
            except Exception:
                br = b.get_rect()
            # ensure rects still have positive size
            if pr.width <= 0 or pr.height <= 0:
                pr = p_rect
            if br.width <= 0 or br.height <= 0:
                br = b.get_rect()
            if pr.colliderect(br):
                collided.append(b)
        for b in collided:
            # only play ding/hit if we haven't reached the target yet
            if score < TARGET_SCORE:
                if ding_sound:
                    try:
                        ding_sound.play()
                    except Exception:
                        pass
                elif hit_sound:
                    try:
                        hit_sound.play()
                    except Exception:
                        pass
            score += 1
            if b in balls:
                balls.remove(b)
        # check win condition after handling collisions
        if not won and score >= TARGET_SCORE:
            won = True
            if victory_sound:
                try:
                    victory_sound.play()
                except Exception:
                    pass
            # load end image
            end_path = find_end_image()
            if end_path:
                try:
                    end_img = pygame.image.load(end_path).convert_alpha()
                    # scale to fit screen while preserving aspect
                    ew, eh = end_img.get_width(), end_img.get_height()
                    scale = min(SCREEN_WIDTH / ew, SCREEN_HEIGHT / eh)
                    new_size = (max(1, int(ew*scale)), max(1, int(eh*scale)))
                    try:
                        # scale to COVER the screen (may crop) so end image fully covers game view
                        scale = max(SCREEN_WIDTH / ew, SCREEN_HEIGHT / eh)
                        new_size = (max(1, int(ew*scale)), max(1, int(eh*scale)))
                        end_surface = pygame.transform.smoothscale(end_img, new_size)
                    except Exception:
                        end_surface = pygame.transform.scale(end_img, new_size)
                except Exception as e:
                    print('Failed to load end image', end_path, e)
            end_start = pygame.time.get_ticks()

        # draw
        if bg_img:
            # 平铺背景，确保完全覆盖屏幕（从 -bg_offset 开始向右一直画到屏幕右边）
            tx = -bg_offset
            while tx < SCREEN_WIDTH:
                screen.blit(bg_img, (tx, 0))
                tx += bg_w
            # 也向左多画一块以防 bg_offset 很小导致左侧空隙
            if -bg_offset > -bg_w:
                screen.blit(bg_img, (-bg_offset - bg_w, 0))
        else:
            screen.fill((20, 20, 60))

        # draw balls
        for b in balls:
            b.draw(screen)

        # draw player
        player.draw(screen)

        # draw score as X/30
        score_surf = font.render(f'{score}/{TARGET_SCORE}', True, (255,255,255))
        screen.blit(score_surf, (10, 10))

        # if won, show end image for 3 seconds then quit
        if won:
            if end_surface:
                # center end image
                ex = SCREEN_WIDTH//2 - end_surface.get_width()//2
                ey = SCREEN_HEIGHT//2 - end_surface.get_height()//2
                screen.blit(end_surface, (ex, ey))
            # check timer
            if end_start and pygame.time.get_ticks() - end_start >= 3000:
                running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
