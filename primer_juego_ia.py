import gymnasium as gym
import time # Para añadir un pequeño retraso y ver la simulación

# 1. Crear el entorno del juego (cambia 'CartPole-v1' si eliges otro)
env = gym.make("CartPole-v1", render_mode="human") # 'human' para ver la ventana del juego

# 2. Reiniciar el entorno para empezar una nueva "partida"
observation, info = env.reset()

# 3. Simular algunas acciones aleatorias
# 'episodes' se refiere a la cantidad de "partidas" que queremos simular
for _ in range(5): # Jugaremos 5 partidas (episodios) de ejemplo
    observation, info = env.reset() # Reiniciar al inicio de cada episodio
    terminated = False # True si el episodio termina (pierdes, ganas, etc.)
    truncated = False  # True si el episodio es truncado (ej. límite de tiempo)
    score = 0          # Para llevar la cuenta de la puntuación en el episodio

    while not terminated and not truncated:
        # env.action_space.sample() elige una acción aleatoria válida para el entorno
        action = env.action_space.sample()

        # Realizar la acción y obtener el nuevo estado, la recompensa, etc.
        # observation: el nuevo estado del juego
        # reward: la recompensa obtenida por la acción
        # terminated: True si el episodio terminó (ej. el poste se cayó)
        # truncated: True si el episodio fue truncado (ej. se agotó el tiempo)
        # info: información adicional del entorno (diccionario)
        observation, reward, terminated, truncated, info = env.step(action)

        score += reward # Acumular la recompensa
        env.render()    # Mostrar la ventana del juego (si render_mode="human")
        time.sleep(0.01) # Pequeña pausa para que podamos ver la simulación

    print(f"Episodio terminado. Puntuación: {score}")

# 4. Cerrar el entorno al finalizar
env.close()
print("Simulación completa.")