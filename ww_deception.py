import pygame, os, random
from pygame.locals import *

# Colors
BACKGROUND_COLOR = (136, 208, 200)
BLOCK_COLOR = (240, 168, 88)
PLAYER_COLOR = (216, 96, 96)
FLICKER_COLOR = (240, 40, 240)
YOU_WIN_COLOR = (52, 177, 235)

# Constants
SCREEN_SIZE = (800, 450)
SCREEN_WIDTH = SCREEN_SIZE[0]
SCREEN_HEIGHT = SCREEN_SIZE[1]
PLAYER_SIZE = SCREEN_HEIGHT / 30
HALF_PLAYER_SIZE = PLAYER_SIZE / 2
PLAYER_SPEED = SCREEN_WIDTH // 600
PLAYER_ACCELERATION = SCREEN_WIDTH / 6400
X_SLOWDOWN = 0.85
START_JUMP_VELOCITY = -15
GRAVITY = 0.8
player_x_velocity = 0
player_y_velocity = 0
trying_to_jump = False

scroll = [0, 0]
move_right = False
move_left = False
flicker_counter = 0
flicker_color = BLOCK_COLOR
background_x_offset = 0
background_y_offset = 0
playing = True

# Functions
def draw_player(x, y):
    pygame.draw.rect(screen, PLAYER_COLOR, ((x - HALF_PLAYER_SIZE, y - HALF_PLAYER_SIZE), (PLAYER_SIZE, PLAYER_SIZE)))


def load_map(map):
    m = open(map + ".txt", "r")
    data = m.readlines()
    m.close()
    
    new_map = []
    for r in data:
        new_map.append([int(i) for i in r.strip()])
    return new_map


def draw_bricks(level, x_offset, y_offset, flicker_color):
    for i in range(len(level)):
        for j in range(len(level[0])):
            if level[i][j] == 1:
                pygame.draw.rect(screen, BLOCK_COLOR, ((j * BRICK_SIZE + x_offset, i * BRICK_SIZE + y_offset), (BRICK_SIZE, BRICK_SIZE)))
            if level[i][j] == 2:
                pygame.draw.rect(screen, flicker_color, ((j * BRICK_SIZE + x_offset, i * BRICK_SIZE + y_offset), (BRICK_SIZE, BRICK_SIZE)))


def test_upper_edge(player_x, player_y, player_x_velocity, player_y_velocity, brick_x, brick_y):
    if player_y + HALF_PLAYER_SIZE >= brick_y:
        if player_x - HALF_PLAYER_SIZE < brick_x + BRICK_SIZE and player_x + HALF_PLAYER_SIZE > brick_x:
            if player_y - HALF_PLAYER_SIZE < brick_y:
                if player_y_velocity > 0:
                    player_y = brick_y - HALF_PLAYER_SIZE
                    player_y_velocity = 0
                    return player_x, player_y, player_x_velocity, player_y_velocity, True
    return player_x, player_y, player_x_velocity, player_y_velocity, False
    

def test_right_edge(player_x, player_y, player_x_velocity, player_y_velocity, brick_x, brick_y):
    if player_x - HALF_PLAYER_SIZE <= brick_x + BRICK_SIZE:
        if player_y + HALF_PLAYER_SIZE > brick_y and player_y - HALF_PLAYER_SIZE < brick_y + BRICK_SIZE:
            if player_x + HALF_PLAYER_SIZE > brick_x + BRICK_SIZE:
                if player_x_velocity < 0:
                    player_x = brick_x + BRICK_SIZE + HALF_PLAYER_SIZE
                    player_x_velocity = 0
                    return player_x, player_y, player_x_velocity, player_y_velocity, True
    return player_x, player_y, player_x_velocity, player_y_velocity, False


def test_bottom_edge(player_x, player_y, player_x_velocity, player_y_velocity, brick_x, brick_y):
    if player_y - HALF_PLAYER_SIZE <= brick_y + BRICK_SIZE:
        if player_x - HALF_PLAYER_SIZE < brick_x + BRICK_SIZE and player_x + HALF_PLAYER_SIZE > brick_x:
            if player_y + HALF_PLAYER_SIZE > brick_y + BRICK_SIZE:
                if player_y_velocity < 0:
                    player_y = brick_y + BRICK_SIZE + HALF_PLAYER_SIZE
                    player_y_velocity = 0
                    return player_x, player_y, player_x_velocity, player_y_velocity, True
    return player_x, player_y, player_x_velocity, player_y_velocity, False


def test_left_edge(player_x, player_y, player_x_velocity, player_y_velocity, brick_x, brick_y):
    if player_x + HALF_PLAYER_SIZE >= brick_x:
        if player_y + HALF_PLAYER_SIZE > brick_y and player_y - HALF_PLAYER_SIZE < brick_y + BRICK_SIZE:
            if player_x - HALF_PLAYER_SIZE < brick_x:
                if player_x_velocity > 0:
                    player_x = brick_x - HALF_PLAYER_SIZE
                    player_x_velocity = 0
                    return player_x, player_y, player_x_velocity, player_y_velocity, True
    return player_x, player_y, player_x_velocity, player_y_velocity, False


def collide(level, player_x, player_y, player_x_velocity, player_y_velocity):
    for i in range(Y_BRICKS):
        for j in range(X_BRICKS):
            if level[i][j] == 1:
                exposed_edges_trbd = [True, True, True, True]
                if i > 0: 
                    if level[i - 1][j] == 1:
                        exposed_edges_trbd[0] = False
                if j < X_BRICKS - 1:
                    if level[i][j + 1] == 1:
                        exposed_edges_trbd[1] = False
                if i < Y_BRICKS - 1:
                    if level[i + 1][j] == 1:
                        exposed_edges_trbd[2] = False
                if j > 0:
                    if level[i][j - 1] == 1:
                        exposed_edges_trbd[3] = False
                if player_y + HALF_PLAYER_SIZE >= len(level) * BRICK_SIZE :
                    player_y_velocity = 0
                    player_y = len(level) * BRICK_SIZE  - HALF_PLAYER_SIZE
                if player_x - HALF_PLAYER_SIZE <= 0:
                    player_x_velocity = 0
                    player_x = HALF_PLAYER_SIZE
                if player_y - HALF_PLAYER_SIZE <= 0:
                    player_y_velocity = 0
                    player_y = HALF_PLAYER_SIZE
                if player_x + HALF_PLAYER_SIZE >= len(level[0]) * BRICK_SIZE:
                    player_x_velocity = 0
                    player_x = len(level[0]) * BRICK_SIZE - HALF_PLAYER_SIZE 

                if exposed_edges_trbd[0]:
                    player_x, player_y, player_x_velocity, player_y_velocity, collided = test_upper_edge(player_x, player_y, player_x_velocity, player_y_velocity, j * BRICK_SIZE, i * BRICK_SIZE)
                    if collided and trying_to_jump:
                        print("tried jump")
                        player_y_velocity = START_JUMP_VELOCITY
                        
                if exposed_edges_trbd[1]:
                    player_x, player_y, player_x_velocity, player_y_velocity, collided = test_right_edge(player_x, player_y, player_x_velocity, player_y_velocity, j * BRICK_SIZE, i * BRICK_SIZE)
                if exposed_edges_trbd[2]:
                    player_x, player_y, player_x_velocity, player_y_velocity, collided = test_bottom_edge(player_x, player_y, player_x_velocity, player_y_velocity, j * BRICK_SIZE, i * BRICK_SIZE)
                if exposed_edges_trbd[3]:
                    player_x, player_y, player_x_velocity, player_y_velocity, collided = test_left_edge(player_x, player_y, player_x_velocity, player_y_velocity, j * BRICK_SIZE, i * BRICK_SIZE)

    return player_x, player_y, player_x_velocity, player_y_velocity


level_1 = load_map("map_1")
you_win = load_map("map_2")
level = level_1
X_BRICKS = len(level[0])
Y_BRICKS = len(level)
BRICK_SIZE = SCREEN_WIDTH / 32
player_x = BRICK_SIZE * 5
player_y = len(level) * BRICK_SIZE - SCREEN_HEIGHT / 4

# Init
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("ww-Deception")
clock = pygame.time.Clock()
carryOn = True
iterNr = 0

while carryOn:
    # User Input

    for event in pygame.event.get():
        if event.type == QUIT:
            carryOn = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                carryOn = False
            if playing:
                if event.key == K_UP or event.key == K_w:
                    trying_to_jump = True                        
                    if player_y_velocity == 0 or player_y == len(level) * BRICK_SIZE - HALF_PLAYER_SIZE:
                        player_y_velocity = START_JUMP_VELOCITY
                        trying_to_jump = False                        
                if event.key == K_RIGHT or event.key == K_d:
                    move_right = True
                if event.key == K_LEFT or event.key == K_a:
                    move_left = True
        if event.type == KEYUP:
            if playing:
                if event.key == K_RIGHT or event.key == K_d:
                    move_right = False
                if event.key == K_LEFT or event.key == K_a:
                    move_left = False
                if event.key == K_UP or event.key == K_w:
                    trying_to_jump = False
            
    # Update Game State

    if playing:
        test_iterations = 4
        for i in range(test_iterations):
            if move_right:
                player_x_velocity += PLAYER_ACCELERATION / test_iterations + PLAYER_SPEED / test_iterations
            if move_left:
                player_x_velocity -= PLAYER_ACCELERATION / test_iterations + PLAYER_SPEED / test_iterations            
            player_y_velocity += GRAVITY / test_iterations
            player_x_velocity *= X_SLOWDOWN ** (1 / test_iterations)
            player_y += player_y_velocity / test_iterations
            player_x += player_x_velocity / test_iterations
            
            player_x, player_y, player_x_velocity, player_y_velocity = collide(level, player_x, player_y, player_x_velocity, player_y_velocity)
            scroll[0] += 1 / test_iterations
            scroll[1] += 1 / test_iterations
            scroll[0] += (player_x / test_iterations - scroll[0] / test_iterations - SCREEN_WIDTH / 2 / test_iterations) / 7
            scroll[1] += (player_y / test_iterations - scroll[1] / test_iterations - SCREEN_HEIGHT / 2 / test_iterations) / 5
            new_player_x = player_x - scroll[0]
            new_player_y = player_y - scroll[1]
            new_background_x_offset = background_x_offset - scroll[0]
            new_background_y_offset = background_y_offset - scroll[1]

        flicker_counter -= 1
        if flicker_counter < 0:
            flicker_counter = 0
        flicker_color = BLOCK_COLOR
        if random.randint(1, 30) == 1 and flicker_counter == 0:
            flicker_counter = random.randint(5, 8)
        if flicker_counter > 0:
            flicker_color = FLICKER_COLOR
        if scroll[0] <= 0:
            new_player_x = player_x
            new_background_x_offset = background_x_offset
        if scroll[1] >= len(level) * BRICK_SIZE - SCREEN_HEIGHT:
            new_player_y = player_y - (len(level) * BRICK_SIZE - SCREEN_HEIGHT)   
            new_background_y_offset = background_y_offset - ((len(level) * BRICK_SIZE) - SCREEN_HEIGHT)
        if scroll[1] <= 0:
            new_player_y = player_y
            new_background_y_offset = background_y_offset
        if scroll[0] >= len(level[0]) * BRICK_SIZE - SCREEN_WIDTH:
            new_player_x = player_x - (len(level[0]) * BRICK_SIZE - SCREEN_WIDTH)
            new_background_x_offset = background_x_offset - (len(level[0]) * BRICK_SIZE - SCREEN_WIDTH)

    if player_x > len(level[0]) * BRICK_SIZE - SCREEN_WIDTH / 4:
        if player_y < SCREEN_HEIGHT / 3:
            playing = False

    # Update Display
    screen.fill(BACKGROUND_COLOR)
    draw_bricks(level, new_background_x_offset, new_background_y_offset, flicker_color if playing else BLOCK_COLOR)
    draw_player(new_player_x, new_player_y)
    if not playing:
        draw_bricks(you_win, 0, SCREEN_HEIGHT / 5, FLICKER_COLOR if (iterNr//30) % 2 != 0 else YOU_WIN_COLOR)
    pygame.display.flip()
    clock.tick(60)
    iterNr +=1 
    
pygame.quit()