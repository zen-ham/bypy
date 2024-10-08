import math, sys, pygame, random, pyperclip

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ByPy")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
player_coords = {}

clock = pygame.time.Clock()
FPS = 60
player_width, player_height = 50, 50
player_speed = 5
jump_strength = 15
gravity = 1
max_players = 8
player_hp = 100
wrecking_ball_radius = 30
chain_length = 150
wrecking_ball_mass = 0.5
wrecking_ball_friction = 0.95
font = pygame.font.SysFont('Arial', 24)
pvp_enabled = False
current_map = 'lobby'
yellow_block = pygame.Rect(WIDTH - 150, HEIGHT - 100, 100, 50)

def generate_random_map():
    platforms = []
    for _ in range(random.randint(3, 6)):
        width = random.randint(200, 400)
        height = 20
        x = random.randint(0, WIDTH - width)
        y = random.randint(HEIGHT // 3, HEIGHT - 100)
        platforms.append(pygame.Rect(x, y, width, height))
    return platforms

lobby_platforms = [
    pygame.Rect(200, HEIGHT - 100, 400, 20),
]
pvp_map_platforms = generate_random_map()

current_player_index = 0

class Player:
    def __init__(self, x, y, color, player_id):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.hp = player_hp
        self.rect = pygame.Rect(self.x, self.y, player_width, player_height)
        self.wrecking_ball_pos = (self.x, self.y + chain_length)
        self.wrecking_ball_vel = [0, 0]
        self.angle = 0
        self.player_id = player_id

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.vel_x = -player_speed
        elif keys[pygame.K_d]:
            self.vel_x = player_speed
        else:
            self.vel_x = 0

        if ((keys[pygame.K_SPACE]) or (keys[pygame.K_w])) and not self.is_jumping:
            self.vel_y = -jump_strength
            self.is_jumping = True

    def update(self, is_active):
        if not is_active:
            self.vel_x = 0
        self.vel_y += gravity
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.topleft = (self.x, self.y)

        self.update_wrecking_ball()
        self.handle_collisions()
        player_coords[self.player_id] = (self.x, self.y)
        if self.y + player_height > HEIGHT:
            self.y = HEIGHT - player_height
            self.vel_y = 0
            self.is_jumping = False

    def update_wrecking_ball(self):
        px, py = self.rect.center
        wx, wy = self.wrecking_ball_pos
        dx = wx - px
        dy = wy - py
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 0.01
        force = (dist - chain_length) * 0.05
        angle = math.atan2(dy, dx)
        self.wrecking_ball_vel[0] += -math.cos(angle) * force * wrecking_ball_mass
        self.wrecking_ball_vel[1] += -math.sin(angle) * force * wrecking_ball_mass + gravity
        if self.vel_x == 0 and self.vel_y == 0:
            self.wrecking_ball_vel[0] *= wrecking_ball_friction
            self.wrecking_ball_vel[1] *= wrecking_ball_friction
        wx += self.wrecking_ball_vel[0]
        wy += self.wrecking_ball_vel[1]
        self.wrecking_ball_pos = (wx, wy)

    def handle_collisions(self):
        platforms = lobby_platforms if current_map == 'lobby' else pvp_map_platforms
        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.vel_y > 0:
                if self.rect.bottom <= platform.top + self.vel_y:
                    self.y = platform.y - player_height
                    self.vel_y = 0
                    self.is_jumping = False
                    on_ground = True
        if not on_ground:
            self.is_jumping = True

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, player_width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, player_width * (self.hp / player_hp), 5))
        pygame.draw.line(screen, BLACK, self.rect.center, self.wrecking_ball_pos, 5)
        pygame.draw.circle(screen, BLACK, (int(self.wrecking_ball_pos[0]), int(self.wrecking_ball_pos[1])), wrecking_ball_radius)

def switch_player():
    global current_player_index
    if players:
        current_player_index = (current_player_index + 1) % len(players)

def add_player():
    if len(players) < max_players:
        new_x = 100 + len(players) * 100
        new_player = new_player = Player(new_x, HEIGHT - 150, [BLUE, RED, GREEN, BLACK][len(players) % 4], len(players))
        players.append(new_player)

def handle_pvp_collisions():
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            if wrecking_ball_hits_head(players[i], players[j]):
                players[j].hp -= 1

def wrecking_ball_hits_head(player, target):
    wx, wy = player.wrecking_ball_pos
    return target.rect.collidepoint(wx, wy)

def switch_to_pvp():
    global pvp_enabled, current_map
    pvp_enabled = True
    current_map = 'pvp_map'
    global pvp_map_platforms
    pvp_map_platforms = generate_random_map()

def check_for_pvp_start():
    global yellow_block
    if yellow_block and any(player.rect.colliderect(yellow_block) for player in players):
        yellow_block = None
        switch_to_pvp()

def display_player_coords():
    y_offset = 0
    for player_id, (x, y) in player_coords.items():
        print(player_coords)
        player = players[player_id]
        text = f"Player {player_id + 1}: ({x:.0f}, {y:.0f})"
        label = font.render(text, True, player.color)
        screen.blit(label, (10, 10 + y_offset))
        y_offset += 30

class TextBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = ''
        self.active = False
        self.FONT = pygame.font.Font(None, 36)
        self.txt_surface = self.FONT.render(self.text, True, self.color)
        self.max_length = 9

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (0, 255, 0) if self.active else (255, 255, 255)

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(f"Room code entered: {self.text}")
                    self.text = ''
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    pasted_text = pyperclip.paste()
                    allowed_text = pasted_text[:self.max_length - len(self.text)]
                    self.text += allowed_text
                elif len(self.text) < self.max_length:
                    self.text += event.unicode
                self.text = self.text[:self.max_length]

                self.txt_surface = self.FONT.render(self.text, True, self.color)
        return False

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 255, 0)
        self.text = text
        self.callback = callback
        self.FONT = pygame.font.Font(None, 36)
        self.txt_surface = self.FONT.render(self.text, True, (255, 255, 255))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

def host_room():
    print("Hosting room...")

def join_room():
    print("Joining Room...")

def room_selection_screen():
    screen_width, screen_height = screen.get_size()
    input_box_width, input_box_height = 200, 40
    host_button_width, host_button_height = 200, 50
    input_box_x = (screen_width - input_box_width) // 2
    input_box_y = screen_height // 2 - input_box_height - 20
    join_button_x = (screen_width - host_button_width) // 2
    join_button_y = screen_height // 2 + 20
    host_button_x = (screen_width - host_button_width) // 2
    host_button_y = screen_height // 2 + 100

    input_box = TextBox(input_box_x, input_box_y, input_box_width, input_box_height)
    join_button = Button("Join Room", join_button_x, join_button_y, host_button_width, host_button_height, join_room)
    host_button = Button("Host Room", host_button_x, host_button_y, host_button_width, host_button_height, host_room)

    selecting_room = True

    while selecting_room:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            room_code_entered = input_box.handle_event(event)
            join_button_clicked = join_button.handle_event(event)
            host_button_clicked = host_button.handle_event(event)

            if room_code_entered or host_button_clicked or join_button_clicked:
                selecting_room = False

        screen.fill((50, 50, 50))
        FONT = pygame.font.Font(None, 36)
        room_code_text = FONT.render("Enter Room Code:", True, WHITE)

        text_width, text_height = room_code_text.get_size()
        text_x = (screen_width - text_width) // 2
        text_y = input_box_y - text_height - 20

        screen.blit(room_code_text, (text_x, text_y))

        input_box.draw(screen)
        join_button.draw(screen)
        host_button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

players = []
yellow_block_exists = True

running = True
input_box = TextBox(200, 150, 200, 40)
host_button = Button("Host a Room", 200, 250, 200, 50, host_room)
def main_game():
    global yellow_block_exists

    running = True
    add_player()
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    switch_player()
                if event.key == pygame.K_i:
                    add_player()

        keys = pygame.key.get_pressed()
        for i, player in enumerate(players):
            if i == current_player_index:
                player.handle_input(keys)
            player.update(is_active=(i == current_player_index))

        if yellow_block_exists:
            check_for_pvp_start()

        if pvp_enabled:
            handle_pvp_collisions()

        for player in players:
            player.draw()

        platforms = lobby_platforms if current_map == 'lobby' else pvp_map_platforms
        for platform in platforms:
            pygame.draw.rect(screen, BLACK, platform)

        if yellow_block:
            pygame.draw.rect(screen, YELLOW, yellow_block)

        display_player_coords()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    room_selection_screen()
    main_game()

    pygame.quit()
