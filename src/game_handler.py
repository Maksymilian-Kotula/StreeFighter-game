import pygame
from settings import SIZE_SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, RED, YELLOW, WHITE, BLACK
from src.scores import ScoreManager


class GameHandler:
    def __init__(self, sound_handler):
        # Flaga: czy runda się zakończyła (i wyświetlamy napis "GAME OVER" lub "VICTORY")
        self.round_over = False
        # Czas, w którym nastąpił koniec walki (do odliczania opóźnienia)
        self.round_over_time = 0
        
        # Zapamiętuję obiekt do obsługi dźwięków, żeby sędzia mógł włączyć fanfary lub smutną muzykę
        self.sound_handler = sound_handler 
        
        # Flaga: czy wynik został już zapisany do pliku (żeby nie zapisywać go 60 razy na sekundę)
        self.logged = False 
        # Tworzę instancję ScoreManager, która zajmie się obsługą pliku z wynikami
        self.score_manager = ScoreManager() 

        # --- PRZYGOTOWANIE "MGŁY" (TŁA EKRANU KOŃCOWEGO) ---
        # Tworzę czarną powierzchnię o wielkości całego ekranu
        self.overlay = pygame.Surface(SIZE_SCREEN)
        self.overlay.fill(BLACK)
        # Ustawiam przezroczystość (alpha) na 150 (zakres 0-255).
        # Dzięki temu tło będzie przyciemnione, ale wciąż będzie widać postacie pod spodem.
        self.overlay.set_alpha(150)

    # Funkcja wywoływana w pętli głównej gry.
    # Sprawdza, czy ktoś umarł, zarządza dźwiękiem i czasem po walce.
    def update(self, player, enemy, game_mode="PvP", current_stage=1):
        # jeśli postacie jeszcze nie istnieją, nic nie rób
        if player is None or enemy is None:
            return

        # ====================================================
        # 1. SPRAWDZAM, CZY GRACZ UMARŁ (PORAŻKA)
        # ====================================================
        # Jeśli życie gracza spadło do zera (lub mniej) I gracz jest wciąż oznaczony jako żywy
        if player.health <= 0 and player.alive:
            player.health = 0   # Ustawiam życie na 0 
            player.alive = False # Oznaczam gracza jako martwego
            
            # --- OBSŁUGA DŹWIĘKU PORAŻKI ---
            self.sound_handler.stop_music()     # Wyłączam muzykę walki
            self.sound_handler.play_sfx('lose') # Odtwarzam dźwięk przegranej
            # -------------------------------
            
            # Jeśli zegar końca rundy jeszcze nie ruszył -> uruchamiam go teraz
            if self.round_over_time == 0:
                self.round_over_time = pygame.time.get_ticks()
        
        # ====================================================
        # 2. SPRAWDZAM, CZY WRÓG UMARŁ (ZWYCIĘSTWO)
        # ====================================================
        elif enemy.health <= 0 and enemy.alive:
            enemy.health = 0
            enemy.alive = False

            # --- OBSŁUGA DŹWIĘKU ZWYCIĘSTWA ---
            # W trybie PvE dźwięk wygranej obsługuje LevelManager (bo tam jest przejście do nast. poziomu).
            # Tutaj obsługuję tylko tryb PvP (Gracz vs Gracz).
            if game_mode == "PvP":
                self.sound_handler.stop_music()
                self.sound_handler.play_sfx('win')
            # ----------------------------------

            # Uruchamiam zegar odliczający czas do pokazania napisu końcowego
            if self.round_over_time == 0:
                self.round_over_time = pygame.time.get_ticks()

        # ====================================================
        # 3. ODLICZANIE CZASU I ZAPIS WYNIKÓW
        # ====================================================
        # Jeśli walka się skończyła (czas jest większy od 0)
        if self.round_over_time > 0:
            # Czekam 1 sekundę (1000 ms) od momentu śmierci, zanim wyświetlę napis "GAME OVER".
            if pygame.time.get_ticks() - self.round_over_time > 1000:
                self.round_over = True # Oficjalnie kończę rundę 
                
                # Zapis do pliku tekstowego
                # Zapisujemy tylko w trybie PvE (z komputerem) 
                if game_mode == "PvE" and not self.logged:
                    # Ustalam status: jeśli gracz żyje, to WYGRANA, jeśli nie - PRZEGRANA
                    status = "WYGRANA" if player.health > 0 else "PRZEGRANA"
                    # Przekazuję dane do ScoreManagera, żeby zapisał je w pliku
                    self.score_manager.save_result(player.name, current_stage, status)
                    # Ustawiam flagę logged na True, żeby nie zapisać tego samego wyniku 100 razy
                    self.logged = True
                    
    # Funkcja rysująca ekran końcowy (napisy i tło)
    def draw_game_over(self, screen, player, font_big):
        # Rysuję tylko wtedy, gdy minęła już 1 sekunda opóźnienia (round_over == True)
        if self.round_over:
            # Rysuję półprzezroczystą mgłę na całym ekranie
            screen.blit(self.overlay, (0, 0))
            
            # Wybieram tekst i kolor w zależności od wyniku
            if player.health <= 0:
                text = "GAME OVER"
                color = RED
            else:
                text = "VICTORY!"
                color = YELLOW
            
            # Renderuję (zamieniam na obrazek) tekst
            draw_text = font_big.render(text, True, color)
            # Pobieram prostokąt tekstu i ustawiam go idealnie na środku ekranu
            text_rect = draw_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            # Wyświetlam tekst na ekranie
            screen.blit(draw_text, text_rect)