import gymnasium as gym
from gymnasium import spaces
import numpy as np
from gymnasium.error import DependencyNotInstalled

class TicTacToeEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': 4}

    def __init__(self, render_mode=None):
        super().__init__()
        # Definir el espacio de observación: un array de 9 elementos (3x3 tablero)
        # 0: vacío, 1: jugador X, -1: jugador O
        self.observation_space = spaces.Box(low=-1, high=1, shape=(9,), dtype=np.int8)

        # Definir el espacio de acción: 9 posibles casillas donde colocar la ficha (0-8)
        self.action_space = spaces.Discrete(9)

        self.board = np.zeros(9, dtype=np.int8) # Tablero de 3x3
        self.current_player = 1 # 1 para X, -1 para O
        self.winner = 0 # 0: nadie, 1: X, -1: O
        self.done = False # True si el juego terminó
        self.info = {} # Información adicional

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.screen = None
        self.clock = None


    def _get_obs(self):
        return self.board.copy() # Devolver una copia para evitar modificaciones externas

    def _get_info(self):
        return self.info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = np.zeros(9, dtype=np.int8)
        self.current_player = 1 # X siempre empieza
        self.winner = 0
        self.done = False
        self.info = {}

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        reward = 0
        terminated = False
        truncated = False # Tic-Tac-Toe no tiene truncación por tiempo/pasos

        # 1. Validar la acción
        if self.board[action] != 0 or self.done: # Si la casilla ya está ocupada o el juego terminó
            reward = -10 # Penalización por movimiento inválido
            terminated = True # El juego termina por un movimiento inválido (el agente hizo algo muy mal)
        else:
            # 2. Ejecutar la acción
            self.board[action] = self.current_player

            # 3. Comprobar si hay ganador o empate
            self.winner = self._check_winner()
            if self.winner != 0: # Si hay un ganador
                reward = 10 if self.winner == 1 else -10 # Recompensa al ganador, penalización al perdedor
                terminated = True
            elif np.all(self.board != 0): # Si el tablero está lleno y no hay ganador (empate)
                reward = 0 # Recompensa neutral por empate
                terminated = True

            # 4. Cambiar de jugador si el juego no ha terminado
            if not terminated:
                self.current_player *= -1 # Cambia de 1 a -1 o de -1 a 1

        self.done = terminated # Actualizar el estado 'done' del entorno

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def _check_winner(self):
        # Filas, columnas y diagonales ganadoras
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columnas
            [0, 4, 8], [2, 4, 6]             # Diagonales
        ]
        for line in winning_lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != 0:
                return self.board[line[0]] # Devuelve 1 (X) o -1 (O)
        return 0 # No hay ganador

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        try:
            import pygame
        except ImportError:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install gymnasium[classic-control]`"
            )

        if self.screen is None:
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode((300, 300))
            pygame.display.set_caption("Tres en Raya AI")
        if self.clock is None:
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((300, 300))
        canvas.fill((255, 255, 255))  # Blanco de fondo

        # Dibujar líneas del tablero
        pygame.draw.line(canvas, (0, 0, 0), (100, 0), (100, 300), 2)
        pygame.draw.line(canvas, (0, 0, 0), (200, 0), (200, 300), 2)
        pygame.draw.line(canvas, (0, 0, 100), (0, 100), (300, 100), 2)
        pygame.draw.line(canvas, (0, 0, 0), (0, 200), (300, 200), 2)

        # Dibujar X y O
        font = pygame.font.Font(None, 100)
        for i in range(9):
            row = i // 3
            col = i % 3
            x_pos = col * 100 + 50
            y_pos = row * 100 + 50
            if self.board[i] == 1:
                text_surface = font.render("X", True, (255, 0, 0)) # Rojo para X
                text_rect = text_surface.get_rect(center=(x_pos, y_pos))
                canvas.blit(text_surface, text_rect)
            elif self.board[i] == -1:
                text_surface = font.render("O", True, (0, 0, 255)) # Azul para O
                text_rect = text_surface.get_rect(center=(x_pos, y_pos))
                canvas.blit(text_surface, text_rect)

        # Si el juego ha terminado, mostrar el ganador
        if self.done and self.winner != 0:
            winner_char = "X" if self.winner == 1 else "O"
            if self.winner == 0 and np.all(self.board != 0): # Es un empate
                message = "¡Empate!"
                color = (0, 0, 0) # Negro
            else:
                message = f"¡Gana {winner_char}!"
                color = (0, 150, 0) if self.winner == 1 else (150, 0, 0) # Verde para X, rojo para O

            text_surface = font.render(message, True, color)
            text_rect = text_surface.get_rect(center=(150, 150))
            canvas.blit(text_surface, text_rect)


        self.screen.blit(canvas, canvas.get_rect())
        pygame.event.pump()
        pygame.display.update()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen is not None:
            import pygame
            pygame.display.quit()
            pygame.quit()
            self.screen = None
            self.clock = None