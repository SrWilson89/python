import json

class ExperienceLogger:
    def __init__(self, filename="game_log.json"):
        self.filename = filename
        self.log_data = []

    def log(self, ia_name, experience_data):
        self.log_data.append({"ia_name": ia_name, **experience_data})

    def save_log(self):
        with open(self.filename, 'w') as f:
            json.dump(self.log_data, f, indent=4)

    def analyze_and_report(self):
        ia_reports = {}
        for entry in self.log_data:
            ia_name = entry['ia_name']
            if ia_name not in ia_reports:
                ia_reports[ia_name] = {
                    "difficulty": [],
                    "satisfaction": [],
                    "frustration": [],
                    "iq_inicial": entry['iq_inicial'],
                    "iq_final": entry['iq_final'],
                }
            ia_reports[ia_name]["difficulty"].append(entry['dificultad_rival'])
            ia_reports[ia_name]["satisfaction"].append(entry['satisfaccion'])
            ia_reports[ia_name]["frustration"].append(entry['frustracion'])
            ia_reports[ia_name]["iq_final"] = entry['iq_final']

        print("\n" + "="*50)
        print(" " * 10 + "INFORME DE PARTIDA")
        print("="*50 + "\n")
        
        for ia_name, data in ia_reports.items():
            avg_difficulty = sum(data['difficulty']) / len(data['difficulty'])
            avg_satisfaction = sum(data['satisfaction']) / len(data['satisfaction'])
            avg_frustration = sum(data['frustration']) / len(data['frustration'])

            print(f"--- Análisis de la IA: {ia_name.upper()} ---")
            print(f"  > Dificultad percibida: {avg_difficulty:.2f} / 10")
            print(f"  > Nivel de Satisfacción: {avg_satisfaction:.2f} / 10")
            print(f"  > Nivel de Frustración: {avg_frustration:.2f} / 10")
            print(f"  > IQ Inicial: {data['iq_inicial']:.2f}")
            print(f"  > IQ Final: {data['iq_final']:.2f}")
            print("--------------------------------------------------")