import pygame
import menu
print("type(menu.Menu) =", type(menu.Menu))

class Game_engine:

    count = 0

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (100, 100, 255)

    states = ["menu", "game"]
    states_state = {"menu": ["main_menu", "load_game_menu", "settings"], "game": ["paused", "running"]}

    def __init__(self):
        Game_engine.count += 1
        if Game_engine.count > 1:
            print("SOMETHING GOES WRONG MORE THAN 1 GAME ENGINE GENERATED")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        print("Дисплей инициализирован:", pygame.display.get_init())
        print("Поверхность экрана:", self.screen)
        print("Размер:", self.screen.get_size())
        self.runs = False
        self.current_process = menu.Menu(self)
        self.current_process.switch_on()
  
    def run(self):
        clock = pygame.time.Clock()
        self.runs = True
        while self.runs is True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.runs = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    self.current_process.process_click(mouse_pos)()
                
            if self.current_process.name == "menu":
                self.current_process.show() 
            
            pygame.display.flip()
            clock.tick(60)


def main():
    try:
        pygame.init()
        engine = Game_engine()
        engine.run()
    except Exception as e:
        print(e)

main()       
