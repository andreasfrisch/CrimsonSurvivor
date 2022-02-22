import pygame
import math
import random
from enum import Enum

## SETTINGS:
game_loop_frequency = 30
run = True
is_paused = True
is_in_menu = True
player_died = False
game_area_max_x = 800
game_area_max_y = 600
x = game_area_max_x/2
y = game_area_max_y/2
width = 20
height = 20
speed = 3
aim_distance = 50

bullet_speed = 5
bullet_reload_speed = 15
bullet_capacity = 4
bullet_count = 4
bullet_reload_count = 0
bullet_box_width = 4.5
bullet_box_height = 4
bullets = []

monster_speed = 2
monster_size = 30
monster_half_size = monster_size/2
monster_spawn_rate = 3
monster_spawn_rate_increase = 20
monster_spawn_rate_counter = 0
monsters = []

points = 0

menu_option_selection = 2
game_in_progress = False
menu_color = (125,125,125)

##INIT
pygame.init()
random.seed()
pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 32)
#win = pygame.display.set_mode((game_area_max_x, game_area_max_y), pygame.FULLSCREEN)
win = pygame.display.set_mode((game_area_max_x, game_area_max_y))
pygame.display.set_caption("Demo Game")
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

##OBJECTS AND STUFF:

def reset_game_state():
    global monsters
    global bullets
    global x
    global y
    global points
    global game_in_progress
    global player_died

    monsters = []
    bullets = []
    x = game_area_max_x/2
    y = game_area_max_y/2
    points = 0
    game_in_progress = False
    player_died = False

class MenuOptions(Enum):
    QUIT = 0
    SETTINGS = 1
    NEW_GAME = 2
    CONTINUE = 3

def get_menu_options():
    global game_in_progress
    if game_in_progress:
        return [
            {'type': MenuOptions.CONTINUE, 'active': True},
            {'type': MenuOptions.NEW_GAME, 'active': True},
            {'type': MenuOptions.SETTINGS, 'active': False},
            {'type': MenuOptions.QUIT, 'active': True},
        ]
    else:
        return [
            {'type': MenuOptions.NEW_GAME, 'active': True},
            {'type': MenuOptions.SETTINGS, 'active': False},
            {'type': MenuOptions.QUIT, 'active': True},
        ]

def get_menu_text(type):
    global game_in_progress
    if type == MenuOptions.QUIT: return "Quit"
    if type == MenuOptions.SETTINGS: return "Settings"
    if type == MenuOptions.NEW_GAME:
        if game_in_progress:
            return "Reset Game"
        else:
            return "New Game"
    if type == MenuOptions.CONTINUE: return "Continue"

def get_menu_color(menu_option):
    if menu_option["active"]:
        if menu_option_selection == menu_option["type"].value:
            return (0,255,255)
        else:
            return (0,0,255)
    else:
        return (0,0,0)

def render_menu_options():
    options = get_menu_options()
    menu_option_height = 30
    first_option_y = game_area_max_y/2-len(options)/2*menu_option_height
    for i, option in enumerate(options):
        text_color = get_menu_color(option)
        text = font.render(get_menu_text(option["type"]), True, text_color, menu_color)
        text_rect = text.get_rect()
        text_rect.center = (game_area_max_x/2, first_option_y+menu_option_height*i)
        win.blit(text, text_rect)

def render_death_screen():
    texts = [
        font.render("You Died", True, (255, 0, 0), menu_color),
        font.render("You Got %d Kills" % points, True, (255, 0, 0), menu_color),
        font.render("press any button", True, (255, 0, 0), menu_color),
    ]
    text_height = 50
    first_text_y = game_area_max_y/2-len(texts)/2*text_height
    for i, text in enumerate(texts):
        text_rect = text.get_rect()
        text_rect.center = (game_area_max_x/2, first_text_y+text_height*i)
        win.blit(text, text_rect)

def next_menu_option():
    global menu_option_selection
    options = get_menu_options()
    menu_option_selection += 1
    possible_options = [opt["type"].value for opt in options if opt["active"]]
    while not menu_option_selection in possible_options:
        menu_option_selection += 1
        if menu_option_selection > len(options):
            menu_option_selection = 0

def previous_menu_option():
    global menu_option_selection
    options = get_menu_options()
    menu_option_selection -= 1
    possible_options = [opt["type"].value for opt in options if opt["active"]]
    while not menu_option_selection in possible_options:
        menu_option_selection -= 1
        if menu_option_selection < 0:
            menu_option_selection = len(options)-1

def select_menu_option():
    global run
    global is_paused
    global is_in_menu
    global game_in_progress
    if menu_option_selection == MenuOptions.QUIT.value:
        run = False
    if menu_option_selection == MenuOptions.SETTINGS.value:
        pass #cannot be selected right now
    if menu_option_selection == MenuOptions.NEW_GAME.value:
        reset_game_state()
        is_paused = False
        is_in_menu = False
        game_in_progress = True
    if menu_option_selection == MenuOptions.CONTINUE.value:
        is_paused = False
        is_in_menu = False

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
        global is_paused
        global player_died
        dx, dy = get_coordinates_for_player_to_mouse_distance((self.x,self.y), player_pos, monster_speed)
        self.x += dx
        self.y += dy

        if self.x-monster_half_size < x < self.x+monster_half_size and self.y-monster_half_size < y < self.y+monster_half_size:
            print("DEBUG >> monster kill; pause: %s, death: %s" % (is_paused, player_died))
            is_paused = True
            player_died = True
            print("DEBUG >> monster kill; pause: %s, death: %s" % (is_paused, player_died))


    def draw(self):
        pygame.draw.rect(win, (0, 0, 255), (self.x-monster_size/2, self.y-monster_size/2, monster_size, monster_size))


class Bullet():
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def update(self, monsters):
        global points
        self.x -= self.dx
        self.y -= self.dy

        if not self.within_screen():
            return False

        #check monster collision
        for i, monster in enumerate(monsters):
            if monster.x-monster_half_size < self.x < monster.x+monster_half_size and monster.y-monster_half_size < self.y < monster.y+monster_half_size:
                monsters.pop(i)
                points += 1
                return False

        return True

    def within_screen(self):
        return 0 < self.x < game_area_max_x and 0 < self.y < game_area_max_y

    def draw(self, window):
        pygame.draw.circle(win, (255, 100, 100), (self.x, self.y), 2)


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
    if not is_paused:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                left, _, right = pygame.mouse.get_pressed()
                if left and bullet_count > 0:
                    dx, dy = get_coordinates_for_player_to_mouse_distance(mouse_pos, (x,y), bullet_speed)
                    bullets.append(Bullet(x, y, dx, dy))
                    bullet_count -= 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_paused = True
                    is_in_menu = True
                    menu_option_selection = 3

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

        win.fill((0,0,0))

        for i, bullet in enumerate(bullets):
            if bullet.update(monsters):
                bullet.draw(win)
            else:
                bullets.pop(i)

        if bullet_count < bullet_capacity:
            if bullet_reload_count >= bullet_reload_speed:
                bullet_count += 1
                bullet_reload_count = 0
            else:
                bullet_reload_count += 1

        for i, monster in enumerate(monsters):
            monster.update((x,y))
            monster.draw()

        #draw player
        pygame.draw.rect(win, (255, 0, 0), (x-width/2, y-height/2, width, height))
        for i in range(bullet_count):
            pygame.draw.rect(win, (0, 255, 255), (x+width/2-bullet_box_width*(i+1)-i, y+height/2+bullet_box_height, bullet_box_width, bullet_box_height))

        draw_aim_marker(win, mouse_pos, (x, y))

        text = font.render("Kills: %d" % points, True, (255,0,0), (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (game_area_max_x-text_rect.width, text_rect.height)
        win.blit(text, text_rect)

        monster_spawn_rate_counter -= 1
        if monster_spawn_rate_counter <= 0:
            monster_spawn_rate += 1
            monster_spawn_rate_counter = monster_spawn_rate_increase
            monsters.append(spawn_monster())

    else:
        if is_in_menu:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and game_in_progress:
                        is_paused = False
                        is_in_menu = False
                    if event.key == pygame.K_s:
                        previous_menu_option()
                    if event.key == pygame.K_w:
                        next_menu_option()
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        select_menu_option()

            overlay = pygame.Surface((game_area_max_x, game_area_max_y))
            overlay.fill(menu_color)
            overlay.set_alpha(100)
            win.blit(overlay, pygame.Rect(0, 0, game_area_max_x, game_area_max_y))

            render_menu_options()

        if player_died:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    reset_game_state()
                    is_in_menu = True

            overlay = pygame.Surface((game_area_max_x, game_area_max_y))
            overlay.fill(menu_color)
            overlay.set_alpha(100)
            win.blit(overlay, pygame.Rect(0, 0, game_area_max_x, game_area_max_y))

            render_death_screen()

    pygame.display.update()

pygame.quit

