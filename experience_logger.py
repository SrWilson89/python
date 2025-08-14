import json
import os

class ExperienceLogger:
    def __init__(self, filename="game_log.json"):
        self.filename = filename
        self.log_data = []

        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    self.log_data = json.load(f)
                except json.JSONDecodeError:
                    self.log_data = []

    def log(self, player_name, game_data):
        self.log_data.append({
            "player": player_name,
            "game_data": game_data
        })

    def save_log(self):
        with open(self.filename, 'w') as f:
            json.dump(self.log_data, f, indent=4)

    def analyze_and_report(self):
        if not self.log_data:
            print("No hay datos para analizar.")
            return

        players = sorted(list(set([entry['player'] for entry in self.log_data])))
        
        print("\n" + "="*50)
        print("                 INFORME DE PARTIDA")
        print("="*50 + "\n")
        
        for player in players:
            player_data = [entry['game_data'] for entry in self.log_data if entry['player'] == player]
            
            dificultad_total = sum(d.get('dificultad_rival', 0) for d in player_data)
            satisfaccion_total = sum(d.get('satisfaccion', 0) for d in player_data)
            iq_mejora_total = sum(d.get('iq_mejora', 0) for d in player_data)
            
            num_entries = len(player_data)
            if num_entries > 0:
                promedio_dificultad = dificultad_total / num_entries
                promedio_satisfaccion = satisfaccion_total / num_entries
                promedio_iq_mejora = iq_mejora_total / num_entries
            else:
                promedio_dificultad = 0
                promedio_satisfaccion = 0
                promedio_iq_mejora = 0
            
            print(f"--- Análisis de la IA: {player.upper()} ---")
            print(f"  > Dificultad percibida: {promedio_dificultad:.2f} / 10")
            print(f"  > Nivel de Satisfacción: {promedio_satisfaccion:.2f} / 10")
            print(f"  > IQ de Mejora (progreso): {promedio_iq_mejora:.2f} / 10")
            print("-" * 50)