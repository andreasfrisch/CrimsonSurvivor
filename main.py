import pygame
import math
import random
from enum import Enum

## SETTINGS:
game_loop_frequency = 30
timer = 0
run = True
is_paused = True
is_in_menu = True
player_died = False
game_area_max_x = 1920
game_area_max_y = 1080
x = game_area_max_x/2
y = game_area_max_y/2
width = 20
height = 20
speed = 3
aim_distance = 50
health = 100
max_health = 100

bullet_speed = 20
bullet_reload_speed = 15
bullet_shoot_through = False
bullet_capacity = 4
bullet_count = 4
bullet_reload_count = 0
bullet_box_height = 3
bullets = []
weapon_cooldown = 0
weapon_cooldown_max = 10

monster_speed = 3
monster_size = 30
monster_half_size = monster_size/2
monster_spawn_rate = 3
monster_spawn_rate_increase = 20
monster_spawn_rate_counter = 0
big_monster_chance = 0
swarm_chance = 10
swarm_count = 5
monsters = []
monster_damage = 20

points = 0

powerups = []
ongoing_effects = []
floating_texts = []
effect_bar_height = 10
effect_bar_length = 200
bottom_bar_x = game_area_max_x - effect_bar_length - 10
bottom_bar_y = game_area_max_y - effect_bar_height - 10

menu_option_selection = 2
game_in_progress = False
menu_color = (125,125,125)

##INIT
pygame.init()
random.seed()
pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 32)
floating_text_font = pygame.font.Font('freesansbold.ttf', 15)
win = pygame.display.set_mode((game_area_max_x, game_area_max_y), pygame.FULLSCREEN)
pygame.display.set_caption("Demo Game")
#pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
pygame.mouse.set_visible(False)

##OBJECTS AND STUFF:

def reset_game_state():
    global monsters
    global bullets
    global x
    global y
    global points
    global game_in_progress
    global player_died
    global ongoing_effects
    global powerups
    global timer
    global floating_texts

    monsters = []
    bullets = []
    x = game_area_max_x/2
    y = game_area_max_y/2
    points = 0
    game_in_progress = False
    player_died = False
    powerups = []
    ongoing_effects = []
    timer = 0
    floating_texts = []

class OngoingEffectOptions(Enum):
    SPEED = 1
    AMMO = 2

class PowerUpOptions(Enum):
    HEALTH = 0
    SPEED = 1
    AMMO = 2

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
    total_seconds = game_loops_to_seconds(timer)
    seconds = total_seconds % 60
    minutes = total_seconds / 60
    texts = [
        font.render("You Died", True, (255, 0, 0), menu_color),
        font.render("You survived for %02d:%02d" % (minutes, seconds), True, (255,0,0), menu_color),
        font.render("You Got %d %s" % (points, "Kill" if points == 1 else "Kills"), True, (255, 0, 0), menu_color),
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

def generate_swarm(position):
    new_swarm = []
    for i in range(swarm_count):
        x, y = position
        if i == 0:
            pass # no need to change coordinates
        if i == 1:
            y -= monster_size*2
        if i == 2:
            y += monster_size*2
        if i == 3:
            x -= monster_size*2
        if i == 4:
            x += monster_size*2

        new_swarm.append(SwarmMonster(x, y, 1, 0.5, monster_size*0.8, monster_speed*1.5))
    return new_swarm

def randomise_monster_type(pos):
    global big_monster_chance
    global swarm_chance
    percent = random.randint(0,99)
    x, y = pos
    if percent <= big_monster_chance:
        big_monster_chance = 0
        return [BigMonster(x, y, 5, monster_damage*4, monster_size*1.2, monster_speed*1.2)]
    elif percent <= swarm_chance:
        swarm_chance -= 20
        return generate_swarm(pos)
    else:
        return [Monster(x, y)]

def spawn_monster():
    border = random.randint(0, 3)
    x = y = None
    if border == 0: #top
        x = random.randint(0, game_area_max_y)
        y = 0-monster_size
    if border == 1: #bottom
        x = random.randint(0, game_area_max_y)
        y = game_area_max_y+monster_size
    if border == 2: #left
        y = random.randint(0, game_area_max_x)
        x = 0-monster_size
    if border == 3: #right
        y = random.randint(0, game_area_max_x)
        x = game_area_max_x+monster_size
    return randomise_monster_type((x, y))

class FloatingText():
    def __init__(self, x, y, text, time=0.5):
        self.x = x
        self.y = y
        self.text = text
        self.loop_counts = time*1000/game_loop_frequency
        self.y_speed = -2

    def update(self):
        self.loop_counts -= 1
        if self.loop_counts <= 0:
            return False
        self.y += self.y_speed
        return True

    def draw(self, window):
        text = floating_text_font.render(self.text, True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.center = (self.x, self.y)
        window.blit(text, text_rect)


class OngoingEffect():
    def __init__(self, type, time):
        self.type = type
        self.init_time = time
        self.loop_counts = time*1000/game_loop_frequency

    def update(self):
        self.loop_counts -= 1
        if self.loop_counts <= 0:
            return False
        return True

    def draw(self, index, total_effects):
        global effect_bar_height
        global effect_bar_length
        global bottom_bar_x
        global bottom_bar_y
        seconds_passed = self.loop_counts*game_loop_frequency/1000
        colored_size = effect_bar_length * float(seconds_passed / self.init_time)
        if self.type == OngoingEffectOptions.SPEED:
            pygame.draw.rect(win, (120, 125, 45), (bottom_bar_x, bottom_bar_y-i*(effect_bar_height+5), effect_bar_length, effect_bar_height))
            pygame.draw.rect(win, (240, 255, 90), (bottom_bar_x+(effect_bar_length-colored_size), bottom_bar_y-i*(effect_bar_height+5), colored_size, effect_bar_height))
        elif self.type == OngoingEffectOptions.AMMO:
            pygame.draw.rect(win, (0, 125, 125), (bottom_bar_x, bottom_bar_y-i*(effect_bar_height+5), effect_bar_length, effect_bar_height))
            pygame.draw.rect(win, (0, 255, 255), (bottom_bar_x+(effect_bar_length-colored_size), bottom_bar_y-i*(effect_bar_height+5), colored_size, effect_bar_height))
        else:
            pass


    def remove(self):
        global speed
        global bullet_reload_speed
        global bullet_shoot_through
        global weapon_cooldown_max
        if self.type == OngoingEffectOptions.SPEED:
            speed /= 2
        elif self.type == OngoingEffectOptions.AMMO:
            bullet_reload_speed = 15
            bullet_shoot_through = False
            weapon_cooldown_max = 10
        else:
            pass

    def update_time(self, time):
        self.loop_counts = time*1000/game_loop_frequency


class PowerUp():
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.orig_y = y
        self.type = type
        self.y_direction = -1

    def draw(self, window):
        if self.type == PowerUpOptions.HEALTH:
            pygame.draw.circle(window, (255, 0, 0), (self.x, self.y), 4)
        if self.type == PowerUpOptions.AMMO:
            pygame.draw.circle(window, (0, 255, 255), (self.x, self.y), 4)
        if self.type == PowerUpOptions.SPEED:
            pygame.draw.circle(window, (240, 255, 90), (self.x, self.y), 4)

    def update(self):
        self.y += self.y_direction
        if self.y >= self.orig_y + 2 or self.y <= self.orig_y-2:
            self.y_direction *= -1

        if x-width/2 < self.x < x+width/2 and y-height/2 < self.y < y+height/2:
            self.apply()
            return False

        return True

    def apply(self):
        global health
        global max_health
        global speed
        global ongoing_effects
        global bullet_reload_speed
        global bullet_shoot_through
        global floating_texts
        global weapon_cooldown_max
        if self.type == PowerUpOptions.HEALTH:
            health += 25
            if health > max_health:
                health = max_health
            floating_texts.append(FloatingText(x, y-height/2, "+25 HP"))
        elif self.type == PowerUpOptions.SPEED:
            ongoing_effects.append(OngoingEffect(OngoingEffectOptions.SPEED, 10))
            speed *= 2
            floating_texts.append(FloatingText(x, y-height/2, "speed"))
        elif self.type == PowerUpOptions.AMMO:
            for e in ongoing_effects:
                if e.type == OngoingEffectOptions.AMMO:
                    e.update_time(10)
                    return
            ongoing_effects.append(OngoingEffect(OngoingEffectOptions.AMMO, 10))
            bullet_reload_speed = 1
            bullet_shoot_through = True
            weapon_cooldown_max = 3
            floating_texts.append(FloatingText(x, y-height/2, "amooook!"))



def spawn_powerup(pos):
    global powerups
    chance = random.randint(0,99)
    if chance > 85:
        x, y = pos
        typeInt = random.randint(0,5)
        if typeInt in [0,1,2]:
            powerups.append(PowerUp(x, y, PowerUpOptions.HEALTH))
        elif typeInt in [3,4]:
            powerups.append(PowerUp(x, y, PowerUpOptions.SPEED))
        elif typeInt in [5]:
            powerups.append(PowerUp(x, y, PowerUpOptions.AMMO))

class SwarmMonster():
    def __init__(self, x, y, health, damage, size, speed):
        self.x = x
        self.y = y
        self.health = health
        self.damage = damage
        self.size = size
        self.speed = speed

    def update(self, player_pos):
        global run
        global is_paused
        global player_died
        global health
        dx, dy = get_coordinates_for_player_to_mouse_distance((self.x,self.y), player_pos, speed)
        self.x += dx
        self.y += dy

        if self.x-monster_half_size < x < self.x+monster_half_size and self.y-monster_half_size < y < self.y+monster_half_size:
            health -= self.damage
            floating_texts.append(FloatingText(x, y-height/2, "-%d" % monster_damage))
            if health <= 0:
                is_paused = True
                player_died = True

            return False

        return True

    def deal_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False


    def draw(self):
        pygame.draw.rect(win, (133, 255, 156), (self.x-self.size/2, self.y-self.size/2, self.size, self.size))

class BigMonster():
    def __init__(self, x, y, health, damage, size, speed):
        self.x = x
        self.y = y
        self.health = health
        self.damage = damage
        self.size = size
        self.speed = speed

    def update(self, player_pos):
        global run
        global is_paused
        global player_died
        global health
        dx, dy = get_coordinates_for_player_to_mouse_distance((self.x,self.y), player_pos, speed)
        self.x += dx
        self.y += dy

        if self.x-monster_half_size < x < self.x+monster_half_size and self.y-monster_half_size < y < self.y+monster_half_size:
            health -= self.damage
            floating_texts.append(FloatingText(x, y-height/2, "-%d" % monster_damage))
            if health <= 0:
                is_paused = True
                player_died = True

            return False

        return True

    def deal_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False


    def draw(self):
        pygame.draw.rect(win, (133, 20, 156), (self.x-self.size/2, self.y-self.size/2, self.size, self.size))

class Monster():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 1

    def deal_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True
        return False

    def update(self, player_pos):
        global run
        global is_paused
        global player_died
        global health
        dx, dy = get_coordinates_for_player_to_mouse_distance((self.x,self.y), player_pos, monster_speed)
        self.x += dx
        self.y += dy

        if self.x-monster_half_size < x < self.x+monster_half_size and self.y-monster_half_size < y < self.y+monster_half_size:
            health -= monster_damage
            floating_texts.append(FloatingText(x, y-height/2, "-%d" % monster_damage))
            if health <= 0:
                is_paused = True
                player_died = True

            return False

        return True


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
        global bullet_shoot_through
        self.x -= self.dx
        self.y -= self.dy

        if not self.within_screen():
            return False

        #check monster collision
        for i, monster in enumerate(monsters):
            if monster.x-monster_half_size < self.x < monster.x+monster_half_size and monster.y-monster_half_size < self.y < monster.y+monster_half_size:
                if monster.deal_damage(1):
                    spawn_powerup((monster.x, monster.y))
                    points += 1
                    monsters.pop(i)
                    return bullet_shoot_through
                else:
                    return bullet_shoot_through

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

def draw_aim_marker_at_position(window, position):
    pygame.draw.circle(win, (0, 255, 255), position, 10, 2)
    pygame.draw.circle(win, (0, 255, 255), position, 1)

def get_coordinates_for_player_to_mouse_distance(mouse_pos, player_pos, distance: int):
    mx, my = mouse_pos
    px, py = player_pos
    rel_x, rel_y = (px-mx, py-my)
    angle = math.atan2(rel_y, rel_x)
    dx = distance*math.cos(angle)
    dy = distance*math.sin(angle)

    return dx, dy

def game_loops_to_seconds(loops):
    return loops*game_loop_frequency/1000

#Hacky main loop
while run:
    pygame.time.delay(game_loop_frequency)
    if not is_paused:
        timer += 1
        if weapon_cooldown > 0:
            weapon_cooldown -= 1
        mouse_pos = pygame.mouse.get_pos()

        seconds = game_loops_to_seconds(timer)
        if seconds % 10 == 0:
            big_monster_chance += 5
            swarm_chance += 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            #if event.type == pygame.MOUSEBUTTONDOWN:
            #    left, _, right = pygame.mouse.get_pressed()
            #    if left and bullet_count > 0:
            #        dx, dy = get_coordinates_for_player_to_mouse_distance(mouse_pos, (x,y), bullet_speed)
            #        bullets.append(Bullet(x, y, dx, dy))
            #        bullet_count -= 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_paused = True
                    is_in_menu = True
                    menu_option_selection = 3

        left, _, right = pygame.mouse.get_pressed()
        if left and bullet_count > 0 and weapon_cooldown == 0:
            dx, dy = get_coordinates_for_player_to_mouse_distance(mouse_pos, (x,y), bullet_speed)
            bullets.append(Bullet(x, y, dx, dy))
            bullet_count -= 1
            weapon_cooldown = weapon_cooldown_max
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

        for i, powerup in enumerate(powerups):
            if powerup.update():
                powerup.draw(win)
            else:
                powerups.pop(i)

        for i, effect in enumerate(ongoing_effects):
            if effect.update():
                total_effects = len(ongoing_effects)
                effect.draw(i, total_effects)
            else:
                effect.remove()
                ongoing_effects.pop(i)

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
            if monster.update((x,y)):
                monster.draw()
            else:
                monsters.pop(i)

        #draw player
        pygame.draw.rect(win, (255, 0, 0), (x-width/2, y-height/2, width, height))
        #draw health_bar
        remaining_health_percent = float(health/max_health)
        colored_health_size = width*remaining_health_percent
        pygame.draw.rect(win, (125, 0, 0), (x-width/2, y+height/2+2, width, 5))
        pygame.draw.rect(win, (255, 0, 0), (x-width/2+(width-colored_health_size), y+height/2+2, colored_health_size, 5))
        #draw ammo
        ammo_spacing = 1
        bullet_space = width - (bullet_capacity*1)*ammo_spacing
        per_bullet_space = float(bullet_space/bullet_capacity)
        for i in range(bullet_count):
            pygame.draw.rect(win, (0, 255, 255), (x+width/2-per_bullet_space*(i+1)-i*ammo_spacing, y+height/2+4+5, per_bullet_space, bullet_box_height))

        #draw_aim_marker(win, mouse_pos, (x, y))
        draw_aim_marker_at_position(win, mouse_pos)

        text = font.render("Kills: %d" % points, True, (255,0,0), (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (game_area_max_x-text_rect.width, text_rect.height)
        win.blit(text, text_rect)

        total_seconds = game_loops_to_seconds(timer)
        seconds = total_seconds % 60
        minutes = total_seconds / 60
        text = font.render("%02d:%02d" % (minutes, seconds), True, (255,255,255), (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (game_area_max_x/2, text_rect.height)
        win.blit(text, text_rect)

        monster_spawn_rate_counter -= 1
        if monster_spawn_rate_counter <= 0:
            monster_spawn_rate += 1
            monster_spawn_rate_counter = monster_spawn_rate_increase
            monsters += spawn_monster()

        for i, text in enumerate(floating_texts):
            if text.update():
                text.draw(win)
            else:
                floating_texts.pop(i)

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

