import gymnasium as gym
import numpy as np
import time

# Importar tu entorno personalizado de Cuatro en Raya
from connect_four_env import ConnectFourEnv

# --- INICIO DE LOS CAMBIOS ---

# Define las dimensiones del tablero aquí para usarlas en el registro
ROWS = 6
COLS = 7

# Registrar el entorno con Gymnasium. Esto debe hacerse una vez.
# Es mejor ponerlo fuera del try-except para gym.make, o asegurarnos de que gym.register se ejecuta.
# Lo haremos una vez al inicio del script.
try:
    gym.register(
        id="ConnectFour-v0",
        entry_point="connect_four_env:ConnectFourEnv", # 'nombre_archivo:ClaseEnv'
        max_episode_steps=ROWS * COLS, # ¡Aquí usamos ROWS y COLS directamente!
        reward_threshold=10.0,
        nondeterministic=False,
    )
except gym.error.AlreadyRegistered:
    # Si ya está registrado de una ejecución anterior, no hacemos nada.
    pass

# --- FIN DE LOS CAMBIOS ---


# 1. Crear una instancia de tu entorno personalizado
# render_mode="human" para que podamos ver el tablero en una ventana
# Ahora el gym.make debería funcionar sin el NameNotFound, ya que ya lo registramos
env = gym.make("ConnectFour-v0", render_mode="human")

print("Entorno de Cuatro en Raya creado.")

# 2. Simular algunas partidas (episodios) con acciones aleatorias
num_episodes = 3 # Jugaremos 3 partidas de prueba

for i_episode in range(num_episodes):
    observation, info = env.reset() # Reiniciar el juego al inicio de cada partida
    done = False
    truncated = False
    score = 0
    moves = 0
    print(f"\n--- Iniciando Partida {i_episode + 1} ---")
    print(f"Tablero inicial:\n{observation}") # Mostrar el tablero

    while not done and not truncated:
        # Encontrar las casillas vacías para una acción válida (columnas no llenas)
        # Accedemos a env.unwrapped para _is_valid_location
        valid_actions = [col for col in range(env.unwrapped.cols) if env.unwrapped._is_valid_location(col)]

        if not valid_actions: # Si no quedan movimientos válidos (tablero lleno o error)
            done = True
            print("No quedan movimientos válidos, terminando el episodio.")
            break

        # Elegir una acción aleatoria entre las *válidas*
        action = np.random.choice(valid_actions)

        # Accedemos a env.unwrapped para current_player
        print(f"Jugador actual: {'Rojo' if env.unwrapped.current_player == 1 else 'Amarillo'}, Acción elegida (columna): {action}")

        # Realizar la acción en el entorno
        observation, reward, done, truncated, info = env.step(action)
        score += reward
        moves += 1

        print(f"Tablero después del movimiento:\n{observation}")
        print(f"Recompensa: {reward}, Juego Terminado: {done}, Movimientos: {moves}")

        # Pequeña pausa para que podamos ver la simulación
        time.sleep(0.5) # Media segundo de pausa por movimiento

    # Imprimir el resultado de la partida
    # Accedemos a env.unwrapped para winner
    if env.unwrapped.winner == 1:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Gana Jugador Rojo! Puntuación total: {score} ---")
    elif env.unwrapped.winner == -1:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Gana Jugador Amarillo! Puntuación total: {score} ---")
    else:
        print(f"--- Partida {i_episode + 1} Terminada: ¡Empate! Puntuación total: {score} ---")

# 3. Cerrar el entorno al finalizar
env.close()
print("\nSimulación de Cuatro en Raya completa.")