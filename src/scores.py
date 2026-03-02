import datetime
import os

class ScoreManager:
    def __init__(self, filename="achievements.txt"):
        self.filename = filename

    def save_result(self, hero_name, stage, result):
        # 1. Przygotowujemy nowy wpis
        now = datetime.datetime.now()
        date_string = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format: [DATA] Bohater: NAZWA | Wynik: STATUS | Stage: X
        new_entry = f"[{date_string}] Bohater: {hero_name.upper()} | Wynik: {result} | Stage: {stage}\n"
        
        # 2. Wczytujemy stare wyniki (jeśli plik istnieje)
        lines = []
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as file:
                    lines = file.readlines()
            except Exception as e:
                print(f"Błąd odczytu: {e}")

        # 3. Dodajemy nowy wynik do listy
        lines.append(new_entry)

        # 4. FUNKCJA POMOCNICZA DO SORTOWANIA
        # Ta funkcja wyciąga numer Stage z linijki tekstu, żeby Python wiedział jak sortować
        def get_stage_number(line):
            try:
                # Szukamy fragmentu "Stage: " i bierzemy to co jest po nim
                # Dzielimy linię na kawałki używając "Stage: " jako separatora
                parts = line.split("Stage: ")
                if len(parts) > 1:
                    # Bierzemy drugą część i czyścimy białe znaki (np. \n), zamieniamy na int
                    return int(parts[1].strip())
                return 0 # Jeśli linia jest uszkodzona, traktujemy jako stage 0
            except ValueError:
                return 0

        # 5. SORTOWANIE
        # key=get_stage_number -> sortuj według wyniku tej funkcji
        # reverse=True -> malejąco (najwyższy wynik na górze)
        lines.sort(key=get_stage_number, reverse=True)

        # 6. Zapisujemy posortowaną listę z powrotem do pliku (tryb 'w' - nadpisz wszystko)
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.writelines(lines)
            print(f"Wynik zapisany i posortowany! (Stage: {stage})")
        except Exception as e:
            print(f"Błąd podczas zapisu do pliku: {e}")