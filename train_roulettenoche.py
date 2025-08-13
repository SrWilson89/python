import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import os
import time
from collections import Counter
from roulette_env import RouletteEnv

# 1. Registrar el entorno de ruleta
try:
    gym.register(
        id="Roulette-v1",
        entry_point="roulette_env:RouletteEnv",
    )
except gym.error.AlreadyRegistered:
    pass

# 2. Configuración del entrenamiento
env_id = "Roulette-v1"
log_dir = "./roulette_logs/"
os.makedirs(log_dir, exist_ok=True)
total_timesteps = 2000000 # Jugadas totales ajustadas a 2.000.000
block_size = 10000 # Bloque de aprendizaje ajustado a 10.000

# 3. Crear el entorno y el modelo PPO
env = gym.make(env_id)
model = PPO(
    "MlpPolicy",
    env,
    verbose=0,
    learning_rate=0.001,
)

# 4. Entrenar el agente y guardar el historial de jugadas
print("Iniciando el entrenamiento de la IA para la ruleta con múltiples apuestas...")
print("Las apuestas y el progreso se registrarán en 'roulette_analysis.txt'")

obs, info = env.reset()
roulette_history = []
winning_numbers = []
total_start_time = time.time()

for i in range(total_timesteps):
    action, _ = model.predict(obs, deterministic=False)
    obs, reward, terminated, truncated, info = env.step(action)

    winning_numbers.append(info['roulette_result'])
    
    roulette_history.append({
        "step": i,
        "action": action,
        "reward": reward,
        "balance": obs[0]
    })

    if (i + 1) % block_size == 0:
        model.learn(total_timesteps=block_size, reset_num_timesteps=False)

        elapsed_time = time.time() - total_start_time
        print(f"Análisis guardado después de {i + 1} jugadas. Tiempo transcurrido: {elapsed_time:.2f} segundos.")

        with open(f"{log_dir}roulette_analysis.txt", "w", encoding="utf-8") as f:
            f.write("--- Análisis de la IA para la ruleta ---\n\n")
            f.write(f"Jugadas totales: {i + 1}\n")
            f.write("\nHistorial de jugadas (últimas 10000):\n")
            for entry in roulette_history[-block_size:]:
                action_str = ', '.join(map(str, entry['action']))
                f.write(f"Paso: {entry['step']+1}, Acción (apuesta): [{action_str}], Recompensa: {entry['reward']:.2f}, Saldo: {entry['balance']:.2f}\n")
    
    if terminated or truncated:
        obs, info = env.reset()
        
total_elapsed_time = time.time() - total_start_time
hours, remainder = divmod(total_elapsed_time, 3600)
minutes, seconds = divmod(remainder, 60)

print("\n¡Entrenamiento completado!")
print(f"Tiempo total de ejecución: {int(hours)}h {int(minutes)}m {int(seconds)}s.")

model.save("./roulette_model/roulette_ppo_model_noche")

with open(f"{log_dir}roulette_resumen.txt", "w", encoding="utf-8") as f:
    f.write("--- RESUMEN DEL ENTRENAMIENTO ---\n\n")
    f.write(f"Jugadas totales: {total_timesteps}\n")
    f.write(f"Saldo inicial: {roulette_history[0]['balance']:.2f}\n")
    f.write(f"Saldo final: {roulette_history[-1]['balance']:.2f}\n\n")
    f.write("--- Primeras 8 jugadas ---\n")
    for entry in roulette_history[:8]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- 8 jugadas intermedias ---\n")
    mid_point = len(roulette_history) // 2
    for entry in roulette_history[mid_point-4:mid_point+4]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- Últimas 8 jugadas ---\n")
    for entry in roulette_history[-8:]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- 10 Números más frecuentes ---\n")
    number_counts = Counter(winning_numbers)
    top_10_numbers = number_counts.most_common(10)
    for number, count in top_10_numbers:
        percentage = (count / total_timesteps) * 100
        f.write(f"Número {number}: {count} veces ({percentage:.2f}%)\n")

env.close()