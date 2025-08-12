import gymnasium as gym
from gymnasium import spaces
import numpy as np

class RouletteEnv(gym.Env):
    def __init__(self, initial_balance=100.0):
        super(RouletteEnv, self).__init__()
        
        # El espacio de acción ahora es MultiBinary(10) para permitir múltiples apuestas.
        # [0:Rojo, 1:Negro, 2:Par, 3:Impar, 4:1-18, 5:19-36, 6:1ª Docena, 7:2ª Docena, 8:3ª Docena, 9:Número Directo]
        self.action_space = spaces.MultiBinary(10)
        
        # El espacio de observación es el saldo actual.
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)
        
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        
        self.single_bet_amount = 1.0
        self.current_step = 0
        self.max_steps = 1000000

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.current_step = 0
        observation = np.array([self.balance], dtype=np.float32)
        info = {}
        return observation, info

    def step(self, action):
        self.current_step += 1
        
        # Genera el resultado de la ruleta (0-36)
        roulette_result = self.np_random.integers(0, 37)
        
        total_reward = 0.0
        
        # Itera sobre todas las posibles apuestas para calcular la recompensa total.
        for bet_index, is_bet_active in enumerate(action):
            if is_bet_active:
                reward = self._calculate_reward(bet_index, roulette_result)
                total_reward += reward

        # Actualiza el saldo con la recompensa total de todas las apuestas.
        self.balance += total_reward
        
        terminated = self.balance <= 0 or self.current_step >= self.max_steps
        truncated = False
        observation = np.array([self.balance], dtype=np.float32)
        info = {'roulette_result': roulette_result}
        
        return observation, total_reward, terminated, truncated, info

    def _calculate_reward(self, bet_index, result):
        # La apuesta se resta aquí, antes de ver el resultado.
        reward = -self.single_bet_amount
        
        # Lógica de las recompensas
        if result == 0:
            return reward
            
        is_red = result in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        is_black = not is_red
        is_even = result % 2 == 0
        is_odd = not is_even
        is_low = 1 <= result <= 18
        is_high = 19 <= result <= 36
        is_first_dozen = 1 <= result <= 12
        is_second_dozen = 13 <= result <= 24
        is_third_dozen = 25 <= result <= 36
        
        # Se verifica qué apuesta ha sido exitosa
        if bet_index == 0 and is_red:
            reward += 2.0
        elif bet_index == 1 and is_black:
            reward += 2.0
        elif bet_index == 2 and is_even:
            reward += 2.0
        elif bet_index == 3 and is_odd:
            reward += 2.0
        elif bet_index == 4 and is_low:
            reward += 2.0
        elif bet_index == 5 and is_high:
            reward += 2.0
        elif bet_index == 6 and is_first_dozen:
            reward += 3.0
        elif bet_index == 7 and is_second_dozen:
            reward += 3.0
        elif bet_index == 8 and is_third_dozen:
            reward += 3.0
        elif bet_index == 9 and result == 7: # Apuesta a un número directo (ej. 7)
            reward += 36.0
            
        return reward

    def _get_obs(self):
        return np.array([self.balance], dtype=np.float32)

    def _get_info(self):
        return {}