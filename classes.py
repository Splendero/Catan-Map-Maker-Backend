from typing import Dict, Set, Optional, List, Tuple
from resourse import _color_with_inventory
from numbers import _assign_numbers_avoid_hot_adjacent

_NEIGHBOR_DIRS: List[Tuple[int, int, int]] = [
    (0, -1,  1),  # TL
    (1, -1,  0),  # TR
    (1,  0, -1),  # R
    (0,  1, -1),  # BR
    (-1, 1,  0),  # BL
    (-1, 0,  1),  # L
]

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

        self.resources = ["Wheat", "Wheat", "Wheat", "Wheat",
                          "Brick", "Brick", "Brick",
                          "Rock", "Rock", "Rock",
                          "Sheep", "Sheep", "Sheep", "Sheep",
                          "Wood", "Wood", "Wood", "Wood",
                          "Desert"]
        # 18 numbers (desert gets no number)
        self.numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

        # Will be (re)built by build_empty_tiles()
        self.coord_to_tile: Dict[tuple, Tile] = {}
        self.coord_to_index: Dict[tuple, int] = {}

    def build_empty_tiles(self):
        """Create 19 Tiles with empty number/resource and wire Adjacent with neighbor indices."""
        self.tiles = []
        for (q, r, s) in self.coordinates:
            t = Tile(number=None, resource=None,
                     adjacent=Adjacent(None, None, None, None, None, None),
                     coordinates=(q, r, s))
            self.tiles.append(t)

        # indexers
        self.coord_to_tile = {t.coordinates: t for t in self.tiles}
        self.coord_to_index = {t.coordinates: i for i, t in enumerate(self.tiles)}

        # fill adjacency using axial neighbor steps
        for i, t in enumerate(self.tiles):
            q, r, s = t.coordinates
            n_indices: List[Optional[int]] = []
            for dq, dr, ds in _NEIGHBOR_DIRS:
                coord = (q + dq, r + dr, s + ds)
                n_indices.append(self.coord_to_index.get(coord))  # int or None
            t.adjacent = Adjacent(*n_indices)

    def _adj_graph(self) -> Dict[int, Set[int]]:
        """Index-based adjacency: {i -> set(neighbor indices)}."""
        g: Dict[int, Set[int]] = {i: set() for i in range(len(self.tiles))}
        for i, tile in enumerate(self.tiles):
            for n in tile.adjacent.to_list_no_none():
                g[i].add(n)
        return g

    def findTileByCoordinate(self, q, r, s):
        return self.coord_to_tile.get((q, r, s))

    def _inventory_counts(self) -> Dict[str, int]:
        """Turn self.resources multiset into counts."""
        inv: Dict[str, int] = {}
        for r in self.resources:
            inv[r] = inv.get(r, 0) + 1
        return inv

    def generate_resources_with_dsatur(self, precolored: Optional[Dict[int, str]] = None) -> bool:
        """Assign tile.resource to all 19 tiles respecting inventory and adjacency."""
        inventory = self._inventory_counts()
        if len(self.coordinates) != sum(inventory.values()):
            raise ValueError("Coordinate count and resource multiset size mismatch.")

        g = self._adj_graph()
        assignment = _color_with_inventory(g, inventory, precolored=precolored)
        if assignment is None:
            return False

        for i, res in assignment.items():
            self.tiles[i].resource = res
        return True

    def assign_numbers_simple(self):
        """Assign numbers to non-Desert tiles in the order provided."""
        pool = list(self.numbers)  # 18 entries
        for t in self.tiles:
            if t.resource == "Desert":
                t.number = None
            else:
                t.number = pool.pop(0)

    def create_from_scratch(self, precolored: Optional[Dict[int, str]] = None, assign_numbers: bool = True):
        """1) build tiles & adjacency, 2) DSATUR inventory coloring, 3) optional numbers."""
        self.build_empty_tiles()
        ok = self.generate_resources_with_dsatur(precolored=precolored)
        if not ok:
            raise RuntimeError("No feasible resource assignment with the given inventory.")
        if assign_numbers:
            self.assign_numbers_simple()
        # refresh coord index
        self.coord_to_tile = {t.coordinates: t for t in self.tiles}

    def printMap(self):
        sp = "        "
        print("\n" + "="*80)
        print("CATAN MAP LAYOUT")
        print("="*80)
        
        print(f"{sp}{sp}{self.getNR(0, -2, 2)}{sp}{self.getNR(1, -2, 1)}{sp}{self.getNR(2, -2, 0)}{sp}{sp}")
        print(f"{sp}{self.getNR(-1, -1, 2)}{sp}{self.getNR(0, -1, 1)}{sp}{self.getNR(1, -1, 0)}{sp}{self.getNR(2, -1, -1)}{sp}")
        print(f"{self.getNR(-2, 0, 2)}{sp}{self.getNR(-1, 0, 1)}{sp}{self.getNR(0, 0, 0)}{sp}{self.getNR(1, 0, -1)}{sp}{self.getNR(2, 0, -2)}{sp}")
        print(f"{sp}{self.getNR(-2, 1, 1)}{sp}{self.getNR(-1, 1, 0)}{sp}{self.getNR(0, 1, -1)}{sp}{self.getNR(1, 1, -2)}{sp}")
        print(f"{sp}{sp}{self.getNR(-2, 2, 0)}{sp}{self.getNR(-1, 2, -1)}{sp}{self.getNR(0, 2, -2)}{sp}{sp}")
        
        print("="*80)

    def getNR(self, q, r, s):
        tile = self.findTileByCoordinate(q, r, s)
        if(tile.resource == "Desert"):
            return f"{tile.resource},{tile.number}"
        if(tile.resource == "Wheat" or tile.resource == "Sheep" or tile.resource == "Brick" or tile.resource == "Wood" or tile.resource == "Rock"):
            return f" {tile.resource},{tile.number}"
        else:
            return f"  {tile.resource},{tile.number}"
    
    def assign_numbers_hot_constraint(self, hot: Set[int] = {6, 8}, precolored: Optional[Dict[int, int]] = None):
        """
        Assign numbers to all non-Desert tiles so that no edge has (6 or 8) touching (6 or 8).
        Duplicates of other numbers are allowed.
        """
        # 1) locate the desert tile (if any)
        desert_index = None
        for i, t in enumerate(self.tiles):
            if t.resource == "Desert":
                desert_index = i
                break

        # 2) build graph over *numbered* vertices only
        numbered_vertices = [i for i in range(len(self.tiles)) if i != desert_index]
        # map old -> compact indices [0..17]
        remap = {old: new for new, old in enumerate(numbered_vertices)}
        adj: Dict[int, Set[int]] = {remap[i]: set() for i in numbered_vertices}
        for i in numbered_vertices:
            for n in self.tiles[i].adjacent.to_list_no_none():
                if n is not None and n != desert_index:
                    adj[remap[i]].add(remap[n])

        # 3) inventory of numbers
        inventory: Dict[int, int] = {}
        for x in self.numbers:
            inventory[x] = inventory.get(x, 0) + 1
        # sanity
        if sum(inventory.values()) != len(numbered_vertices):
            raise ValueError("Numbers inventory does not match count of non-desert tiles.")

        # 4) optional precolored (using original indices); remap keys if provided
        pre = None
        if precolored:
            pre = {remap[i]: v for i, v in precolored.items() if i in remap}

        # 5) solve
        solution = _assign_numbers_avoid_hot_adjacent(adj, inventory, hot=hot, precolored=pre)
        if solution is None:
            raise RuntimeError("No feasible numbering under hot-adjacency constraint.")

        # 6) write back to tiles (invert remap)
        inv_remap = {v: k for k, v in remap.items()}
        for j_new, num in solution.items():
            i_old = inv_remap[j_new]
            self.tiles[i_old].number = num
        if desert_index is not None:
            self.tiles[desert_index].number = None
