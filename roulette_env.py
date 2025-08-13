import gymnasium as gym
from gymnasium import spaces
import numpy as np
from collections import deque
import os

class RouletteEnv(gym.Env):
    def __init__(self, initial_balance=100.0):
        super(RouletteEnv, self).__init__()
        
        self.action_space = spaces.MultiBinary(16)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(38,), dtype=np.float32)
        
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.current_step = 0
        self.max_steps = 1000000
        
        # El historial de la IA se limita a las últimas 10,000 jugadas para optimizar el rendimiento.
        self.history_size = 10000 
        self.full_history_file = './roulette_logs/roulette_full_history.txt'
        self.winning_numbers_history = self._load_history()

    def _load_history(self):
        history = deque(maxlen=self.history_size)
        if os.path.exists(self.full_history_file):
            with open(self.full_history_file, 'r') as f:
                content = f.read().strip()
                if content:
                    numbers = [int(n) for n in content.split(',') if n]
                    history.extend(numbers[-self.history_size:])
        return history

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.current_step = 0
        
        observation = self._get_obs()
        info = {}
        return observation, info

    def step(self, action):
        self.current_step += 1
        
        roulette_result = self.np_random.integers(0, 37)
        self.winning_numbers_history.append(roulette_result)
        
        total_reward = 0.0
        active_bets_count = np.sum(action)
        
        if active_bets_count == 0:
            total_reward -= 0.5
        
        for bet_index, is_bet_active in enumerate(action):
            if is_bet_active:
                reward = self._calculate_reward(bet_index, roulette_result)
                total_reward += reward

        self.balance += total_reward
        
        terminated = self.balance <= 0 or self.current_step >= self.max_steps
        truncated = False
        observation = self._get_obs()
        info = {'roulette_result': roulette_result}
        
        return observation, total_reward, terminated, truncated, info

    def _get_obs(self):
        number_frequencies = np.zeros(37, dtype=np.float32)
        if self.winning_numbers_history:
            for number in self.winning_numbers_history:
                number_frequencies[number] += 1
            number_frequencies /= len(self.winning_numbers_history)
        
        observation = np.concatenate(([self.balance], number_frequencies)).astype(np.float32)
        return observation

    def _calculate_reward(self, bet_index, result):
        reward = -1.0 
        
        is_red = result in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        is_even = result % 2 == 0
        is_low = 1 <= result <= 18
        is_first_dozen = 1 <= result <= 12
        is_second_dozen = 13 <= result <= 24
        is_third_dozen = 25 <= result <= 36
        is_first_column = result in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        is_second_column = result in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
        is_third_column = result in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

        voisins_du_zero = [2, 0, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35]
        tiers_du_cylindre = [5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36]
        orphelins = [1, 6, 9, 14, 17, 20, 31, 34]
        
        if bet_index == 0 and is_red:
            reward = 1.0
        elif bet_index == 1 and not is_red:
            reward = 1.0
        elif bet_index == 2 and is_even:
            reward = 1.0
        elif bet_index == 3 and not is_even:
            reward = 1.0
        elif bet_index == 4 and is_low:
            reward = 1.0
        elif bet_index == 5 and not is_low:
            reward = 1.0
        elif bet_index == 6 and is_first_dozen:
            reward = 2.0
        elif bet_index == 7 and is_second_dozen:
            reward = 2.0
        elif bet_index == 8 and is_third_dozen:
            reward = 2.0
        elif bet_index == 9 and is_first_column:
            reward = 2.0
        elif bet_index == 10 and is_second_column:
            reward = 2.0
        elif bet_index == 11 and is_third_column:
            reward = 2.0
        elif bet_index == 12 and result == 7:
            reward = 35.0
        elif bet_index == 13 and result in voisins_du_zero:
            reward = 2.0
        elif bet_index == 14 and result in tiers_du_cylindre:
            reward = 2.0
        elif bet_index == 15 and result in orphelins:
            reward = 2.0
            
        return reward