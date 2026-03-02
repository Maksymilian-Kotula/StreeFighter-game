import pygame
from settings import *
from src.fighters.player import Player
from src.fighters.enemy import Enemy
from src.logic import LevelManager
from src.ui import draw_health_bar
from src.game_handler import GameHandler
from src.menu import Menu
from src.background import Background
from src.scores import ScoreManager
from src.sound_handler import SoundHandler 

# Tworzę instancję menadżera wyników, aby móc zapisywać i odczytywać osiągnięcia
score_manager = ScoreManager()

# Inicjalizacja biblioteki Pygame (grafika) oraz modułu mixer (dźwięk)
pygame.init()
pygame.mixer.init()

# --- ŁADOWANIE CZCIONEK ---

try:
    count_font = pygame.font.Font("assets/fonts/japonia.otf", 80) # Duża czcionka do odliczania/napisów końcowych
    name_font = pygame.font.Font("assets/fonts/japonia.otf", 30)  # Mniejsza czcionka do imion postaci
except FileNotFoundError:
    print("Brak czcionki! Używam domyślnej.")
    count_font = pygame.font.SysFont("arial", 80, bold=True)
    name_font = pygame.font.SysFont("arial", 30, bold=True)

# Ustawienie okna gry o wymiarach zdefiniowanych w settings.py
screen = pygame.display.set_mode(SIZE_SCREEN)
pygame.display.set_caption("Street Fighter")
# Zegar do kontrolowania liczby klatek na sekundę (FPS)
clock = pygame.time.Clock()

# --- TWORZENIE GŁÓWNYCH OBIEKTÓW ---



sound_handler = SoundHandler() 
sound_handler.play_music('menu') # Od razu włączam muzykę pasującą do menu


# Tworzę "Sędziego" (GameHandler) i przypisuje sound_handlera, 
# aby sędzia mógł włączyć fanfary po wygranej lub smutną muzykę po przegranej.
game_handler = GameHandler(sound_handler) 

# Tworzę obiekt Menu, który zarządza wyborem trybu, mapy i postaci
menu = Menu()

# Deklaruję zmienne na postacie i tło jako None (puste). 
# Zostaną wypełnione dopiero, gdy gracz wybierze wszystko w menu.
player = None
enemy = None
background = None
level_manager = None

# --- GŁÓWNA PĘTLA GRY ---
running = True
while running:
    # Ustawiam stałą liczbę klatek na sekundę (settings)
    clock.tick(FPS)
    
    # --- 4. ZARZĄDZANIE MUZYKĄ ---
    # Sprawdzam stan menu, aby wiedzieć, jaki utwór grać w tle.
    # Jeśli jesteśmy w menu (dowolna podstrona: MODE, MAP, CHAR, SCORES)...
    if menu.menu_state != "GAME":
        sound_handler.play_music('menu')
    # Jeśli gra już wystartowała...
    else:
        sound_handler.play_music('fight')

    # --- OBSŁUGA ZDARZEŃ (KLIKNIĘCIA, KLAWISZE) ---
    for event in pygame.event.get():
        # Obsługa zamknięcia okna (krzyżyk)
        if event.type == pygame.QUIT:
            running = False
        
        # Jeśli jesteśmy w menu, przekazujemy zdarzenia (np. kliknięcia myszką) do obiektu Menu
        if menu.menu_state != "GAME":
            menu.handle_input(event)
        
        # Obsługa klawiszy funkcyjnych
        if event.type == pygame.KEYDOWN:
            # Klawisz ESCAPE służy do cofania się
            if event.key == pygame.K_ESCAPE:
                # Wyjście z tabeli wyników do wyboru trybu
                if menu.menu_state == "SCORES":
                    menu.menu_state = "MODE"
                # Wyjście z gry (walki) do menu głównego
                elif menu.menu_state == "GAME":
                    menu.menu_state = "MODE"
                    # Czyścimy wszystkie obiekty gry, aby przy nowym starcie stworzyć je na świeżo
                    menu.p1_fighter = None
                    menu.p2_fighter = None
                    player = None
                    enemy = None
                    background = None 
                    level_manager = None 
                    # Resetujemy sędziego (tworzymy nowego i dajemy mu sound_handlera)
                    game_handler = GameHandler(sound_handler) 
                    # Zatrzymujemy muzykę walki i wracamy do muzyki menu
                    sound_handler.play_music('menu')
                # Jeśli jesteśmy w głównym menu, ESC wyłącza grę
                else:
                    running = False

    # ==========================================
    # --- INICJALIZACJA ROZGRYWKI (SETUP) ---
    # ==========================================
    # Ten blok wykonuje się TYLKO RAZ w momencie przejścia z menu do gry (gdy player jest jeszcze None)
    if menu.menu_state == "GAME" and player is None:
        # Pobieram skalę (wielkość) wybranych postaci ze słownika
        p1_scale = FIGHTER_SCALES.get(menu.p1_fighter, 1.0)
        p2_scale = FIGHTER_SCALES.get(menu.p2_fighter, 1.0)
        
        #  TWORZENIE GRACZA Z DŹWIĘKIEM 
        # Tworzę obiekt gracza, przekazując mu pozycję, nazwę, HP, skalę i sound_handler (do efektów ciosów)
        player = Player(200, 310, menu.p1_fighter, 100, p1_scale, sound_handler)
        
        # Sprawdzam tryb gry wybrany w menu
        if menu.game_mode == "PvE":
            # Tryb Kampanii: Przeciwnikiem jest Bot (klasa Enemy)
            
            enemy = Enemy(700, 310, menu.p2_fighter, 100, p2_scale, sound_handler)
            
            # Tworzę LevelManagera do zarządzania poziomami trudności
            # Przekazuję sound_handler, aby LevelManager mógł zagrać fanfary po przejściu poziomu
            level_manager = LevelManager(player, enemy, sound_handler)
        else:
            # Tryb PvP: Przeciwnikiem jest drugi Gracz (klasa Player z ID=2)
            # ID=2 zmienia sterowanie na strzałki
            enemy = Player(700, 310, menu.p2_fighter, 100, p2_scale, sound_handler, player_id=2)
            enemy.flip = True # Drugi gracz patrzy w lewo
            level_manager = None # W PvP nie ma poziomów
            
        # Tworzę tło na podstawie wybranej mapy
        background = Background(menu.selected_map)

    # ==========================================
    #            RYSOWANIE I LOGIKA
    # ==========================================
    
    #  Jesteśmy w menu
    if menu.menu_state != "GAME":
        if menu.menu_state == "SCORES":
            menu.draw_scores(screen) # Rysuję tabelę wyników
        else:
            menu.draw(screen) # Rysuję przyciski menu

    #  Jesteśmy w trakcie gry
    else:
        # Upewniam się, że postacie istnieją 
        if player is not None and enemy is not None:

            # 1. RYSOWANIE TŁA
            if background:
                background.update() # Animacja tła (jeśli jest)
                background.draw(screen)
            else:
                screen.fill(BG_COLOR)

            # 2. LOGIKA SĘDZIEGO (GameHandler)
            # Ustalam obecny numer poziomu (dla PvE) lub 1 (dla PvP)
            current_level = 1
            if level_manager:
                current_level = level_manager.bot_level

            # Sędzia sprawdza, czy ktoś umarł, liczy czas i zarządza końcem rundy
            game_handler.update(player, enemy, menu.game_mode, current_level)

            # 3. RUCH I WALKA
            # Postacie mogą się ruszać i atakować tylko, jeśli runda trwa (nie ma Game Over)
            if not game_handler.round_over:
                player.move(SCREEN_WIDTH, enemy) # Ruch gracza (klawisze)
                enemy.move(SCREEN_WIDTH, player) # Ruch wroga (AI lub klawisze)
                
                # Sprawdzam, czy nie ma pauzy między poziomami w PvE
                if not level_manager or not level_manager.waiting_for_next_level:
                    # Wywołuję metody ataku.
                    # WAŻNE: Dźwięk uderzenia odtwarza się wewnątrz metody attack() w klasie Fighter
                    player.attack(enemy)
                    enemy.attack(player)

            # W trybie PvE sprawdzam, czy należy awansować bota na wyższy poziom
            if menu.game_mode == "PvE" and level_manager:
                level_manager.check_level_up(game_handler)

            # 4. RYSOWANIE POSTACI
            player.draw(screen)
            enemy.draw(screen)
            
            # 5. RYSOWANIE UI (Paski życia)
            draw_health_bar(screen, player.health, player.max_health, 20, 50, f"{menu.p1_fighter.upper()}", name_font)
            draw_health_bar(screen, enemy.health, enemy.max_health, 655, 50, f"{menu.p2_fighter.upper()}", name_font, is_enemy=True)

            # Dodatkowe napisy w trybie PvE (numer poziomu, komunikat o wygranej rundzie)
            if menu.game_mode == "PvE" and level_manager:
                from src.ui import draw_stage_info
                draw_stage_info(screen, level_manager.bot_level, name_font)
                level_manager.draw_victory_msg(screen, count_font)

            # 6. EKRAN KOŃCOWY (GAME OVER / VICTORY)
            # Rysuję go, jeśli sędzia zarządził koniec rundy
            if level_manager:
                # W PvE nie rysuję "Game Over", jeśli po prostu przechodzę do następnego poziomu
                if not level_manager.waiting_for_next_level:
                    game_handler.draw_game_over(screen, player, count_font)
            else:
                # W PvP zawsze rysuję ekran końcowy po śmierci kogoś
                game_handler.draw_game_over(screen, player, count_font)

    # Odświeżenie ekranu (wyświetlenie nowej klatki)
    pygame.display.flip()


pygame.quit()