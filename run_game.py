import pygame
import sys
import os
import time
import random
import json
import traceback
from ia_players import IA, IAD, IAA, IAJ, IAF, IAC, IAL, IAM, IAR
from experience_logger import ExperienceLogger

# Mapeo de IA a colores
IA_COLORS = {
    "IAD": (255, 0, 0),    # Rojo
    "IAA": (0, 200, 255),  # Azul Claro
    "IAJ": (128, 0, 128),  # Morado
    "IAF": (255, 165, 0),  # Naranja
    "IAC": (100, 100, 100), # Gris oscuro
    "IAL": (0, 0, 139),     # Azul oscuro
    "IAM": (255, 215, 0),      # Dorado
    "IAR": (192, 192, 192)    # Plateado
}

def start_game(player1, player2, player1_name, player2_name, time_limit=60, consecutive_score_limit=1, point_score_limit=1, diablo_mode=False, diablo_round=0, diablo_points=0, diablo_victories=0, ball_speed=4, game_mode="default"):
    # Inicialización del juego y de las variables
    global last_point_time, start_game_time, current_player1_score, current_player2_score, consecutive_scores_player1, consecutive_scores_player2, last_winner
    global ball_speed_boost, ball_speed_normal
    global initial_ball_speed, ball_speeds, ball_speed_history

    screen_width = 800
    screen_height = 600
    paddle_width = 15
    paddle_height = 100
    ball_size = 15
    
    # Colores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Inicialización de la pantalla
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Diablo Pong")
    
    # Configuración de los paddles
    player1_x = 10
    player1_y = (screen_height - paddle_height) // 2
    
    player2_x = screen_width - paddle_width - 10
    player2_y = (screen_height - paddle_height) // 2
    
    # Configuración de las pelotas
    balls = [{'x': screen_width // 2, 'y': screen_height // 2, 'speed_x': random.choice([-ball_speed, ball_speed]), 'speed_y': random.choice([-ball_speed, ball_speed])}]
    
    # Puntuaciones
    score_player1 = 0
    score_player2 = 0
    
    # Contador de frames
    frame_counter_player1 = 0
    frame_counter_player2 = 0
    
    running = True
    clock = pygame.time.Clock()
    
    last_point_time = time.time()
    game_start_time = time.time()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Movimiento de la IA (Corregido)
        # Se verifica si la IA es de tipo IAA o IAL para pasarle los argumentos correctos
        if isinstance(player1, (IAA, IAL)):
            player1_y += player1.move(balls[0]['y'], player1_y, balls[0]['x'], balls[0]['speed_x'], balls[0]['speed_y'])
        else:
            player1_y += player1.move(balls[0]['y'], player1_y)
        
        if isinstance(player2, (IAA, IAL)):
            player2_y += player2.move(balls[0]['y'], player2_y, balls[0]['x'], balls[0]['speed_x'], balls[0]['speed_y'])
        else:
            player2_y += player2.move(balls[0]['y'], player2_y)

        # Asegurar que las paletas no salgan de la pantalla
        player1_y = max(min(player1_y, screen_height - paddle_height), 0)
        player2_y = max(min(player2_y, screen_height - paddle_height), 0)

        # Lógica de la pelota
        for ball in balls:
            ball['x'] += ball['speed_x']
            ball['y'] += ball['speed_y']

            # Colisiones con el techo y el suelo
            if ball['y'] <= 0 or ball['y'] >= screen_height - ball_size:
                ball['speed_y'] = -ball['speed_y']

            # Colisiones con el paddle del jugador 1
            if player1_x <= ball['x'] <= player1_x + paddle_width and player1_y <= ball['y'] <= player1_y + paddle_height:
                ball['speed_x'] = abs(ball['speed_x'])
                
            # Colisiones con el paddle del jugador 2
            if player2_x <= ball['x'] <= player2_x + paddle_width and player2_y <= ball['y'] <= player2_y + paddle_height:
                ball['speed_x'] = -abs(ball['speed_x'])

            # Puntos
            if ball['x'] < 0:
                score_player2 += 1
                if isinstance(player2, IA):
                    player2.register_point(frame_counter_player2)
                ball['x'] = screen_width // 2
                ball['y'] = screen_height // 2
                ball['speed_x'] = random.choice([-ball_speed, ball_speed])
                ball['speed_y'] = random.choice([-ball_speed, ball_speed])
                frame_counter_player1 = 0
                frame_counter_player2 = 0
            
            if ball['x'] > screen_width:
                score_player1 += 1
                if isinstance(player1, IA):
                    player1.register_point(frame_counter_player1)
                ball['x'] = screen_width // 2
                ball['y'] = screen_height // 2
                ball['speed_x'] = random.choice([-ball_speed, ball_speed])
                ball['speed_y'] = random.choice([-ball_speed, ball_speed])
                frame_counter_player1 = 0
                frame_counter_player2 = 0

        # Renderizado
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (player1_x, player1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, WHITE, (player2_x, player2_y, paddle_width, paddle_height))
        
        for ball in balls:
            pygame.draw.rect(screen, WHITE, (ball['x'], ball['y'], ball_size, ball_size))

        font = pygame.font.Font(None, 74)
        text_player1 = font.render(str(score_player1), True, WHITE)
        text_player2 = font.render(str(score_player2), True, WHITE)
        screen.blit(text_player1, (screen_width / 4, 10))
        screen.blit(text_player2, (screen_width * 3 / 4, 10))

        pygame.display.flip()
        
        frame_counter_player1 += 1
        frame_counter_player2 += 1
        
        # Lógica de fin de partida
        if score_player1 >= point_score_limit or score_player2 >= point_score_limit or time.time() - game_start_time > time_limit:
            if score_player1 > score_player2:
                return 1, score_player1, score_player2
            elif score_player2 > score_player1:
                return -1, score_player1, score_player2
            else:
                return 0, score_player1, score_player2
        
        clock.tick(60)
    
    pygame.quit()
    sys.exit()    
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
    ui_font = pygame.font.Font(None, 36)

    # Colores de los jugadores
    player1_color = IA_COLORS.get(player1_name, WHITE)
    player2_color = IA_COLORS.get(player2_name, WHITE)

    # Creación de las instancias de IA
    p1_is_multi_paddle = player1_name == "IAF"
    p2_is_multi_paddle = player2_name == "IAF"
    
    p1_is_iaj = player1_name == "IAJ"
    p2_is_iaj = player2_name == "IAJ"
    
    p1_is_ial = player1_name == "IAL"
    p2_is_ial = player2_name == "IAL"

    if p1_is_multi_paddle:
        player1_y = [i * (player1.paddle_height + 5) for i in range(5)]
    else:
        player1_y = HEIGHT // 2 - player1.paddle_height // 2
    
    if p2_is_multi_paddle:
        player2_y = [i * (player2.paddle_height + 5) for i in range(5)]
    else:
        player2_y = HEIGHT // 2 - player2.paddle_height // 2

    p1_display_name = f"{player1_name}1" if player1_name == player2_name else player1_name
    p2_display_name = f"{player2_name}2" if player1_name == player2_name else player2_name
    
    clock = pygame.time.Clock()
    frames_this_point = 0

    score_player1 = 0
    score_player2 = 0
    consecutive_score_player1 = 0
    consecutive_score_player2 = 0
    
    start_time = time.time()
    
    initial_ball_speed_x = random.choice([ball_speed, -ball_speed])
    initial_ball_speed_y = random.choice([ball_speed, -ball_speed])
    balls = [{'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': initial_ball_speed_x, 'speed_y': initial_ball_speed_y, 'size': BALL_SIZE}]
    
    logger = ExperienceLogger(filename="game_log.json")
    logger.log_data = []
    
    running = True
    while running:
        elapsed_time = time.time() - start_time
        
        if elapsed_time >= time_limit:
            print("¡Juego terminado por límite de tiempo!")
            # Se llama a register_point y get_experience para ambos jugadores
            player1.register_point(frames_this_point)
            player2.register_point(frames_this_point)
            
            if score_player1 > score_player2:
                winner = player1_name
            elif score_player2 > score_player1:
                winner = player2_name
            else:
                winner = "Empate"
            
            logger.log(p1_display_name.lower(), player1.get_experience(final_score=1 if score_player1 > score_player2 else -1 if score_player2 > score_player1 else 0))
            logger.log(p2_display_name.lower(), player2.get_experience(final_score=1 if score_player2 > score_player1 else -1 if score_player1 > score_player2 else 0))
            logger.save_log()
            
            running = False
            return winner, score_player1, score_player2

        time_left = time_limit - elapsed_time
        time_text = score_font.render(f"{int(time_left/60):02}:{int(time_left%60):02}", True, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, 0, 0
        
        if p1_is_multi_paddle:
            movement = player1.move(balls[0]['y'], player1_y)
            player1_y = [player1_y[i] + movement[i] for i in range(len(player1_y))]
        elif p1_is_ial:
            player1_y += player1.move(balls[0]['y'], player1_y, balls[0]['x'], balls[0]['speed_x'], balls[0]['speed_y'])
        else:
            player1_y += player1.move(balls[0]['y'], player1_y)
        
        if p2_is_multi_paddle:
            movement = player2.move(balls[0]['y'], player2_y)
            player2_y = [player2_y[i] + movement[i] for i in range(len(player2_y))]
        elif p2_is_ial:
            player2_y += player2.move(balls[0]['y'], player2_y, balls[0]['x'], balls[0]['speed_x'], balls[0]['speed_y'])
        else:
            player2_y += player2.move(balls[0]['y'], player2_y)

        if p1_is_multi_paddle:
            for i in range(len(player1_y)):
                player1_y[i] = max(0, min(HEIGHT - player1.paddle_height, player1_y[i]))
        else:
            player1_y = max(0, min(HEIGHT - player1.paddle_height, player1_y))

        if p2_is_multi_paddle:
            for i in range(len(player2_y)):
                player2_y[i] = max(0, min(HEIGHT - player2.paddle_height, player2_y[i]))
        else:
            player2_y = max(0, min(HEIGHT - player2.paddle_height, player2_y))
        
        frames_this_point += 1
        
        balls_to_remove = []
        new_balls = []
        for ball in balls:
            ball['x'] += ball['speed_x']
            ball['y'] += ball['speed_y']
            
            if ball['y'] <= 0 or ball['y'] >= HEIGHT - ball['size']:
                ball['speed_y'] *= -1
                
            p1_collision = False
            if p1_is_multi_paddle:
                for y in player1_y:
                    if pygame.Rect(10, y, PALETA_WIDTH, player1.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                        p1_collision = True
                        ball['speed_x'] *= -1
                        ball['x'] = 10 + PALETA_WIDTH # Reposiciona la pelota
                        break
            else:
                if pygame.Rect(10, player1_y, PALETA_WIDTH, player1.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p1_collision = True
                    ball['speed_x'] *= -1
                    ball['x'] = 10 + PALETA_WIDTH # Reposiciona la pelota
                    if p1_is_iaj and len(balls) < 5:
                        new_balls.append({'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': ball_speed, 'speed_y': random.choice([ball_speed, -ball_speed]), 'size': BALL_SIZE})
            
            p2_collision = False
            if p2_is_multi_paddle:
                for y in player2_y:
                    if pygame.Rect(WIDTH - 10 - PALETA_WIDTH, y, PALETA_WIDTH, player2.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                        p2_collision = True
                        ball['speed_x'] *= -1
                        ball['x'] = WIDTH - 10 - PALETA_WIDTH - ball['size'] # Reposiciona la pelota
                        break
            else:
                if pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y, PALETA_WIDTH, player2.paddle_height).colliderect(pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size'])):
                    p2_collision = True
                    ball['speed_x'] *= -1
                    ball['x'] = WIDTH - 10 - PALETA_WIDTH - ball['size'] # Reposiciona la pelota
                    if p2_is_iaj and len(balls) < 5:
                        new_balls.append({'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': -ball_speed, 'speed_y': random.choice([ball_speed, -ball_speed]), 'size': BALL_SIZE})

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
            # Se llama a register_point y get_experience para ambos jugadores
            player1.register_point(frames_this_point)
            player2.register_point(frames_this_point)
            logger.log(p1_display_name.lower(), player1.get_experience(final_score=1 if score_player1 > score_player2 else -1 if score_player2 > score_player1 else 0))
            logger.log(p2_display_name.lower(), player2.get_experience(final_score=1 if score_player2 > score_player1 else -1 if score_player1 > score_player2 else 0))
            frames_this_point = 0
            
        for ball in balls_to_remove:
            balls.remove(ball)
            
        balls.extend(new_balls)
            
        if not balls:
            balls.append({'x': WIDTH // 2, 'y': HEIGHT // 2, 'speed_x': random.choice([ball_speed, -ball_speed]), 'speed_y': random.choice([ball_speed, -ball_speed]), 'size': BALL_SIZE})

        if diablo_mode:
            if score_player1 > 0 or score_player2 > 0:
                winner = p1_display_name if score_player1 > 0 else p2_display_name
                print(f"¡{winner} gana la partida!")
                
                final_score_p1 = 1 if winner == p1_display_name else -1
                final_score_p2 = 1 if winner == p2_display_name else -1
                
                logger.log(p1_display_name.lower(), player1.get_experience(final_score_p1))
                logger.log(p2_display_name.lower(), player2.get_experience(final_score_p2))
                logger.save_log()
                
                return winner, score_player1, score_player2

        if consecutive_score_player1 >= consecutive_score_limit or score_player1 >= point_score_limit:
            winner = p1_display_name
            print(f"¡{winner} gana la partida!")
            
            logger.log(p1_display_name.lower(), player1.get_experience(final_score=1))
            logger.log(p2_display_name.lower(), player2.get_experience(final_score=-1))
            logger.save_log()
            
            return winner, score_player1, score_player2
        
        if consecutive_score_player2 >= consecutive_score_limit or score_player2 >= point_score_limit:
            winner = p2_display_name
            print(f"¡{winner} gana la partida!")

            logger.log(p1_display_name.lower(), player1.get_experience(final_score=-1))
            logger.log(p2_display_name.lower(), player2.get_experience(final_score=1))
            logger.save_log()
            
            return winner, score_player1, score_player2

        screen.fill(BLACK)
        if p1_is_multi_paddle:
            for y in player1_y:
                pygame.draw.rect(screen, player1_color, pygame.Rect(10, y, PALETA_WIDTH, player1.paddle_height))
        else:
            pygame.draw.rect(screen, player1_color, pygame.Rect(10, player1_y, PALETA_WIDTH, player1.paddle_height))
        
        if p2_is_multi_paddle:
            for y in player2_y:
                pygame.draw.rect(screen, player2_color, pygame.Rect(WIDTH - 10 - PALETA_WIDTH, y, PALETA_WIDTH, player2.paddle_height))
        else:
            pygame.draw.rect(screen, player2_color, pygame.Rect(WIDTH - 10 - PALETA_WIDTH, player2_y, PALETA_WIDTH, player2.paddle_height))
            

        for ball in balls:
            pygame.draw.ellipse(screen, WHITE, pygame.Rect(ball['x'], ball['y'], ball['size'], ball['size']))
            
        score_text = score_font.render(f"{score_player1} - {score_player2}", True, WHITE)
        screen.blit(score_text, (WIDTH/2 - score_text.get_width()/2, 10))
        screen.blit(time_text, (WIDTH/2 - time_text.get_width()/2, 50)) 

        # --- CÓDIGO ACTUALIZADO PARA LA VISUALIZACIÓN DEL MODO DIABLO ---
        if diablo_mode:
            # Mostrar la ronda debajo del tiempo
            round_text = ui_font.render(f"Ronda: {diablo_round}/20", True, WHITE)
            screen.blit(round_text, (WIDTH/2 - round_text.get_width()/2, 90))

            # Mostrar el ranking en la esquina inferior izquierda
            ranking_text_title = ui_font.render("Ranking del Modo Diablo", True, WHITE)
            screen.blit(ranking_text_title, (10, HEIGHT - 150))
            
            # Ordenar las IA por puntos y luego por victorias
            sorted_ranking = sorted(diablo_points.items(), key=lambda item: (-item[1], -diablo_victories[item[0]]))

            y_offset = HEIGHT - 110
            for ia_name, points in sorted_ranking:
                victories = diablo_victories[ia_name]
                ranking_text = ui_font.render(f"{ia_name}: {points} pts ({victories} vic)", True, IA_COLORS.get(ia_name, WHITE))
                screen.blit(ranking_text, (10, y_offset))
                y_offset += 40
        # --- FIN DEL CÓDIGO ACTUALIZADO ---

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    logger.save_log()
    
    return "Empate", score_player1, score_player2

def generate_tournament_report(ia_players, tournament_victories, total_time):
    """
    Genera un informe completo del torneo en un archivo de texto.
    Ahora incluye el tiempo total del torneo.
    """
    with open("informe_torneo.txt", "w") as f:
        f.write("========================================\n")
        f.write("          INFORME FINAL DEL TORNEO\n")
        f.write("========================================\n\n")
        
        # Nueva línea para el tiempo total de juego
        f.write(f"Tiempo total del torneo: {int(total_time/60):02}:{int(total_time%60):02} minutos\n\n")
        
        f.write("--- Resultados por victorias ---\n")
        sorted_victories = sorted(tournament_victories.items(), key=lambda item: item[1], reverse=True)
        for name, victories in sorted_victories:
            f.write(f"> {name}: {victories} victorias\n")
        f.write("\n")
        
        f.write("--- Progreso de IQ de las IA ---\n")
        for name, ia_obj in ia_players.items():
            f.write(f"> IA: {name}\n")
            f.write(f"  - IQ Inicial del torneo: {ia_obj.initial_iq:.2f}\n")
            f.write(f"  - IQ Final del torneo: {ia_obj.final_iq:.2f}\n")
            f.write("\n")

def generate_diablo_report(diablo_points, diablo_victories, winner_name, ia_players, final_round, total_time):
    """
    Genera un informe del Modo Diablo.
    Ahora incluye el progreso del IQ de cada IA, la ronda final y el tiempo total de juego.
    """
    with open("informe_diablo.txt", "w") as f:
        f.write("========================================\n")
        f.write("          INFORME FINAL MODO DIABLO\n")
        f.write("========================================\n\n")
        
        # Nuevas líneas para la ronda final y el tiempo total
        f.write(f"Partida finalizada en la ronda: {final_round}\n")
        f.write(f"Tiempo total de juego: {int(total_time/60):02}:{int(total_time%60):02} minutos\n")
        f.write(f"Ganador del torneo: {winner_name}\n\n")

        f.write("--- Resultados por victorias ---\n")
        sorted_victories = sorted(diablo_victories.items(), key=lambda item: item[1], reverse=True)
        for name, victories in sorted_victories:
            f.write(f"> {name}: {victories} victorias\n")
        f.write("\n")
        
        f.write("--- Resultados por puntos ---\n")
        sorted_points = sorted(diablo_points.items(), key=lambda item: item[1], reverse=True)
        for name, points in sorted_points:
            f.write(f"> {name}: {points} puntos\n")
        f.write("\n")

        # Código nuevo para el progreso del IQ
        f.write("--- Progreso de IQ de las IA ---\n")
        for name, ia_obj in ia_players.items():
            f.write(f"> IA: {name}\n")
            f.write(f"  - IQ Inicial del torneo: {ia_obj.initial_iq:.2f}\n")
            f.write(f"  - IQ Final del torneo: {ia_obj.final_iq:.2f}\n")
            f.write("\n")

def save_ia_state(ia_players):
    """
    Guarda el estado actual de las IA en un archivo JSON.
    """
    state_to_save = {}
    for name, ia_obj in ia_players.items():
        ia_obj_experience = ia_obj.get_experience(0)
        state_to_save[name] = ia_obj_experience.get("state", {})

    with open("ia_state.json", "w") as f:
        json.dump(state_to_save, f, indent=4)
        print("Estado de las IA guardado en ia_state.json")

def load_ia_state():
    """
    Carga el estado de las IA desde un archivo JSON si existe.
    """
    if os.path.exists("ia_state.json"):
        with open("ia_state.json", "r") as f:
            return json.load(f)
    return {}
    
def create_ia_players_from_state(ia_states):
    """
    Crea las instancias de IA a partir de los datos guardados.
    """
    player_map = {"IAD": IAD, "IAA": IAA, "IAJ": IAJ, "IAF": IAF, "IAC": IAC, "IAL": IAL, "IAM": IAM, "IAR": IAR}
    ia_players = {}
    for name in player_map:
        if name in ia_states:
            if name == "IAF":
                ia_players[name] = player_map[name](600, initial_state=ia_states[name])
            else:
                ia_players[name] = player_map[name](600, 100, initial_state=ia_states[name])
        else:
            ia_players[name] = player_map[name](600, 100) if name != "IAF" else player_map[name](600)
    return ia_players

def start_tournament(ia_players):
    rival_options = ["IAD", "IAA", "IAJ", "IAF", "IAC", "IAL", "IAM", "IAR"]
    tournament_victories = {name: 0 for name in rival_options}
    tournament_winner = None
    
    tournament_start_time = time.time()
    
    # Elegir un campeón inicial al azar
    champion_name = random.choice(rival_options)
    print(f"El campeón inicial es: {champion_name}")
    
    # Registrar el IQ inicial de todas las IAs
    for ia_name in rival_options:
        ia_players[ia_name].initial_iq = ia_players[ia_name].get_iq()

    while not tournament_winner:
        challengers = [name for name in rival_options if name != champion_name]
        
        print(f"\n--- CAMPEÓN: {champion_name} ({tournament_victories[champion_name]} victorias) ---")
        
        all_challengers_defeated = True
        
        for challenger_name in challengers:
            if tournament_victories[champion_name] >= len(rival_options) - 1:
                break
                
            print(f"¡Comienza la batalla: {champion_name} vs {challenger_name}!")
            
            champion = ia_players[champion_name]
            challenger = ia_players[challenger_name]

            winner, _, _ = start_game(champion, challenger, champion_name, challenger_name, time_limit=60, consecutive_score_limit=2, point_score_limit=5)
            
            save_ia_state(ia_players)
            
            if winner == champion_name:
                tournament_victories[champion_name] += 1
                print(f"¡El campeón {champion_name} defiende su título! Victorias: {tournament_victories[champion_name]}")
            elif winner == challenger_name:
                print(f"¡El retador {challenger_name} ha derrotado al campeón {champion_name}!")
                champion_name = challenger_name
                tournament_victories[challenger_name] += 1
                all_challengers_defeated = False
                break
            else: # Empate
                print("La partida ha terminado en un empate. El campeón se mantiene.")
        
        if all_challengers_defeated:
             if tournament_victories[champion_name] >= len(rival_options) - 1:
                tournament_winner = champion_name
                print(f"🎉 ¡{tournament_winner} gana el torneo derrotando a todos los rivales! 🎉")
             else:
                # Si el campeón no ha derrotado a todos, pero no hay más retadores disponibles
                # Reiniciar la ronda de retadores para que el campeón se enfrente de nuevo a los que ya venció
                pass
    
    tournament_end_time = time.time()
    total_tournament_time = tournament_end_time - tournament_start_time
    
    # Registrar el IQ final de todas las IAs
    for ia_name in rival_options:
        ia_players[ia_name].final_iq = ia_players[ia_name].get_iq()
        
    print("\n¡Torneo completado!")
    generate_tournament_report(ia_players, tournament_victories, total_tournament_time)
    save_ia_state(ia_players)

def start_diablo_mode(ia_players):
    rival_options = ["IAD", "IAA", "IAJ", "IAF", "IAC", "IAL", "IAM", "IAR"]
    diablo_points = {name: 0 for name in rival_options}
    diablo_victories = {name: 0 for name in rival_options}
    diablo_winner = None
    
    # Parámetros iniciales del Modo Diablo
    initial_time_limit = 30
    initial_ball_speed = 5
    
    # Registrar el IQ inicial utilizando la nueva función get_iq
    for ia_name in rival_options:
        ia_players[ia_name].initial_iq = ia_players[ia_name].get_iq()

    match_list = []
    for i in range(len(rival_options)):
        for j in range(i + 1, len(rival_options)):
            match_list.append((rival_options[i], rival_options[j]))
    
    diablo_mode_start_time = time.time()

    for round_num in range(1, 21):
        if diablo_winner:
            break
            
        current_time_limit = max(5, initial_time_limit - (round_num - 1))
        current_ball_speed = initial_ball_speed + (round_num - 1)
            
        print(f"\n--- RONDA {round_num}/20 ---")
        print(f"Tiempo de la partida: {current_time_limit} segundos | Velocidad de la bola: {current_ball_speed}")
        random.shuffle(match_list)

        for match in match_list:
            if diablo_winner:
                break
            
            player1_name, player2_name = match
            player1 = ia_players[player1_name]
            player2 = ia_players[player2_name]

            print(f"¡Comienza la batalla: {player1_name} vs {player2_name}!")
            
            winner, _, _ = start_game(player1, player2, player1_name, player2_name, 
                                      time_limit=current_time_limit, consecutive_score_limit=1, point_score_limit=1, 
                                      diablo_mode=True, diablo_round=round_num, diablo_points=diablo_points, diablo_victories=diablo_victories,
                                      ball_speed=current_ball_speed)
            
            save_ia_state(ia_players)
            
            if winner and winner != "Empate":
                diablo_points[winner] += 3
                diablo_victories[winner] += 1
                print(f"El ganador de la partida es: {winner}")
            else:
                if winner:
                    diablo_points[player1_name] += 1
                    diablo_points[player2_name] += 1
                    print("La partida ha terminado en un empate.")
            
            for ia_name, victories in diablo_victories.items():
                if victories >= 10:
                    diablo_winner = ia_name
                    print(f"🎉 ¡La {diablo_winner} gana el Modo Diablo con 10 victorias! 🎉")
                    break

    if not diablo_winner:
        final_ranking = sorted(diablo_points.items(), key=lambda item: item[1], reverse=True)
        top_score = final_ranking[0][1]
        winners = [name for name, score in final_ranking if score == top_score]
        
        if len(winners) > 1:
            diablo_winner = f"Empate entre: {', '.join(winners)}"
        else:
            diablo_winner = winners[0]
            
        print(f"🎉 ¡{diablo_winner} gana el Modo Diablo después de 20 rondas! 🎉")
    
    diablo_mode_end_time = time.time()
    total_diablo_time = diablo_mode_end_time - diablo_mode_start_time

    for ia_name in rival_options:
        ia_players[ia_name].final_iq = ia_players[ia_name].get_iq()

    print("\n¡Modo Diablo completado!")
    generate_diablo_report(diablo_points, diablo_victories, diablo_winner, ia_players, round_num, total_diablo_time)
    save_ia_state(ia_players)

# --- Interfaz de selección de rivales y manejo de errores ---
if __name__ == "__main__":
    try:
        rival_options = ["IAD", "IAA", "IAJ", "IAF", "IAC", "IAL", "IAM", "IAR"]
        
        print("Selecciona un modo de juego:")
        print(f"1. Torneo")
        print(f"2. Modo Diablo")
        
        ia_states = load_ia_state()
        ia_players = create_ia_players_from_state(ia_states)
        
        while True:
            try:
                choice = int(input("Introduce el número de tu opción: "))
                
                if choice == 1:
                    start_tournament(ia_players)
                    break
                elif choice == 2:
                    start_diablo_mode(ia_players)
                    break
                else:
                    print("Opción no válida. Inténtalo de nuevo.")
            except ValueError:
                print("Entrada no válida. Por favor, introduce un número.")

    except Exception as e:
        with open("errorespong.txt", "w") as f:
            f.write("========================================\n")
            f.write("            ERROR EN EL PROGRAMA\n")
            f.write("========================================\n")
            f.write(f"Hora del error: {time.ctime()}\n")
            f.write(f"Tipo de error: {type(e).__name__}\n")
            f.write(f"Mensaje: {str(e)}\n\n")
            f.write("--- Traceback ---\n")
            f.write(traceback.format_exc())
        
        print("\n¡Ha ocurrido un error inesperado! Se ha generado un archivo 'errorespong.txt' con los detalles.")