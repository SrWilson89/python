import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import os
import time
from roulette_env import RouletteEnv

# 1. Registrar el entorno de ruleta
try:
    gym.register(
        id="Roulette-v1", # ¡Cambiamos la versión para que no haya conflicto!
        entry_point="roulette_env:RouletteEnv",
    )
except gym.error.AlreadyRegistered:
    pass

# 2. Configuración del entrenamiento
env_id = "Roulette-v1"
log_dir = "./roulette_logs/"
os.makedirs(log_dir, exist_ok=True)
total_timesteps = 10000

# 3. Crear el entorno y el modelo PPO
env = gym.make(env_id)
model = PPO(
    "MlpPolicy",
    env,
    verbose=0,
    learning_rate=0.0001,
)

# 4. Entrenar el agente y guardar el historial de jugadas
print("Iniciando el entrenamiento de la IA para la ruleta con múltiples apuestas...")
print("Las apuestas y el progreso se registrarán en 'roulette_analysis.txt'")

# Bucle de entrenamiento y registro
obs, info = env.reset()
roulette_history = []
block_start_time = time.time()
total_start_time = time.time()

for i in range(total_timesteps):
    action, _ = model.predict(obs, deterministic=False)
    obs, reward, terminated, truncated, info = env.step(action)

    roulette_history.append({
        "step": i,
        "action": action,
        "reward": reward,
        "balance": obs[0]
    })

    if (i + 1) % 1000 == 0:
        elapsed_time = time.time() - block_start_time
        print(f"Análisis guardado después de {i + 1} jugadas. Tiempo transcurrido: {elapsed_time:.2f} segundos.")
        block_start_time = time.time()

        with open(f"{log_dir}roulette_analysis.txt", "w", encoding="utf-8") as f:
            f.write("--- Análisis de la IA para la ruleta ---\n\n")
            f.write(f"Jugadas totales: {i + 1}\n")
            f.write("\nHistorial de jugadas (últimas 1000):\n")
            for entry in roulette_history[-1000:]:
                # Muestra el array de apuestas en lugar de un solo número
                action_str = ', '.join(map(str, entry['action']))
                f.write(f"Paso: {entry['step']+1}, Acción (apuesta): [{action_str}], Recompensa: {entry['reward']:.2f}, Saldo: {entry['balance']:.2f}\n")

    model.learn(total_timesteps=1, reset_num_timesteps=False)

total_elapsed_time = time.time() - total_start_time
print("\n¡Entrenamiento completado!")
print(f"Tiempo total de ejecución: {total_elapsed_time:.2f} segundos.")