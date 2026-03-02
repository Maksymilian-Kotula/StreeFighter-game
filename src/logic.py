import pygame


# Przechodzenie między poziomami, wzmacnianie bota i resetowanie rundy.
class LevelManager:
    def __init__(self, player, enemy, sound_handler):
        # Zapamiętuję referencje do gracza i przeciwnika, żeby móc zmieniać ich życie i pozycję
        self.player = player
        self.enemy = enemy
        
        # Ustawiam startowy poziom trudności na 1
        self.bot_level = 1
        # Ustalam maksymalny poziom, po którym gra się kończy definitywnie
        self.max_level = 4
        
        # Zmienna do odliczania czasu przerwy między rundami
        self.level_up_timer = 0  
        # Zapamiętuję obiekt dźwiękowy, żeby móc zagrać fanfary po wygranej rundzie
        self.sound_handler = sound_handler  
        # Flaga: czy aktualnie trwa przerwa i czekam na załadowanie kolejnego poziomu?
        self.waiting_for_next_level = False


    # Główna metoda sprawdzająca, czy należy awansować do następnego poziomu
    def check_level_up(self, game_handler):
        # Pobieram aktualny czas gry w milisekundach
        current_time = pygame.time.get_ticks()

        # 1. SPRAWDZAM MOMENT ŚMIERCI BOTA
        # Warunek: Bot nie ma życia ORAZ nie czekam już na poziom ORAZ nie jest to ostatni level
        if self.enemy.health <= 0 and not self.waiting_for_next_level and self.bot_level < self.max_level:
            # Ustawiam flagę oczekiwania na True - zaczynamy przerwę między rundami
            self.waiting_for_next_level = True
            # Zapamiętuję czas rozpoczęcia tej przerwy
            self.level_up_timer = current_time
            
            # Odtwarzam dźwięk zwycięstwa (fanfary)
            self.sound_handler.play_sfx('win')
            
            # Resetuję licznik "Game Over" u głównego sędziego (GameHandler).
            # Dzięki temu sędzia nie wyświetli napisu "VICTORY" i nie zakończy całej gry,
            # bo LevelManager przejmuje teraz kontrolę.
            game_handler.round_over_time = 0 
            return False

        # 2. OBSŁUGA CZASU OCZEKIWANIA (PAUZA Z NAPISEM)
        # Jeśli flaga oczekiwania jest włączona
        if self.waiting_for_next_level:
            # Cały czas blokuję sędziego, żeby nie zakończył gry w tle
            game_handler.round_over = False
            game_handler.round_over_time = 0
            
            # Sprawdzam, czy minęły już 2 sekundy (2000 ms) od pokonania bota
            if current_time - self.level_up_timer > 2000:
                # Zwiększam poziom trudności o 1
                self.bot_level += 1
                # Wywołuję funkcję wzmacniającą bota (więcej HP, siły)
                self.apply_buffs()
                # Resetuję pozycje postaci do startowych
                self.reset_positions(game_handler)
                # Wyłączam flagę oczekiwania - wracamy do gry
                self.waiting_for_next_level = False
                return True 
        return False

    # Metoda przywracająca postacie do stanu początkowego przed nową rundą
    def reset_positions(self, game_handler):
       
        # Upewniam się, że główny sędzia myśli, że gra trwa dalej
        game_handler.round_over = False
        game_handler.round_over_time = 0 
        
        # Ustawiam gracza po lewej stronie ekranu
        self.player.rect.centerx = 200
        # Ustawiam wroga po prawej stronie ekranu
        self.enemy.rect.centerx = 700
        
        # Ożywiam obie postacie (flaga alive na True)
        self.player.alive = True
        self.enemy.alive = True
        
        # Leczę obie postacie do pełna (do nowej wartości max_health)
        self.player.health = self.player.max_health
        self.enemy.health = self.enemy.max_health
        
        # Resetuję flagi trafienia (żeby nikt nie otrzymał obrażeń na start)
        self.player.attack_landed = False
        self.enemy.attack_landed = False
        
        # Ustawiam animację na stanie w miejscu (Idle)
        self.player.update_action(0) 
        self.enemy.update_action(0)

    # Metoda zwiększająca trudność (Buffowanie bota)
    def apply_buffs(self):
        # Zwiększam maksymalne życie bota o 40 punktów
        self.enemy.max_health += 40
        # Odnawiam jego życie do nowej wartości maksymalnej
        self.enemy.health = self.enemy.max_health
       
        self.player.health = self.player.max_health
        
        # Sprawdzam, czy bot ma atrybut 'attack_damage' 
        if hasattr(self.enemy, 'attack_damage'):
            # Zwiększam siłę ataku bota o 5 punktów
            self.enemy.attack_damage += 5

   
    # Metoda rysująca napis informacyjny podczas przerwy między poziomami
    def draw_victory_msg(self, surface, font):
        # Rysuję napisy tylko wtedy, gdy czekamy na następny poziom
        if self.waiting_for_next_level:
            # Tworzę napis "Gratulacje [Poziom] WIN" w kolorze złotym
            text = font.render(f"Gratulacje {self.bot_level} WIN", True, (255, 215, 0))
            # Ustawiam napis na środku ekranu, nieco wyżej
            text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
            
            # Tworzę napis "Kolejna runda [Następny poziom]" w kolorze białym
            next_text = font.render(f"Kolejna runda {self.bot_level + 1}", True, (255, 255, 255))
            # Ustawiam ten napis na środku, nieco niżej
            next_rect = next_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
            
            # Wyświetlam (blituję) oba napisy na ekranie
            surface.blit(text, text_rect)
            surface.blit(next_text, next_rect)