import pygame
import game
import game2
import object
import menu
import game_widget

class GameScreen:

    #черновик игрового экрана

    STATUS_BAR_HEIGHT_RATIO = 0.08
    RIGHT_PANEL_WIDTH_RATIO = 0.25
    GAME_PANEL_WIDTH_RATIO = 1 - RIGHT_PANEL_WIDTH_RATIO
    GAME_PANEL_HEIGHT_RATIO = 1 - STATUS_BAR_HEIGHT_RATIO * 2
    GAME_PANEL_X = 0
    GAME_PANEL_Y = STATUS_BAR_HEIGHT_RATIO

    def __init__(self, game_engine, starting_process=None, map_path=None, **kwargs):
        self.game_engine = game_engine
        self.starting_process = starting_process
        self.map_path = map_path
        grid = game2.MapGrid(game.GameGrid.load_from_file(map_path, game_engine, x=0, y=0, w=1, h=1))
        self.game = game2.Game(self, 0, self.STATUS_BAR_HEIGHT_RATIO, self.GAME_PANEL_WIDTH_RATIO, self.GAME_PANEL_HEIGHT_RATIO, mapGrid=grid)
        self.game.add_mob(object.Mob(self.game.grid, (1, 1)))
        #self.game.add_tower(object.Tower(self.game.grid, (10, 10)))
        #self.game.add_tower(object.Tower(self.game.grid, (15, 15)))
        #self.game.add_tower(object.Tower(self.game.grid, (12, 33)))
        self.game.add_tower(object.FireTower(self.game.grid, (13, 13)))
        self.game.add_tower(object.IceTower(self.game.grid, (20, 20)))
        self.game.add_tower(object.WallTower(self.game.grid, (10, 13)))
        self.works = True

        width, height = game_engine.screen.get_size()
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.w = kwargs.get("width", width)
        self.h = kwargs.get("height", height)

        self._context_panel_label = None
        self._build_layout()
        self.select_tower_menu = None

    def _build_layout(self):
        status_bar_h = int(self.h * self.STATUS_BAR_HEIGHT_RATIO)
        right_panel_w = int(self.w * self.RIGHT_PANEL_WIDTH_RATIO)

        self.field_rect = pygame.Rect(self.x, self.y + status_bar_h, self.w - right_panel_w, self.h - status_bar_h * 2)
        self.status_bar_rect = pygame.Rect(self.x, self.y, self.w - status_bar_h, status_bar_h)
        self.exit_rect = pygame.Rect(self.x + self.w - status_bar_h, self.y, status_bar_h, status_bar_h)
        self.settings_rect = pygame.Rect(self.x + self.w - right_panel_w / 3, self.y + self.h - status_bar_h, right_panel_w / 3 + 1, status_bar_h)
        self.right_panel_rect = pygame.Rect(self.x + self.w - right_panel_w, self.y + status_bar_h, right_panel_w, self.h - status_bar_h - status_bar_h)
        self.save_rect = pygame.Rect(self.x + self.w - (right_panel_w / 3) * 2, self.y + self.h - status_bar_h, right_panel_w / 3 + 1, status_bar_h)
        self.pause_rect = pygame.Rect(self.x + self.w - right_panel_w, self.y + self.h - status_bar_h, right_panel_w / 3, status_bar_h)
        self.name_rect = pygame.Rect(self.x, self.y + self.h - status_bar_h, self.w - right_panel_w, status_bar_h)

    def switch_on(self):
        self.works = True

    def switch_off(self):
        self.works = False

    def get_pos(self):
        return (self.x, self.y)
    
    def get_size(self):
        return (self.w, self.h)
    
    def update_geometry(self, screen_width, screen_height):
        self.w, self.h = screen_width, screen_height
        self._build_layout()

    def show(self):
        if not self.works:
            return
        scr = self.game_engine.screen
        font = pygame.font.Font(None, 28)
        icon_font = pygame.font.Font(None, 80)

        def draw(rect, color, label, label_font=font):
            pygame.draw.rect(scr, color, rect)
            pygame.draw.rect(scr, self.game_engine.BLACK, rect, 1)
            if label:
                surf = label_font.render(label, True, self.game_engine.BLACK)
                scr.blit(surf, surf.get_rect(center=rect.center))

        #draw(self.field_rect, self.game_engine.BLUE, "Game field")
        self.game.show()
        draw(self.status_bar_rect, self.game_engine.GRAY, "Status-bar")
        draw(self.exit_rect, (240, 150, 150), "X", icon_font)
        draw(self.settings_rect, (200, 200, 240), "*", icon_font)
        draw(self.right_panel_rect, (250, 240, 180) if self._context_panel_label else (230, 230, 230), self._context_panel_label)
        draw(self.save_rect, (200, 200, 240), "S", icon_font)
        draw(self.pause_rect, (200, 200, 240), "P", icon_font)
        draw(self.name_rect, self.game_engine.BLUE, "Tower Defence")
        if self.select_tower_menu:
            self.select_tower_menu.show()

    def update_game(self, dt):
        if self.works and self.game:
            self.game.update(dt)

    def process_event(self, event, **kwargs):
        if not self.works:
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos

        if self.field_rect.collidepoint(pos):
            tw, th = self.game.grid.width, self.game.grid.height
            def get_object_rect(mob):
                grx, gry = mob.pos
                grx /= tw
                gry /= th
                grw, grh = mob.show_wid, mob.show_hei
                grw /= tw
                grh /= th
                mx, my = self.field_rect.x, self.field_rect.y
                mw, mh = self.field_rect.size
                x, y = mx + grx*mw, my + gry*mh
                w, h = grw*mw, grh*mh
                return pygame.Rect(x, y, w, h)
            def get_tile_by_pos(pos):
                x, y = pos
                mw, mh = self.field_rect.size
                mx, my = self.field_rect.x, self.field_rect.y
                tile_w, tile_h = mw / tw, mh / th
                first = int((x - mx) / tile_w)
                second = int((y - my) / tile_h)
                return (first, second)
            
            object_clicked = False
            mobs = self.game.mobs
            towers = self.game.towers
            
            for mob in mobs:
                mob_rect = get_object_rect(mob)
                if mob_rect.collidepoint(pos):
                    self.select_tower_menu = None
                    object_clicked = True
                    self._context_panel_label = f"mob hp: {int(mob.health)}"
            if not object_clicked:
                for tower in towers:
                    tower_rect = get_object_rect(tower)
                    if tower_rect.collidepoint(pos):
                        self.select_tower_menu = None
                        object_clicked = True
                        self._context_panel_label = f"tower hp: {tower.health}"
            if not object_clicked:
                relx, rely  = GameScreen.GAME_PANEL_X + GameScreen.GAME_PANEL_WIDTH_RATIO, GameScreen.GAME_PANEL_Y
                relw, relh = GameScreen.RIGHT_PANEL_WIDTH_RATIO, GameScreen.GAME_PANEL_HEIGHT_RATIO
                t_x, t_y = get_tile_by_pos(pos)
                t_x //= 4
                t_y //= 4
                if self.game.mapGrid.field[t_y][t_x].tile_type() == game.TileTypes.ROCK:
                    object_clicked = True
                    self.select_tower_menu = None
                    self._context_panel_label = "Гора"
                if not object_clicked:
                    object_clicked = True
                    self.select_tower_menu = select_tower_menu(relx, rely, relw, relh, get_tile_by_pos(pos), self)
                    self.select_tower_menu.switch_on()
            if not object_clicked:
                self.select_tower_menu = None
                self._context_panel_label = "Выбор башни/инфа"
            return
        if self.exit_rect.collidepoint(pos):
            self._exit()
            return
        if self.settings_rect.collidepoint(pos):
            print("Настройки: пока не реализовано")
            return
        if self.right_panel_rect.collidepoint(pos):
            if self.select_tower_menu:
                callback = self.select_tower_menu.process_click(pos)
                if callback:
                    callback()
            return
        if self.save_rect.collidepoint(pos):
            print("Сохранение: пока не реализовано")
            return
        if self.pause_rect.collidepoint(pos):
            print("Пауза: пока не реализовано")
            return
        self._context_panel_label = None

    def _exit(self):
        engine = self.game_engine
        self.switch_off()
        processes = engine.get_processes()
        if self in processes:
            processes.remove(self)
        if self.starting_process is not None:
            width, height = engine.screen.get_size()
            self.starting_process.switch_on()
            self.starting_process.update_geometry(width, height)


class select_tower_menu(menu.Menu):
    def __init__(self, relx, rely, relw, relh, cur_tile, parent):
        super().__init__(parent.game_engine)
        self.rel_x = relx
        self.rel_y = rely
        self.rel_w = relw
        self.rel_h = relh
        self.game = parent.game
        self.buttons = [{"name": "Tower", "callback": lambda: self.add_tower()},
                        {"name": "FireTower", "callback": lambda: self.add_firetower()},
                        {"name": "IceTower", "callback": lambda: self.add_icetower()},
                        {"name": "WallTower", "callback": lambda: self.add_walltower()}]
        self.cur_tile = cur_tile
        self.update_geometry(*parent.game_engine.screen.get_size())
        

    def add_tower(self):
        self.game.add_tower(object.Tower(self.game.grid, self.cur_tile))

    def add_firetower(self):
        self.game.add_tower(object.FireTower(self.game.grid, self.cur_tile))

    def add_icetower(self):
        self.game.add_tower(object.IceTower(self.game.grid, self.cur_tile))

    def add_walltower(self):
        self.game.add_tower(object.WallTower(self.game.grid, self.cur_tile))

    def show(self):
        self.update_geometry(*self.game_engine.screen.get_size())
        super().show()
