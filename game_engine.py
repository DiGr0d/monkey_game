import pygame
import menu
import game
#print("type(menu.Menu) =", type(menu.Menu))
import game_widget
import object
import menus
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
        game.load_tile_images() 
        print("Дисплей инициализирован:", pygame.display.get_init())
        print("Поверхность экрана:", self.screen)
        print("Размер:", self.screen.get_size())
        self.runs = False
        self.current_processes = []

    def get_processes(self):
        return self.current_processes
  
    def add_process(self, process):
        self.current_processes.append(process)

    def run(self):
        clock = pygame.time.Clock()
        self.runs = True

        from menus import MainMenu
        #menu1 = MainMenu(self, x=0, y=0, width=self.screen.get_width(), height=self.screen.get_height())
        try:
            main_menu = menus.MainMenu(self, x=0, y=0, width=self.screen.get_width(), height=self.screen.get_height())
            #gw = game_widget.GameWidget(self, x=0, y=0, width=self.screen.get_width(), height=self.screen.get_height())
            #gw.add_mob(object.Mob(gw.game.grid, (1, 1)))
            #gw.add_tower(object.Tower(gw.game.grid, (10, 10)))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.runs = False
        self.current_processes.append(main_menu)
        for process in self.current_processes:
            process.switch_on()

        try:
            while self.runs:
                dt = clock.tick(60) / 1000.0   # время в секунда

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.runs = False
                        break
                    self.update_event(event)
                    if event.type == pygame.VIDEORESIZE:
                        self.resize_every_process()

                for process in self.current_processes:
                    print(type(process).__name__)
                # Обновляем GameWidget-ы перед отрисовкой
                for process in self.current_processes:
                    if isinstance(process, game_widget.GameWidget):   # проверяем, что это наш виджет
                        process.update(dt)

                # Отрисовка
                self.screen.fill(self.WHITE)
                for process in self.current_processes:
                    process.show()

                pygame.display.flip()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.runs = False

    def update_event(self, event):
        #mouse_pos = event.pos
        #gen = (process.process_click(mouse_pos) for process in self.current_processes)
        for process in list(self.current_processes):
            process.process_event(event)

    def resize_every_process(self):
        now = pygame.time.get_ticks()
        if hasattr(self, '_last_resize_time') and now - self._last_resize_time < 50:
            return
        self._last_resize_time = now
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
