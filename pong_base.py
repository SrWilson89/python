import pygame
import sys
from ia_players import IAD, IAA

# Inicializar Pygame
pygame.init()

# --- Configuración de la pantalla ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong IA")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# --- Objetos del juego ---
# Paletas
PALETA_WIDTH, PALETA_HEIGHT = 15, 100
player_y = HEIGHT // 2 - PALETA_HEIGHT // 2
opponent_y = HEIGHT // 2 - PALETA_HEIGHT // 2

# Pelota
BALL_SIZE = 15
ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
ball_speed_x, ball_speed_y = 5, 5

# --- Creación de las IAs ---
# Elige qué IAs quieres que jueguen
# Por ejemplo, IAD vs IAA:
ia_jugador_1 = IAD(HEIGHT, PALETA_HEIGHT)
ia_jugador_2 = IAA(HEIGHT, PALETA_HEIGHT)

# Si quieres IAD vs IAD:
# ia_jugador_1 = IAD(HEIGHT, PALETA_HEIGHT)
# ia_jugador_2 = IAD(HEIGHT, PALETA_HEIGHT)

# Si quieres IAA vs IAA:
# ia_jugador_1 = IAA(HEIGHT, PALETA_HEIGHT)
# ia_jugador_2 = IAA(HEIGHT, PALETA_HEIGHT)

# --- Bucle principal del juego ---
running = True
clock = pygame.time.Clock()

while running:
    # Manejar eventos (cerrar ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Lógica de movimiento de las IA ---
    player_y += ia_jugador_1.move(ball_y, player_y)
    opponent_y += ia_jugador_2.move(ball_y, opponent_y)
    
    # Limitar el movimiento de las paletas para que no salgan de la pantalla
    if player_y < 0:
        player_y = 0
    if player_y > HEIGHT - PALETA_HEIGHT:
        player_y = HEIGHT - PALETA_HEIGHT
    
    if opponent_y < 0:
        opponent_y = 0
    if opponent_y > HEIGHT - PALETA_HEIGHT:
        opponent_y = HEIGHT - PALETA_HEIGHT

    # --- Lógica de movimiento de la pelota ---
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Colisiones de la pelota con las paredes superiores e inferiores
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_speed_y *= -1

    # Colisiones de la pelota con las paletas
    player_rect = pygame.Rect(10, player_y, PALETA_WIDTH, PALETA_HEIGHT)
    if player_rect.colliderect(pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)):
        ball_speed_x *= -1
        
    opponent_rect = pygame.Rect(WIDTH - 10 - PALETA_WIDTH, opponent_y, PALETA_WIDTH, PALETA_HEIGHT)
    if opponent_rect.colliderect(pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)):
        ball_speed_x *= -1

    # Puntos
    if ball_x <= 0 or ball_x >= WIDTH - BALL_SIZE:
        ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
        ball_speed_x *= -1

    # --- Dibujar en pantalla ---
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player_rect)
    pygame.draw.rect(screen, WHITE, opponent_rect)
    pygame.draw.ellipse(screen, WHITE, pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE))

    # Actualizar la pantalla
    pygame.display.flip()

    # Limitar los FPS para que el juego no corra demasiado rápido
    clock.tick(60)