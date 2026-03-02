import pygame
from settings import RED, YELLOW, WHITE, BLACK

UI_BG_COLOR = (50, 0, 0)

def draw_health_bar(surface, health, max_health, x, y, name, font, is_enemy=False):
    ratio = health / max_health
    
    # --- ZMIANY TUTAJ: MNIEJSZE WYMIARY ---
    bar_width = 300  # Było 400
    bar_height = 20  # Było 30 (będzie smuklejszy)
    skew = 25        # Trochę mniejszy skos
    
    # --- ZMIANY TUTAJ: NAPISY WYŻEJ ---
    # Zmieniamy y - 30 na y - 45 (żeby poszły w górę)
    name_y_offset = y - 45 
    shadow_offset = 2 

    if not is_enemy:
        # --- GRACZ ---
        # Cień
        surface.blit(font.render(name, True, BLACK), (x + shadow_offset, name_y_offset + shadow_offset))
        # Tekst właściwy
        surface.blit(font.render(name, True, WHITE), (x, name_y_offset))
        
        bg_shape = [
            (x + skew, y),                  
            (x + bar_width + skew, y),      
            (x + bar_width, y + bar_height),
            (x, y + bar_height)             
        ]
        
        current_width = bar_width * ratio
        hp_shape = [
            (x + skew, y), 
            (x + current_width + skew, y), 
            (x + current_width, y + bar_height), 
            (x, y + bar_height)
        ]
        
    else:
        # --- WRÓG ---
        name_text = font.render(name, True, WHITE)
        name_shadow = font.render(name, True, BLACK)
        text_width = name_text.get_width()
        
        # Tekst (też wyżej)
        surface.blit(name_shadow, (x + bar_width - text_width + shadow_offset + skew, name_y_offset + shadow_offset))
        surface.blit(name_text, (x + bar_width - text_width + skew, name_y_offset))

        bg_shape = [
            (x, y),                         
            (x + bar_width, y),             
            (x + bar_width + skew, y + bar_height), 
            (x + skew, y + bar_height)      
        ]
        
        current_width = bar_width * ratio
        hp_shape = [
            (x + bar_width - current_width, y), 
            (x + bar_width, y), 
            (x + bar_width + skew, y + bar_height), 
            (x + bar_width - current_width + skew, y + bar_height)
        ]

    # Rysowanie
    pygame.draw.polygon(surface, WHITE, bg_shape, 3) 
    pygame.draw.polygon(surface, BLACK, bg_shape, 1) 
    pygame.draw.polygon(surface, UI_BG_COLOR, bg_shape) 

    if health > 0:
        pygame.draw.polygon(surface, YELLOW, hp_shape)

def draw_stage_info(surface, stage, font):
    # Tworzymy tekst poziomu (np. STAGE 1)
    stage_text = font.render(f"Level {stage}", True, (255, 255, 255))
    text_rect = stage_text.get_rect(center=(surface.get_width() // 2, 30)) 
    
    # Rysujemy cień pod tekstem
    shadow = font.render(f"Level {stage}", True, (0, 0, 0))
    surface.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
    surface.blit(stage_text, text_rect)