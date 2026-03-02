# Stałe konfiguracyjne
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SIZE_SCREEN = (SCREEN_WIDTH,SCREEN_HEIGHT)
FPS = 60

# Kolory
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
BG_COLOR = (50, 50, 50)  # Szare tło
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# Fizyka i Rozmiar
GRAVITY = 1.5
SPEED = 5
JUMP_FORCE = 20
SCALE = 0.75 # Mnożnik wielkości postaci
FLOOR_Y = 500

# Czas oczekiwania między atakami (w milisekundach)
# 500 ms = 0.5 sekundy, 1000 ms = 1 sekunda
ATTACK_COOLDOWN = 500 

# Szybkość animacji (im mniej, tym szybciej zmieniają się klatki)
ANIM_SPEED = {
    "IDLE": 200,    
    "RUN": 80,      
    "ATTACK": 50,    
    "HIT": 150,     

}

# Skale dla różnych typów wojowników

FIGHTER_SCALES = {
    "warrior": 0.7,     
    "warrior1": 0.6,  
    "warrior2": 0.5   
}