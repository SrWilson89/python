import pygame
import sys
import os
import time
import random
from ia_players import IAD, IAA, IAJ, IAF
from experience_logger import ExperienceLogger

def start_game(player1_name, player2_name):
    """
    Función principal para ejecutar el juego con las IAs seleccionadas.
    """
    pygame.init()

    # Configuración de la pantalla
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Pong - {player1_name} vs {player2_name}")

    # Colores y objetos del juego
    BLACK, WHITE = (0, 0, 0), (255, 255, 255)
    PALETA_WIDTH = 15
    BALL_SIZE = 15
    score_font = pygame.font.Font(None, 74)

    # Creación de las instancias de IA
    player_map = {"IAD": IAD, "IAA": IAA, "IAJ": IAJ, "IAF": IAF}
    
    p1_is_multi_paddle = player1_name == "IAF"
    p2_is_multi_paddle = player2_name == "IAF"

    if p1_is_multi_paddle:
        ia_player1 = player_map[player1_name](HEIGHT)
        player1_y = [HEIGHT // 2 - ia_player1.paddle_height, HEIGHT // 2]
    else:
        ia_player1 = player_map[player1_name](HEIGHT, 100)
        player1_y = HEIGHT // 2 - ia_player1.paddle_height // 2
    
    if p2_is_multi_paddle:
        ia_player2 = player_map[player2_name](HEIGHT)
        player2_y = [HEIGHT // 2 - ia_player2.paddle_height, HEIGHT // 2]
    else:
        ia_player2 = player_map[player2_name](HEIGHT, 100)
        player2_y = HEIGHT // 2 - ia_player2.paddle_height // 2

    p1_display_name = f"{player1_name}1" if player1_name == player2_name else player1_name
    p2_display_name = f"{player2_name}2" if player1_name == player2_name else player2_name
    
    clock = pygame.time.Clock()
    frames_this_point = 0

    # Variables de puntuación
    score_player1 = 0
    score_player2 = 0
    consecutive_score_player1 = 0
    consecutive_score_player2 = 0

    # Límite de tiempo (en segundos)
    TIME_LIMIT = 2 * 60
    start_time = time.time()
    
    balls = [{'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': random.choice([5, -5]), 'speed_y': random.choice([5, -5]), 'size': BALL_SIZE}]
    
    # Reinicia el logger y borra el archivo para cada nueva partida
    logger = ExperienceLogger(filename="game_log.json")
    logger.log_data = []
    
    running = True
    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time >= TIME_LIMIT:
            print("¡Juego terminado por límite de tiempo!")
            if frames_this_point > 0:
                ia_player1.register_point(frames_this_point)
                ia_player2.register_point(frames_this_point)
            running = False
        
        time_left = TIME_LIMIT - elapsed_time
        time_text = score_font.render(f"{int(time_left/60):02}:{int(time_left%60):02}", True, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Lógica de movimiento de las paletas
        if p1_is_multi_paddle:
            movement = ia_player1.move(balls[0]['y'], player1_y[0], player1_y[1])
            player1_y[0] += movement[0]
            player1_y[1] += movement[1]
        else:
            player1_y += ia_player1.move(balls[0]['y'], player1_y)
        
        if p2_is_multi_paddle:
            movement = ia_player2.move(balls[0]['y'], player2_y[0], player2_y[1])
            player2_y[0] += movement[0]
            player2_y[1] += movement[1]
        else:
            player2_y += ia_player2.move(balls[0]['y'], player2_y)
            
        # Limitar la posición de las paletas
        if p1_is_multi_paddle:
            player1_y[0] = max(0, min(HEIGHT - ia_player1.paddle_height*2 - 5, player1_y[0]))
            player1_y[1] = max(0, min(HEIGHT - ia_player1.paddle_height, player1_y[1]))
        else:
            player1_y = max(0, min(HEIGHT - ia_player1.paddle_height, player1_y))

        if p2_is_multi_paddle:
            player2_y[0] = max(0, min(HEIGHT - ia_player2.paddle_height*2 - 5, player2_y[0]))
            player2_y[1] = max(0, min(HEIGHT - ia_player2.paddle_height, player2_y[1]))
        else:
            player2_y = max(0, min(HEIGHT - ia_player2.paddle_height, player2_y))
        
        frames_this_point += 1
        
        balls_to_remove = []
        for ball in balls:
            ball['x'] += ball['speed_x']
            ball['y'] += ball['speed_y']
            
            if ball['y'] <= 0 or ball['y'] >= HEIGHT - ball['size']:
                ball['speed_y'] *= -1
                
            p1_collision = False
            if p1_is_multi_paddle:
                if pygame.Rect(10, player1_y[0], PALETA_WIDTH, ia_player1.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p1_collision = True
                if pygame.Rect(10, player1_y[1], PALETA_WIDTH, ia_player1.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p1_collision = True
            else:
                if pygame.Rect(10, player1_y, PALETA_WIDTH, ia_player1.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p1_collision = True
            
            p2_collision = False
            if p2_is_multi_paddle:
                if pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y[0], PALETA_WIDTH, ia_player2.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p2_collision = True
                if pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y[1], PALETA_WIDTH, ia_player2.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p2_collision = True
            else:
                if pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y, PALETA_WIDTH, ia_player2.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p2_collision = True

            if p1_collision:
                ball['speed_x'] *= -1
            if p2_collision:
                ball['speed_x'] *= -1

            if ball['x'] <= 0:
                score_player2 += 1
                consecutive_score_player2 += 1
                consecutive_score_player1 = 0
                balls_to_remove.append(ball)
            elif ball['x'] >= WIDTH - ball['size']:
                score_player1 += 1
                consecutive_score_player1 += 1
                consecutive_score_player2 = 0
                balls_to_remove.append(ball)
        
        if balls_to_remove:
            ia_player1.register_point(frames_this_point)
            ia_player2.register_point(frames_this_point)
            logger.log(p1_display_name.lower(), ia_player1.get_experience(final_score=1 if score_player1 > score_player2 else -1 if score_player2 > score_player1 else 0))
            logger.log(p2_display_name.lower(), ia_player2.get_experience(final_score=1 if score_player2 > score_player1 else -1 if score_player1 > score_player2 else 0))
            frames_this_point = 0
            
        for ball in balls_to_remove:
            balls.remove(ball)
            
        if not balls:
            balls.append({'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': random.choice([5, -5]), 'speed_y': random.choice([5, -5]), 'size': BALL_SIZE})

        if consecutive_score_player1 >= 5 or consecutive_score_player2 >= 5:
            print(f"¡{p1_display_name if consecutive_score_player1 >= 5 else p2_display_name} gana con 5 puntos consecutivos!")
            running = False

        # --- Dibujar en pantalla ---
        screen.fill(BLACK)
        if p1_is_multi_paddle:
            pygame.draw.rect(screen, WHITE, pygame.Rect(10, player1_y[0], PALETA_WIDTH, ia_player1.paddle_height))
            pygame.draw.rect(screen, WHITE, pygame.Rect(10, player1_y[1], PALETA_WIDTH, ia_player1.paddle_height))
        else:
            pygame.draw.rect(screen, WHITE, pygame.Rect(10, player1_y, PALETA_WIDTH, ia_player1.paddle_height))
        
        if p2_is_multi_paddle:
            pygame.draw.rect(screen, WHITE, pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y[0], PALETA_WIDTH, ia_player2.paddle_height))
            pygame.draw.rect(screen, WHITE, pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y[1], PALETA_WIDTH, ia_player2.paddle_height))
        else:
            pygame.draw.rect(screen, WHITE, pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y, PALETA_WIDTH, ia_player2.paddle_height))
            

        for ball in balls:
            pygame.draw.ellipse(screen, WHITE, pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size']))
            
        score_text = score_font.render(f"{score_player1} - {score_player2}", True, WHITE)
        screen.blit(score_text, (WIDTH/2 - score_text.get_width()/2, 10))

        screen.blit(time_text, (WIDTH/2 - time_text.get_width()/2, 50)) 

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    logger.save_log()
    logger.analyze_and_report()

# --- Interfaz de selección de rivales ---
if __name__ == "__main__":
    rival_options = ["IAD", "IAA", "IAJ", "IAF"]
    
    print("Selecciona el primer jugador:")
    for i, option in enumerate(rival_options):
        print(f"{i+1}. {option}")
    
    while True:
        try:
            choice1 = int(input("Introduce el número del jugador 1: "))
            if 1 <= choice1 <= len(rival_options):
                player1_name = rival_options[choice1-1]
                break
            else:
                print("Opción no válida. Inténtalo de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número.")
            
    print("\nSelecciona el segundo jugador:")
    for i, option in enumerate(rival_options):
        print(f"{i+1}. {option}")
        
    while True:
        try:
            choice2 = int(input("Introduce el número del jugador 2: "))
            if 1 <= choice2 <= len(rival_options):
                player2_name = rival_options[choice2-1]
                break
            else:
                print("Opción no válida. Inténtalo de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número.")
    
    print(f"\n¡Comienza la batalla: {player1_name} vs {player2_name}!")
    start_game(player1_name, player2_name)