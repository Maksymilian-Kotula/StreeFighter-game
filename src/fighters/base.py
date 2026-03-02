import pygame
import os
from settings import SCALE, ANIM_SPEED

class Fighter():
    # 1. ZMIANA W INIT: Dodajemy sound_handler na końcu argumentów
    def __init__(self, x, y, name, max_hp, image_scale, sound_handler):
        # Przypisanie podstawowych parametrów postaci (imię, skala grafiki)
        self.name = name
        self.image_scale = image_scale
        
        # Zapisuję przekazany obiekt do obsługi dźwięków, aby postać mogła ich używać (np. przy trafieniu)
        self.sound_handler = sound_handler 
        
        # --- HITBOX (Fizyczne ciało postaci) ---
        # Obliczam szerokość i wysokość prostokąta kolizji na podstawie skali
        self.width = 320 * image_scale
        self.height = 180 * image_scale
        
        # Tworzę prostokąt (Rect), który służy do wykrywania kolizji i pozycji
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        # Ustawiam środek postaci w podanych współrzędnych (x, y)
        self.rect.center = (x, y)
        
        # Ustawienie statystyk walki i ruchu
        self.attack_damage = 10     # Siła ataku
        self.vel_y = 0              # Prędkość pionowa (do grawitacji i skoków)
        self.flip = False           # Czy postać jest obrócona w lewo (False = prawo)
        self.last_attack_time = 0   # Czas ostatniego ataku (do cooldownu)

        # --- ZMIENNE ATAKU ---
        self.attacking = False      # Czy postać aktualnie wykonuje atak
        self.attack_type = 0        # Rodzaj ataku (np. 1 = lekki, 2 = ciężki)
        self.attack_landed = False  # Flaga: czy cios już "trafił" (żeby nie zadawać dmg co klatkę)
        
        # --- ZMIENNE STANU ---
        self.health = max_hp        # Aktualne życie
        self.max_health = max_hp    # Maksymalne życie (do paska HP)
        self.alive = True           # Czy postać żyje
        self.hit = False            # Czy postać właśnie obrywa (animacja bólu)
        
        # --- ANIMACJE ---
        self.animation_list = []    # Lista przechowująca wszystkie klatki wszystkich animacji
        self.frame_index = 0        # Numer aktualnie wyświetlanej klatki animacji
        self.action = 0             # Numer aktualnej akcji (0=Idle, 1=Run itd.)
        self.update_time = pygame.time.get_ticks() # Czas ostatniej zmiany klatki (do kontroli prędkości animacji)
        
        # Definicja nazw folderów z animacjami, które będziemy ładować
        self.animation_types = ["Idle", "Run", "Attack1", "Attack2", "Hit"]
        
        # Wywołanie metody ładującej grafiki z dysku
        self.load_images(name)
        
        # Ustawienie początkowego obrazka
        self.image = self.animation_list[self.action][self.frame_index]

    # Metoda odpowiedzialna za wczytanie plików graficznych z folderów
    def load_images(self, name):
        # Budowanie ścieżki do folderu postaci (np. "assets/images/warrior")
        path = f"assets/images/{name}"
        
        # Pętla po każdym typie animacji (Idle, Run, itd.)
        for animation in self.animation_types:
            temp_list = [] # Tymczasowa lista na klatki jednej animacji
            try:
                # Pełna ścieżka do konkretnej animacji (np. ".../warrior/Idle")
                full_path = f"{path}/{animation}"
                
                # Zabezpieczenie: sprawdzam, czy folder istnieje
                if not os.path.exists(full_path):
                    # print(f"BŁĄD: Brak folderu {full_path}") # Można zakomentować, żeby nie śmieciło
                    self.animation_list.append([]) # Dodaję pustą listę, żeby indeksy się zgadzały
                    continue

                # Pobieram listę plików w folderze
                file_list = os.listdir(full_path)
                # Filtruję tylko pliki PNG
                valid_files = [f for f in file_list if f.endswith(".png")]
                # Sortuję pliki numerycznie (żeby 10.png było po 9.png, a nie po 1.png)
                valid_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
                
                # Ładowanie każdego pliku po kolei
                for f in valid_files:
                    img_path = f"{full_path}/{f}"
                    # Wczytanie obrazka z zachowaniem przezroczystości (convert_alpha)
                    img = pygame.image.load(img_path).convert_alpha()
                    # Skalowanie obrazka do odpowiedniej wielkości w grze
                    img = pygame.transform.scale(img, (int(img.get_width() * self.image_scale), int(img.get_height() * self.image_scale)))
                    temp_list.append(img)
            except Exception as e:
                print(f"Błąd ładowania {animation}: {e}")
            
            # Dodanie gotowej listy klatek danej animacji do głównej listy
            self.animation_list.append(temp_list)

    # Metoda aktualizująca stan postaci (wywoływana co klatkę gry)
    def update(self):
        # Domyślny czas trwania klatki (szybkość animacji)
        animation_cooldown = 100
        
        # Ustawienie prędkości animacji w zależności od tego, co postać robi
        # Pobieram wartości ze słownika ANIM_SPEED (zdefiniowanego w settings.py)
        if self.action == 0: animation_cooldown = ANIM_SPEED.get("IDLE", 200)
        elif self.action == 1: animation_cooldown = ANIM_SPEED.get("RUN", 80)
        elif self.action == 2 or self.action == 3: animation_cooldown = ANIM_SPEED.get("ATTACK", 50)
        elif self.action == 4: animation_cooldown = ANIM_SPEED.get("HIT", 150)

        # Ustawienie aktualnego obrazka na podstawie akcji i numeru klatki
        self.image = self.animation_list[self.action][self.frame_index]
        
        # Sprawdzam, czy minęło wystarczająco dużo czasu, by zmienić klatkę animacji
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1 # Przesuwam na następną klatkę
            self.update_time = pygame.time.get_ticks() # Resetuję zegar klatki
            
            # Sprawdzam, czy animacja dobiegła końca (skończyły się klatki)
            if self.frame_index >= len(self.animation_list[self.action]):
                
                # Jeśli postać nie żyje, zatrzymuję ją na ostatniej klatce (leży na ziemi)
                if self.alive == False:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    # Jeśli skończył się atak -> wracam do stania (Idle)
                    if self.action == 2 or self.action == 3:
                        self.attacking = False
                        self.attack_landed = False 
                        self.update_action(0)
                    # Jeśli skończyła się animacja obrywania (Hit) -> wracam do stania
                    elif self.action == 4:
                        self.hit = False
                        self.attacking = False
                        self.update_action(0)
                    # Dla pętli (np. bieg, stanie) -> wracam do klatki 0
                    else:
                        self.frame_index = 0

    # Metoda zmieniająca aktualną akcję (animację)
    def update_action(self, new_action):
        # Zmieniam akcję tylko, jeśli jest inna niż obecna (żeby nie resetować animacji ciągle)
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0 # Resetuję animację do początku
            self.update_time = pygame.time.get_ticks()

    # Metoda rysująca postać na ekranie
    def draw(self, surface):
        # Obracam obrazek w zależności od kierunku (self.flip)
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        
        # Pobieram prostokąt obrazka i ustawiam go w miejscu hitboxa (self.rect)
        # Dzięki temu grafika podąża za logiczną pozycją postaci
        img_rect = flipped_image.get_rect()
        img_rect.centerx = self.rect.centerx
        img_rect.bottom = self.rect.bottom
        
        # Rysuję (blituję) obrazek na powierzchni ekranu
        surface.blit(flipped_image, img_rect)
        
        # ODKOMENTUJ TO KONIECZNIE DO TESTÓW (rysuje czerwony kwadrat kolizji):
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)

    # Metoda obsługująca logikę ataku
    def attack(self, target):
        # Wykonuję logikę ataku tylko, jeśli postać atakuje i cios jeszcze nie trafił w tej animacji
        if self.attacking and not self.attack_landed:
            
            # Obliczam zasięg ataku na podstawie skali
            attack_range = 110 * self.image_scale 
            # Tworzę prostokąt ataku (hitbox miecza/pięści)
            attacking_rect = pygame.Rect(0, self.rect.y, attack_range, self.rect.height)
            
            # Ustawiam pozycję ataku z prawej lub lewej strony, zależnie od zwrotu postaci
            if not self.flip:
                attacking_rect.x = self.rect.right
            else:
                attacking_rect.x = self.rect.left - attack_range

            # --- BLOKADA (CLASH - zderzenie broni) ---
            # Sprawdzam, czy przeciwnik też teraz atakuje
            if target.attacking:
                # Obliczam, gdzie jest atak przeciwnika
                target_attack_range = 110 * target.image_scale
                target_attack_rect = pygame.Rect(0, target.rect.y, target_attack_range, target.rect.height)
                
                if not target.flip:
                    target_attack_rect.x = target.rect.right
                else:
                    target_attack_rect.x = target.rect.left - target_attack_range

                # Sprawdzam, czy mój atak zderzył się z atakiem wroga
                if attacking_rect.colliderect(target_attack_rect):
                    print("⚔️ ZDERZENIE CIOSÓW! Nikt nie traci HP.")
                    self.attack_landed = True # Uznaję atak za "zużyty"
                    # self.sound_handler.play_sfx('clash')
                    return # Wychodzę z funkcji, nikt nie obrywa

            # --- ZADAWANIE OBRAŻEŃ ---
            # Sprawdzam, czy mój prostokąt ataku dotknął hitboxa (ciała) przeciwnika
            if attacking_rect.colliderect(target.rect):
                if target.alive:
                    # Odejmuję życie przeciwnikowi
                    target.health -= self.attack_damage
                    # Wywołuję reakcję na uderzenie u przeciwnika (animacja + odrzut)
                    target.hit_reaction(self.rect.centerx)
                    # Oznaczam cios jako trafiony (żeby nie zadać obrażeń 60 razy na sekundę)
                    self.attack_landed = True
                    print(f"BUM! {self.name} trafił {target.name}!")
                    
                    # 2. ZMIANA W ATTACK: GRAMY DŹWIĘK TRAFIENIA
                    # Używam sound_handlera, żeby odtworzyć dźwięk 'hit'
                    if self.sound_handler:
                        self.sound_handler.play_sfx('hit')
    
    # Metoda wywoływana, gdy postać otrzyma obrażenia
    def hit_reaction(self, attacker_x):
        self.hit = True        # Ustawiam flagę, że postać obrywa
        self.attacking = False # Przerywam ewentualny atak
        self.update_action(4)  # Zmieniam animację na "Hit" (4)
        
        # Logika odrzutu (knockback)
        knockback_force = 50 
        # Jeśli atakujący był z lewej, odlatuję w prawo (i na odwrót)
        if self.rect.centerx < attacker_x:
            self.rect.x -= knockback_force 
        else:
            self.rect.x += knockback_force