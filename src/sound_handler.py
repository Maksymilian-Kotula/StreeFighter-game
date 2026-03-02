import pygame
import os

class SoundHandler:
    def __init__(self):
        # Inicjalizacja miksera
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Ustawienia głośności (0.0 - 1.0)
        self.music_volume = 0.5
        self.sfx_volume = 0.6
        
        self.current_track = None
        self.sounds = {}

        # Lista efektów (nazwa_w_kodzie : nazwa_pliku)
        sfx_files = {
            'hit': 'punch.wav',
            'win': 'win.wav',
            'lose': 'lose.wav'
        }

        print("--- ŁADOWANIE DŹWIĘKÓW ---")
        for name, filename in sfx_files.items():
            path = f"assets/audio/{filename}"
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[name] = sound
                except Exception as e:
                    print(f"Błąd pliku {filename}: {e}")
            else:
                print(f"BRAK PLIKU SFX: {path}")

    def play_music(self, track_type):
        # Mapowanie typów muzyki na pliki
        tracks = {
            'menu': 'assets/audio/music_menu.mp3',
            'fight': 'assets/audio/music_fight.mp3'
        }
        
        # Jeśli ta sama muzyka już gra, nie resetuje jej
        if self.current_track == track_type:
            return

        filename = tracks.get(track_type)
        if filename:
            path = filename # Zakładamy pełną ścieżkę w słowniku wyżej lub tutaj
            if os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1) # Pętla nieskończona
                    self.current_track = track_type
                except Exception as e:
                    print(f"Błąd muzyki: {e}")
            else:
                print(f"BRAK PLIKU MUZYKI: {path}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()