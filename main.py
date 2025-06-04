import pygame
import random
import sys
import math

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Climb High")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
big_font = pygame.font.SysFont("Arial", 32, bold=True)
title_font = pygame.font.SysFont("Arial", 42, bold=True)

# Farben - Clean und hell
SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (255, 255, 255)
PLATFORM_GREEN = (34, 139, 34)
PLATFORM_DARK = (0, 100, 0)
PLATFORM_SPECIAL = (255, 215, 0)  # Gold für spezielle Plattformen
PLAYER_BLUE = (30, 144, 255)
PLAYER_RED = (220, 20, 60)
PLAYER_YELLOW = (255, 215, 0)
PLAYER_BROWN = (139, 69, 19)
PLAYER_SKIN = (255, 220, 177)
UI_WHITE = (255, 255, 255)
UI_BLACK = (0, 0, 0)
SHADOW_GRAY = (200, 200, 200)
COIN_GOLD = (255, 215, 0)
POWER_UP_PURPLE = (147, 0, 211)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Spieler - jetzt größer!
player_width = 40
player_height = 48
player = pygame.Rect(WIDTH // 2, HEIGHT - 60, player_width, player_height)
player_vy = 0
jump_strength = -15
gravity = 0.5
move_speed = 6
player_facing_right = True
player_animation_frame = 0

# Spiel-Features
coins = []
power_ups = []
coin_count = 0
bounce_platforms = []
moving_platforms = []
particle_effects = []

# Wolken für Hintergrund
clouds = []
for i in range(8):
    x = random.randint(-50, WIDTH + 50)
    y = random.randint(50, HEIGHT - 100)
    size = random.randint(40, 80)
    speed = random.uniform(0.2, 0.8)
    clouds.append({'x': x, 'y': y, 'size': size, 'speed': speed})

# Plattformen
platforms = []
score = 0
high_score = 0
time_counter = 0

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.animation = 0
    
    def update(self):
        self.animation += 0.2
    
    def draw(self):
        if not self.collected:
            # Goldmünze mit Animation
            size = 12 + math.sin(self.animation) * 2
            pygame.draw.circle(screen, COIN_GOLD, (int(self.x), int(self.y)), int(size))
            pygame.draw.circle(screen, UI_BLACK, (int(self.x), int(self.y)), int(size), 2)
            # "$" Symbol
            font_small = pygame.font.SysFont("Arial", 12, bold=True)
            coin_text = font_small.render("$", True, UI_BLACK)
            text_rect = coin_text.get_rect(center=(self.x, self.y))
            screen.blit(coin_text, text_rect)

class PowerUp:
    def __init__(self, x, y, type="speed"):
        self.x = x
        self.y = y
        self.type = type
        self.collected = False
        self.animation = 0
    
    def update(self):
        self.animation += 0.1
        self.y += math.sin(self.animation) * 0.5
    
    def draw(self):
        if not self.collected:
            # Power-Up Box
            size = 16
            box_rect = pygame.Rect(self.x - size//2, self.y - size//2, size, size)
            pygame.draw.rect(screen, POWER_UP_PURPLE, box_rect)
            pygame.draw.rect(screen, UI_BLACK, box_rect, 2)
            # "!" Symbol
            font_small = pygame.font.SysFont("Arial", 12, bold=True)
            text = font_small.render("!", True, UI_WHITE)
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)

class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 30
        self.max_life = 30
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
    
    def draw(self):
        if self.life > 0:
            size = max(1, int(4 * (self.life / self.max_life)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

def create_jump_particles(x, y):
    for _ in range(6):
        velocity = (random.uniform(-2, 2), random.uniform(-2, 0))
        color = random.choice([PLATFORM_GREEN, UI_WHITE, SKY_BLUE])
        particle_effects.append(Particle(x, y, color, velocity))

def create_coin_particles(x, y):
    for _ in range(8):
        velocity = (random.uniform(-3, 3), random.uniform(-3, -1))
        particle_effects.append(Particle(x, y, COIN_GOLD, velocity))

def draw_cloud(x, y, size):
    """Zeichne eine einfache, cleane Wolke"""
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x), int(y)), int(size * 0.6))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x - size * 0.4), int(y)), int(size * 0.4))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x + size * 0.4), int(y)), int(size * 0.4))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x - size * 0.2), int(y - size * 0.3)), int(size * 0.35))
    pygame.draw.circle(screen, CLOUD_WHITE, (int(x + size * 0.2), int(y - size * 0.3)), int(size * 0.35))

def draw_background():
    """Zeichne cleanen Himmel mit Wolken"""
    screen.fill(SKY_BLUE)
    
    for cloud in clouds:
        draw_cloud(cloud['x'], cloud['y'], cloud['size'])
        cloud['x'] += cloud['speed']
        
        if cloud['x'] > WIDTH + cloud['size']:
            cloud['x'] = -cloud['size']

def draw_enhanced_mario():
    """Zeichne größeren, detaillierten Mario-Charakter"""
    x, y = player.x, player.y
    
    # Animation
    player_animation_frame = int(time_counter * 0.3) % 4
    walk_offset = 1 if player_animation_frame < 2 else -1
    
    # Schatten
    pygame.draw.ellipse(screen, SHADOW_GRAY, (x + 4, y + player_height - 4, player_width - 8, 8))
    
    # Füße (Schuhe)
    if player_facing_right:
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 2, y + 40, 12, 8))
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 26, y + 40, 12, 8))
    else:
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 2, y + 40, 12, 8))
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 26, y + 40, 12, 8))
    
    # Beine (blaue Hose)
    leg_rect = pygame.Rect(x + 8, y + 28, 24, 16)
    pygame.draw.rect(screen, PLAYER_BLUE, leg_rect)
    
    # Körper/Shirt (rot)
    body_rect = pygame.Rect(x + 4, y + 16, 32, 20)
    pygame.draw.rect(screen, PLAYER_RED, body_rect)
    
    # Träger (gelb)
    pygame.draw.rect(screen, PLAYER_YELLOW, (x + 12, y + 18, 6, 12))
    pygame.draw.rect(screen, PLAYER_YELLOW, (x + 22, y + 18, 6, 12))
    
    # Arme
    if player_facing_right:
        # Rechter Arm
        pygame.draw.rect(screen, PLAYER_SKIN, (x + 32, y + 20, 8, 12))
        # Linker Arm (hinter Körper)
        pygame.draw.rect(screen, PLAYER_SKIN, (x - 4, y + 22, 8, 10))
    else:
        # Linker Arm
        pygame.draw.rect(screen, PLAYER_SKIN, (x - 4, y + 20, 8, 12))
        # Rechter Arm (hinter Körper)
        pygame.draw.rect(screen, PLAYER_SKIN, (x + 32, y + 22, 8, 10))
    
    # Kopf
    head_rect = pygame.Rect(x + 8, y + 4, 24, 20)
    pygame.draw.rect(screen, PLAYER_SKIN, head_rect)
    
    # Mütze
    hat_rect = pygame.Rect(x + 6, y, 28, 12)
    pygame.draw.rect(screen, PLAYER_RED, hat_rect)
    
    # Mützen-Schirm
    if player_facing_right:
        pygame.draw.rect(screen, PLAYER_RED, (x + 30, y + 6, 8, 6))
    else:
        pygame.draw.rect(screen, PLAYER_RED, (x + 2, y + 6, 8, 6))
    
    # Augen
    if player_facing_right:
        pygame.draw.circle(screen, UI_BLACK, (x + 16, y + 12), 3)
        pygame.draw.circle(screen, UI_BLACK, (x + 24, y + 12), 3)
        # Pupillen
        pygame.draw.circle(screen, UI_WHITE, (x + 17, y + 11), 1)
        pygame.draw.circle(screen, UI_WHITE, (x + 25, y + 11), 1)
    else:
        pygame.draw.circle(screen, UI_BLACK, (x + 16, y + 12), 3)
        pygame.draw.circle(screen, UI_BLACK, (x + 24, y + 12), 3)
        pygame.draw.circle(screen, UI_WHITE, (x + 15, y + 11), 1)
        pygame.draw.circle(screen, UI_WHITE, (x + 23, y + 11), 1)
    
    # Nase
    pygame.draw.circle(screen, (255, 200, 150), (x + 20, y + 16), 2)
    
    # Schnurrbart
    if player_facing_right:
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 14, y + 18, 12, 3))
    else:
        pygame.draw.rect(screen, PLAYER_BROWN, (x + 14, y + 18, 12, 3))
    
    # "M" auf der Mütze
    m_font = pygame.font.SysFont("Arial", 12, bold=True)
    m_text = m_font.render("M", True, UI_WHITE)
    m_rect = m_text.get_rect(center=(x + 20, y + 6))
    screen.blit(m_text, m_rect)

def draw_enhanced_platforms():
    """Zeichne verschiedene Plattform-Typen"""
    for i, platform in enumerate(platforms):
        # Schatten
        shadow_rect = pygame.Rect(platform.x + 2, platform.y + 2, platform.width, platform.height)
        pygame.draw.rect(screen, SHADOW_GRAY, shadow_rect)
        
        # Bestimme Plattform-Typ
        if i in bounce_platforms:
            # Sprungfeder-Plattform
            pygame.draw.rect(screen, PLATFORM_SPECIAL, platform)
            pygame.draw.rect(screen, UI_BLACK, platform, 2)
            # Sprungfeder-Symbol
            spring_x = platform.centerx
            pygame.draw.line(screen, UI_BLACK, (spring_x - 10, platform.y + 5), (spring_x + 10, platform.y + 5), 3)
            pygame.draw.line(screen, UI_BLACK, (spring_x - 8, platform.y + 8), (spring_x + 8, platform.y + 8), 2)
            pygame.draw.line(screen, UI_BLACK, (spring_x - 6, platform.y + 11), (spring_x + 6, platform.y + 11), 2)
        elif i in moving_platforms:
            # Bewegliche Plattform
            pygame.draw.rect(screen, (100, 100, 255), platform)
            pygame.draw.rect(screen, UI_BLACK, platform, 2)
            # Pfeil-Symbole
            pygame.draw.polygon(screen, UI_WHITE, [(platform.x + 10, platform.centery), 
                                                 (platform.x + 20, platform.centery - 5), 
                                                 (platform.x + 20, platform.centery + 5)])
            pygame.draw.polygon(screen, UI_WHITE, [(platform.right - 10, platform.centery), 
                                                 (platform.right - 20, platform.centery - 5), 
                                                 (platform.right - 20, platform.centery + 5)])
        else:
            # Normale Plattform
            pygame.draw.rect(screen, PLATFORM_GREEN, platform)
            pygame.draw.rect(screen, PLATFORM_DARK, platform, 2)
            
            # Gras-Textur
            for grass_x in range(platform.x + 5, platform.right - 5, 8):
                pygame.draw.line(screen, (60, 179, 60), (grass_x, platform.y), (grass_x, platform.y - 3), 2)
                pygame.draw.line(screen, (60, 179, 60), (grass_x + 2, platform.y), (grass_x + 2, platform.y - 2), 1)

def draw_enhanced_ui():
    """Zeichne verbessertes UI mit Münzen"""
    # Haupt UI Box
    ui_bg = pygame.Rect(10, 10, 200, 80)
    pygame.draw.rect(screen, UI_WHITE, ui_bg)
    pygame.draw.rect(screen, UI_BLACK, ui_bg, 3)
    
    # Score
    score_text = font.render(f"Score: {int(score)}", True, UI_BLACK)
    screen.blit(score_text, (15, 15))
    
    # High Score
    high_score_text = font.render(f"Best: {int(high_score)}", True, UI_BLACK)
    screen.blit(high_score_text, (15, 40))
    
    # Münzen
    coin_text = font.render(f"Coins: {coin_count}", True, COIN_GOLD)
    screen.blit(coin_text, (15, 65))
    
    # Münz-Symbol
    pygame.draw.circle(screen, COIN_GOLD, (180, 72), 8)
    pygame.draw.circle(screen, UI_BLACK, (180, 72), 8, 2)
    coin_symbol = pygame.font.SysFont("Arial", 10, bold=True).render("$", True, UI_BLACK)
    symbol_rect = coin_symbol.get_rect(center=(180, 72))
    screen.blit(coin_symbol, symbol_rect)

def draw_menu():
    """Zeichne verbessertes Start-Menü"""
    draw_background()
    
    # Titel mit Schatten
    title_shadow = title_font.render("CLIMB HIGH", True, UI_BLACK)
    title_text = title_font.render("CLIMB HIGH", True, UI_WHITE)
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    
    title_bg = pygame.Rect(title_rect.x - 15, title_rect.y - 10, title_rect.width + 30, title_rect.height + 20)
    pygame.draw.rect(screen, PLAYER_RED, title_bg)
    pygame.draw.rect(screen, UI_BLACK, title_bg, 4)
    
    screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
    screen.blit(title_text, title_rect)
    
    # Start Button mit Animation
    pulse = 1 + 0.1 * math.sin(time_counter * 0.1)
    start_text = big_font.render("Press SPACE to Start", True, UI_BLACK)
    start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    start_bg = pygame.Rect(start_rect.x - 15, start_rect.y - 8, start_rect.width + 30, start_rect.height + 16)
    
    # Pulsierender Effekt
    pygame.draw.rect(screen, (
        max(0, min(255, int(UI_WHITE[0] * pulse))),
        max(0, min(255, int(UI_WHITE[1] * pulse))),
        max(0, min(255, int(UI_WHITE[2] * pulse)))
    ), start_bg)
    pygame.draw.rect(screen, UI_BLACK, start_bg, 3)
    screen.blit(start_text, start_rect)

def draw_game_over():
    """Zeichne Game Over Screen mit Statistiken"""
    draw_background()
    
    # Game Over mit Schatten
    game_over_shadow = title_font.render("GAME OVER", True, UI_BLACK)
    game_over_text = title_font.render("GAME OVER", True, UI_WHITE)
    game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    game_over_bg = pygame.Rect(game_over_rect.x - 20, game_over_rect.y - 15, game_over_rect.width + 40, game_over_rect.height + 30)
    
    pygame.draw.rect(screen, PLAYER_RED, game_over_bg)
    pygame.draw.rect(screen, UI_BLACK, game_over_bg, 4)
    screen.blit(game_over_shadow, (game_over_rect.x + 3, game_over_rect.y + 3))
    screen.blit(game_over_text, game_over_rect)
    
    # Statistiken Box
    stats_y = HEIGHT//2 - 20
    stats = [
        f"Final Score: {int(score)}",
        f"Coins Collected: {coin_count}",
        f"Best Score: {int(high_score)}"
    ]
    
    for i, stat in enumerate(stats):
        stat_text = font.render(stat, True, UI_BLACK)
        stat_rect = stat_text.get_rect(center=(WIDTH//2, stats_y + i * 25))
        stat_bg = pygame.Rect(stat_rect.x - 10, stat_rect.y - 5, stat_rect.width + 20, stat_rect.height + 10)
        pygame.draw.rect(screen, UI_WHITE, stat_bg)
        pygame.draw.rect(screen, UI_BLACK, stat_bg, 2)
        screen.blit(stat_text, stat_rect)

def spawn_collectibles():
    """Spawne Münzen und Power-Ups auf Plattformen"""
    for i, platform in enumerate(platforms):
        if random.randint(1, 100) < 3:  # 3% Chance für Münze
            coin_x = random.randint(platform.x + 10, platform.right - 10)
            coin_y = platform.y - 20
            coins.append(Coin(coin_x, coin_y))
        
        if random.randint(1, 100) < 1:  # 1% Chance für Power-Up
            power_x = random.randint(platform.x + 10, platform.right - 10)
            power_y = platform.y - 25
            power_ups.append(PowerUp(power_x, power_y))

def reset_game():
    """Spiel zurücksetzen"""
    global player, player_vy, platforms, score, coins, power_ups, coin_count
    global bounce_platforms, moving_platforms, particle_effects
    
    player.x = WIDTH // 2 - player_width // 2
    player_vy = 0
    score = 0
    coin_count = 0
    
    platforms.clear()
    coins.clear()
    power_ups.clear()
    particle_effects.clear()
    bounce_platforms.clear()
    moving_platforms.clear()
    
    # Startplattform
    start_platform = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 60, 120, 20)
    platforms.append(start_platform)
    
    player.y = start_platform.y - player.height
    
    # Weitere Plattformen mit verschiedenen Typen
    for i in range(1, 8):
        x = random.randint(0, WIDTH - 100)
        y = HEIGHT - i * 80
        width = random.randint(80, 120)
        platforms.append(pygame.Rect(x, y, width, 20))
        
        # Spezielle Plattformen
        if random.randint(1, 10) < 3:  # 30% Chance für Sprungfeder
            bounce_platforms.append(i)
        elif random.randint(1, 10) < 2:  # 20% Chance für bewegliche Plattform
            moving_platforms.append(i)

# Spiel initialisieren
reset_game()

# Game Loop
running = True
while running:
    time_counter += 1
    clock.tick(60)
    
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == MENU:
                    game_state = PLAYING
                    reset_game()
                elif game_state == GAME_OVER:
                    game_state = PLAYING
                    reset_game()
            elif event.key == pygame.K_ESCAPE:
                if game_state == GAME_OVER:
                    game_state = MENU
    
    if game_state == PLAYING:
        # Bewegung
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= move_speed
            player_facing_right = False
        if keys[pygame.K_RIGHT]:
            player.x += move_speed
            player_facing_right = True
        
        # Bildschirmgrenzen
        if player.right < 0:
            player.left = WIDTH
        elif player.left > WIDTH:
            player.right = 0
        
        # Bewegliche Plattformen
        for i in moving_platforms:
            if i < len(platforms):
                platform = platforms[i]
                platform.x += math.sin(time_counter * 0.05 + i) * 2
                platform.x = max(0, min(WIDTH - platform.width, platform.x))
        
        # Physik
        player_vy += gravity
        player.y += player_vy
        
        # Plattform-Kollision
        if player_vy > 0:
            for i, platform in enumerate(platforms):
                if player.colliderect(platform) and player.bottom <= platform.bottom + player_vy:
                    player.bottom = platform.top
                    
                    if i in bounce_platforms:
                        player_vy = jump_strength * 1.5  # Stärkerer Sprung
                        create_jump_particles(player.centerx, player.bottom)
                    else:
                        player_vy = jump_strength
                        create_jump_particles(player.centerx, player.bottom)
        
        # Münzen sammeln
        for coin in coins[:]:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x - 15, coin.y - 15, 30, 30)
                if player.colliderect(coin_rect):
                    coin.collected = True
                    coin_count += 1
                    score += 50
                    create_coin_particles(coin.x, coin.y)
                    coins.remove(coin)
                else:
                    coin.update()
        
        # Power-Ups sammeln
        for power_up in power_ups[:]:
            if not power_up.collected:
                power_rect = pygame.Rect(power_up.x - 16, power_up.y - 16, 32, 32)
                if player.colliderect(power_rect):
                    power_up.collected = True
                    score += 100
                    # Temporärer Geschwindigkeitsboost
                    move_speed = min(8, move_speed + 1)
                    power_ups.remove(power_up)
                else:
                    power_up.update()
        
        # Partikel aktualisieren
        for particle in particle_effects[:]:
            particle.update()
            if particle.life <= 0:
                particle_effects.remove(particle)
        
        # Kamera-Effekt
        if player.y < HEIGHT // 2:
            offset = HEIGHT // 2 - player.y
            player.y = HEIGHT // 2
            score += offset * 0.1
            
            for platform in platforms:
                platform.y += offset
            
            for coin in coins:
                coin.y += offset
            
            for power_up in power_ups:
                power_up.y += offset
        
        # Neue Plattformen und Collectibles
        while len(platforms) < 12:
            last_y = min(p.y for p in platforms)
            new_x = random.randint(0, WIDTH - 120)
            new_y = last_y - random.randint(60, 100)
            width = random.randint(80, 120)
            platforms.append(pygame.Rect(new_x, new_y, width, 20))
            
            # Spezielle Plattformen
            new_index = len(platforms) - 1
            if random.randint(1, 10) < 3:
                bounce_platforms.append(new_index)
            elif random.randint(1, 10) < 2:
                moving_platforms.append(new_index)
        
        spawn_collectibles()
        
        # Objekte entfernen die zu weit unten sind
        platforms = [p for p in platforms if p.y < HEIGHT + 50]
        coins = [c for c in coins if c.y < HEIGHT + 100]
        power_ups = [p for p in power_ups if p.y < HEIGHT + 100]

        # Indices für spezielle Plattformen aktualisieren
        bounce_platforms = [i for i in bounce_platforms if i < len(platforms)]
        moving_platforms = [i for i in moving_platforms if i < len(platforms)]   
             
        # Game Over
        if player.top > HEIGHT:
            if score > high_score:
                high_score = score
            game_state = GAME_OVER
        
        # Zeichnen
        draw_background()
        draw_enhanced_platforms()
        
        # Collectibles zeichnen
        for coin in coins:
            coin.draw()
        for power_up in power_ups:
            power_up.draw()
        
        # Partikel zeichnen
        for particle in particle_effects:
            particle.draw()
        
        draw_enhanced_mario()
        draw_enhanced_ui()
    
    elif game_state == MENU:
        draw_menu()
    
    elif game_state == GAME_OVER:
        draw_game_over()
    
    pygame.display.flip()

pygame.quit()
sys.exit()