import pygame
import game2
import game

class GameWidget:
    def __init__(self, game_engine, **kwargs):
        """
        :param game_engine: объект, содержащий screen и, возможно, цвета
        :param game: экземпляр класса Game с методами update(dt) и show()
        :param kwargs: x, y, width, height (в пикселях) для начального размещения
        """
        self.screen = game_engine.screen
        self.game = game2.Game(self, 0, 0, 1, 1, mapGrid=game2.MapGrid(game.GameGrid(t_width=10, t_height=10, game_engine=self, x=0,y=0,w=game_engine.SCREEN_WIDTH,h=game_engine.SCREEN_HEIGHT)))
        self.works = False          # включён ли виджет (отображается и обновляется)
        self.game_engine = game_engine

        width, height = game_engine.screen.get_size()
        self.x, self.y = kwargs.get("x", 0), kwargs.get("y", 0)
        self.w, self.h = kwargs.get("width", width), kwargs.get("height", height)

        # относительные координаты для масштабирования
        self.rel_x = self.x / width if width else 0
        self.rel_y = self.y / height if height else 0
        self.rel_w = self.w / width if width else 0
        self.rel_h = self.h / height if height else 0

        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    # ---------- Геометрия (аналогично Menu) ----------
    def resize_object(self, **kwargs):
        """Обновляет абсолютные координаты и размеры, применяя ограничения экрана."""
        width, height = self.game_engine.screen.get_size()
        x = kwargs.get("x", self.x)
        y = kwargs.get("y", self.y)
        w = kwargs.get("width", self.w)
        h = kwargs.get("height", self.h)

        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError("x or y out of screen bounds in resize_object")
        if w < 0 or h < 0:
            raise ValueError("width/height cannot be negative")

        if x + w > width:
            w = width - x
        if y + h > height:
            h = height - y

        self.x, self.y, self.w, self.h = x, y, w, h

        # Если ваш Game имеет метод для обновления своей области, раскомментируйте:
        # if hasattr(self.game, 'set_rect'):
        #     self.game.set_rect(self.x, self.y, self.w, self.h)

    def update_geometry(self, screen_width, screen_height):
        """Вызывается при изменении размера окна для пересчёта позиции/размера."""
        if not self.works:
            return
        if self.w < 10:
            self.w = 10
        if self.h < 10:
            self.h = 10

        self.x = int(self.rel_x * screen_width)
        self.y = int(self.rel_y * screen_height)
        self.w = int(self.rel_w * screen_width)
        self.h = int(self.rel_h * screen_height)

        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def scale(self, **kwargs):
        """Масштабирует виджет (опционально и позицию)."""
        resize_pos = kwargs.get("pos_too", False)
        scale_x, scale_y = kwargs.get("scale_x", 1), kwargs.get("scale_y", 1)

        self.w *= scale_x
        self.h *= scale_y
        if resize_pos:
            self.x *= scale_x
            self.y *= scale_y

        screen_w, screen_h = self.game_engine.screen.get_size()
        self.rel_x = self.x / screen_w if screen_w else 0
        self.rel_y = self.y / screen_h if screen_h else 0
        self.rel_w = self.w / screen_w if screen_w else 0
        self.rel_h = self.h / screen_h if screen_h else 0

        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)

    def get_pos(self):
        return (self.x, self.y)

    def get_size(self):
        return (self.w, self.h)

    def get_engine(self):
        return self.game_engine

    def switch_on(self):
        self.works = True

    def switch_off(self):
        self.works = False

    def update(self, dt):
        """Вызывается каждый кадр, передаёт dt внутрь Game."""
        if self.works and self.game:
            self.game.update(dt)

    def show(self):
        """Отрисовывает Game, если виджет активен и имеет положительные размеры."""
        if not self.works:
            return
        if self.w <= 0 or self.h <= 0:
            return
        if self.game:
            self.game.show()

    def process_event(self, event):
        if not self.works:
            return
        if self.game and hasattr(self.game, 'handle_event'):
            self.game.handle_event(event)

    def add_mob(self, mob):
        self.game.mobs.append(mob)

    def add_tower(self, tower):
        self.game.towers.append(tower)