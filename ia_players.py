import random
import numpy as np
import time

# Constantes del juego para las IAs
PADDLE_WIDTH = 15
BALL_SIZE = 15

# ====================================================================
# Clase base para las IAs
# ====================================================================
class IA:
    def __init__(self, screen_height, paddle_height, initial_state=None):
        self.screen_height = screen_height
        self.paddle_height = paddle_height
        self.frames_per_point = []
        self.state = {"iq": 0.0}
        self.initial_iq = 0.0
        self.final_iq = 0.0
        self.screen_width = 800
        if initial_state:
            self.state.update(initial_state)

    def move(self, ball_y, paddle_y):
        raise NotImplementedError("Este método debe ser implementado por las subclases")

    def register_point(self, frames):
        self.frames_per_point.append(frames)

    def get_iq(self):
        """
        Devuelve el valor actual de la IQ de la IA.
        """
        return self.state.get("iq", 0.0)

    def get_experience(self, final_score):
        """
        Calcula y registra la experiencia de la IA, actualizando su IQ.
        """
        if final_score == 1:
            self.state["iq"] += random.uniform(1.0, 5.0)
        elif final_score == -1:
            self.state["iq"] -= random.uniform(1.0, 5.0)
        
        experience = {
            "final_score": final_score,
            "average_frames_per_point": np.mean(self.frames_per_point) if self.frames_per_point else 0,
            "state": self.state
        }
        return experience

# ====================================================================
# Implementaciones de las IAs
# ====================================================================

# Implementación de IAD (Diablo)
class IAD(IA):
    """
    IA Diablo: Juega con movimientos aleatorios.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 5
        self.move_direction = 0
        self.move_change_frame = 0
        
        # Nuevas métricas para IAD
        self.state["iq_caos"] = initial_state.get("iq_caos", random.uniform(50.0, 100.0))
        self.state["iq_imprevisibilidad"] = initial_state.get("iq_imprevisibilidad", random.uniform(50.0, 100.0))
        self.state["iq_adaptabilidad"] = initial_state.get("iq_adaptabilidad", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y):
        if self.move_change_frame >= 30:
            self.move_direction = random.choice([-self.velocidad_base, self.velocidad_base])
            self.move_change_frame = 0
        
        self.move_change_frame += 1

        if paddle_y <= 0:
            self.move_direction = self.velocidad_base
        elif paddle_y + self.paddle_height >= self.screen_height:
            self.move_direction = -self.velocidad_base
            
        return self.move_direction
        
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_caos"] += random.uniform(1.0, 3.0)
            self.state["iq_imprevisibilidad"] += random.uniform(1.0, 3.0)
        elif final_score == -1:
            self.state["iq_caos"] -= random.uniform(1.0, 3.0)
            self.state["iq_imprevisibilidad"] -= random.uniform(1.0, 3.0)

        # El IQ total es un promedio ponderado de sus métricas
        self.state["iq"] = (self.state["iq_caos"] + self.state["iq_imprevisibilidad"] + self.state["iq_adaptabilidad"]) / 3
        
        return experience

# Implementación de IAA (Adivina)
class IAA(IA):
    """
    IA Adivina: Intenta predecir la posición de la bola.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 7
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAA
        self.state["iq_prediccion"] = initial_state.get("iq_prediccion", random.uniform(50.0, 100.0))
        self.state["iq_precision"] = initial_state.get("iq_precision", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y, ball_x, ball_speed_x, ball_speed_y):
        if ball_speed_x < 0:
            time_to_reach_paddle = (ball_x - (10 + PADDLE_WIDTH)) / -ball_speed_x
            predicted_y = ball_y + time_to_reach_paddle * ball_speed_y
            
            if predicted_y > paddle_y + self.paddle_height/2:
                return self.velocidad_base
            elif predicted_y < paddle_y + self.paddle_height/2:
                return -self.velocidad_base
        
        return 0

    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_prediccion"] += random.uniform(2.0, 5.0)
            self.state["iq_precision"] += random.uniform(2.0, 5.0)
        elif final_score == -1:
            self.state["iq_prediccion"] -= random.uniform(1.0, 3.0)
            self.state["iq_precision"] -= random.uniform(1.0, 3.0)
        
        self.state["iq"] = (self.state["iq_prediccion"] + self.state["iq_precision"]) / 2
        
        return experience

# Implementación de IAJ (Jugadora)
class IAJ(IA):
    """
    IA Jugadora: Se enfoca en la sensación del juego.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 6
        self.state["sentimiento"] = "frustración y sed de venganza"
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAJ
        self.state["iq_emocional"] = initial_state.get("iq_emocional", random.uniform(50.0, 100.0))
        self.state["iq_motivacion"] = initial_state.get("iq_motivacion", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y):
        if abs(paddle_y + self.paddle_height/2 - ball_y) > 10:
            if ball_y > paddle_y + self.paddle_height/2:
                return self.velocidad_base
            else:
                return -self.velocidad_base
        return 0

    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["sentimiento"] = "sentimiento de victoria y poder absoluto"
            self.state["iq_emocional"] += random.randint(10, 20)
            self.state["iq_motivacion"] += random.randint(5, 10)
        elif final_score == -1:
            self.state["sentimiento"] = "frustración y sed de venganza"
            self.state["iq_emocional"] -= random.randint(5, 10)
            self.state["iq_motivacion"] -= random.randint(1, 5)

        self.state["iq"] = (self.state["iq_emocional"] + self.state["iq_motivacion"]) / 2
        
        return experience

# Implementación de IAF (Flotadora)
class IAF(IA):
    """
    IA Flotadora: Utiliza múltiples paletas.
    """
    def __init__(self, screen_height, initial_state=None):
        super().__init__(screen_height, 20, initial_state)
        self.velocidad_base = 3
        self.num_paddles = 5
        self.paddles = [random.randint(0, screen_height - self.paddle_height) for _ in range(self.num_paddles)]
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAF
        self.state["iq_coordinacion"] = initial_state.get("iq_coordinacion", random.uniform(50.0, 100.0))
        self.state["iq_estrategia"] = initial_state.get("iq_estrategia", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddles_y):
        movement = [0] * self.num_paddles
        target_paddle_index = np.argmin([abs((y + self.paddle_height/2) - ball_y) for y in paddles_y])
        
        if ball_y > paddles_y[target_paddle_index] + self.paddle_height/2:
            movement[target_paddle_index] = self.velocidad_base
        elif ball_y < paddles_y[target_paddle_index] + self.paddle_height/2:
            movement[target_paddle_index] = -self.velocidad_base
            
        return movement
        
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_coordinacion"] += random.uniform(2.0, 5.0)
            self.state["iq_estrategia"] += random.uniform(2.0, 5.0)
        elif final_score == -1:
            self.state["iq_coordinacion"] -= random.uniform(1.0, 3.0)
            self.state["iq_estrategia"] -= random.uniform(1.0, 3.0)

        self.state["iq"] = (self.state["iq_coordinacion"] + self.state["iq_estrategia"]) / 2
        
        return experience

# Implementación de IAC (Cautelin)
class IAC(IA):
    """
    IA Cautelin: Juega de forma más pasiva, moviéndose aleatoriamente.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 3
        self.move_direction = 0
        self.move_change_frame = 0
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0

        # Nuevas métricas para IAC
        self.state["iq_cautela"] = initial_state.get("iq_cautela", random.uniform(50.0, 100.0))
        self.state["iq_paciencia"] = initial_state.get("iq_paciencia", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y):
        if self.move_change_frame >= 60:
            self.move_direction = random.choice([-self.velocidad_base, self.velocidad_base, 0])
            self.move_change_frame = 0
        
        self.move_change_frame += 1
        
        return self.move_direction
    
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_cautela"] += random.uniform(1.0, 3.0)
            self.state["iq_paciencia"] += random.uniform(1.0, 3.0)
        elif final_score == -1:
            self.state["iq_cautela"] -= random.uniform(1.0, 3.0)
            self.state["iq_paciencia"] -= random.uniform(1.0, 3.0)

        self.state["iq"] = (self.state["iq_cautela"] + self.state["iq_paciencia"]) / 2
        
        return experience

# Implementación de IAL (Lógico)
class IAL(IA):
    """
    IA Lógico: Calcula dónde va a llegar la pelota.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 7
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAL
        self.state["iq_analisis"] = initial_state.get("iq_analisis", random.uniform(50.0, 100.0))
        self.state["iq_logica"] = initial_state.get("iq_logica", random.uniform(50.0, 100.0))
        
    def move(self, ball_y, paddle_y, ball_x, ball_speed_x, ball_speed_y):
        if ball_speed_x > 0:
            return 0
        
        time_to_reach = (ball_x - (10 + PADDLE_WIDTH)) / -ball_speed_x
        predicted_y = ball_y + ball_speed_y * time_to_reach
        
        num_bounces = int(predicted_y / self.screen_height)
        if num_bounces % 2 == 1:
            predicted_y = (self.screen_height - predicted_y) % self.screen_height
        else:
            predicted_y = predicted_y % self.screen_height
            
        if predicted_y > paddle_y + self.paddle_height / 2:
            return self.velocidad_base
        elif predicted_y < paddle_y + self.paddle_height / 2:
            return -self.velocidad_base
        
        return 0
        
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_analisis"] += random.uniform(2.0, 5.0)
            self.state["iq_logica"] += random.uniform(2.0, 5.0)
        elif final_score == -1:
            self.state["iq_analisis"] -= random.uniform(1.0, 3.0)
            self.state["iq_logica"] -= random.uniform(1.0, 3.0)

        self.state["iq"] = (self.state["iq_analisis"] + self.state["iq_logica"]) / 2
        
        return experience
        
# Implementación de IAM (Movi)
class IAM(IA):
    """
    IA Movi: Mueve la paleta de forma reactiva y constante.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 5
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAM
        self.state["iq_reactividad"] = initial_state.get("iq_reactividad", random.uniform(50.0, 100.0))
        self.state["iq_constancia"] = initial_state.get("iq_constancia", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y):
        if ball_y > paddle_y + self.paddle_height/2:
            return self.velocidad_base
        elif ball_y < paddle_y + self.paddle_height/2:
            return -self.velocidad_base
        return 0
    
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_reactividad"] += random.uniform(1.0, 3.0)
            self.state["iq_constancia"] += random.uniform(1.0, 3.0)
        elif final_score == -1:
            self.state["iq_reactividad"] -= random.uniform(1.0, 3.0)
            self.state["iq_constancia"] -= random.uniform(1.0, 3.0)
        
        self.state["iq"] = (self.state["iq_reactividad"] + self.state["iq_constancia"]) / 2
        
        return experience
        
# Implementación de IAR (Velocidad)
class IAR(IA):
    """
    IA de Velocidad: Muy rápida, pero con lógica simple.
    """
    def __init__(self, screen_height, paddle_height, initial_state=None):
        super().__init__(screen_height, paddle_height, initial_state)
        self.velocidad_base = 10
        self.state["iq"] = initial_state.get("iq", 0.0) if initial_state else 0.0
        
        # Nuevas métricas para IAR
        self.state["iq_reaccion"] = initial_state.get("iq_reaccion", random.uniform(50.0, 100.0))
        self.state["iq_velocidad"] = initial_state.get("iq_velocidad", random.uniform(50.0, 100.0))
        self.state["iq_agresividad"] = initial_state.get("iq_agresividad", random.uniform(50.0, 100.0))

    def move(self, ball_y, paddle_y):
        if ball_y > paddle_y + self.paddle_height/2:
            return self.velocidad_base
        elif ball_y < paddle_y + self.paddle_height/2:
            return -self.velocidad_base
        return 0
        
    def get_experience(self, final_score):
        experience = super().get_experience(final_score)
        
        if final_score == 1:
            self.state["iq_reaccion"] += random.uniform(5.0, 10.0)
            self.state["iq_velocidad"] += random.uniform(5.0, 10.0)
            self.state["iq_agresividad"] += random.uniform(5.0, 10.0)
        elif final_score == -1:
            self.state["iq_reaccion"] -= random.uniform(3.0, 7.0)
            self.state["iq_velocidad"] -= random.uniform(3.0, 7.0)
            self.state["iq_agresividad"] -= random.uniform(3.0, 7.0)
        
        self.state["iq"] = (self.state["iq_reaccion"] + self.state["iq_velocidad"] + self.state["iq_agresividad"]) / 3
            
        return experience