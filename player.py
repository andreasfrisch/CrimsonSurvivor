import pygame

class Player():
    def __init__(self):
        #super().__init__()
        #pygame.sprite.Sprite.__init__()

        self.width = 20
        self.height = 20
        self.speed = 4
        self.aim_distance = 50
        self.health = 100
        self.max_health = 100
        self.crystals = 0
        self.level = 0
        self.crystals_for_level = [1,1,2,3,5,8,13,21,34]
        self.bullet_speed = 20
        self.bullet_reload_speed = 15
        self.bullet_shoot_through = False
        self.bullet_capacity = 4
        self.bullet_count = 4
        self.bullet_reload_count = 0
        self.bullet_box_height = 3
        self.bullets = []
        self.weapon_cooldown = 0
        self.weapon_cooldown_max = 10

    def pos(self):
        return self.x, self.y

    def mod_health(self, amount):
        self.health += amount

    def mod_crystals(self, amount):
        self.crystals += amount

    def mod_speed(self, amount):
        self.crystals += amount

    def mod_max_health(self, amount):
        self.max_health += amount

    def mod_level(self, amount):
        self.level += amount

    def mod_reload_speed(self, amount):
        self.bullet_reload_speed += amount

    def mod_weapon_cooldown_max(self, amount):
        self.weapon_cooldown_max += amount

    def is_dead(self):
        return health <= 0

    def update(self, game_area_size, bullets):
        game_area_max_x, game_area_max_y = game_area_size
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

    def draw(self, win):
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
