import pygame
import os
from settings import SIZE_SCREEN


class Background:
    def __init__(self, map_name):
        # Tworzę pustą listę, w której będę przechowywał wszystkie klatki animacji tła
        self.animation_list = []
        
        # Ustawiam indeks aktualnie wyświetlanej klatki na 0 (początek)
        self.frame_index = 0
        
        # Zapamiętuję czas ostatniej aktualizacji klatki, aby kontrolować prędkość animacji
        self.update_time = pygame.time.get_ticks()
        
        # Zapamiętuję nazwę mapy (np. "1", "2"),
        self.map_name = map_name
        
        # Prędkość animacji tła w milisekundach.
        self.animation_speed = 220 
        
        # Wywołuję metodę, która fizycznie wczyta pliki z dysku
        self.load_images(map_name)

    # Metoda odpowiedzialna za znalezienie, posortowanie i załadowanie grafik
    def load_images(self, map_name):
        # Buduję ścieżkę do folderu z tłem. Używam f-stringa, żeby wstawić numer mapy.
        
        path = f"assets/images/backgrounds/{map_name}"
        
        # Zabezpieczenie: Sprawdzam, czy taki folder w ogóle istnieje na dysku.
        # Jeśli nie, wypisuję błąd i przerywam funkcję, żeby gra się nie wyłączyła.
        if not os.path.exists(path):
            print(f"BŁĄD: Nie znaleziono folderu tła: {path}")
            return

        try:
            # Pobieram listę wszystkich plików znajdujących się w tym folderze
            file_list = os.listdir(path)
            
            # Filtruję listę: interesują mnie tylko pliki graficzne (.png lub .jpg).
            # Dzięki temu ignoruję pliki systemowe czy śmieci.
            valid_files = [f for f in file_list if f.endswith(".png") or f.endswith(".jpg")]
            
            # Sortuję pliki numerycznie.
            # Wyrażenie lambda wyciąga cyfry z nazwy pliku.
            valid_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))) if any(char.isdigit() for char in f) else f)

            # Pętla po posortowanych plikach
            for f in valid_files:
                img_path = f"{path}/{f}"
                
                # Wczytuję obrazek do Pygame i używam .convert().
                # .convert() optymalizuje format pikseli pod ekran, co znacznie przyspiesza rysowanie (FPS).
                img = pygame.image.load(img_path).convert()
                
                # Skaluję obrazek do wielkości ekranu (SIZE_SCREEN)
                img = pygame.transform.scale(img, SIZE_SCREEN)
                
                # Dodaję gotowy, przeskalowany obrazek do listy klatek
                self.animation_list.append(img)
                
            # Informacja diagnostyczna w konsoli
            print(f"Załadowano tło '{map_name}': {len(self.animation_list)} klatek.")
            
        except Exception as e:
            # Jeśli cokolwiek pójdzie nie tak (np. uszkodzony plik), wypisuję błąd
            print(f"Błąd podczas ładowania tła: {e}")

    # Metoda aktualizująca stan animacji (wywoływana w pętli gry)
    def update(self):
        # Aktualizuję animację TYLKO wtedy, gdy mam więcej niż 1 obrazek.
        # Jeśli obrazek jest jeden, to tło jest statyczne i nie ma sensu nic obliczać.
        if len(self.animation_list) > 1:
            
            # Sprawdzam, czy minął już czas określony w animation_speed
            if pygame.time.get_ticks() - self.update_time > self.animation_speed:
                
                # Przesuwam indeks na następną klatkę
                self.frame_index += 1
                
                # Resetuję zegar, żeby zacząć odliczać czas dla nowej klatki
                self.update_time = pygame.time.get_ticks()
                
                # Sprawdzam, czy doszedłem do końca listy klatek.
                # Jeśli tak, wracam na początek (index 0), tworząc pętlę animacji.
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0

    # Metoda rysująca tło na ekranie
    def draw(self, screen):
        # Sytuacja idealna: Jeśli udało się załadować obrazki -> rysuję aktualną klatkę
        if len(self.animation_list) > 0:
            current_image = self.animation_list[self.frame_index]
            # Blituję (rysuję) obrazek w punkcie (0, 0), czyli w lewym górnym rogu
            screen.blit(current_image, (0, 0))
        else:
            # Jeśli folder był pusty lub nie istniał.
            # Rysuję jednolite tło w zależności od wybranej mapy, żeby gracz nie widział czarnego ekranu.
            if self.map_name == "1":
                screen.fill((34, 139, 34)) 
            elif self.map_name == "2":
                screen.fill((50, 20, 20))  
            elif self.map_name == "3":
                screen.fill((25, 25, 112)) 
            else:
                screen.fill((0, 0, 0))     