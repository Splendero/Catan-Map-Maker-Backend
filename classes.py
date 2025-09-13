class Adjacent:
    def __init__(self,TL,TR,R,BR,BL,L):
        self.TL = TL
        self.TR = TR
        self.R = R
        self.BR = BR
        self.BL = BL
        self.L = L

    def to_list(self):
        return [self.TL, self.TR, self.R, self.BR, self.BL, self.L]

    def to_list_no_none(self):
        return [tile for tile in [self.TL, self.TR, self.R, self.BR, self.BL, self.L] if tile is not None]
    
    def __str__(self):
        return f"adjacent(TL={self.TL}, TR={self.TR}, R={self.R}, BR={self.BR}, BL={self.BL}, L={self.L})"
    
    def __repr__(self):
        return self.__str__()
        

class Tile:
    def __init__(self, number, resource, adjacent, coordinates ):
        self.number = number
        self.resource = resource
        self.coordinates = coordinates
        self.adjacent = adjacent

    def __str__(self):
        return f"Tile(number={self.number}, resource={self.resource}, coordinates={self.coordinates}, row={self.row})"

    def update_number(self, new_number):
        self.number = new_number

    def update_resource(self, new_resource):
        self.resource = new_resource


class Map:
    def __init__(self):
        self.tiles = [None] * 19
        self.array = None

        # Axial coordinates (q,r,s)
        self.coordinates = [
            (0, -2, 2), (1, -2, 1), (2, -2, 0),
            (-1, -1, 2), (0, -1, 1), (1, -1, 0), (2, -1, -1),
            (-2, 0, 2), (-1, 0, 1), (0, 0, 0), (1, 0, -1), (2, 0, -2),
            (-2, 1, 1), (-1, 1, 0), (0, 1, -1), (1, 1, -2),
            (-2, 2, 0), (-1, 2, -1), (0, 2, -2)
        ]

        self.resources = ["Wheat", "Wheat", "Wheat", "Wheat", "Brick", "Brick", "Brick", "Rock", "Rock", "Rock", "Sheep", "Sheep", "Sheep", "Sheep", "Wood", "Wood", "Wood", "Wood", "Desert"]
        self.numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

        # This only stores tiles that actually exist (not all possible coordinates)
        self.coord_to_tile = {tile.coordinates: tile for tile in self.tiles if tile}
    
    def findTileByCoordinate(self, q, r, s):
        return self.coord_to_tile.get((q, r, s))
