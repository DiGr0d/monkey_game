import object
import random
import game

class MapGrid:
    def __init__(self, GameGrid):
        self.field = GameGrid.get_field()
        self.width, self.height = GameGrid.get_size_in_tiles()
    def get_size(self):
        return(self.width, self.height)

def GridFromMapGrid(MapGrid):
    w, h = MapGrid.get_size()
    new_grid = object.Grid(w*4, h*4)
    for y in range(h*4):
        for x in range(w*4):
            mx, my = x//4, y//4
            walkable = MapGrid.field[my][mx].is_walkable()
            new_grid.cells[x][y] = object.Cell(x, y, walkable)
    return new_grid


class Game:
    WAVE_COOLDOWN = 20.0
    SPAWNPOINT_RADIUS = 5
    def __init__(self, parent, rel_x, rel_y, rel_w, rel_h, mapGrid=None, **kwargs):
        self.grid = GridFromMapGrid(mapGrid)
        self.mapGrid = mapGrid  
        if "spawnpoint" in kwargs:
            self.spawnpoint = kwargs["spawnpoint"]
        else:
            self.spawnpoint = self.find_spawnpoint() 
        self.wave_number = 1
        self.wave_cooldown_accumulator = self.WAVE_COOLDOWN
        self.parent = parent
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.rel_w = rel_w
        self.rel_h = rel_h
        self.mobs = []
        self.towers = []

    def spawn_wave(self):
        self.wave_number += 1
        spx, spy = self.spawnpoint
        x, y = max(0, spx), max(0, spy)
        wid, hei = (Game.SPAWNPOINT_RADIUS * 2 for _ in range(2))
        for _ in range(self.wave_number):
            i = random.randint(y, y + hei - 1)
            j = random.randint(x, x + wid - 1) 
            self.spawn_mob(j, i)

    def spawn_mob(self, x, y):
        self.add_mob(object.Mob(self.grid, (x, y)))
        

    def find_spawnpoint(self):
        for i in range(self.grid.height):
            for j in range(self.grid.width):
                if self.grid.is_walkable(j, i):
                    return (j, i)

    def get_pos(self):
        return (self.rel_x, self.rel_y)
    def get_size(self):
        return (self.rel_w, self.rel_h)
    
    def add_mob(self, mob):
        self.mobs.append(mob)

    def add_tower(self, tower):
        self.towers.append(tower)

    def update(self, dt):
        self.wave_cooldown_accumulator-=dt
        if self.wave_cooldown_accumulator <= 0:
            self.wave_cooldown_accumulator = Game.WAVE_COOLDOWN
            self.spawn_wave()
        # 1) Обновляем всех мобов (передаём им список всех мобов как потенциальных врагов)
        for mob in self.mobs:
            mob.update(dt, self.towers)

        # 2) Удаляем мёртвых мобов (health <= 0)
        self.mobs = [mob for mob in self.mobs if mob.health > 0]

        # 3) Обновляем башни (если у них есть свой update)
        for tower in self.towers:
            if hasattr(tower, 'update'):
                tower.update(dt, self.mobs)   # можно передавать мобов для стрельбы
        self.towers = [tower for tower in self.towers if tower.health > 0]

    def ShowMapGrid(self, canvas, parx, pary, tw, th):
        gr_x, gr_y = parx, pary
        in_t_width, in_t_height = self.mapGrid.get_size()
        for i in range(in_t_height):
            for j in range(in_t_width):
                x = gr_x + j * tw
                y = gr_y + i * th
                self.mapGrid.field
                self.mapGrid.field[i][j].fill(x, y, tw+1, th+1, canvas)

    def show(self):
        """Отрисовка: сначала карта, потом объекты."""
        
        parx, pary = self.parent.get_pos()
        parw, parh = self.parent.get_size()
        sx, sy = self.get_pos()
        parx, pary = parx + parw * sx, pary + parh * sy

        canvas = self.parent.game_engine.screen
        grw, grh = self.mapGrid.get_size()
        map_tile_width = self.rel_w * parw / grw
        map_tile_height = self.rel_h * parh / grh
        #print(map_tile_width, map_tile_height)
        self.ShowMapGrid(canvas, parx, pary, map_tile_width, map_tile_height)

        tile_width = self.rel_w * parw / self.grid.width
        tile_height = self.rel_h * parh / self.grid.height

        for mob in self.mobs:
            #screen_x = self.rel_x + (mob.pos[0] + 0.5) * tile_width
            #screen_y = self.rel_y + (mob.pos[1] + 0.5) * tile_height
            mob.draw(canvas, parx, pary, tile_width, tile_height)

        for tower in self.towers:
            #screen_x = self.rel_x + (tower.pos[0] + 0.5) * tile_width
            #screen_y = self.rel_y + (tower.pos[1] + 0.5) * tile_height
            tower.draw(canvas, parx, pary, tile_width, tile_height)