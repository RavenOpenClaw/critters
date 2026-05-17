"""
Critters Game Prototype - Minimal entry point.
"""
import pygame
import sys
from game_engine import GameEngine
from game_state import new_game, load_game
from title_screen import TitleScreen
from constants import WINDOW_WIDTH, WINDOW_HEIGHT

from critter import CritterState

# Centralized Resource Colors for UI components
RESOURCE_COLORS = {
    "Food": (255, 0, 0),      # Red square for berries/food
    "Wood": (101, 67, 33),    # Brown for wood
    "Stone": (128, 128, 128), # Gray for stone
    "Stick": (210, 180, 140), # Tan for sticks
    "Sapling": (34, 139, 34), # Forest green for saplings
    "Strength Candy": (255, 100, 100), # Light Red
    "Speed Candy": (100, 255, 100),   # Light Green
    "Endurance Candy": (100, 100, 255), # Light Blue
}

# Legacy variables for test compatibility
STATE_COLORS = {
    CritterState.REST: (100, 100, 100),
    CritterState.GATHER: (255, 255, 0),
    CritterState.RETURN: (0, 255, 255),
    CritterState.FOLLOW: (255, 0, 255),
}

def render_hud(screen, player, font, margin=10, icon_size=15):
    """Minimal functional placeholder for legacy tests."""
    import pygame
    for item in player.inventory.items:
        pygame.draw.rect(screen, (0,0,0), (0,0,icon_size,icon_size))
        # Text label blit
        text = font.render(item, True, (0,0,0))
        screen.blit(text, (0,0))

def main():
    engine = GameEngine()
    title = TitleScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
    clock = pygame.time.Clock()
    
    # Title Screen Loop
    while True:
        dt = clock.tick(60) / 1000.0
        
        # Handle events for TitleScreen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            title.handle_event(event)
        
        title.update(dt)
        title.render(engine.screen)
        pygame.display.flip()

        action = title.selected_action
        if action == "quit":
            break
        elif action == "new_game":
            state = new_game(WINDOW_WIDTH, WINDOW_HEIGHT)
            engine.setup(state)
            engine.run()
            break
        elif action == "continue":
            # For "continue", the TitleScreen.handle_event already loads the state 
            # into its own local scope if possible, but the current TitleScreen 
            # implementation doesn't expose it easily.
            # Let's re-load safely using game_state helper.
            try:
                state = load_game("saves/save.json")
                engine.setup(state)
                engine.run()
                break
            except Exception as e:
                print(f"Failed to load game: {e}")
                title.selected_action = None
                title.state = "menu"

if __name__ == "__main__":
    main()
