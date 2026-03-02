import pygame
from src.fighters.base import Fighter
from settings import SPEED, GRAVITY, JUMP_FORCE, FLOOR_Y, ATTACK_COOLDOWN


class Player(Fighter):
    
    
    def __init__(self, x, y, name, max_hp, image_scale, sound_handler, player_id=1):
        super().__init__(x, y, name, max_hp, image_scale, sound_handler)
        
        # Specyficzne zmienne dla gracza:
        self.jump = False           # Czy postać jest w trakcie skoku
        self.attack_locked = False  # Blokada ataku (żeby nie można było trzymać klawisza i spamować)
        self.player_id = player_id  # ID gracza (1 lub 2) do rozróżniania sterowania

    # Główna metoda ruchu i sterowania
    def move(self, screen_width, target):
        dx = 0 # Zmiana pozycji w poziomie (Delta X)
        dy = 0 # Zmiana pozycji w pionie (Delta Y)
        self.attack_type = 0 # Reset typu ataku w nowej klatce
        
        current_time = pygame.time.get_ticks() # Pobieram aktualny czas gry
        key = pygame.key.get_pressed()         # Pobieram stan wszystkich klawiszy

        # Logika ruchu działa tylko, jeśli postać nie atakuje (jest zablokowana animacją)
        # ORAZ jeśli postać nie obrywa (nie jest w animacji "Hit")
        if self.attacking == False and self.hit == False:
            
            # --- PRZYPISANIE KLAWISZY ZALEŻNIE OD ID ---
            # Sprawdzam, czy jestem Graczem 1 czy Graczem 2, żeby przypisać odpowiednie klawisze
            if self.player_id == 1:
                # Gracz 1: Sterowanie WASD + ataki R/T
                left_key, right_key, jump_key = pygame.K_a, pygame.K_d, pygame.K_w
                at1_key, at2_key = pygame.K_r, pygame.K_t
            else:
                # Gracz 2: Sterowanie Strzałkami + ataki O/P
                left_key, right_key, jump_key = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP
                at1_key, at2_key = pygame.K_o, pygame.K_p

            # --- RUCH (Obsługa wciśniętych klawiszy) ---
            # Jeśli wciśnięto LEWO -> przesuwam dx na minus, ustawiam flip na True (obrót w lewo)
            if key[left_key]:
                dx = -SPEED
                self.flip = True
            # Jeśli wciśnięto PRAWO -> przesuwam dx na plus, ustawiam flip na False (obrót w prawo)
            if key[right_key]:
                dx = SPEED
                self.flip = False
            # Skok: tylko jeśli wciśnięto przycisk skoku I postać nie jest już w powietrzu
            if key[jump_key] and self.jump == False:
                self.vel_y = -JUMP_FORCE # Nadaję prędkość w górę (ujemną)
                self.jump = True

            # --- ATAK ---
            # Sprawdzam, czy wciśnięto któryś z klawiszy ataku
            if key[at1_key] or key[at2_key]:
                # Warunki ataku: 
                # 1. Minął czas cooldownu (żeby nie bić za szybko)
                # 2. Klawisz nie był trzymany ciągle (attack_locked)
                if current_time - self.last_attack_time > ATTACK_COOLDOWN and self.attack_locked == False:
                    # Rozpoczynamy atak - Dźwięk uderzenia zagra sam w metodzie attack() w base.py
                    self.update_action(2 if key[at1_key] else 3)
                    self.attack_type = 1 if key[at1_key] else 2
                    
                    self.attacking = True # Ustawiam flagę ataku
                    self.last_attack_time = current_time # Resetuję zegar cooldownu
                    self.attack_locked = True # Blokuję atak (trzeba puścić klawisz, żeby uderzyć znów)
            else:
                # Jeśli gracz puścił klawisz, zdejmuję blokadę
                self.attack_locked = False

        # 2. FIZYKA (Grawitacja działa zawsze, nawet jak atakuję)
        self.vel_y += GRAVITY # Zwiększam prędkość w dół (symulacja spadania)
        dy += self.vel_y      # Dodaję prędkość pionową do zmiany pozycji (dy)

        # Ograniczenia ekranu (żeby postać nie wyszła poza okno gry)
        if self.rect.left + dx < 0:
            dx = -self.rect.left # Blokada z lewej
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right # Blokada z prawej

        # Kolizja z podłogą
        if self.rect.bottom + dy > FLOOR_Y:
            self.vel_y = 0      # Zeruję prędkość (przestaję spadać)
            self.jump = False   # Resetuję flagę skoku (można skoczyć ponownie)
            dy = FLOOR_Y - self.rect.bottom # Ustawiam postać idealnie na ziemi

        # --- OSTATECZNA BLOKADA PRZENIKANIA (Kolizja z przeciwnikiem) ---
        if target.alive:
            # Tworzę "przyszły" prostokąt - sprawdzam, gdzie będę po wykonaniu ruchu dx
            future_rect = self.rect.copy()
            future_rect.x += dx
            
            # Jeśli w przyszłym miejscu wpadłbym na przeciwnika...
            if future_rect.colliderect(target.rect):
                # ...to koryguję ruch (dx), żeby zatrzymać się PRZED nim.
                if dx > 0 and self.rect.right <= target.rect.left:
                    dx = target.rect.left - self.rect.right # Zatrzymuję się na lewym boku wroga
                elif dx < 0 and self.rect.left >= target.rect.right:
                    dx = target.rect.right - self.rect.left # Zatrzymuję się na prawym boku wroga
                else:
                    dx = 0 # Jeśli już na siebie wleźliśmy, blokuję ruch całkowicie

        

        # 3. LOGIKA ANIMACJI (Maszyna stanów)
        # Decyduję, jaką animację wyświetlić na podstawie priorytetów
        if self.alive:
            # PRIORYTET 1: OBRYWANIE (HIT) - najważniejsze, przerywa wszystko inne
            if self.hit == True:
                self.update_action(4) # Animacja Hit
            # PRIORYTET 2: ATAK
            elif self.attacking == True:
                if self.attack_type == 1: self.update_action(2)
                elif self.attack_type == 2: self.update_action(3)
            # PRIORYTET 3: RUCH (Jeśli dx jest różne od 0, to znaczy że biegnę)
            elif dx != 0:
                self.update_action(1) # Animacja Run
            # PRIORYTET 4: STANIE (Idle)
            else:
                self.update_action(0) # Animacja Idle

        # 4. APLIKOWANIE RUCHU
        # Fizycznie przesuwam prostokąt postaci o wyliczone wartości
        self.rect.x += dx
        self.rect.y += dy
        
        # Wywołuję update z klasy bazowej, żeby obsłużyć klatki animacji
        self.update()