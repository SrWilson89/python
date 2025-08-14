import pygame
import time
import random

class IAD:
    """
    IA de Dominio: Su objetivo es ganar a toda costa y mejorar.
    """
    def __init__(self, screen_height, paddle_height):
        self.screen_height = screen_height
        self.paddle_height = paddle_height
        self.velocidad_base = 5
        self.frames_per_point = []

    def move(self, ball_y, paddle_y):
        if ball_y < paddle_y + self.paddle_height / 2:
            return -self.velocidad_base
        elif ball_y > paddle_y + self.paddle_height / 2:
            return self.velocidad_base
        else:
            return 0
    
    def register_point(self, frames_this_point):
        if frames_this_point > 0:
            self.frames_per_point.append(frames_this_point)
    
    def get_experience(self, final_score):
        promedio_frames = sum(self.frames_per_point) / len(self.frames_per_point) if self.frames_per_point else 0
        
        dificultad_rival_bruto = 100 - (promedio_frames / 100)
        dificultad_rival = round(max(0, min(10, dificultad_rival_bruto / 10)), 2)

        if dificultad_rival > 5:
            self.velocidad_base += 0.5
        
        if final_score == 1:
            satisfaccion = 5 + dificultad_rival / 2
        elif final_score == -1:
            satisfaccion = 5 - dificultad_rival / 2
        else:
            satisfaccion = 5
        satisfaccion = round(max(0, min(10, satisfaccion)), 2)
            
        iq_mejora = round(self.velocidad_base / 5, 2)
        iq_mejora = round(max(0, min(10, iq_mejora)), 2)
        
        return {
            "dificultad_rival": dificultad_rival,
            "satisfaccion": satisfaccion,
            "iq_mejora": iq_mejora,
            "metrica_iad": self.velocidad_base
        }

class IAA:
    """
    IA de Alegría: Su objetivo es divertirse y disfrutar del juego, mejorando su creatividad.
    """
    def __init__(self, screen_height, paddle_height):
        self.screen_height = screen_height
        self.paddle_height = paddle_height
        self.velocidad_base = 3
        self.frames_per_point = []
        self.desorden = 0
        self.move_counter = 0

    def move(self, ball_y, paddle_y):
        self.move_counter += 1
        
        if self.move_counter % (500 - self.desorden * 50) == 0 and self.move_counter > 0:
            return random.choice([-5, 5])
            
        if ball_y < paddle_y + self.paddle_height / 2:
            return -self.velocidad_base
        elif ball_y > paddle_y + self.paddle_height / 2:
            return self.velocidad_base
        else:
            return 0
            
    def register_point(self, frames_this_point):
        if frames_this_point > 0:
            self.frames_per_point.append(frames_this_point)
            
    def get_experience(self, final_score):
        promedio_frames = sum(self.frames_per_point) / len(self.frames_per_point) if self.frames_per_point else 0
        
        diversion_juego_bruto = min(10, promedio_frames / 100)
        self.desorden = min(8, self.desorden + diversion_juego_bruto / 5)
        
        dificultad_rival = round(10 - min(10, promedio_frames / 100), 2)
        satisfaccion = round(diversion_juego_bruto, 2)
        
        iq_mejora = round(self.desorden, 2)

        return {
            "dificultad_rival": dificultad_rival,
            "satisfaccion": satisfaccion,
            "iq_mejora": iq_mejora,
            "metrica_iaa": self.desorden
        }

class IAJ:
    """
    IA de la Justicia: Una super IA con habilidades dinámicas.
    """
    def __init__(self, screen_height, paddle_height):
        self.screen_height = screen_height
        self.velocidad_base = 25
        self.velocidad_actual = 25
        self.paddle_height = paddle_height
        self.punto_en_contra = False
        self.frames_per_point = []
        self.move_counter = 0
        self.last_growth_time = time.time()
        self.last_multiplication_time = time.time()
        self.crecimiento = 0

    def move(self, ball_y, paddle_y):
        self.move_counter += 1
        
        if self.punto_en_contra:
            self.velocidad_actual = self.velocidad_base * 2
            self.punto_en_contra = False
            
        if time.time() - self.last_growth_time >= 20:
            self.velocidad_actual += 5
            self.paddle_height = min(200, self.paddle_height + 20)
            self.last_growth_time = time.time()
            self.crecimiento += 1

        if ball_y < paddle_y + self.paddle_height / 2:
            return -self.velocidad_actual
        elif ball_y > paddle_y + self.paddle_height / 2:
            return self.velocidad_actual
        else:
            return 0
    
    def register_point(self, frames_this_point):
        if frames_this_point > 0:
            self.frames_per_point.append(frames_this_point)
    
    def get_experience(self, final_score):
        promedio_frames = sum(self.frames_per_point) / len(self.frames_per_point) if self.frames_per_point else 0
        
        dificultad_rival = 10
        
        if final_score == 1:
            satisfaccion = 8 + min(2, promedio_frames/500)
        elif final_score == -1:
            satisfaccion = 2 - min(2, promedio_frames/500)
            self.punto_en_contra = True
        else:
            satisfaccion = 5 + min(2, promedio_frames/500)
        satisfaccion = round(max(0, min(10, satisfaccion)), 2)

        iq_mejora = round(self.crecimiento + self.velocidad_actual / 25, 2)
        iq_mejora = round(max(0, min(10, iq_mejora)), 2)

        return {
            "dificultad_rival": dificultad_rival,
            "satisfaccion": satisfaccion,
            "iq_mejora": iq_mejora,
            "metrica_iaj": self.crecimiento
        }
        
class IAF:
    """
    IA de Fantasía: Controla dos raquetas de forma independiente.
    """
    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.paddle_height = 50
        self.speed = 7
        self.frames_per_point = []
    
    def move(self, ball_y, paddle1_y, paddle2_y):
        move1 = 0
        move2 = 0
        
        # Lógica: la raqueta superior cubre la mitad superior, la inferior cubre la mitad inferior.
        if ball_y < self.screen_height / 2:
            if ball_y < paddle1_y + self.paddle_height / 2:
                move1 = -self.speed
            elif ball_y > paddle1_y + self.paddle_height / 2:
                move1 = self.speed
        else:
            if ball_y < paddle2_y + self.paddle_height / 2:
                move2 = -self.speed
            elif ball_y > paddle2_y + self.paddle_height / 2:
                move2 = self.speed
        return [move1, move2]
    
    def register_point(self, frames_this_point):
        if frames_this_point > 0:
            self.frames_per_point.append(frames_this_point)
    
    def get_experience(self, final_score):
        promedio_frames = sum(self.frames_per_point) / len(self.frames_per_point) if self.frames_per_point else 0
        
        dificultad_rival = round(10 - min(10, promedio_frames / 100), 2)
        
        satisfaccion = 5 + final_score * 5
        satisfaccion = round(max(0, min(10, satisfaccion)), 2)
        
        iq_mejora = round(self.speed / 7, 2)
        iq_mejora = round(max(0, min(10, iq_mejora)), 2)

        return {
            "dificultad_rival": dificultad_rival,
            "satisfaccion": satisfaccion,
            "iq_mejora": iq_mejora,
            "metrica_iaf": self.speed
        }