import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnNoModelImprovement
import os

# --- Configuración del entrenamiento ---
# Directorio para guardar logs y el mejor modelo
log_dir = "./lunarlander_ppo_logs/" 
os.makedirs(log_dir, exist_ok=True)

# ID del entorno (actualizado a la versión v3)
env_id = "LunarLander-v3"

# Número total de pasos de interacción con el entorno (puedes aumentar esto para más entrenamiento)
total_timesteps = 500000 

# Frecuencia de evaluación (cada cuántos timesteps se evalúa el modelo)
eval_freq = 10000 
n_eval_episodes = 10 # Número de episodios para la evaluación

print(f"Preparando el entrenamiento para el entorno: {env_id}")
print(f"Los logs y modelos se guardarán en: {log_dir}")

# 1. Crear el entorno vectorializado
# Creamos 4 entornos paralelos para acelerar PPO
vec_env = make_vec_env(env_id, n_envs=4, seed=0)

# 2. Definir Callbacks para el entrenamiento:
# - StopTrainingOnNoModelImprovement: Detiene el entrenamiento si el modelo no mejora
#   (ahora es un sub-callback de EvalCallback).
stop_callback = StopTrainingOnNoModelImprovement(
    max_no_improvement_evals=3,
    min_evals=5,
    verbose=1
)

# - EvalCallback: Evalúa el modelo periódicamente y guarda el mejor modelo.
eval_callback = EvalCallback(
    vec_env,
    best_model_save_path=log_dir,
    log_path=log_dir,
    eval_freq=eval_freq // 4,
    n_eval_episodes=n_eval_episodes,
    deterministic=True,
    render=False, 
    callback_after_eval=stop_callback
)

# La lista de callbacks solo necesita el EvalCallback principal
callbacks = [eval_callback]

# 3. Definir el modelo PPO (Proximal Policy Optimization)
# policy="MlpPolicy" usa una red neuronal de tipo Multi-Layer Perceptron (MLP).
# verbose=1 muestra información de progreso durante el entrenamiento.
# tensorboard_log nos permite ver el progreso en TensorBoard.
# Opcionalmente, puedes añadir hiperparámetros aquí:
# por ejemplo: learning_rate=0.0001, gamma=0.999
model = PPO("MlpPolicy", vec_env, verbose=1, tensorboard_log=log_dir)

print(f"Iniciando el entrenamiento de la IA. Esto puede tomar un tiempo (aproximadamente {total_timesteps/1000:.0f}K pasos).")

# 4. Entrenar el agente
model.learn(total_timesteps=total_timesteps, callback=callbacks)

print("\n¡Entrenamiento completado!")

# 5. Guardar el modelo final (además del mejor guardado por EvalCallback)
model.save(f"{log_dir}lunarlander_ppo_final")
print(f"Modelo final guardado en {log_dir}lunarlander_ppo_final.zip")