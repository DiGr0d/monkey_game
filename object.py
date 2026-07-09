from path_find import a_star
import pygame
import math
import image_loader
from functools import lru_cache

class Cell:
    def __init__(self, x, y, walkable=True, weight=1):
        self.x = x
        self.y = y
        self.walkable = walkable
        if not walkable:
            self.weight = 100000
        else:
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
        self.prev_health = health
        self.target = None      # целевая клетка (int, int) или None
        self.show_wid = 1.0 # ширина показываемой части
        self.show_hei  = 1.0# высота показваемой части
    
    def set_size(self, sz):
        self.show_wid, self.show_hei = sz

    def take_damage(self, damage):
        self.prev_health = self.health
        """Уменьшает здоровье на указанное значение."""
        self.health -= damage

    def draw(self, canvas, x, y, tile_width, tile_height):
        """Базовый метод отрисовки (переопределяется в наследниках)."""
        pass

class Mob(GameObject):
    def __init__(self, grid, pos, speed=2.0, health=100):
        super().__init__(grid, pos, health)
        self.speed = speed
        self.path = []             # текущий маршрут (без стартовой клетки)
        self._accumulator = 0.0        # накопленное время для обновления пути
        self._attack_latency = 1.0
        self._attack_accumulator = 0.0
        self.damage = 10
        self._prev_target = None       # предыдущая цель для сравнения
        self.mobAnimation = image_loader.mobAnimation()
        self.changed_anim_state = False
        self.show_wid = 3.0
        self.show_hei = 3.0
        
    @lru_cache(maxsize=100)
    def path_cost(self, sx, sy, gx, gy):
        cost = a_star(self.grid, (sx, sy), (gx, gy), return_cost=True)
        return cost

    def find_target(self, enemies):
        """Выбирает врага, путь до которого (по A*) имеет наименьшую стоимость."""
        if not enemies:
            self.target = None
            return

        start = (round(self.pos[0]), round(self.pos[1]))
        best_enemy = None
        best_cost = float('inf')

        for enemy in enemies:
            if enemy is self:
                continue
            goal = (round(enemy.pos[0]), round(enemy.pos[1]))
            cost = self.path_cost(*start, *goal)
            if cost < best_cost:
                best_cost = cost
                best_enemy = enemy

        self.target = best_enemy

    def pathfind(self):
        """Пересчитывает путь от текущей позиции до self.target с помощью A*."""
        if self.target is None:
            self.path = []
            return
        start = (round(self.pos[0]), round(self.pos[1]))
        goal = (round(self.target.pos[0]), round(self.target.pos[1]))
        full_path = a_star(self.grid, start, goal)   # функция из pathfinding.py
        if not full_path:
            self.path = []
        else:
            self.path = full_path[1:]   # убираем стартовую клетку

    def distance_to(self, pos):
        sx, sy = self.pos
        otherx, othery = pos
        dx, dy =  otherx - sx, othery - sy
        return (dx**2 + dy**2)**0.5

    def collides_with_target(self):
        if not self.target:
            return False
        otx, oty = self.target.pos
        otw, oth = self.target.show_wid, self.target.show_hei
        otx1, oty1 = otw + otx, oty + oth
        sx, sy = self.pos
        sw, sh = self.show_wid, self.show_hei
        sx1, sy1 = sx + sw, sy + sh
        if sx1 < otx:
            return False
        if sx > otx1:
            return False
        if sy1 < oty:
            return False
        if sy > oty1:
            return False
        return True   

    def do_work(self, dt):
        if not self.target:
            return
        if (not self.path) or self.distance_to(self.target.pos) < min(self.target.show_wid, self.target.show_hei) or self.collides_with_target():
           if (not self.changed_anim_state):
               self.mobAnimation.set_state(image_loader.MobState.ATTACKS, dt)
               tx, ty = self.target.pos
               x, y = self.pos
               dx, dy = tx - x, ty - y
               self.mobAnimation.update_facing((dx, dy)) 
           if self._attack_accumulator > self._attack_latency:
               self.attack(self.target) 
               self._attack_accumulator = 0
           else:
               self._attack_accumulator += dt
        else:
            if (not self.changed_anim_state):
               self.mobAnimation.set_state(image_loader.MobState.MOVES, dt)
            self.move(dt)

    def attack(self, target):
        target.take_damage(self.damage)

    def move(self, dt):
        """Плавное движение по маршруту (вызывается каждый кадр)."""
        if not self.path:
            return
        target_cell = self.path[0]
        target_pos = (target_cell[0] + 0.5, target_cell[1] + 0.5)
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        self.mobAnimation.update_facing((dx, dy))
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
        if self.prev_health != self.prev_health:
            self.mobAnimation.set_state(image_loader.MobState.DAMAGED, dt)
            self.changed_anim_state = True
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
        self.do_work(dt)
    def draw(self, canvas, scrx, scry, tile_width, tile_height):
        px, py = self.pos
        wid, hei = self.show_wid, self.show_hei
        sw = wid * tile_width
        sh = hei * tile_height
        
        offset_x = (tile_width - sw) / 2
        offset_y = (tile_height - sh) / 2 # возможно лучше чтобы 
        #отрисовывался начиная с центар, но тогда может быть атака будет выглядеть криво
        
        x = scrx + tile_width * px #+ offset_x
        y = scry + tile_height * py #+ offset_y
        
        canvas.blit(self.mobAnimation.get_animation(sw, sh), (x, y))
        

# ------------------------------------------------------------
# Класс башни (наследуется от GameObject)
# ------------------------------------------------------------
class Tower(GameObject):
    def __init__(self, grid, pos, range_radius=3.0):
        super().__init__(grid, pos)
        self.range = range_radius   # радиус атаки в клетках
        self.health = 20

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
        x = scrx + tile_width * px# - wid/2
        y = scry + tile_height * py #- hei/2
        # offset_x = (tile_width - sw) / 2
        # offset_y = (tile_height - sh) / 2
        
        # x = scrx + tile_width * px + offset_x
        # y = scry + tile_height * py 
        #print(self.health)
        #pygame.draw.rect(canvas, (0,0,255), (x, y, wid, hei))
        pygame.draw.rect(canvas, (0,0,255), (x, y, sw, sh))
    

