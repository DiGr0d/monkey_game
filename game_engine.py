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
    ALPHA_GRAY = (64, 64, 64, 128)

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
        self.current_processes = []

    def get_processes(self):
        return self.current_processes
  
    def run(self):
        clock = pygame.time.Clock()
        self.runs = True
        menu1 = menu.Menu(self, x=0,y=0,width=self.screen.get_width()/2)
        menu2 = menu.Menu(self, x=self.screen.get_width()/2)
        self.current_processes.append(menu1)
        self.current_processes.append(menu2)
        for process in self.current_processes:
            process.switch_on()
        try:
            while self.runs:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.runs = False
                        break
                    self.update_event(event)
                    if event.type == pygame.VIDEORESIZE:
                        self.resize_every_process()
                    
                for process in self.current_processes:
                    process.show()
                
                pygame.display.flip()
                clock.tick(60)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.runs = False

    def update_event(self, event):
        #mouse_pos = event.pos
        #gen = (process.process_click(mouse_pos) for process in self.current_processes)
        for process in self.current_processes:
            process.process_event(event)

    def resize_every_process(self):
        nw, nh = self.screen.get_size()
        for process in self.current_processes:
            process.update_geometry(nw, nh)

def main():
    try:
        pygame.init()
        engine = Game_engine()
        engine.run()
    except Exception as e:
        print(e)

main()       
