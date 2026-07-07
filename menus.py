import pygame
import os
import re
import game
from menu import Menu


# ключ для сортировки типа save2 < save10 (а не по буквам)
def _natural_sort_key(text):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', text)]


# возвращает список json файлов в папке, создает папку если ее нет
def list_json_filenames(folder_path):
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        return []
    filenames = (f for f in os.listdir(folder_path) if f.lower().endswith(".json"))
    return sorted(filenames, key=_natural_sort_key)


# меню с фиксированной высотой кнопки и прокруткой колесом мыши,
# если кнопок больше чем влезает на экран
class ScrollableMenu(Menu):

    MIN_BUTTON_HEIGHT = 36
    SCROLL_STEP = 1

    def __init__(self, game_engine, **kwargs):
        self.scroll_offset = 0
        self.visible_count = 0
        super().__init__(game_engine, **kwargs)

    # тут высота кнопки фиксированная а не делится на все кнопки как в Menu
    def calculate_button_sizes(self, **kwargs):
        super().calculate_button_sizes(**kwargs)

        num_buttons = len(self.buttons)
        if num_buttons == 0:
            self.visible_count = 0
            return

        fixed_height = max(self.MIN_BUTTON_HEIGHT, self.h * 0.12)
        spacing = fixed_height * 0.25

        self.button_heigth = fixed_height
        self.spacing = spacing

        available_h = self.h * 0.8 - self.height_indent * 2
        step = fixed_height + spacing
        self.visible_count = max(1, int(available_h // step)) if step > 0 else num_buttons

        max_offset = max(0, num_buttons - self.visible_count)
        self.scroll_offset = min(self.scroll_offset, max_offset)

    # скролл колесом мыши, если курсор над меню
    def process_event(self, event):
        if not self.works:
            return
        if event.type == pygame.MOUSEWHEEL:
            rect = pygame.Rect(self.x, self.y, self.w, self.h)
            if rect.collidepoint(pygame.mouse.get_pos()):
                max_offset = max(0, len(self.buttons) - self.visible_count)
                self.scroll_offset -= event.y * self.SCROLL_STEP
                self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
            return
        super().process_event(event)

    # как в Menu, но номер кнопки считается с учетом scroll_offset
    def process_click(self, pos):
        if not self.works:
            return
        if len(pos) != 2:
            raise ValueError("process_click needs a tuple of two elements (x, y)")
        x, y = pos
        if not all(isinstance(a, int) for a in pos):
            raise ValueError("Every tuple element must be an integer in process_click")

        x_pos = self.with_indent + self.x
        y_pos = self.height_indent + self.y
        x_right_pos = self.x + self.w - self.with_indent
        y_down_pos = self.y + self.h - self.height_indent

        if not (x_pos < x < x_right_pos and y_pos < y < y_down_pos):
            return None

        rect_hei = self.spacing + self.button_heigth
        if rect_hei <= 0:
            return None

        row = int((y - y_pos) // rect_hei)
        if row < 0 or row >= self.visible_count:
            return None

        idx = row + self.scroll_offset
        if idx < 0 or idx >= len(self.buttons):
            return None

        row_y = y_pos + row * rect_hei
        if row_y + self.button_heigth < y:
            return None

        return self.buttons[idx]["callback"]

    # рисуем только видимый кусок buttons + полоску скролла справа
    def show(self):
        if not self.works or self.w <= 0 or self.h <= 0:
            return

        scr = self.game_engine.screen
        scrrect = pygame.Rect(self.x, self.y, self.w, self.h)
        color = self.game_engine.WHITE if scrrect.collidepoint(pygame.mouse.get_pos()) else self.game_engine.ALPHA_GRAY
        pygame.draw.rect(scr, color, scrrect)

        font = pygame.font.Font(None, 26)
        pos_x = self.with_indent + self.x
        pos_y = self.height_indent + self.y
        rect_hei = self.spacing + self.button_heigth

        visible_buttons = self.buttons[self.scroll_offset:self.scroll_offset + self.visible_count]

        for button in visible_buttons:
            rect = (pos_x, pos_y, self.button_width, self.button_heigth)
            prect = pygame.Rect(rect)
            color = self.game_engine.BLUE if prect.collidepoint(pygame.mouse.get_pos()) else self.game_engine.GRAY
            pygame.draw.rect(scr, color, rect)
            pygame.draw.rect(scr, self.game_engine.BLACK, rect, 1)

            text_surface = font.render(button["name"], True, self.game_engine.BLACK)
            text_rect = text_surface.get_rect(center=prect.center)
            scr.blit(text_surface, text_rect)
            pos_y += rect_hei

        if len(self.buttons) > self.visible_count:
            bar_x = self.x + self.w - 6
            bar_h = self.h - self.height_indent * 2
            bar_y = self.y + self.height_indent
            pygame.draw.rect(scr, self.game_engine.BLACK, (bar_x, bar_y, 4, bar_h), 1)

            max_offset = max(1, len(self.buttons) - self.visible_count)
            thumb_h = max(10, bar_h * self.visible_count / len(self.buttons))
            thumb_y = bar_y + (bar_h - thumb_h) * (self.scroll_offset / max_offset)
            pygame.draw.rect(scr, self.game_engine.GRAY, (bar_x, thumb_y, 4, thumb_h))


# добавляет кнопку назад, которая возвращает в родительское меню
class SubMenu(ScrollableMenu):

    BACK_BUTTON_NAME = "Назад"

    def __init__(self, game_engine, **kwargs):
        self.back_menu = kwargs.pop("back_menu", None)
        super().__init__(game_engine, **kwargs)
        self.buttons.append({"name": self.BACK_BUTTON_NAME, "callback": self.go_back})
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def go_back(self):
        if self.back_menu is not None:
            self.back_menu.return_from_child()


# кнопка на каждый json файл в saves/
class LoadGameMenu(SubMenu):

    SAVE_DIR = "saves"

    def __init__(self, game_engine, **kwargs):
        super().__init__(game_engine, **kwargs)
        for filename in list_json_filenames(self.SAVE_DIR):
            display_name = os.path.splitext(filename)[0]
            path = os.path.join(self.SAVE_DIR, filename)
            self.buttons.insert(len(self.buttons) - 1, {
                "name": display_name,
                "callback": lambda p=path: self.load_save(p)
            })
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def load_save(self, path):
        print(f"Загружаем сохранение: {path}")


# кнопка на каждый json файл в map_saves/ + кнопка создать карту в конце
class MapMakerMenu(SubMenu):

    MAP_SAVE_DIR = "map_saves"

    def __init__(self, game_engine, **kwargs):
        super().__init__(game_engine, **kwargs)
        for filename in list_json_filenames(self.MAP_SAVE_DIR):
            display_name = os.path.splitext(filename)[0]
            path = os.path.join(self.MAP_SAVE_DIR, filename)
            self.buttons.insert(len(self.buttons) - 1, {
                "name": display_name,
                "callback": lambda p=path: self.open_existing_map(p)
            })
        self.buttons.insert(len(self.buttons) - 1, {
            "name": "Создать новую карту",
            "callback": self.create_new_map
        })
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def open_existing_map(self, path):
        self._launch_map_maker(load_path=path)

    def create_new_map(self):
        self._launch_map_maker(load_path=None)

    def _launch_map_maker(self, load_path):
<<<<<<< HEAD
=======
        print("launch map maker")
>>>>>>> c092d7d (fixed mapmenu bug)
        engine = self.get_engine()
        main_menu = self.back_menu
        width, height = engine.screen.get_size()
        mapmaker = game.MapMaker(engine, main_menu, x=0, y=0, width=width, height=height, load_path=load_path)
        if main_menu is not None:
            main_menu._close_child()
        engine.add_process(mapmaker)
        mapmaker.switch_on()
<<<<<<< HEAD


class NewGameMapMenu(SubMenu):
    
    MAP_SAVE_DIR = "map_saves"

    def __init__(self, game_engine, **kwargs):
        super().__init__(game_engine, **kwargs)
        for filename in list_json_filenames(self.MAP_SAVE_DIR):
            display_name = os.path.splitext(filename)[0]
            path = os.path.join(self.MAP_SAVE_DIR, filename)
            self.buttons.insert(len(self.buttons) - 1, {
                "name": display_name,
                "callback": lambda p=path:self.start_game(p)
            })
        self.resize_object(x=self.x, y=self.y, width = self.w, height = self.h)

    def start_game(self, map_path):
        from game_screen import GameScreen
        engine = self.get_engine()
        main_menu = self.back_menu
        width, height = engine.screen.get_size()
        screen = GameScreen(engine, starting_process=main_menu, map_path=map_path, x=0, y=0, width=width, height=height)
        if main_menu is not None:
            main_menu._close_child()
        engine.add_process(screen)
        screen.switch_on()


=======
>>>>>>> c092d7d (fixed mapmenu bug)


# пока пустое, только кнопка назад от SubMenu
class SettingsMenu(SubMenu):
    pass


# главное меню, переключает дочерние меню через _open_child/_close_child
class MainMenu(Menu):

    def __init__(self, game_engine, **kwargs):
        super().__init__(game_engine, **kwargs)
        self.buttons.extend([
            {"name": "Новая игра", "callback": self.open_new_game},
            {"name": "Загрузить игру", "callback": self.open_load_game},
            {"name": "Map Maker", "callback": self.open_map_maker},
            {"name": "Настройки", "callback": self.open_settings},
        ])
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)
        self._child_menu = None

    def _open_child(self, menu_cls):
        if self._child_menu is not None:
            self._close_child()
        engine = self.get_engine()
        child = menu_cls(engine, back_menu=self, x=self.x, y=self.y, width=self.w, height=self.h)
        self._child_menu = child
        engine.add_process(child)
        # for process in engine.current_processes:
        #     print(type(process).__name__)
        child.switch_on()
        self.switch_off()

    def _close_child(self):
        if self._child_menu is not None:
            print("close child")
            engine = self.get_engine()
            self._child_menu.switch_off()
            processes = engine.get_processes()
            if self._child_menu in processes:
                processes.remove(self._child_menu)
            self._child_menu = None

    def return_from_child(self):
        self._close_child()
        self.switch_on()

    def open_new_game(self):
        self._open_child(NewGameMapMenu)

    def open_load_game(self):
        self._open_child(LoadGameMenu)

    def open_map_maker(self):
        print("pressed")
        try:
            self._open_child(MapMakerMenu)
        except:
            import traceback
            traceback.print_exc()

    def open_settings(self):
        self._open_child(SettingsMenu)