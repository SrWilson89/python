import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_atari_env
from stable_baselines3.common.vec_env import VecFrameStack
import os

# --- Configuración del entrenamiento ---
# Directorio para guardar logs y el mejor modelo
log_dir = "./breakout_dqn_logs/" 
os.makedirs(log_dir, exist_ok=True)

# ID del entorno de Atari
env_id = "ALE/Breakout-v5"

# Número total de pasos de entrenamiento. Los juegos de Atari necesitan muchos más pasos.
total_timesteps = 2500000

print(f"Preparando el entrenamiento para el entorno: {env_id}")
print(f"Los logs y modelos se guardarán en: {log_dir}")

# 1. Crear el entorno Atari vectorializado y preprocesado
# make_atari_env aplica automáticamente varios wrappers importantes
# como el de preprocesamiento de imágenes (AtariPreprocessing).
# N.º de entornos = 4, para acelerar el entrenamiento.
env = make_atari_env(env_id, n_envs=4, seed=0)

# 2. Apilar 4 frames para que la IA entienda el movimiento
# La IA necesita ver varios frames seguidos para detectar movimiento (por ejemplo, la pelota).
env = VecFrameStack(env, n_stack=4)

# 3. Definir el modelo DQN (Deep Q-Network)
# policy="CnnPolicy" usa una red neuronal convolucional para procesar las imágenes.
# learning_rate y buffer_size son hiperparámetros que puedes ajustar.
model = DQN(
    "CnnPolicy", 
    env, 
    verbose=1, 
    learning_rate=0.00001, 
    buffer_size=10000, 
    tensorboard_log=log_dir
)

print(f"Iniciando el entrenamiento de la IA. Esto puede tomar un tiempo (aproximadamente {total_timesteps/1000000:.1f}M pasos).")

# 4. Entrenar el agente
model.learn(total_timesteps=total_timesteps)

print("\n¡Entrenamiento completado!")

# 5. Guardar el modelo final
model.save(f"{log_dir}breakout_dqn_final")
print(f"Modelo final guardado en {log_dir}breakout_dqn_final.zip")