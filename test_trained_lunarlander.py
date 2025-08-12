import gymnasium as gym
from stable_baselines3 import PPO
import os
import time

# --- Configuración de la prueba ---
# Ruta al mejor modelo guardado por el script de vtrenamiento
# Asegúrate de que esta ruta es correcta. Por defecto, EvalCallback lo guarda como 'best_model.zip'
model_path = "./lunarlander_ppo_logs/best_model.zip"
env_id = "LunarLander-v3"
num_episodes_to_test = 5 # Cuántas partidas queremos que la IA juegue de prueba

# --- Código de prueba ---
if not os.path.exists(model_path):
    print(f"Error: No se encontró el modelo entrenado en la ruta '{model_path}'")
    print("Asegúrate de haber ejecutado primero 'python train_lunarlander.py' y que se haya guardado un modelo.")
else:
    print(f"Cargando el modelo de IA desde: '{model_path}'")
    # 1. Cargar el modelo entrenado
    model = PPO.load(model_path)

    # 2. Crear el entorno de prueba (con render_mode="human" para visualizar)
    env = gym.make(env_id, render_mode="human")

    print(f"Iniciando la simulación de prueba con {num_episodes_to_test} episodios.")

    # 3. Probar el modelo
    for episode in range(num_episodes_to_test):
        obs, info = env.reset() # Reiniciar el entorno para una nueva partida
        done = False
        truncated = False
        episode_reward = 0 # Recompensa acumulada en este episodio
        steps = 0 # Pasos en este episodio

        print(f"\n--- Episodio de prueba {episode + 1} ---")
        while not done and not truncated:
            # El modelo predice la mejor acción basándose en la observación actual
            # 'deterministic=True' asegura que siempre elija la acción más probable
            action, _states = model.predict(obs, deterministic=True)

            # Ejecutar la acción en el entorno y obtener el nuevo estado, recompensa, etc.
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward # Acumular la recompensa
            steps += 1 # Incrementar contador de pasos

            env.render() # Mostrar la simulación en la ventana de Pygame
            time.sleep(0.05) # Pequeña pausa para que sea visible

        print(f"Episodio {episode + 1} terminado. Recompensa total: {episode_reward:.2f}, Pasos: {steps}")

    # 4. Cerrar el entorno al finalizar la prueba
    env.close()
    print("\nSimulación de prueba de LunarLander completada.")