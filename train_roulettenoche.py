import gymnasium as gym
from stable_baselines3 import PPO
import numpy as np
import os
import time
from collections import Counter, deque
from roulette_env import RouletteEnv
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd

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

# --- RUTA ÚNICA PARA LOS ARCHIVOS DE LOG NOCTURNOS ---
log_dir = "./roulette_logs_noche/"
os.makedirs(log_dir, exist_ok=True)
# ---------------------------------------------

# Definiciones de nombres de archivos
timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
total_timesteps = 500000
block_size = 1000

# Archivos únicos por cada ejecución
balance_plot_file = f"{log_dir}balance_plot_{timestamp}.png"
resumen_texto_file = f"{log_dir}roulette_resumen_{timestamp}.txt"
modelo_file = f"./roulette_model/roulette_ppo_model_noche_{timestamp}"

# Archivos maestros (se adjuntan los datos)
historial_completo_csv = f"{log_dir}roulette_historial_completo_noche.csv"
informe_maestro_html = f"{log_dir}roulette_informe_maestro_noche.html"

# 3. Crear el entorno y el modelo PPO
env = gym.make(env_id, initial_balance=100000)
model = PPO(
    "MlpPolicy",
    env,
    verbose=0,
    learning_rate=0.001,
    gamma=0.95
)

# 4. Entrenar el agente y guardar el historial de jugadas
print(f"Iniciando el entrenamiento de la IA nocturno para la ruleta con {total_timesteps} jugadas...")
print(f"Los avances y el informe se registrarán en la carpeta '{log_dir}'")

obs, info = env.reset()
initial_balance = obs[0]
roulette_history_session = deque(maxlen=total_timesteps)
total_start_time = time.time()

with tqdm(total=total_timesteps, desc="Entrenamiento de la IA", unit=" jugadas", leave=False) as pbar:
    for i in range(total_timesteps):
        progress_percentage = (i + 1) / total_timesteps
        if progress_percentage < 0.20:
            pbar.colour = "red"
        elif progress_percentage < 0.40:
            pbar.colour = "red"
        elif progress_percentage < 0.60:
            pbar.colour = "yellow"
        elif progress_percentage < 0.80:
            pbar.colour = "green"
        else:
            pbar.colour = "green"

        action, _ = model.predict(obs, deterministic=False)
        obs, reward, terminated, truncated, info = env.step(action)
        
        roulette_history_session.append({
            "timestamp": timestamp,
            "step": i + 1,
            "action": list(action),
            "reward": reward,
            "balance": obs[0],
            "roulette_result": info['roulette_result']
        })

        if (i + 1) % block_size == 0:
            model.learn(total_timesteps=block_size, reset_num_timesteps=False)
            pbar.update(block_size)
            pbar.set_postfix(saldo=f"{obs[0]:.2f}")
        
        if terminated or truncated:
            obs, info = env.reset()

total_elapsed_time = time.time() - total_start_time
hours, remainder = divmod(total_elapsed_time, 3600)
minutes, seconds = divmod(remainder, 60)

print("\n¡Entrenamiento completado!")
print(f"Tiempo total de ejecución: {int(hours)}h {int(minutes)}m {int(seconds)}s.")

# Guardamos el modelo con la marca de tiempo para no sobrescribir
model.save(modelo_file)

current_time_str = time.strftime('%Y-%m-%d %H:%M:%S')
winning_numbers = [item['roulette_result'] for item in roulette_history_session]

# --- GUARDAR HISTORIAL COMPLETO EN UN ÚNICO CSV (se adjunta) ---
df_history_session = pd.DataFrame(list(roulette_history_session))
df_history_session.to_csv(historial_completo_csv, mode='a', header=not os.path.exists(historial_completo_csv), index=False)
print(f"Historial de jugadas guardado en: {historial_completo_csv}")

# --- CREAR RESUMEN DE TEXTO ---
with open(resumen_texto_file, "w", encoding="utf-8") as f:
    f.write("--- RESUMEN DEL ENTRENAMIENTO ---\n\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Jugadas totales: {total_timesteps}\n")
    f.write(f"Saldo inicial: {initial_balance:.2f}\n")
    f.write(f"Saldo final: {roulette_history_session[-1]['balance']:.2f}\n\n")
    f.write("--- Primeras 8 jugadas ---\n")
    for entry in list(roulette_history_session)[:8]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- 8 jugadas intermedias ---\n")
    mid_point = len(roulette_history_session) // 2
    for entry in list(roulette_history_session)[mid_point-4:mid_point+4]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
    f.write("\n--- Últimas 8 jugadas ---\n")
    for entry in list(roulette_history_session)[-8:]:
        action_str = ', '.join(map(str, entry['action']))
        f.write(f"Paso: {entry['step']}, Acción: [{action_str}], Saldo: {entry['balance']:.2f}\n")
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
        if number in voisins_du_zero: zone_counts['Zona del Cero'] += 1
        elif number in tiers_du_cylindre: zone_counts['Tercio del Cilindro'] += 1
        elif number in orphelins: zone_counts['Huérfanos'] += 1
        if number in first_dozen: dozen_counts['Primera Docena'] += 1
        elif number in second_dozen: dozen_counts['Segunda Docena'] += 1
        elif number in third_dozen: dozen_counts['Tercera Docena'] += 1
        if number in first_column: column_counts['Primera Columna'] += 1
        elif number in second_column: column_counts['Segunda Columna'] += 1
        elif number in third_column: column_counts['Tercera Columna'] += 1
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
    
# --- Generar el gráfico y el informe HTML ---
try:
    # 1. Crear el gráfico de progreso del saldo
    df_history = pd.DataFrame(list(roulette_history_session))
    
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 6))
    plt.plot(df_history['step'], df_history['balance'], label='Saldo', color='lime')
    plt.axhline(y=initial_balance, color='red', linestyle='--', label='Saldo Inicial')
    plt.title('Evolución del Saldo de la IA')
    plt.xlabel('Paso de la Simulación')
    plt.ylabel('Saldo')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(balance_plot_file)
    plt.close()

    # 2. Leer el resumen de texto
    with open(resumen_texto_file, "r", encoding="utf-8") as f:
        resumen_texto = f.read()

    # 3. Crear el bloque HTML del informe
    html_block = f"""
        <div class="section">
            <h2>Informe de Entrenamiento - {current_time_str}</h2>
            <img src="{os.path.basename(balance_plot_file)}" alt="Gráfico de evolución del saldo">
            <pre>{resumen_texto}</pre>
        </div>
    """

    # 4. Adjuntar al informe maestro HTML
    if not os.path.exists(informe_maestro_html):
        # Si el archivo no existe, creamos la estructura completa
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Historial de Entrenamientos de la IA</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 2em; line-height: 1.6; background-color: #121212; color: #e0e0e0; }}
                h1 {{ color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 0.5em; }}
                .container {{ display: flex; flex-direction: column; gap: 2em; }}
                .section {{ background-color: #1e1e1e; padding: 1.5em; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
                pre {{ background-color: #1e1e1e; color: #e0e0e0; padding: 1em; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
                img {{ max-width: 100%; height: auto; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <h1>Historial de Entrenamientos de la IA para la Ruleta</h1>
            <div class="container">
                {html_block}
            </div>
        </body>
        </html>
        """
        with open(informe_maestro_html, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        # Si ya existe, insertamos el nuevo bloque antes de la etiqueta </div>
        with open(informe_maestro_html, "r+", encoding="utf-8") as f:
            content = f.read()
            pos = content.rfind('</div>')
            if pos != -1:
                content = content[:pos] + html_block + content[pos:]
            f.seek(0)
            f.write(content)

    print(f"Informe HTML de esta sesión guardado y adjuntado en: {informe_maestro_html}")

except Exception as e:
    print(f"Error al generar el informe HTML: {e}")

env.close()