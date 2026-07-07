# mob.py
from path_find import a_star
import pygame
import math

class Cell:
    def __init__(self, x, y, walkable=True, weight=1):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.weight = weight
        
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[x][y].walkable
        return False

    def get_neighbors(self, x, y, allow_diagonal=True):
        """Возвращает список соседних координат (до 8 направлений)."""
        neighbors = []
        directions = [(-1,0),(1,0),(0,-1),(0,1)]  # 4 направления
        if allow_diagonal:
            directions += [(-1,-1),(-1,1),(1,-1),(1,1)]  # диагонали
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                # Проверка на "срезание углов" – нельзя проходить по диагонали между двумя стенами.
                # Если это диагональ, проверяем, что обе соседние клетки (по горизонтали и вертикали) проходимы.
                if dx != 0 and dy != 0:
                    if not (self.is_walkable(x + dx, y) and self.is_walkable(x, y + dy)):
                        continue
                neighbors.append((nx, ny))
        return neighbors


class GameObject:
    def __init__(self, grid, pos, health=100):
        self.grid = grid
        self.pos = pos          # (float, float) – координаты в клетках
        self.health = health    # текущее здоровье
        self.target = None      # целевая клетка (int, int) или None
        self.show_wid = 0.5 # ширина показываемой части
        self.show_hei  = 0.5# высота показваемой части

    def take_damage(self, damage):
        """Уменьшает здоровье на указанное значение."""
        self.health -= damage

    def draw(self, canvas, x, y, tile_width, tile_height):
        """Базовый метод отрисовки (переопределяется в наследниках)."""
        pass

class Mob(GameObject):
    def __init__(self, grid, pos, speed=2.0, health=100):
        super().__init__(grid, pos, health)
        self.speed = speed
        self.path = []                 # текущий маршрут (без стартовой клетки)
        self._accumulator = 0.0        # накопленное время для обновления пути
        self._prev_target = None       # предыдущая цель для сравнения

    def find_target(self, enemies):
        """Выбирает ближайшего врага (исключая себя) и сохраняет его клетку как цель."""
        if not enemies:
            self.target = None
            return
        # Исключаем самого себя из списка
        others = [e for e in enemies if e is not self]
        if not others:
            self.target = None
            return
        nearest = min(others, key=lambda e: (e.pos[0]-self.pos[0])**2 + (e.pos[1]-self.pos[1])**2)
        self.target = (round(nearest.pos[0]), round(nearest.pos[1]))

    def pathfind(self):
        """Пересчитывает путь от текущей позиции до self.target с помощью A*."""
        if self.target is None:
            self.path = []
            return
        start = (round(self.pos[0]), round(self.pos[1]))
        goal = self.target
        full_path = a_star(self.grid, start, goal)   # функция из pathfinding.py
        if not full_path:
            self.path = []
        else:
            self.path = full_path[1:]   # убираем стартовую клетку

    def move(self, dt):
        """Плавное движение по маршруту (вызывается каждый кадр)."""
        if not self.path:
            return
        target_cell = self.path[0]
        target_pos = (target_cell[0] + 0.5, target_cell[1] + 0.5)
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        distance = math.hypot(dx, dy)
        if distance < 0.001:
            self.pos = target_pos
            self.path.pop(0)
            return
        step = self.speed * dt
        if step >= distance:
            self.pos = target_pos
            self.path.pop(0)
        else:
            self.pos = (self.pos[0] + dx / distance * step,
                        self.pos[1] + dy / distance * step)

    def update(self, dt, enemies):
        """
        Обновление моба:
        - раз в секунду ищет новую цель и пересчитывает путь (если цель изменилась или путь пуст);
        - каждый кадр двигается по текущему маршруту.
        """
        self._accumulator += dt
        if self._accumulator >= 1.0:
            self._accumulator = 0.0
            # 1) обновляем цель
            self.find_target(enemies)
            # 2) если цель изменилась или маршрут пуст – пересчитываем путь
            if self.target != self._prev_target or not self.path:
                self.pathfind()
                self._prev_target = self.target
        # движение выполняется каждый кадр
        self.move(dt)
    def draw(self, canvas, scrx, scry, tile_width, tile_height):
        px, py = self.pos
        wid, hei = self.show_wid, self.show_hei
        sw = self.show_wid * tile_width
        sh = self.show_hei * tile_height
        x = scrx + tile_width * px - wid/2
        y = scry + tile_height * py - hei/2
        pygame.draw.rect(canvas, (255,0,0), (x, y, sw, sh))
        

# ------------------------------------------------------------
# Класс башни (наследуется от GameObject)
# ------------------------------------------------------------
class Tower(GameObject):
    def __init__(self, grid, pos, range_radius=3.0):
        super().__init__(grid, pos)
        self.range = range_radius   # радиус атаки в клетках

    def shoot(self, target):
        """
        Заглушка для атаки по цели.
        target – объект (например, моб), по которому стреляем.
        """
        # Здесь будет логика выстрела
        pass

    def draw(self, canvas, scrx, scry, tile_width, tile_height):
        px, py = self.pos
        wid, hei = self.show_wid, self.show_hei
        sw = self.show_wid * tile_width
        sh = self.show_hei * tile_height
        x = scrx + tile_width * px - wid/2
        y = scry + tile_height * py - hei/2
        print(x, y, wid, hei)
        #pygame.draw.rect(canvas, (0,0,255), (x, y, wid, hei))
        pygame.draw.rect(canvas, (0,0,255), (x, y, sw, sh))
    