import pygame
import menu
from enum import Enum

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
    def get_grid(self):
        return self.grid

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
            TileTypes.Grass: "images/grass_image.png",
            TileTypes.Rock: "images/rock_image.png"}

class GameTile(Tile):
    def __init__(self, x, y, **kwargs):
        super().__init__()
        self.is_empty = True
        self.mobs = {}
        self.facing = 0
    
    def get_image(self, **kwargs):
        return self.image(**kwargs)
    
    def image(self, **kwargs):
        return pygame.image.load(TileImagePath.path[self.type()].convert())

    def fill(self, px, py, pw, ph, screen):
        rect = pygame.Rect(px, py, pw, ph)
        image = self.get_image()
        scaled_image = pygame.transform.scale(image, (rect.width, rect.height))
        screen.blit(scaled_image, rect.x, rect.y)

    def add_mob():
        pass

class GrassTile(GameTile):
    def is_walkable(self):
        return True
    def is_flyable(self):
        return True
    def is_buildable(self):
        return True
    def type(self):
        return TileTypes.GRASS
    def __init__(self, x, y, **kwargs):
        super().__init__(self)

class RockTile(GameTile):
    def is_walkable(self):
        return False
    def is_flyable(self):
        return True
    def is_buildable(self):
        return False
    def type(self):
        return TileTypes.ROCK
    def image(self, x, y, **kwargs):
        super().__init__(self)
    
class TileFabric:
    def makeGrass(*args):
        return GrassTile(*args)
    def makeRock(*args):
        return RockTile(*args)
    def getTileImage(str, param = None): # don't really know if I need that
        if param:
            result = param + "_" + str
        match str:
            case "grass":
                return pygame.image.load(f"images/{result}_image.png")
            case "rock":
                return pygame.image.load(f"images/{result}.png")
    def getNewTile(str):
        match str:
            case "grass":
                return makeGrass()
            case "rock":
                return makeRock()
            case _:
                print("Undefined type in TileFabric.getNewTile()")
                return None

class GameGrid:
    name = "Grid"
    update_geometry = menu.Menu.update_geometry
    def __init__(self, t_width, t_height,  x, y, w, h, type="grass", game_engine = None):
        self.field = [[TileFabric.getNewTile(type) for j in range(t_width)] for i in range(t_height)]
        self.selected = None
        if not game_engine:
            raise ValueError("no game engine in grid")
        self.t_width, self.t_height = t_width, t_height
        self.game_engine = game_engine
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rel_x = self.x / w, self.rel_y = self.y / h
        self.rel_w = self.w / w, self.rel_h = self.h / h
        self.tile_w, self.tile_h = 0, 0
        self.resize_object()
    
    def resize_object(self, x, y, width, height):
        screen = self.game_engine.screen
        scr_width, scr_height = screen.get_size()
        w, h = width, height
        if not(x >= 0 and x <= width  and y >= 0 and y <= height):
            raise ValueError("x or y more than screen width/height in grid.resize_object")
        if not(w >= 0 and h >= 0):
            raise ValueError("menu width/height below zero")
        
        if x + w > scr_width:
            w = scr_width - x
        if y + h > scr_height:
            h = scr_height - y

        self.x, self.y, self.w, self.h = x, y, w, h

        t_width, t_height = self.get_size_in_tiles()
        self.tile_w, self.tile_h = w / t_width, h / t_height
        
    def get_size_in_tiles(self):
        return (self.t_width, self.t_height)
    
    def get_size(self):
        return(self.w, self.h)
    
    def get_position(self):
        return(self.x, self.y)
    
    def get_tile_size(self):
        return(self.t_width, self.t_height)

    def get_engine(self):
        return self.game_engine
    #returns a grid full of grass 10 X 10
    def get_default_grid(*args):
        return  GameGrid(10, 10, *args)
    
    def pocess_event

    def show(self):
        scr = self.game_engine.screen
        in_t_width, in_t_height = self.get_size_in_tiles()
        gr_x, gr_y = self.get_position()
        cur_y = gr_y
        t_w, t_h = self.get_tile_size()
        for i in range(in_t_height):
            cur_x = gr_x
            for j in range(in_t_width):
                cur_x += t_w
                self.field[i, j].fill(cur_x, cur_y, gr_x, gr_y, scr)
            cur_y += t_h
    


class TileMenu(menu.Menu):
    def __init__(self, Tile, x, y):
        #game_engine.get_processes().clear() //let menu do all work
        super().__init__(self)
        super.get_buttons() = [{"rotate": self.rotate, "replace": self.open_replace_menu}]
        self.Tile = Tile

        
    def rotate_tile(self):
        self.Tile.rotate()

    def open_replace_menu(self):
        super.scale(scale_x=1,scale_y=0.5)
        grandparent = self.Grid.get_parent()
        if not grandparent:
            print("Grid without parent (found in TileMenu)")
            return
        grandparent.game_engine
        
           
