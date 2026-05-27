import pygame
import sys
from core.game import Game

def main() -> None:
    pygame.init()
    
    try:
        # Create and run the game instance
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game crashed with error: {e}")
        pygame.quit()
        sys.exit(1)
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()