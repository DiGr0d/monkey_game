import pygame
import menu
import json
import os
import time
from enum import Enum

def d_game():
    pass

# Кеш для загруженных изображений
_tile_images = {}

def load_tile_images():
    global _tile_images
    for tile_type, path in TileImagePath.path.items():
        if path is not None:
            try:
                _tile_images[tile_type] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(f"Не удалось загрузить {path}: {e}")
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                _tile_images[tile_type] = surf
        else:
            _tile_images[tile_type] = None

# Oxy , where (0, 0) in upper left corner and Oy looks donward
#Tile <- GameTile <- (GrassTile, RockTile and etc...)
class Tile:
    name = "tile"
    def __init__(self, grid, x, y, **kwargs):
        if not all(isinstance(coord, int) for coord in (x, y)):
            raise ValueError("x and y mast be integers in Tile")
        self.type = "undefined"
        self.x = x
        self.y = y
        self.grid = grid
        #grid.get_field()[y][x] = self

    def get_grid(self):
        return self.grid

    def get_pos(self):
        return(self.x, self.y)

    def set_pos(self, pos):
        g_w, g_h = self.grid.get_size_in_tiles()
        x, y = pos
        if not (0 <= x < g_w and 0 <= y < g_h):
            raise ValueError("x and y must be in grid_tile_sizes Tile.set_pos")
        self.x, self.y = x, y
        
class TileTypes(Enum):
        UNDEFINED = 0
        GRASS = 1
        ROCK = 2

class TileImagePath:
    path = {TileTypes.UNDEFINED: None, 
            TileTypes.GRASS: "images/grass_image.png",
            TileTypes.ROCK: "images/rock_image.png"}

class GameTile(Tile):
    def __init__(self, grid, x, y, **kwargs):
        super().__init__(grid, x, y, **kwargs)
        self.is_empty = True
        self.mobs = {}
        self.facing = 0
        self.scaled_image = None 

    def get_image(self):
        return self.image() 

    def image(self):
        tile_type = self.tile_type()
        img = _tile_images.get(tile_type)
        if img is None:
            raise ValueError(f"No loaded image for tile type {tile_type}")
        return img

    def rotate(self):
        self.facing += 1
        self.facing &= 3

    def update_scale(self, tile_w, tile_h):
        if tile_w <= 0 or tile_h <= 0:
            self.scaled_image = None
            return
        original = self.get_image()
        self.scaled_image = pygame.transform.scale(original, (int(tile_w), int(tile_h)))

    def fill(self, px, py, pw, ph, screen):
        if pw <= 0 or ph <= 0:
            return
        
        if (self.scaled_image is None or 
            self.scaled_image.get_width() != pw or 
            self.scaled_image.get_height() != ph):
            self.update_scale(pw, ph)

        if self.scaled_image is None:
            return

        screen.blit(self.scaled_image, (px, py))

    def add_mob(self):
        pass

class GrassTile(GameTile):
    def is_walkable(self):
        return True
    def is_flyable(self):
        return True
    def is_buildable(self):
        return True
    def tile_type(self):        
        return TileTypes.GRASS

class RockTile(GameTile):
    def is_walkable(self):
        return False
    def is_flyable(self):
        return True
    def is_buildable(self):
        return False
    def tile_type(self):     
        return TileTypes.ROCK
    
class TileFabric:
    @staticmethod
    def makeGrass(*args):
        return GrassTile(*args)
    @staticmethod
    def makeRock(*args):
        return RockTile(*args)
    @staticmethod
    def getTileImage(tile_type, param=None):
        if param:
            filename = f"images/{param}_{tile_type}.png"
        else:
            filename = f"images/{tile_type}.png"
        return pygame.image.load(filename)
    @staticmethod
    def getNewTile(str, *args):
        match str:
            case "grass":
                return TileFabric.makeGrass(*args)
            case "rock":
                return TileFabric.makeRock(*args)
            case _:
                print("Undefined type in TileFabric.getNewTile()")
                return None

class GameGrid:
    name = "Grid"

    def __init__(self, t_width, t_height, game_engine = None, x=0, y=0, w=100, h=100,  type="grass"):
        self.last_tile_size = (0, 0)
        self.field = [[TileFabric.getNewTile(type, self, j, i) for j in range(t_width)] for i in range(t_height)]
        self.selected = None
        if not game_engine:
            raise ValueError("no game engine in grid")
        self.t_width, self.t_height = t_width, t_height
        self.game_engine = game_engine
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rel_x, self.rel_y = self.x / w, self.y / h
        self.rel_w, self.rel_h = self.w / w, self.h / h
        self.tile_w, self.tile_h = 0, 0
        screen_w, screen_h = game_engine.screen.get_size()
        self.rel_x = self.x / screen_w if screen_w else 0
        self.rel_y = self.y / screen_h if screen_h else 0
        self.rel_w = self.w / screen_w if screen_w else 0
        self.rel_h = self.h / screen_h if screen_h else 0
        self.resize_object(self.x, self.y, self.w, self.h)

    def switch_on(self):
        pass
    
    def update_geometry(self, screen_width, screen_height):
        self.x = int(self.rel_x * screen_width)
        self.y = int(self.rel_y * screen_height)
        self.w = int(self.rel_w * screen_width)
        self.h = int(self.rel_h * screen_height)
        self.resize_object(self.x, self.y, self.w, self.h)

    def resize_object(self, x, y, width, height):
        screen = self.game_engine.screen
        scr_width, scr_height = screen.get_size()
        w, h = width, height

        if not (0 <= x <= scr_width and 0 <= y <= scr_height):
            raise ValueError("x or y out of screen bounds")
        if w <= 0 or h <= 0:
            raise ValueError("width/height must be positive")
        if x + w > scr_width:
            w = max(0, scr_width - x)
        if y + h > scr_height:
            h = max(0, scr_height - y)

        self.x, self.y = x, y

        t_width, t_height = self.get_size_in_tiles()

        tile_w = int(w / t_width)
        tile_h = int(h / t_height)

        if tile_w < 1:
            tile_w = 1
        if tile_h < 1:
            tile_h = 1

        #make grid smaller if it too big(to avoid black lines beetween tiles)
        self.w = tile_w * t_width
        self.h = tile_h * t_height

        if self.x + self.w > scr_width:
            self.w = scr_width - self.x
        if self.y + self.h > scr_height:
            self.h = scr_height - self.y
       
        self.tile_w = int(self.w / t_width)
        self.tile_h = int(self.h / t_height)

        # scaling only if size is changed
        if (self.tile_w, self.tile_h) != self.last_tile_size:
            self.last_tile_size = (self.tile_w, self.tile_h)
            for row in self.field:
                for tile in row:
                    if tile:
                        tile.update_scale(self.tile_w, self.tile_h)
        
    def get_size_in_tiles(self):
        return (self.t_width, self.t_height)
    
    def get_size(self):
        return(self.w, self.h)
    
    def get_position(self):
        return(self.x, self.y)
    
    def get_tile_size(self):
        return (self.tile_w, self.tile_h)

    def get_engine(self):
        return self.game_engine
    #returns a grid full of grass 10 X 10
    def get_default_grid(*args):
        return  GameGrid(10, 10, *args)
    
    def get_field(self):
        return self.field
    #may be I would do another events
    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            self.selected = self.clicked_tile(mouse_pos)

    def process_click(self, pos):
        self.selected = self.clicked_tile(pos)

    def clicked_tile(self, pos):
        if len(pos) != 2:
            raise ValueError("In menu class, process_click needs a tuple of two elements (x, y)")
        if not all(isinstance(a, int) for a in pos):
            raise ValueError("Every tuple element must be an integar in process_click function of menu class")
        
        x, y = pos
        gx, gy = self.get_position()
        gw, gh = self.get_size()
        tw, th = self.get_tile_size()
        
        x_landed = True if x > gx and x < gx + gw else False
        y_landed = True if y > gy and y < gy + gh else False

        if not (x_landed and y_landed):
            return None
        
        relx = x - gx
        rely = y - gy
        sw, sh = int(relx // tw), int(rely // th)
        clicked_tile = self.field[sh][sw]
        a, b = clicked_tile.get_pos()
        return clicked_tile
    
    def select(self, Tile):
        self.selected = Tile
    
    def get_selected(self):
        return self.selected

    def show(self):
        scr = self.game_engine.screen
        in_t_width, in_t_height = self.get_size_in_tiles()
        gr_x, gr_y = self.get_position()
        t_w, t_h = self.get_tile_size() 

        if t_w <= 0 or t_h <= 0:
            return

        for i in range(in_t_height):
            for j in range(in_t_width):
                x = gr_x + j * t_w
                y = gr_y + i * t_h
                self.field[i][j].fill(x, y, t_w, t_h, scr)

    def to_dict(self):
        return {
            "t_width": self.t_width,
            "t_height": self.t_height,
            "tiles": [
                [{"type": tile.tile_type().name, "facing": tile.facing} for tile in row]
                for row in self.field
            ]
        }   

    def load_from_dict(self, data):
        self.t_width = data["t_width"]
        self.t_height = data["t_height"]
        new_field = []
        for i, row in enumerate(data["tiles"]):
            new_row = []
            for j, tile_data in enumerate(row):
                tile = TileFabric.getNewTile(tile_data["type"].lower(), self, j, i)
                tile.facing = tile_data.get("facing", 0)
                new_row.append(tile)
            new_field.append(new_row)
        self.field = new_field
        self.last_tile_size = (0, 0)
        self.resize_object(self.x, self.y, self.w, self.h)  

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)    

    @classmethod
    def load_from_file(cls, path, game_engine, x=0, y=0, w=100, h=100):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        grid = cls(data["t_width"], data["t_height"], game_engine=game_engine, x=x, y=y, w=w, h=h)
        grid.load_from_dict(data)
        return grid


class TileMenu(menu.Menu):
    def __init__(self, Tile, Grid, game_engine, **kwargs):
        super().__init__(game_engine, **kwargs)  
        self.Tile = Tile
        self.Grid = Grid
        self.changed = False
        self.replace_menu = None

        self.buttons.extend([
            {"name": "rotate", "callback": self.rotate_tile},
            {"name": "replace", "callback": self.open_replace_menu}
        ])
        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)
        self.switch_on()

    def current_tile(self):
        return self.Tile

    def rotate_tile(self):
        self.Tile.rotate()   

    def select_tile(self, selected):
        if self.Tile == selected:
            return
        self.Tile = selected
        self.close_replace_menu()

    def close_replace_menu(self):
        if self.replace_menu is not None:
            self.replace_menu = None
            super().scale(scale_y=2)   

    def open_replace_menu(self):
        if self.replace_menu is not None:
            print("replace_menu already exists, returning")
            return
        x, y = self.get_pos()
        w, h = self.get_size()
        new_h = h / 2
        new_y = y + h / 2
        super().scale(scale_y=0.5) 
        kwargs = {"x": x, "y": new_y, "width": w, "height": new_h}
        eng = self.get_engine()
        self.replace_menu = ReplaceMenu(self.current_tile(), eng, parent_menu=self, **kwargs)
        self.replace_menu.switch_on()
    def show(self):
        super().show()
        if self.replace_menu:
            self.replace_menu.show()
    def process_click(self, pos):
        tx, ty = self.get_pos() 
        tw, th = self.get_size()
        rect = pygame.Rect(tx, ty, tw, th)
        if self.replace_menu and not rect.collidepoint(pos) :
           return self.replace_menu.process_click(pos)
        return super().process_click(pos)
        
# tile constructors gets (Grid , x , y, **kwargs)
# menu constructor gets game_engine and kwargs: x, y, width ,height
class ReplaceMenu(menu.Menu):
    def __init__(self,tile,  game_engine, parent_menu, **kwargs):
        super().__init__(game_engine, **kwargs)
        self.parent_menu = parent_menu
        self.tile = tile
        grid = tile.get_grid()
        x, y = grid.get_selected().get_pos()

        self.buttons.extend([
            {"name": "grass", "callback": lambda: self.replace_tile(TileFabric.makeGrass(grid, x, y))},
            {"name": "rock", "callback": lambda: self.replace_tile(TileFabric.makeRock(grid, x, y))}
        ])

        self.resize_object(x=self.x, y=self.y, width=self.w, height=self.h)
        self.switch_on()
        
    def replace_tile(self, new_tile):
        x, y = new_tile.get_pos()
        grid = self.tile.get_grid()
        grid.get_field()[y][x] = new_tile
        self.tile = new_tile
        self.close()

    def close(self):
        self.switch_off()
        engine = self.get_engine()
        if self in engine.get_processes():
            engine.get_processes().remove(self)
        if self.parent_menu:
            self.parent_menu.close_replace_menu()
    
    def show(self):
        #pygame.draw.rect(self.game_engine.screen, (255, 0, 0), (self.x, self.y, self.w, self.h))
        super().show() 

class MapMaker:
    def __init__(self, game_engine, starting_process, **kwargs):
        self.works = True
        self.game_engine = game_engine
        self.starting_process = starting_process
        self.objects = {}

        width, height = game_engine.screen.get_size()
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.w = kwargs.get("width", width)
        self.h = kwargs.get("height", height)

        exitmenu_height = self.h * 0.1
        grid_x = self.x
        grid_y = self.y + exitmenu_height
        grid_w = self.w
        grid_h = self.h - exitmenu_height

        exitmenu = menu.Menu(game_engine, x=self.x, y=self.y, width=self.w, height=exitmenu_height)
        exitmenu.buttons.append({"name": "exit", "callback": self.exit})
        exitmenu.buttons.append({"name": "save", "callback": self.save_map})
        exitmenu.resize_object(x=self.x, y=self.y, width=self.w, height=exitmenu_height)
        self.objects["exitmenu"] = exitmenu
        exitmenu.switch_on()

        load_path = kwargs.get("load_path")
        if load_path:
            grid = GameGrid.load_from_file(load_path, game_engine, x=grid_x, y=grid_y, w=grid_w, h=grid_h)
        else:
            grid = GameGrid(t_width=10, t_height=10, game_engine=game_engine, x=grid_x, y=grid_y, w=grid_w, h=grid_h)
        self.objects["grid"] = grid

        self.objects["tilemenu"] = None

        if starting_process:
            starting_process.switch_off()

        self.rel_x = self.x / width if width else 0
        self.rel_y = self.y / height if height else 0
        self.rel_w = self.w / width if width else 0
        self.rel_h = self.h / height if height else 0

        self.update_geometry(width, height)

    def exitmenu(self):
        return self.objects.get("exitmenu")

    def grid(self):
        return self.objects.get("grid")

    def tilemenu(self):
        return self.objects.get("tilemenu")

    def switch_on(self):
        self.works = True

    def switch_off(self):
        self.works = False
    
    def get_pos(self):
        return (self.x, self.y)
    
    def get_size(self):
        return (self.w, self.h)

    def open_tile_menu(self, selected):
        if self.tilemenu() is not None:
            self.close_tile_menu()

        exm = self.exitmenu()
        gr = self.grid()
        ex, ey = exm.get_pos()
        ew, eh = exm.get_size()
        gx, gy = gr.get_position()
        gw, gh = gr.get_size()

        new_grid_w = gw * 0.8
        gr.resize_object(x=gx, y=gy, width=new_grid_w, height=gh)

        tile_x = gx + new_grid_w
        tile_y = ey + eh
        tile_w = self.w - new_grid_w
        tile_h = self.h - eh

       
        tilemenu = TileMenu(selected, self.grid(), self.game_engine,
                            x=tile_x, y=tile_y, width=tile_w, height=tile_h)
        self.objects["tilemenu"] = tilemenu
        tilemenu.switch_on()

    def close_tile_menu(self):
        tilemenu = self.tilemenu()
        if tilemenu is not None:
            tilemenu.switch_off()
            self.objects["tilemenu"] = None

            gr = self.grid()
            gx, gy = gr.get_position()
            gh = gr.get_size()[1]  
            gr.resize_object(x=gx, y=gy, width=self.w, height=gh)

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            exm = self.exitmenu()
            gr = self.grid()
            tilemenu = self.tilemenu()

            ex, ey = exm.get_pos()
            ew, eh = exm.get_size()
            rect_exit = pygame.Rect(ex, ey, ew, eh)

            gx, gy = gr.get_position()
            gw, gh = gr.get_size()
            rect_grid = pygame.Rect(gx, gy, gw, gh)

            if rect_exit.collidepoint(mouse_pos):
                callback = exm.process_click(mouse_pos)
                if callback:
                    callback()
            elif rect_grid.collidepoint(mouse_pos):
                gr.process_click(mouse_pos)
                selected = gr.get_selected()
                if selected is not None:
                    if tilemenu is None:
                        self.open_tile_menu(selected)
                    else:
                        tilemenu.select_tile(selected)
            else:
                if tilemenu is not None:
                    
                    callback = tilemenu.process_click(mouse_pos)
                    if callback:
                        callback()
                    else:
                        self.close_tile_menu()

    def show(self):
        for val in self.objects.values():
            if val:
                val.show()

    def exit(self):
        if self.starting_process is not None:
            self.starting_process.switch_on()
            processes = self.game_engine.get_processes()
            if self in processes:
                processes.remove(self)

    MAP_SAVE_DIR = "map_saves"

    def save_map(self):
        os.makedirs(self.MAP_SAVE_DIR, exist_ok=True)
        filename = f"map_{int(time.time())}.json"
        path = os.path.join(self.MAP_SAVE_DIR, filename)
        self.grid().save_to_file(path)
        print(f"Карта сохранена: {path}")

    def update_geometry(self, screen_width, screen_height):
        self.w = int(self.rel_w * screen_width)
        self.h = int(self.rel_h * screen_height)
        self.x = int(self.rel_x * screen_width)
        self.y = int(self.rel_y * screen_height)

        # 2. Размеры меню выхода
        exitmenu_height = int(self.h * 0.1)
        grid_y = self.y + exitmenu_height
        grid_h = self.h - exitmenu_height

        # 3. Обновляем exitmenu
        exitmenu = self.exitmenu()
        if exitmenu:
            exitmenu.x, exitmenu.y = self.x, self.y
            exitmenu.w, exitmenu.h = self.w, exitmenu_height
            exitmenu.resize_object(x=exitmenu.x, y=exitmenu.y,
                                width=exitmenu.w, height=exitmenu.h)

        # 4. Обновляем grid
        grid = self.grid()
        if grid is None:
            return

        tilemenu = self.tilemenu()
        if tilemenu is None:
            # Если меню тайлов закрыто – сетка на всю ширину
            grid_w = self.w
            grid.x, grid.y = self.x, grid_y
            grid.w, grid.h = grid_w, grid_h
            grid.resize_object(x=grid.x, y=grid.y, width=grid.w, height=grid.h)
        else:
            # Если меню тайлов открыто – сетка занимает 80% ширины
            grid_w = int(self.w * 0.8)
            grid.x, grid.y = self.x, grid_y
            grid.w, grid.h = grid_w, grid_h
            grid.resize_object(x=grid.x, y=grid.y, width=grid.w, height=grid.h)


            tile_x = grid.x + grid.w
            tile_y = grid_y
            tile_w = self.w - grid_w

            replace_menu = getattr(tilemenu, 'replace_menu', None)
            if replace_menu is not None and replace_menu.works:
                # Если открыт – делим доступную высоту пополам
                half_h = grid_h // 2
                tile_h = half_h
                replace_h = grid_h - half_h
            else:
                tile_h = grid_h
                replace_h = 0

            tilemenu.x, tilemenu.y = tile_x, tile_y
            tilemenu.w, tilemenu.h = tile_w, tile_h
            tilemenu.resize_object(x=tile_x, y=tile_y,
                                width=tile_w, height=tile_h)

            if replace_menu is not None and replace_menu.works:
                replace_x = tile_x
                replace_y = tile_y + tile_h
                replace_w = tile_w
                replace_menu.x, replace_menu.y = replace_x, replace_y
                replace_menu.w, replace_menu.h = replace_w, replace_h
                replace_menu.resize_object(x=replace_x, y=replace_y,
                                        width=replace_w, height=replace_h)
        
