import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import os
import time
from collections import Counter, deque
from roulette_env import RouletteEnv
from tqdm import tqdm

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
total_timesteps = 10000
block_size = 1000
full_history_file = f"{log_dir}roulette_full_history.txt"

# 3. Crear el entorno y el modelo PPO
# NUEVO: Pasar el saldo inicial al crear el entorno
env = gym.make(env_id, initial_balance=100000)
model = PPO(
    "MlpPolicy",
    env,
    verbose=0,
    learning_rate=0.001,
    gamma=0.95
)

# 4. Entrenar el agente y guardar el historial de jugadas
print("Iniciando el entrenamiento de la IA para la ruleta con múltiples apuestas...")
print("Los avances se registrarán en los archivos del directorio 'roulette_logs/'")

obs, info = env.reset()
initial_balance = obs[0]
roulette_history_session = deque(maxlen=total_timesteps)
total_start_time = time.time()
block_start_time = time.time()

# Usamos tqdm para mostrar la barra de progreso
with tqdm(total=total_timesteps, desc="Entrenamiento de la IA", unit=" jugadas") as pbar:
    for i in range(total_timesteps):
        
        # --- LÓGICA PARA CAMBIAR EL COLOR DE LA BARRA DE PROGRESO ---
        progress_percentage = (i + 1) / total_timesteps
        if progress_percentage < 0.20:
            pbar.colour = "darkred"
        elif progress_percentage < 0.40:
            pbar.colour = "red"
        elif progress_percentage < 0.60:
            pbar.colour = "orange"
        elif progress_percentage < 0.80:
            pbar.colour = "lime"
        else:
            pbar.colour = "green"
        # ------------------------------------------------------------------

        action, _ = model.predict(obs, deterministic=False)
        obs, reward, terminated, truncated, info = env.step(action)
        
        roulette_history_session.append({
            "step": i,
            "action": action,
            "reward": reward,
            "balance": obs[0],
            "roulette_result": info['roulette_result']
        })

        if (i + 1) % block_size == 0:
            model.learn(total_timesteps=block_size, reset_num_timesteps=False)
            pbar.update(block_size)

            # Actualizamos la descripción de la barra de progreso con el saldo actual
            pbar.set_postfix(saldo=f"{obs[0]:.2f}")
        
        if terminated or truncated:
            obs, info = env.reset()

total_elapsed_time = time.time() - total_start_time
hours, remainder = divmod(total_elapsed_time, 3600)
minutes, seconds = divmod(remainder, 60)

print("\n¡Entrenamiento completado!")
print(f"Tiempo total de ejecución: {int(hours)}h {int(minutes)}m {int(seconds)}s.")

model.save("./roulette_model/roulette_ppo_model_optimized")

current_time_str = time.strftime('%Y-%m-%d %H:%M:%S')

winning_numbers = list(env.unwrapped.winning_numbers_history)
winning_numbers_in_session = [item['roulette_result'] for item in roulette_history_session]


# Guardamos el historial completo de la sesión en el archivo persistente
with open(full_history_file, 'a', encoding="utf-8") as f:
    f.write(','.join(map(str, winning_numbers_in_session)) + ',')
    
# --- Escribir el resumen combinado en un solo archivo, sobrescribiendo el anterior ---
# Nota: Ahora todo se escribe en "roulette_resumen.txt"
with open(f"{log_dir}roulette_resumen.txt", "w", encoding="utf-8") as f:
    # Contenido del resumen
    f.write("--- RESUMEN DEL ENTRENAMIENTO ---\n\n")
    f.write(f"Jugadas totales: {total_timesteps}\n")
    f.write(f"Saldo inicial: {initial_balance:.2f}\n")
    f.write(f"Saldo final: {roulette_history_session[-1]['balance']:.2f}\n\n")
    
    # Secciones de las jugadas
    f.write("--- Primeras 8 jugadas ---\n")
    for entry in list(roulette_history_session)[:8]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- 8 jugadas intermedias ---\n")
    mid_point = len(roulette_history_session) // 2
    for entry in list(roulette_history_session)[mid_point-4:mid_point+4]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- Últimas 8 jugadas ---\n")
    for entry in list(roulette_history_session)[-8:]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']+1}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
        
    # Contenido del análisis macro
    f.write("\n" + "="*50 + "\n")
    f.write(f"--- ANÁLISIS MACRO | {current_time_str} ---\n")
    f.write(f"Jugadas totales: {len(winning_numbers)}\n\n")
    
    voisins_du_zero = [2, 0, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35]
    tiers_du_cylindre = [5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36]
    orphelins = [1, 6, 9, 14, 17, 20, 31, 34]
    
    first_dozen = list(range(1, 13))
    second_dozen = list(range(13, 25))
    third_dozen = list(range(25, 37))
    
    first_column = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
    second_column = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
    third_column = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
    
    number_counts = Counter(winning_numbers)
    top_10_numbers = number_counts.most_common(10)

    zone_counts = Counter()
    dozen_counts = Counter()
    column_counts = Counter()
    
    for number in winning_numbers:
        if number in voisins_du_zero:
            zone_counts['Zona del Cero'] += 1
        elif number in tiers_du_cylindre:
            zone_counts['Tercio del Cilindro'] += 1
        elif number in orphelins:
            zone_counts['Huérfanos'] += 1
            
        if number in first_dozen:
            dozen_counts['Primera Docena'] += 1
        elif number in second_dozen:
            dozen_counts['Segunda Docena'] += 1
        elif number in third_dozen:
            dozen_counts['Tercera Docena'] += 1
            
        if number in first_column:
            column_counts['Primera Columna'] += 1
        elif number in second_column:
            column_counts['Segunda Columna'] += 1
        elif number in third_column:
            column_counts['Tercera Columna'] += 1
            
    f.write("--- 10 Números más frecuentes ---\n")
    for number, count in top_10_numbers:
        percentage = (count / len(winning_numbers)) * 100
        f.write(f"Número {number}: {count} veces ({percentage:.2f}%)\n")

    f.write("\n-- Zonas más frecuentes --\n")
    if zone_counts:
        top_zone = zone_counts.most_common(1)[0]
        percentage = (top_zone[1] / len(winning_numbers)) * 100
        f.write(f"Zona más frecuente: {top_zone[0]} con {top_zone[1]} veces ({percentage:.2f}%)\n")

    f.write("\n-- Docenas más frecuentes --\n")
    if dozen_counts:
        top_dozen = dozen_counts.most_common(1)[0]
        percentage = (top_dozen[1] / len(winning_numbers)) * 100
        f.write(f"Docena más frecuente: {top_dozen[0]} con {top_dozen[1]} veces ({percentage:.2f}%)\n")

    f.write("\n-- Columnas más frecuentes --\n")
    if column_counts:
        top_column = column_counts.most_common(1)[0]
        percentage = (top_column[1] / len(winning_numbers)) * 100
        f.write(f"Columna más frecuente: {top_column[0]} con {top_column[1]} veces ({percentage:.2f}%)\n")

# Borramos los otros archivos de log para que solo tengamos el resumen combinado
if os.path.exists(f"{log_dir}roulette_analysis.txt"):
    os.remove(f"{log_dir}roulette_analysis.txt")
if os.path.exists(f"{log_dir}roulette_macro.txt"):
    os.remove(f"{log_dir}roulette_macro.txt")

env.close()