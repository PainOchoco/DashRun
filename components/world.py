import os
import csv
import random
import pygame as pg
from components.settings import *

class World():
    def __init__(self, path, length, tileset):
        self.length = length
        self.world_map = {}
        self.tile_rects = []
        self.path = path
        self.map_files = []
        self.maps = []
        self.tileset = tileset
        self.tile_list = tileset.get_tile_list(TILE_SIZE, TILE_SIZE)
        self.offset = 1

    def generate(self):
        start = self.load_map("start.csv")
        self.slice_map(start)

        self.map_files = os.listdir(self.path + "/parts/")

        for i in range(self.length):
            random_map = random.choice(self.map_files)
            map = self.load_map("/parts/" + random_map)
            self.maps.append(map)
            self.slice_map(map, self.offset)
            self.offset += (len(map[0]) / CHUNK_SIZE)

    def load_map(self, file_name):
        data = list(csv.reader(open(self.path + file_name, "r")))
        return data

    def load_terrain(self, display, scroll):
        self.tile_rects = []

        for y in range(3):
            for x in range(4):
                target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * TILE_SIZE)))
                target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * TILE_SIZE)))
                target_chunk = "{};{}".format(str(target_x), str(target_y))

                if target_chunk not in self.world_map:
                    self.world_map[target_chunk] = [[4 for x in range(8)] for y in range(8)] # ? empty chunk

                for y_pos in range(CHUNK_SIZE):
                    for x_pos in range(CHUNK_SIZE):
                        tile = int(self.world_map[target_chunk][x_pos][y_pos])
                        tile_x = (target_x * CHUNK_SIZE + x_pos) * TILE_SIZE
                        tile_y = (target_y * CHUNK_SIZE + y_pos) * TILE_SIZE

                        # if tile != 4:
                        display.blit(self.tile_list[tile], (tile_x - scroll[0] + 10, tile_y - scroll[1]))

                        if tile not in [4, 9, 14, 19, 23, 24, 28, 29]:
                            self.tile_rects.append(pg.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        return self.tile_rects
    
    def slice_map(self, map, offset = 0):
        height = int(len(map) / CHUNK_SIZE)
        width = int(len(map[0]) / CHUNK_SIZE)
    
        for h in range(height):
            for w in range(width):
                columns = []
                for i in range(CHUNK_SIZE):
                    rows = []
                    for j in range(CHUNK_SIZE):
                        rows.append(map[j + h * CHUNK_SIZE][i + w * CHUNK_SIZE])
                    columns.append(rows)
    
                chunk_name = "{};{}".format(int(w + offset), h)
                self.world_map[chunk_name] = columns


class Tileset():
    def __init__(self, path):
        self.image = pg.image.load(path)

    def get_tile(self, x, y, w, h):
        tile = pg.Surface((w, h))
        tile.blit(self.image, (0, 0), (x, y, w, h))    
        return tile

    def get_tile_list(self, w, h):
        tiles = []
        for height in range(int(self.image.get_height() / h)):
            for width in range(int(self.image.get_width() / w)):
                tile = pg.Surface((w, h))
                tile.set_colorkey((0, 0, 0))
                tile.blit(self.image, (0, 0), (width * w, height * h, w, h))
                tiles.append(tile)

        return tiles