import os
import sys
import random
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
BALL_SPAWN_INTERVAL = 1500  # milliseconds
BALL_SPEED = BG_SPEED  # balls move left at background speed so they appear to approach

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

    def update(self, dt, keys):
        # animate
        self.anim_timer += dt
        if self.anim_timer >= self.anim_interval:
            self.anim_timer -= self.anim_interval
            self.frame_idx = (self.frame_idx + 1) % max(1, len(self.frames))
        # move right automatically
        self.x += PLAYER_SPEED_X
        # move up/down by input
        if keys[pygame.K_UP]:
            self.y -= PLAYER_SPEED_Y
        if keys[pygame.K_DOWN]:
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
    player_gif_path = find_player_gif()
    player_frames = []
    if player_gif_path:
        player_frames = load_gif_frames(player_gif_path)
    ball_imgs = []
    for p in find_ball_images():
        try:
            ball_imgs.append(pygame.image.load(p).convert_alpha())
        except Exception as e:
            print('Failed to load ball image', p, e)
    hit_sound_path = find_sound()
    hit_sound = None
    if hit_sound_path:
        try:
            hit_sound = pygame.mixer.Sound(hit_sound_path)
        except Exception as e:
            print('Failed to load sound', hit_sound_path, e)

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
        player = Player(player_frames, x=50, y=SCREEN_HEIGHT//2)
    else:
        # create a red square if no GIF
        surf = pygame.Surface((50,50), pygame.SRCALPHA)
        surf.fill((255,0,0))
        player = Player([surf], x=50, y=SCREEN_HEIGHT//2)

    # balls list
    balls = []
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, BALL_SPAWN_INTERVAL)

    score = 0
    font = pygame.font.SysFont(None, 36)

    running = True
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
                    y = random.randint(0, SCREEN_HEIGHT - surf.get_height())
                    balls.append(Ball(surf, x, y))

        keys = pygame.key.get_pressed()
        player.update(dt, keys)

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
            if p_rect.colliderect(b.get_rect()):
                collided.append(b)
        for b in collided:
            if hit_sound:
                hit_sound.play()
            score += 1
            if b in balls:
                balls.remove(b)

        # draw
        if bg_img:
            # draw two tiles to create infinite scrolling to left
            x1 = -bg_offset
            x2 = x1 + bg_w
            screen.blit(bg_img, (x1, 0))
            screen.blit(bg_img, (x2, 0))
        else:
            screen.fill((20, 20, 60))

        # draw balls
        for b in balls:
            b.draw(screen)

        # draw player
        player.draw(screen)

        # draw score
        score_surf = font.render(f'Score: {score}', True, (255,255,255))
        screen.blit(score_surf, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
