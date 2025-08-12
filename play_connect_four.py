import gymnasium as gym
import numpy as np
from stable_baselines3 import DQN
import time
import os

# Importar tu entorno personalizado de Cuatro en Raya
from connect_four_env import ConnectFourEnv

# --- Configuración del entorno ---
ROWS = 6
COLS = 7

# Registrar el entorno con Gymnasium.
try:
    gym.register(
        id="ConnectFour-v0",
        entry_point="connect_four_env:ConnectFourEnv",
        max_episode_steps=ROWS * COLS,
        reward_threshold=10.0,
        nondeterministic=False,
    )
except gym.error.AlreadyRegistered:
    pass

# --- Configuración de la prueba ---
# Ruta al modelo entrenado que acabas de guardar
model_path = "./connect_four_dqn_logs/connect_four_dqn_final.zip"
env_id = "ConnectFour-v0"

# Crear el entorno en modo humano para visualizarlo
env = gym.make(env_id, render_mode="human")

# Cargar el modelo entrenado
try:
    model = DQN.load(model_path)
    print(f"Modelo de IA cargado desde: '{model_path}'")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()

# Bucle principal para jugar una partida
observation, info = env.reset()
done = False
truncated = False

print("\n--- ¡Empezando una nueva partida de Cuatro en Línea! ---")
print("Eres el jugador Rojo (fichas rojas). La IA es el jugador Amarillo (fichas amarillas).")

while not done and not truncated:
    # Verificamos si es el turno de la IA (Jugador -1) o el tuyo (Jugador 1)
    if env.unwrapped.current_player == -1:
        # Turno de la IA
        print("Turno de la IA...")
        # La IA toma una acción (columna)
        action, _ = model.predict(observation, deterministic=True)
        # Nos aseguramos de que la acción sea válida
        valid_actions = env.unwrapped._get_valid_locations()
        if action not in valid_actions:
            # Si la IA predice una acción inválida (tablero lleno), elegimos una al azar
            action = np.random.choice(valid_actions)
        
        print(f"La IA elige la columna: {action}")
    else:
        # Tu turno como jugador humano
        action = -1
        while action == -1:
            try:
                # Pedir al usuario que elija una columna
                user_input = input("Elige una columna (0-6): ")
                action = int(user_input)

                # Validar la acción
                if not 0 <= action <= 6 or not env.unwrapped._is_valid_location(action):
                    print("Movimiento inválido. Elige una columna vacía entre 0 y 6.")
                    action = -1
            except ValueError:
                print("Entrada inválida. Por favor, introduce un número.")
                action = -1

    # Ejecutar la acción
    observation, reward, done, truncated, info = env.step(action)
    env.render()
    time.sleep(0.5)

# Final de la partida
if env.unwrapped.winner == 1:
    print("¡Felicidades! ¡Has ganado la partida!")
elif env.unwrapped.winner == -1:
    print("¡La IA ha ganado! Mejor suerte la próxima vez.")
else:
    print("¡La partida ha terminado en empate!")
0
env.close()