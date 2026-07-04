import pygame

# Oxy , where (0, 0) in upper left corner and Oy looks donward
class Tile:
    name = "tile"
    def __init__(self, grid, x, y, **kwargs):
        self.type = "undefined"
        self.x = x
        self.y = y
        self.is_walkable = kwargs.get("walk", False)
        self.is_flyable = kwargs.get("fly", False)
        self.buildable = kwargs.get("build", False)

class Grid:
    name = "Grid"
    def __init__(self, width, height):
        field = [[Tile(self, i, j) for j in range(width)] for i in range(height)]

    

        