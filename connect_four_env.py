import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame

class ConnectFourEnv(gym.Env):
    # ¡IMPORTANTE! Hemos añadido 'rgb_array' aquí
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 1}

    def __init__(self, render_mode=None):
        super().__init__()
        self.rows = 6
        self.cols = 7
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = 1  # 1 for player 1 (red), -1 for player 2 (yellow)
        self.winner = 0

        # El espacio de observación es el tablero
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.rows, self.cols), dtype=int)
        # El espacio de acción son las 7 columnas
        self.action_space = spaces.Discrete(self.cols)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        self.clock = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = 1
        self.winner = 0
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        row = self._get_next_open_row(action)
        self.board[row][action] = self.current_player
        
        # Verificar si hay un ganador o un empate
        if self._is_winning_move(self.current_player):
            self.winner = self.current_player
            reward = self._get_reward(self.winner)
            terminated = True
        elif len(self._get_valid_locations()) == 0:
            self.winner = 0  # Empate
            reward = self._get_reward(self.winner)
            terminated = True
        else:
            reward = 0
            terminated = False

        # Cambiar de jugador
        self.current_player *= -1

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

    def _get_obs(self):
        return self.board.copy()

    def _get_info(self):
        return {"current_player": self.current_player, "winner": self.winner}

    def _is_valid_location(self, col):
        return self.board[self.rows - 1][col] == 0

    def _get_next_open_row(self, col):
        for r in range(self.rows):
            if self.board[r][col] == 0:
                return r
        return -1

    def _get_valid_locations(self):
        return [col for col in range(self.cols) if self._is_valid_location(col)]

    def _is_winning_move(self, player):
        # Comprobar movimientos horizontales
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if self.board[r][c] == player and self.board[r][c + 1] == player and \
                   self.board[r][c + 2] == player and self.board[r][c + 3] == player:
                    return True

        # Comprobar movimientos verticales
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if self.board[r][c] == player and self.board[r + 1][c] == player and \
                   self.board[r + 2][c] == player and self.board[r + 3][c] == player:
                    return True

        # Comprobar movimientos diagonales positivos
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if self.board[r][c] == player and self.board[r + 1][c + 1] == player and \
                   self.board[r + 2][c + 2] == player and self.board[r + 3][c + 3] == player:
                    return True

        # Comprobar movimientos diagonales negativos
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if self.board[r][c] == player and self.board[r - 1][c + 1] == player and \
                   self.board[r - 2][c + 2] == player and self.board[r - 3][c + 3] == player:
                    return True
        return False

    def _get_reward(self, winner):
        if winner == 1:
            return 1  # Gana jugador 1 (IA)
        elif winner == -1:
            return -1  # Gana jugador 2 (aleatorio)
        else:
            return 0  # Empate

    def render(self):
        if self.render_mode == "human":
            self._render_frame()
        return self._render_frame() if self.render_mode == "rgb_array" else None

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window_size = 100
            self.cell_size = 80
            self.width = self.cols * self.cell_size
            self.height = self.rows * self.cell_size + self.cell_size
            self.window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Cuatro en Raya")

        canvas = pygame.Surface((self.width, self.height))
        canvas.fill((240, 240, 240))

        # Dibujar tablero
        for c in range(self.cols):
            for r in range(self.rows):
                pygame.draw.rect(canvas, (0, 0, 255), (c * self.cell_size, (r + 1) * self.cell_size, self.cell_size, self.cell_size))
                
                # Dibujar las fichas
                if self.board[r][c] == 1:
                    pygame.draw.circle(canvas, (255, 0, 0), 
                                       (c * self.cell_size + self.cell_size // 2, (self.rows - r) * self.cell_size + self.cell_size // 2), 
                                       self.cell_size // 2 - 5)
                elif self.board[r][c] == -1:
                    pygame.draw.circle(canvas, (255, 255, 0), 
                                       (c * self.cell_size + self.cell_size // 2, (self.rows - r) * self.cell_size + self.cell_size // 2), 
                                       self.cell_size // 2 - 5)
                else:
                    pygame.draw.circle(canvas, (0, 0, 0), 
                                       (c * self.cell_size + self.cell_size // 2, (self.rows - r) * self.cell_size + self.cell_size // 2), 
                                       self.cell_size // 2 - 5)
        
        # Dibujar las fichas en la parte superior
        for c in range(self.cols):
            if self.board[self.rows - 1][c] == 0:
                pygame.draw.circle(canvas, (0, 0, 0), 
                                   (c * self.cell_size + self.cell_size // 2, self.cell_size // 2), 
                                   self.cell_size // 2 - 5)

        if self.render_mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
        elif self.render_mode == "rgb_array":
            return np.transpose(
                pygame.surfarray.array3d(canvas), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None