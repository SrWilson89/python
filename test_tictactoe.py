import gymnasium as gym
import numpy as np
import time

# Importar tu entorno personalizado
# Asegúrate de que tictactoe_env.py está en la misma carpeta
from tictactoe_env import TicTacToeEnv

# Para que Gymnasium pueda encontrar tu entorno, necesitas registrarlo.
# Solo haz esto una vez en tu código principal antes de gym.make().
# Esto permite que gymnasium reconozca "TicTacToe-v0" como tu entorno.
try:
    gym.make("TicTacToe-v0")
except gym.error.UnregisteredEnv:
    gym.register(
        id="TicTacToe-v0",
        entry_point="tictactoe_env:TicTacToeEnv", # 'nombre_archivo:ClaseEnv'
        max_episode_steps=9, # Un juego de Tres en Raya tiene un máximo de 9 movimientos
        reward_threshold=10.0, # El agente gana una recompensa de 10
        nondeterministic=False, # El juego es determinista
    )

# 1. Crear una instancia de tu entorno personalizado
# render_mode="human" para que podamos ver el tablero en una ventana
env = gym.make("TicTacToe-v0", render_mode="human")

print("Entorno de Tres en Raya creado.")

# 2. Simular algunas partidas (episodios) con acciones aleatorias
num_episodes = 5 # Jugar 5 partidas de prueba

for i_episode in range(num_episodes):
    observation, info = env.reset() # Reiniciar el juego al inicio de cada partida
    done = False
    truncated = False
    score = 0
    moves = 0
    print(f"\n--- Iniciando Partida {i_episode + 1} ---")
    print(f"Tablero inicial:\n{observation.reshape(3, 3)}") # Mostrar el tablero 3x3

    while not done and not truncated:
        # El agente actual es siempre el jugador 'X' (1) en nuestro entorno para simplificar el entrenamiento con RL.
        # Por ahora, ambos jugadores harán movimientos aleatorios para probar el entorno.
        # En el entrenamiento real, la IA solo controlará al jugador 'X'.

        # Encontrar las casillas vacías para una acción válida
        valid_actions = np.where(observation == 0)[0] # Obtener índices de casillas vacías

        if len(valid_actions) == 0: # Si no quedan movimientos válidos (tablero lleno)
            done = True # El juego debería haber terminado en un empate o victoria antes de esto
            print("Tablero lleno, terminando el episodio.")
            break

        # Elegir una acción aleatoria entre las válidas
        action = np.random.choice(valid_actions)

        print(f"Jugador actual: {'X' if env.unwrapped.current_player == 1 else 'O'}, Acción elegida (casilla): {action}")

        # Realizar la acción en el entorno
        observation, reward, done, truncated, info = env.step(action)
        score += reward
        moves += 1

        print(f"Tablero después del movimiento:\n{observation.reshape(3, 3)}")
        print(f"Recompensa: {reward}, Juego Terminado: {done}")

        # Pequeña pausa para que podamos ver la simulación
        time.sleep(1.0) # Un segundo de pausa por movimiento

    # Imprimir el resultado de la partida
    if env.unwrapped.winner == 1:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Gana X! Puntuación total: {score} ---")
    elif env.unwrapped.winner == -1:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Gana O! Puntuación total: {score} ---")
    else:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Empate! Puntuación total: {score} ---")

# 3. Cerrar el entorno al finalizar
env.close()
print("\nSimulación de Tres en Raya completa.")