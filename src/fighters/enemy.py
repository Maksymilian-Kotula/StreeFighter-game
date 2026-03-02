import pygame
import random
from src.fighters.base import Fighter
from settings import SPEED, GRAVITY, FLOOR_Y, ATTACK_COOLDOWN


class Enemy(Fighter):
    
    
    def __init__(self, x, y, name, max_hp, image_scale, sound_handler):
        
        super().__init__(x, y, name, max_hp, image_scale, sound_handler)
        
        # Ustawiam, żeby bot patrzył w lewo na starcie (bo stoi po prawej stronie ekranu)
        self.flip = True
        
        # --- ZMIENNE AI (Sztucznej Inteligencji) ---
        # Zapamiętuję czas startu, żeby bot nie atakował od razu po włączeniu gry
        self.start_time = pygame.time.get_ticks()
        # Czas, przez jaki bot stoi w miejscu na początku rundy (2 sekundy)
        self.wait_at_start = 2000
        # Opóźnienie reakcji bota - żeby nie był idealną maszyną i czasem "zaspał" przed atakiem
        self.reaction_delay = 0 
        
        # --- ZMIENNE LOGIKI ODWROTU ---
        # Czy bot aktualnie ucieka od gracza?
        self.is_retreating = False
        # Kiedy zaczął uciekać?
        self.retreat_start_time = 0
        # Jak długo ma uciekać (losowane później)?
        self.retreat_duration = 1000

    

    # Główna metoda sterująca botem (zamiast klawiszy, tu decyduje algorytm)
    def move(self, screen_width, target):
        dx = 0 # Zmiana pozycji w poziomie
        dy = 0 # Zmiana pozycji w pionie
        self.attack_type = 0 # Resetuję typ ataku
        current_time = pygame.time.get_ticks() # Pobieram aktualny czas gry
        
        # LOGIKA DYSTANSU 
        # Obliczam różnicę środków postaci, żeby wiedzieć, po której stronie jest gracz
        x_diff = target.rect.centerx - self.rect.centerx
        
        # Obliczam fizyczną przerwę między hitboxami 
        
        if x_diff > 0: # Gracz jest po prawej stronie bota
            # Od lewej krawędzi gracza odejmuję prawą krawędź bota
            actual_gap = target.rect.left - self.rect.right
        else: # Gracz jest po lewej stronie bota
            # Od lewej krawędzi bota odejmuję prawą krawędź gracza
            actual_gap = self.rect.left - target.rect.right
        
        # Zwykły dystans (wartość bezwzględna) do ogólnej orientacji
        distance = abs(x_diff)

        # --- GŁÓWNA LOGIKA AI (MÓZG BOTA) ---
        # Bot myśli tylko, jeśli żyje, nie atakuje (nie jest w trakcie animacji ataku) i nie obrywa
        if self.alive and self.attacking == False and self.hit == False:
            
            # KROK 1: Logika odwrotu (Czy mam uciekać?)
            if self.is_retreating:
                # Sprawdzam, czy czas ucieczki już minął
                if current_time - self.retreat_start_time > self.retreat_duration:
                    self.is_retreating = False # Koniec ucieczki, wracam do walki
                else:
                    # Logika uciekania w stronę przeciwną do gracza
                    if x_diff > 0: # Gracz z prawej -> uciekaj w lewo
                        # Sprawdzam, czy nie jestem przy ścianie (margines 10px)
                        if self.rect.left <= 10: 
                            self.is_retreating = False # Jak ściana, to przestań uciekać
                        else:
                            dx = -SPEED # Idź w lewo
                            self.flip = True # Patrz w lewo
                    else: # Gracz z lewej -> ucieka w prawo
                        if self.rect.right >= screen_width - 10: 
                            self.is_retreating = False
                        else:
                            dx = SPEED # Idzie w prawo
                            self.flip = False # Patrz w prawo
            
            # KROK 2: Normalna walka (jeśli nie ucieka)
            else:
                # Zawsze obraca się twarzą do gracza
                if x_diff > 0: self.flip = False # Gracz z prawej, patrz w prawo
                else: self.flip = True # Gracz z lewej, patrz w lewo

                # Czy minął czas oczekiwania na start rundy?
                if current_time - self.start_time < self.wait_at_start:
                    dx = 0 # Stój w miejscu
                else:
                    # --- DECYZJA: ATAKOWAĆ CZY GONIĆ? ---
                    
                    # Jeśli przerwa między nami jest mniejsza niż 15 pikseli 
                    if actual_gap < 15:
                        dx = 0 # Zatrzymuję się, żeby uderzyć
                        
                        # Sprawdzam Cooldown (czy mogę znowu uderzyć) + moje opóźnienie (Reaction Delay)
                        if current_time - self.last_attack_time > (ATTACK_COOLDOWN + self.reaction_delay):
                            # Jeśli gotowy -> Wywołuję funkcję losującą atak
                            self.attack_ai(current_time)
                        else:
                            # --- SZANSA NA UCIECZKE (Gdy czekam na odnowienie ataku) ---
                            can_retreat = True
                            # Sprawdzam, czy mam miejsce za plecami, żeby uciekać
                            if x_diff > 0 and self.rect.left < 60: can_retreat = False # Za mało miejsca z lewej
                            if x_diff < 0 and self.rect.right > screen_width - 60: can_retreat = False # Za mało z prawej

                            # Jeśli mam miejsce i wylosuję 5% szansy -> uciekam
                            if can_retreat and random.randint(1, 100) < 5:
                                self.is_retreating = True
                                self.retreat_start_time = current_time
                                # Losuję, jak długo będę uciekał (pół sekundy do sekundy)
                                self.retreat_duration = random.randint(500, 1000)
                    
                    # --- DECYZJA O POŚCIGU ---
                    # Jeśli przerwa jest większa niż 20 pikseli 
                    elif actual_gap >= 20:
                        # Idę w stronę gracza
                        if x_diff > 0: dx = SPEED
                        else: dx = -SPEED

        

        # --- FIZYKA (GRAWITACJA I KOLIZJE) ---
        # Dodaję siłę grawitacji do prędkości pionowej
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        # Ograniczam ruch bota do granic ekranu (lewo/prawo)
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > screen_width: dx = screen_width - self.rect.right
        
        # Kolizja z podłogą - zatrzymuję spadanie, gdy dotknę ziemi
        if self.rect.bottom + dy > FLOOR_Y:
            self.vel_y = 0
            dy = FLOOR_Y - self.rect.bottom

        # --- OSTATECZNA BLOKADA PRZENIKANIA  ---
        # Sprawdzam, czy po wykonaniu ruchu (dx) wejdę w gracza
        if target.alive:
            future_rect = self.rect.copy() # Tworzę kopię swojego hitboxa
            future_rect.x += dx # Przesuwam go "na próbę"
            
            # Jeśli próbny hitbox koliduje z graczem...
            if future_rect.colliderect(target.rect):
                # ...to cofam ruch (dx) dokładnie o tyle, ile wynosi nakładka.
                # Dzięki temu postacie stykają się, ale nie przenikają.
                if dx > 0 and self.rect.right <= target.rect.left:
                    dx = target.rect.left - self.rect.right
                elif dx < 0 and self.rect.left >= target.rect.right:
                    dx = target.rect.right - self.rect.left
                else:
                    dx = 0 # Jeśli już w nim jestem, zatrzymuję się całkowicie


        # --- ANIMACJE ---
        # Ustawiam odpowiednią akcję w zależności od tego, co robi bot
        if self.alive:
            if self.hit:
                self.update_action(4) 
            elif self.attacking:
                dx = 0 # Podczas ataku nie można się ruszać
            elif dx != 0:
                self.update_action(1) 
            else:
                self.update_action(0) 

        # Aplikuję obliczone zmiany pozycji do hitboxa
        self.rect.x += dx
        self.rect.y += dy
        
        # Wywołuję update z klasy Fighter, żeby obsłużyć klatki animacji
        self.update()

    # Metoda losująca, jaki atak wykonać
    def attack_ai(self, current_time):
        # 10% szansy, że bot "się zagapi" i nie zaatakuje od razu (zwiększa reaction_delay)
        if random.randint(1, 100) < 10:
             self.reaction_delay = 500
             return

        # Losuję liczbę od 1 do 10
        attack_choice = random.randint(1, 10)
        
        # 70% szans na Atak 1 (szybki/słabszy), 30% na Atak 2 (wolny/mocny)
        if attack_choice > 3: 
            self.update_action(2) # Atak 1
            self.attack_type = 1
        else:
            self.update_action(3) # Atak 2
            self.attack_type = 2
        
        # Ustawiam flagi ataku i resetuję czasy
        self.attacking = True
        self.last_attack_time = current_time
        # Po ataku ustawiam losowe opóźnienie na następny raz (0.2s - 1.0s)
        self.reaction_delay = random.randint(200, 1000)