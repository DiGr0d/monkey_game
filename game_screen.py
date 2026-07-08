import pygame

class GameScreen:

    #черновик игрового экрана

    STATUS_BAR_HEIGHT_RATIO = 0.08
    RIGHT_PANEL_WIDTH_RATIO = 0.25

    def __init__(self, game_engine, starting_process=None, map_path=None, **kwargs):
        self.game_engine = game_engine
        self.starting_process = starting_process
        self.map_path = map_path
        self.works = True

        width, height = game_engine.screen.get_size()
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.w = kwargs.get("width", width)
        self.h = kwargs.get("height", height)

        self._context_panel_label = None
        self._build_layout()

    def _build_layout(self):
        status_bar_h = int(self.h * self.STATUS_BAR_HEIGHT_RATIO)
        right_panel_w = int(self.w * self.RIGHT_PANEL_WIDTH_RATIO)

        self.field_rect = pygame.Rect(self.x, self.y + status_bar_h, self.w - right_panel_w, self.h - status_bar_h)
        self.status_bar_rect = pygame.Rect(self.x, self.y, self.w - status_bar_h, status_bar_h)
        self.exit_rect = pygame.Rect(self.x + self.w - status_bar_h, self.y, status_bar_h, status_bar_h)
        self.settings_rect = pygame.Rect(self.x + self.w - right_panel_w / 3, self.y + self.h - status_bar_h, right_panel_w / 3 + 1, status_bar_h)
        self.right_panel_rect = pygame.Rect(self.x + self.w - right_panel_w, self.y + status_bar_h, right_panel_w, self.h - status_bar_h - status_bar_h)
        self.save_rect = pygame.Rect(self.x + self.w - (right_panel_w / 3) * 2, self.y + self.h - status_bar_h, right_panel_w / 3 + 1, status_bar_h)
        self.pause_rect = pygame.Rect(self.x + self.w - right_panel_w, self.y + self.h - status_bar_h, right_panel_w / 3, status_bar_h)

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
        icon_font = pygame.font.Font(None, 46)

        def draw(rect, color, label, label_font=font):
            pygame.draw.rect(scr, color, rect)
            pygame.draw.rect(scr, self.game_engine.BLACK, rect, 1)
            if label:
                surf = font.render(label, True, self.game_engine.BLACK)
                scr.blit(surf, surf.get_rect(center=rect.center))

        draw(self.field_rect, self.game_engine.BLUE, "Game field")
        draw(self.status_bar_rect, self.game_engine.GRAY, "Status-bar")
        draw(self.exit_rect, (240, 150, 150), "X", icon_font)
        draw(self.settings_rect, (200, 200, 240), "*", icon_font)
        draw(self.right_panel_rect, (250, 240, 180) if self._context_panel_label else (230, 230, 230), self._context_panel_label)
        draw(self.save_rect, (200, 200, 240), "S", icon_font)
        draw(self.pause_rect, (200, 200, 240), "P", icon_font)


    def process_event(self, event):
        if not self.works:
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos

        if self.field_rect.collidepoint(pos):
            # позже будет либо выбор башни, либо инфа об объекте
            self._context_panel_label = "Выбор башни/инфа"
            return
        if self.exit_rect.collidepoint(pos):
            self._exit()
            return
        if self.settings_rect.collidepoint(pos):
            print("Настройки: пока не реализовано")
            return
        if self.right_panel_rect.collidepoint(pos):
            return
        self._context_panel_label = None

    def _exit(self):
        #позже добавить подтверждение выхода
        engine = self.game_engine
        processes = engine.get_processes()
        if self in processes:
            processes.remove(self)
        if self.starting_process is not None:
            self.starting_process.switch_on()
