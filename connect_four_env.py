import gymnasium as gym
from gymnasium import spaces
import numpy as np
from gymnasium.error import DependencyNotInstalled

class ConnectFourEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': 4}

    def __init__(self, render_mode=None):
        super().__init__()
        self.rows = 6
        self.cols = 7
        self.winning_length = 4 # Cuatro en raya

        # Espacio de observación: El tablero de 6x7
        # 0: vacío, 1: Jugador 1 (rojo), -1: Jugador 2 (amarillo)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.rows, self.cols), dtype=np.int8)

        # Espacio de acción: Elegir una columna (0 a 6)
        self.action_space = spaces.Discrete(self.cols)

        self.board = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.current_player = 1 # 1 para Jugador 1 (rojo), -1 para Jugador 2 (amarillo)
        self.winner = 0 # 0: nadie, 1: J1, -1: J2
        self.done = False # True si el juego terminó
        self.info = {}

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.screen = None
        self.clock = None
        self.square_size = 80
        self.radius = int(self.square_size / 2 - 5)

    def _get_obs(self):
        return self.board.copy()

    def _get_info(self):
        return self.info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.current_player = 1 # El Jugador 1 siempre empieza
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
        truncated = False

        # 1. Validar la acción: la columna debe estar dentro del rango y no estar llena
        if not (0 <= action < self.cols) or not self._is_valid_location(action) or self.done:
            reward = -10 # Penalización por movimiento inválido
            terminated = True
            self.info['invalid_move'] = True # Añadir info para depuración
        else:
            self.info['invalid_move'] = False
            # 2. Ejecutar la acción: soltar la ficha
            row = self._get_next_open_row(action)
            self.board[row][action] = self.current_player

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

    def _is_valid_location(self, col):
        return self.board[self.rows - 1][col] == 0

    def _get_next_open_row(self, col):
        for r in range(self.rows):
            if self.board[r][col] == 0:
                return r

    def _check_winner(self):
        player = self.current_player # El jugador que acaba de hacer el movimiento

        # Check horizontal locations for win
        for c in range(self.cols - self.winning_length + 1):
            for r in range(self.rows):
                if all(self.board[r][c + i] == player for i in range(self.winning_length)):
                    return player

        # Check vertical locations for win
        for c in range(self.cols):
            for r in range(self.rows - self.winning_length + 1):
                if all(self.board[r + i][c] == player for i in range(self.winning_length)):
                    return player

        # Check positively sloped diagonals
        for c in range(self.cols - self.winning_length + 1):
            for r in range(self.rows - self.winning_length + 1):
                if all(self.board[r + i][c + i] == player for i in range(self.winning_length)):
                    return player

        # Check negatively sloped diagonals
        for c in range(self.cols - self.winning_length + 1):
            for r in range(self.winning_length - 1, self.rows):
                if all(self.board[r - i][c + i] == player for i in range(self.winning_length)):
                    return player
        return 0 # No hay ganador

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        try:
            import pygame
        except ImportError:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install pygame`"
            )

        if self.screen is None:
            pygame.init()
            pygame.display.init()
            # El tamaño de la pantalla se calcula por el tamaño del tablero y el tamaño de las casillas
            screen_width = self.cols * self.square_size
            screen_height = (self.rows + 1) * self.square_size # +1 para la fila superior de donde caen las fichas
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Cuatro en Raya AI")
        if self.clock is None:
            self.clock = pygame.time.Clock()

        # Dibujar el tablero de Cuatro en Raya
        # Fondo azul del tablero
        canvas = pygame.Surface((self.cols * self.square_size, (self.rows + 1) * self.square_size))
        canvas.fill((0, 0, 255)) # Azul

        # Dibujar círculos para los espacios vacíos y las fichas
        for c in range(self.cols):
            for r in range(self.rows):
                # Calcular la posición central del círculo
                center_x = int(c * self.square_size + self.square_size / 2)
                # + square_size para dejar espacio para la fila superior de "caída"
                center_y = int(r * self.square_size + self.square_size + self.square_size / 2)

                if self.board[self.rows - 1 - r][c] == 0: # Fichas se apilan desde abajo
                    # Dibujar círculos negros para espacios vacíos
                    pygame.draw.circle(canvas, (0, 0, 0), (center_x, center_y), self.radius)
                elif self.board[self.rows - 1 - r][c] == 1:
                    # Dibujar fichas rojas para Jugador 1
                    pygame.draw.circle(canvas, (255, 0, 0), (center_x, center_y), self.radius)
                else: # self.board[self.rows - 1 - r][c] == -1
                    # Dibujar fichas amarillas para Jugador 2
                    pygame.draw.circle(canvas, (255, 255, 0), (center_x, center_y), self.radius)

        # Mostrar mensaje de ganador/empate
        if self.done:
            font = pygame.font.Font(None, 75)
            message = ""
            color = (0, 0, 0) # Negro
            if self.winner == 1:
                message = "¡Gana Jugador Rojo!"
                color = (255, 0, 0)
            elif self.winner == -1:
                message = "¡Gana Jugador Amarillo!"
                color = (255, 255, 0)
            elif np.all(self.board != 0): # Empate
                message = "¡Empate!"
                color = (200, 200, 200) # Gris claro

            text_surface = font.render(message, True, color)
            # Posición en la fila superior (donde caen las fichas)
            text_rect = text_surface.get_rect(center=(self.cols * self.square_size / 2, self.square_size / 2))
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