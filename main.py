import random
import math
import pygame
from os import listdir
from os.path import isfile, join
from pygame.sprite import Group

# Initialize pygame
pygame.init()
pygame.display.set_caption('Mario Game')


# DEFAULT VALUES

BG_COLOR = (255, 255, 200)
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VELOCITY = 5

# Create pygame window
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        print(image)
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        print(sprites)
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 255, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets( "MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x +=dx
        self.rect.y +=dy
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        # self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel,self.y_vel)
        self.fall_count+=1
        self.update_sprites()
    
    
    def jump(self, vel):
        self.y_vel -= vel
        

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprites(self):
        sprite_sheet = "idle"
        if self.x_vel !=0:
            sprite_sheet = "run"
        
        sprites = self.SPRITES[sprite_sheet + '_' + self.direction]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

        
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for x in range(WIDTH//width + 1):
        for y in range(HEIGHT//height + 1):
            tiles.append(( x*width, y*width ))

    return tiles, image


def handle_move(player):
    keys = pygame.key.get_pressed()
    player.x_vel = 0

    if keys[pygame.K_LEFT]: player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT]: player.move_right(PLAYER_VELOCITY)
    if keys[pygame.K_SPACE]: player.jump(PLAYER_VELOCITY)

    return

def draw(window, background, bg_image, player, objects):
    for tile in background:
        window.blit(bg_image, tile)
    
    for obj in objects:
        obj.draw(window)

    player.draw(window)
    pygame.display.update()

def main(window):

    clock = pygame.time.Clock()
    background, bg_image = get_background("Green.png")
    block_size = 96

    player = Player(50,50, 100, 100)
    floors = [Block( i*block_size , HEIGHT-block_size, block_size) for i in range(-WIDTH//block_size, (WIDTH*2)//block_size)]
    # blocks = [Block(0, HEIGHT-block_size, block_size)]


    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_image, player, floors)


if __name__ == '__main__':
    main(window=window)
