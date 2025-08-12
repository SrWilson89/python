import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
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

# --- Configuración del entrenamiento ---
log_dir = "./connect_four_dqn_logs/"
os.makedirs(log_dir, exist_ok=True)

env_id = "ConnectFour-v0"

# Vamos a entrenar por 50,000 pasos.
total_timesteps = 50000

print(f"Preparando el entrenamiento para el entorno: {env_id}")
print(f"Los logs y modelos se guardarán en: {log_dir}")

# 1. Crear el entorno
vec_env = make_vec_env(env_id, n_envs=1, seed=0)

# 2. Definir el modelo DQN
model = DQN(
    "MlpPolicy", 
    vec_env, 
    verbose=1, 
    learning_rate=0.0005, 
    buffer_size=10000, 
    tensorboard_log=log_dir
)

# 3. Entrenar el agente sin callbacks
print(f"Iniciando el entrenamiento de la IA. Esto puede tomar un tiempo.")
model.learn(total_timesteps=total_timesteps)

print("\n¡Entrenamiento completado!")

# 4. Guardar el modelo final
model.save(f"{log_dir}connect_four_dqn_final")
print(f"Modelo final guardado en {log_dir}connect_four_dqn_final.zip")