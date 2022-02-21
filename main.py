import pygame
import math
import random

## SETTINGS:
game_loop_frequency = 60
run = True
game_area_max_x = 1920
game_area_max_y = 1080
x = game_area_max_x/2
y = game_area_max_y/2
width = 20
height = 20
speed = 6
aim_distance = 50

bullet_speed = 10
bullet_reload_speed = 5
bullet_capacity = 3
bullet_count = 3
bullet_reload_count = 0
bullets = []

monster_speed = 3
monster_size = 30
monster_half_size = monster_size/2
monster_spawn_rate = 3
monster_spawn_rate_increase = 20
monster_spawn_rate_counter = 0
monsters = []


##INIT
pygame.init()
random.seed()

##OBJECTS AND STUFF:

def spawn_monster():
    border = random.randint(0, 3)
    if border == 0: #top
        position = random.randint(0, game_area_max_y)
        monster = Monster(position, 0-monster_size)
        #print("DEBUG >> monster spawn (x,y) = (%d,%d)" % (monster.x, monster.y))
        return monster
    if border == 1: #bottom
        position = random.randint(0, game_area_max_y)
        monster = Monster(position, game_area_max_y+monster_size)
        #print("DEBUG >> monster spawn (x,y) = (%d,%d)" % (monster.x, monster.y))
        return monster
    if border == 2: #left
        position = random.randint(0, game_area_max_x)
        monster = Monster(0-monster_size, position)
        #print("DEBUG >> monster spawn (x,y) = (%d,%d)" % (monster.x, monster.y))
        return monster
    if border == 3: #right
        position = random.randint(0, game_area_max_x)
        monster = Monster(game_area_max_x+monster_size, position)
        #print("DEBUG >> monster spawn (x,y) = (%d,%d)" % (monster.x, monster.y))
        return monster


class Monster():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, player_pos):
        global run
        dx, dy = get_coordinates_for_player_to_mouse_distance((self.x,self.y), player_pos, monster_speed)
        self.x += dx
        self.y += dy

        if self.x-monster_half_size < x < self.x+monster_half_size and self.y-monster_half_size < y < self.y+monster_half_size:
            run = False

    def draw(self):
        pygame.draw.rect(win, (0, 0, 255), (self.x-monster_size/2, self.y-monster_size/2, monster_size, monster_size))


class Bullet():
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def update(self, monsters):
        self.x -= self.dx
        self.y -= self.dy

        if not self.within_screen():
            return False

        #check monster collision
        for i, monster in enumerate(monsters):
            if monster.x-monster_half_size < self.x < monster.x+monster_half_size and monster.y-monster_half_size < self.y < monster.y+monster_half_size:
                monsters.pop(i)
                return False

        return True

    def within_screen(self):
        return 0 < self.x < game_area_max_x and 0 < self.y < game_area_max_y

    def draw(self, window):
        pygame.draw.circle(win, (255, 100, 100), (self.x, self.y), 2)

## LOGIC:

win = pygame.display.set_mode((game_area_max_x, game_area_max_y))
pygame.display.set_caption("Demo Game")
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

def draw_aim_marker(window, mouse_pos, player_pos):
    dx, dy = get_coordinates_for_player_to_mouse_distance(mouse_pos, player_pos, aim_distance)
    px, py = player_pos
    #pygame.draw.circle(win, (0, 255, 0), (mx, my), 5) # mouse debug
    pygame.draw.circle(win, (0, 255, 255), (px-dx, py-dy), 5)

def get_coordinates_for_player_to_mouse_distance(mouse_pos, player_pos, distance: int):
    mx, my = mouse_pos
    px, py = player_pos
    rel_x, rel_y = (px-mx, py-my)
    angle = math.atan2(rel_y, rel_x)
    dx = distance*math.cos(angle)
    dy = distance*math.sin(angle)

    return dx, dy


#Hacky main loop
while run:
    pygame.time.delay(game_loop_frequency)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            left, _, right = pygame.mouse.get_pressed()
            if left:
                dx, dy = get_coordinates_for_player_to_mouse_distance(mouse_pos, (x,y), bullet_speed)
                bullets.append(Bullet(x, y, dx, dy))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y -= speed
        if y < 0:
            y = 0
    if keys[pygame.K_s]:
        y += speed
        if y > game_area_max_y:
            y = game_area_max_y
    if keys[pygame.K_a]:
        x -= speed
        if x < 0:
            x = 0
    if keys[pygame.K_d]:
        x += speed
        if x > game_area_max_x:
            x = game_area_max_x
    if keys[pygame.K_ESCAPE]:
        run = False


    win.fill((0,0,0))

    for i, bullet in enumerate(bullets):
        if bullet.update(monsters):
            bullet.draw(win)
        else:
            bullets.pop(i)

    for i, monster in enumerate(monsters):
        monster.update((x,y))
        monster.draw()

    pygame.draw.rect(win, (255, 0, 0), (x-width/2, y-height/2, width, height))

    draw_aim_marker(win, mouse_pos, (x, y))
    pygame.display.update()

    monster_spawn_rate_counter -= 1
    if monster_spawn_rate_counter <= 0:
        monster_spawn_rate += 1
        monster_spawn_rate_counter = monster_spawn_rate_increase
        monsters.append(spawn_monster())

pygame.quit

