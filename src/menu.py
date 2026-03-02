import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, YELLOW, WHITE, RED, BLACK, GREEN, BLUE


class Menu:
    def __init__(self):
        # 1. LISTA POSTACI 
        # Definiuję nazwy folderów, z których będę pobierać grafiki wojowników.
        self.fighters_list = ["warrior", "warrior1", "warrior2"] 
        
        # 2. LISTA MAP
        # Tworzę listę słowników. Każda mapa ma swoją "ładną nazwę" do wyświetlenia
        # oraz nazwę folderu, gdzie leżą jej pliki graficzne.
        self.maps_data = [
            {"name": "MAPA 1", "folder": "1"},
            {"name": "MAPA 2", "folder": "2"},
            {"name": "MAPA 3", "folder": "3"}
        ]
        
        # --- ŁADOWANIE CZCIONEK ---
        
        try:
            self.title_font = pygame.font.Font("assets/fonts/japonia.otf", 60)
            self.button_font = pygame.font.Font("assets/fonts/japonia.otf", 30)
        except FileNotFoundError:
            # Jeśli nie znajdę pliku, używam domyślnej czcionki systemowej 
            self.title_font = pygame.font.SysFont("arial", 60, bold=True)
            self.button_font = pygame.font.SysFont("arial", 30, bold=True)

        # --- ZMIENNE STANU MENU ---
        # Tutaj będę przechowywał decyzje gracza. Na początku są puste
        self.game_mode = None    # Czy PvE czy PvP?
        self.selected_map = None # Którą mapę wybrano?
        self.p1_fighter = None   # Kim gra Gracz 1?
        self.p2_fighter = None   # Kim gra Gracz 2 lub bot
        
        # Ta zmienna steruje tym, który ekran widzi gracz. Zaczynamy od wyboru trybu ("MODE").
        self.menu_state = "MODE" 

        # --- PRZYGOTOWANIE GRAFIK ---
        self.char_icons = {} # Pusty słownik, do którego załaduję ikonki twarzy postaci
        self.map_icons = {}  # Pusty słownik na miniaturki map
        
        # Wywołuję funkcję pomocniczą, która wczyta wszystkie obrazki raz na start,
        # żeby menu chodziło płynnie.
        self.load_previews()

        # --- TŁO MENU ---
        try:
            # Próbuję wczytać dedykowany obrazek tła menu
            self.menu_bg = pygame.image.load("assets/images/menu_bg.png").convert()
            # Skaluję go, żeby idealnie pasował do rozdzielczości ekranu
            self.menu_bg = pygame.transform.scale(self.menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            print("Nie znaleziono menu_bg.png. Używam tła zastępczego.")
            # Jeśli brak pliku, ustawiam None. Później narysuję szary ekran lub wezmę tło mapy.
            self.menu_bg = None
            # Awaryjnie: próbuję wziąć tło pierwszej mapy, jeśli udało się ją załadować
            if "1" in self.map_icons and self.map_icons["1"]:
                 self.menu_bg = pygame.transform.scale(self.map_icons["1"], (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- WARSTWA PRZYCIEMNIAJĄCA ---
        # Tworzę czarną powierzchnię o wielkości ekranu.
        # Użyję jej, żeby przyciemnić tło, dzięki czemu napisy będą lepiej widoczne.
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0)) # Czarny kolor
        self.overlay.set_alpha(120)  # Półprzezroczystość (0-255)

    # Funkcja ładująca małe obrazki  do wyboru w menu
    def load_previews(self):
        print("Ładowanie podglądów do menu...")

        # 1. ŁADOWANIE IKON POSTACI
        # Przechodzę pętlą przez nazwę każdej postaci 
        for fighter_name in self.fighters_list:
            # Szukamy pierwszego obrazka z animacji stania (Idle), żeby zrobić z niego ikonkę
            path = f"assets/images/{fighter_name}/Idle/1.png"
            
            try:
                if os.path.exists(path):
                    # Wczytuję obrazek z zachowaniem przezroczystości
                    img = pygame.image.load(path).convert_alpha()
                    
                    # Obliczam skalę, żeby obrazek miał zawsze 80 pikseli wysokości,
                    # ale zachował swoje oryginalne proporcje (żeby nie był rozciągnięty).
                    scale = 80 / img.get_height()
                    new_width = int(img.get_width() * scale)
                    
                    # Skaluję i zapisuję w słowniku pod nazwą postaci
                    img = pygame.transform.scale(img, (new_width, 80))
                    self.char_icons[fighter_name] = img
                else:
                    print(f"Brak ikonki dla {fighter_name} (szukano: {path})")
                    self.char_icons[fighter_name] = None
            except Exception as e:
                print(f"Błąd ikony {fighter_name}: {e}")
                self.char_icons[fighter_name] = None

        # 2. ŁADOWANIE MINIATUREK MAP
        # Iteruję po mojej liście map
        for i, map_info in enumerate(self.maps_data):
            folder = map_info["folder"]
            # Ścieżka do folderu z tłami danej mapy
            path_folder = f"assets/images/backgrounds/{folder}"
            icon = None
            
            # Sprawdzam, czy folder istnieje
            if os.path.exists(path_folder):
                # Pobieram listę plików i sortuję ją
                files = sorted(os.listdir(path_folder))
                # Szukam pierwszego pliku, który jest obrazkiem (png lub jpg)
                valid_files = [f for f in files if f.endswith(".png") or f.endswith(".jpg")]
                
                if len(valid_files) > 0:
                    img_path = f"{path_folder}/{valid_files[0]}"
                    try:
                        img = pygame.image.load(img_path).convert()
                        # Skaluję tło do rozmiaru małej miniaturki (200x150)
                        img = pygame.transform.scale(img, (200, 150))
                        icon = img
                    except:
                        pass
            
            # Zapisuję miniaturkę w słowniku
            self.map_icons[folder] = icon

    
    def draw(self, screen):
        
        screen.fill((30, 30, 30)) 
        
        # RYSOWANIE TŁA I PRZYCIEMNIENIA
        if self.menu_bg:
            screen.blit(self.menu_bg, (0, 0))
            screen.blit(self.overlay, (0, 0)) # Nakładam czarną mgiełkę
        else:
            screen.fill((30, 30, 30)) # Jeśli brak tapety, zostaje szary

        
        # Sprawdzam, w jakim etapie menu jesteśmy i wywołuję odpowiednią funkcję rysującą.
        if self.menu_state == "MODE":
            self.draw_mode_select(screen) # Wybór trybu (PvE / PvP / Wyniki)
        elif self.menu_state == "MAP":
            self.draw_map_select(screen)  # Wybór mapy
        elif self.menu_state == "CHAR":
            self.draw_char_select(screen) # Wybór postaci
        elif self.menu_state == "SCORES":
            self.draw_scores(screen)      # Tabela wyników
    
    # Funkcja rysująca tabelę wyników 
    def draw_scores(self, screen):
        # Rysuję ciemniejsze tło, żeby tabela była czytelna
        if self.menu_bg:
            darker_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            darker_overlay.fill((0, 0, 0))
            darker_overlay.set_alpha(200) # Mocniejsze przyciemnienie
            screen.blit(darker_overlay, (0, 0))
        else:
            screen.fill((50, 50, 50))
        
        # Rysuję tytuł na górze
        self.draw_text(screen, "HALL OF FAME", 60, YELLOW, font=self.title_font)
        
        # Przygotowuję mniejszą czcionkę do listy wyników
        list_font = pygame.font.SysFont("arial", 22, bold=True)
        
        try:
            # Próbuję otworzyć plik z wynikami
            if os.path.exists("achievements.txt"):
                with open("achievements.txt", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    
                    # Biorę 10 pierwszych linii 
                    top_results = lines[:10]
                    
                    y_offset = 140
                    
                    
                    for i, line in enumerate(top_results): 
                        line = line.strip() # Usuwam białe znaki (np. enter)
                        if not line: continue

                        # Definiuję prostokąt dla pojedynczego wyniku
                        row_rect = pygame.Rect(50, y_offset - 5, SCREEN_WIDTH - 100, 35)
                        
                        # --- LOGIKA KOLORÓW PASKÓW ---
                        if i == 0:
                            # Pierwsze miejsce ma złote tło!
                            pygame.draw.rect(screen, (60, 50, 0), row_rect) 
                            border_col = YELLOW
                        else:
                            # Reszta ma standardowe ciemne tło
                            pygame.draw.rect(screen, (40, 40, 40), row_rect)
                            border_col = (80, 80, 80)
                            
                        # Rysuję obramowanie paska
                        pygame.draw.rect(screen, border_col, row_rect, 1) 
                        
                        # Przygotowuję tekst z numeracją 
                        full_text = f"{i+1}. {line}"
                        
                        # --- LOGIKA KOLORÓW TEKSTU ---
                        text_color = WHITE
                        # Jeśli w linii jest słowo "WYGRANA", koloruję na zielono
                        if "WYGRANA" in line: text_color = (100, 255, 100)
                        # Jeśli "PRZEGRANA", na czerwono
                        elif "PRZEGRANA" in line: text_color = (255, 100, 100)

                        # Renderuję tekst i wyświetlam go na pasku
                        txt_surf = list_font.render(full_text, True, text_color)
                        screen.blit(txt_surf, (row_rect.x + 10, row_rect.y + 5))
                        
                        # Przesuwam się w dół dla następnego wyniku
                        y_offset += 40
            else:
                self.draw_text(screen, "BRAK ZAPISANYCH WYNIKOW", 300, WHITE)
        except Exception as e:
            self.draw_text(screen, f"BLAD ODCZYTU: {e}", 300, RED)

        # Na dole rysuję instrukcję powrotu
        back_font = pygame.font.SysFont("arial", 18, italic=True)
        back_surf = back_font.render("Nacisnij ESC, aby wrocic do menu", True, (200, 200, 200))
        screen.blit(back_surf, (SCREEN_WIDTH // 2 - back_surf.get_width() // 2, 560))
        
    # Funkcja rysująca ekran wyboru trybu gry 
    def draw_mode_select(self, screen):
        self.draw_text(screen, "WYBIERZ TRYB", 100, YELLOW, font=self.title_font)
        
        self.draw_button(screen, "1. GRACZ   VS   KOMPUTER", 250)
        self.draw_button(screen, "2. GRACZ   VS  GRACZ", 350)
        self.draw_button(screen, "3. Tabela", 450) 

    # Funkcja rysująca ekran wyboru mapy
    def draw_map_select(self, screen):
        self.draw_text(screen, "WYBIERZ MAPE", 50, YELLOW, font=self.title_font)
        
        # Ustalam pozycje trzech kwadratów z mapami
        positions = [(150, 200), (400, 200), (650, 200)]
        
        # Iteruję po dostępnych mapach
        for i, map_info in enumerate(self.maps_data):
            folder = map_info["folder"]
            name = map_info["name"]
            x, y = positions[i]
            
            rect = pygame.Rect(x, y, 200, 150)
            
            # Jeśli mam załadowaną miniaturkę, wyświetlam ją
            if self.map_icons.get(folder):
                screen.blit(self.map_icons[folder], (x, y))
                pygame.draw.rect(screen, WHITE, rect, 2) # Biała ramka
            else:
                # Jeśli brak obrazka, rysuję kolorowy prostokąt zastępczy
                color = (50, 50, 50)
                if folder == "1": color = (34, 139, 34)
                if folder == "2": color = (100, 0, 0)
                if folder == "3": color = (0, 0, 100)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)

            # Sprawdzam, czy myszka najechała na mapę 
            mx, my = pygame.mouse.get_pos()
            if rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, YELLOW, rect, 4) # Gruba żółta ramka

            # Wyświetlam nazwę mapy pod obrazkiem
            self.draw_text(screen, name, y + 180, WHITE, x_offset=(x - SCREEN_WIDTH/2 + 100))

    # Funkcja rysująca ekran wyboru postaci
    def draw_char_select(self, screen):
        # Ustalam nagłówek w zależności od tego, kto teraz wybiera
        if self.p1_fighter is None:
            title = "GRACZ 1:  Wybierz "
            color = GREEN
        else:
            if self.game_mode == "PvE":
                title = "KOMPUTER:  Wybierz "
                color = RED
            else:
                title = "GRACZ 2:  Wybierz "
                color = BLUE

        self.draw_text(screen, title, 50, color, font=self.title_font)

        y_pos = 150
        mx, my = pygame.mouse.get_pos()
        
        # Tworzę przyciski dla każdej dostępnej postaci
        for fighter in self.fighters_list:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y_pos, 400, 100) 
            
            # Efekt najechania myszką (Highlight)
            if rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, (70, 70, 70), rect) # Jaśniejszy szary
                border_color = YELLOW
            else:
                pygame.draw.rect(screen, (40, 40, 40), rect) # Ciemny szary
                border_color = WHITE
            
            pygame.draw.rect(screen, border_color, rect, 2)
            
            # Rysuję ikonkę postaci wewnątrz przycisku
            icon = self.char_icons.get(fighter)
            if icon:
                icon_rect = icon.get_rect(midleft=(rect.left + 20, rect.centery))
                screen.blit(icon, icon_rect)
            else:
                pass # Brak ikony - nic nie rysuję

            # Rysuję nazwę postaci
            text_surf = self.button_font.render(fighter.upper(), True, border_color)
            text_rect = text_surf.get_rect(midleft=(rect.left + 150, rect.centery))
            screen.blit(text_surf, text_rect)
            
            y_pos += 120

    # Funkcja obsługująca interakcję użytkownika (kliknięcia myszką)
    def handle_input(self, event):
        mx, my = pygame.mouse.get_pos()

        # Sprawdzam, czy wciśnięto lewy przycisk myszy
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                # --- ETAP 1: WYBÓR TRYBU ---
                if self.menu_state == "MODE":
                    # Sprawdzam strefy kliknięcia  dla przycisków
                    if 230 < my < 270: # Wybrano PvE
                        self.game_mode = "PvE"
                        self.menu_state = "MAP" # Przechodzę do wyboru mapy
                    elif 330 < my < 370: # Wybrano PvP
                        self.game_mode = "PvP"
                        self.menu_state = "MAP"
                    elif 430 < my < 470: # Wybrano Tabelę wyników
                        self.menu_state = "SCORES"

                # --- ETAP 2: WYBÓR MAPY ---
                elif self.menu_state == "MAP":
                    positions = [(150, 200), (400, 200), (650, 200)]
                    # Sprawdzam każdy z 3 prostokątów map
                    for i, map_info in enumerate(self.maps_data):
                        x, y = positions[i]
                        rect = pygame.Rect(x, y, 200, 150)
                        
                        if rect.collidepoint((mx, my)):
                            self.selected_map = map_info["folder"] 
                            self.menu_state = "CHAR" # Przechodzę do wyboru postaci

                # --- ETAP 3: WYBÓR POSTACI ---
                elif self.menu_state == "CHAR":
                    y_pos = 150
                    for fighter in self.fighters_list:
                        rect = pygame.Rect(SCREEN_WIDTH//2 - 200, y_pos, 400, 100)
                        
                        if rect.collidepoint((mx, my)):
                            # Jeśli Gracz 1 jeszcze nie wybrał -> zapisuję dla niego
                            if self.p1_fighter is None:
                                self.p1_fighter = fighter
                                pygame.time.delay(200) # Mała pauza, żeby nie kliknąć 2 razy
                            else:
                                # Jeśli Gracz 1 już ma postać -> zapisuję dla Gracza 2 / Bota
                                self.p2_fighter = fighter
                                self.menu_state = "GAME" # Wszystko wybrane
                        y_pos += 120

    # Funkcja pomocnicza do szybkiego rysowania wyśrodkowanego tekstu
    def draw_text(self, screen, text, y, color, font=None, x_offset=0):
        if font is None: font = self.button_font
        img = font.render(text, True, color)
        rect = img.get_rect(center=(SCREEN_WIDTH/2 + x_offset, y))
        screen.blit(img, rect)

    # Funkcja pomocnicza do rysowania przycisku z efektem podświetlenia
    def draw_button(self, screen, text, y):
        mx, my = pygame.mouse.get_pos()
        img = self.button_font.render(text, True, WHITE) # Domyślnie biały
        rect = img.get_rect(center=(SCREEN_WIDTH/2, y))
        
        # Jeśli myszka jest nad napisem -> zmień kolor na żółty
        if rect.collidepoint((mx, my)):
            img = self.button_font.render(text, True, YELLOW)
        
        screen.blit(img, rect)