# NULL is replaced with None for cross-platform compatibility
import random
from classes import Map, Tile, Adjacent

def randomizeBoard(map):
    numbers = map.numbers[:]
    coordinates = map.coordinates[:]
    random.shuffle(numbers)
    random.shuffle(coordinates)

    for i in range(len(map.resources)-1):
        map.tiles[i] = Tile(numbers[i], map.resources[i], None, coordinates[i])

    map.tiles[len(map.resources)-1] = Tile(0, map.resources[len(map.resources)-1], None, coordinates[len(map.resources)-1])

    return fillAdjacentNumbers(map)

def fillAdjacentNumbers(map):
    map.coord_to_tile = {tile.coordinates: tile for tile in map.tiles if tile}

    for i in range(len(map.resources)):
        q, r, s = map.tiles[i].coordinates[0], map.tiles[i].coordinates[1], map.tiles[i].coordinates[2]
        TL = map.coord_to_tile.get((q, r - 1 , s + 1))
        TR = map.coord_to_tile.get((q + 1, r - 1, s))
        R = map.coord_to_tile.get((q - 1, r, s + 1))
        BR = map.coord_to_tile.get((q , r + 1, s - 1))
        BL = map.coord_to_tile.get((q - 1, r + 1, s))
        L = map.coord_to_tile.get((q + 1, r, s - 1))
        map.tiles[i].adjacent = Adjacent(TL, TR, R, BR, BL, L)
    return map

def noNumberPairs(map, pairs):
    sort(map)
    for tile in map.tiles:
        if tile is not None and tile.number in pairs:
            adjacent_pairs = []
            for adj in tile.adjacent.to_list_no_none():
                if adj is not None and adj.number in pairs:
                    adjacent_pairs.append(adj)
            
            if adjacent_pairs:
                swap_candidate = findSwapCandidate(tile, map, pairs, 1)
                if swap_candidate is None:
                    swap_candidate = findSwapCandidate(tile, map, pairs, 2)
                if swap_candidate is None:
                    swap_candidate = findSwapCandidate(tile, map, pairs, 0)
                if swap_candidate is not None:
                    temp_number = tile.number
                    tile.number = swap_candidate.number
                    swap_candidate.number = temp_number
                    map = fillAdjacentNumbers(map)
                    break
    return map

def findSwapCandidate(original_tile, map, pairs, search_depth):
    if search_depth == 0:
        candidates = [tile for tile in map.tiles if tile is not None]
    elif search_depth == 1:
        candidates = original_tile.adjacent.to_list_no_none()
    elif search_depth == 2:
        candidates = []
        for adj in original_tile.adjacent.to_list_no_none():
            if adj is not None:
                candidates.extend(adj.adjacent.to_list_no_none())
        candidates = list(set([c for c in candidates if c is not None]))
    
    for candidate in candidates:
        if (candidate is not None and 
            candidate.number not in pairs and
            candidate.number != 0):
            is_safe = True
            for other_tile in map.tiles:
                if (other_tile is not None and 
                    other_tile.number in pairs and 
                    other_tile != original_tile):
                    for adj in other_tile.adjacent.to_list_no_none():
                        if adj == candidate:
                            is_safe = False
                            break
                    if not is_safe:
                        break
            
            if is_safe:
                return candidate
    return None

def checkForPairs(map, pairs):
    """Check if any adjacent tiles have numbers in the pairs list"""
    for tile in map.tiles:
        if tile is not None and tile.number in pairs:
            for adj in tile.adjacent.to_list_no_none():
                if adj is not None and adj.number in pairs:
                    return True  # Found a pair
    return False  # No pairs found

def rerandomizeNumbersUntilNoPairs(map, pairs, max_attempts=100):
    """Keep randomizing until no pairs are found or max attempts reached"""
    attempts = 0
    
    while checkForPairs(map, pairs) and attempts < max_attempts:
        # Rerandomize the board
        numbers = map.numbers[:]
        coordinates = map.coordinates[:]
        random.shuffle(numbers)
        random.shuffle(coordinates)
        
        # Create new tiles with shuffled numbers and coordinates
        for i in range(len(map.resources)-1):
            map.tiles[i] = Tile(numbers[i], map.resources[i], None, coordinates[i])
        
        map.tiles[len(map.resources)-1] = Tile(0, map.resources[len(map.resources)-1], None, coordinates[len(map.resources)-1])
        
        # Update adjacent relationships
        map = fillAdjacentNumbers(map)
        attempts += 1
    
    if attempts >= max_attempts:
        print(f"Warning: Could not eliminate pairs after {max_attempts} attempts")
    else:
        print(f"Successfully eliminated pairs after {attempts} attempts")
    
    return map

def sort(map):
    # Create a mapping from coordinates to their original index
    coord_to_index = {coord: i for i, coord in enumerate(map.coordinates)}
    
    # Filter out None tiles and sort by their original coordinate order
    valid_tiles = []
    for tile in map.tiles:
        if tile is not None:
            original_index = coord_to_index[tile.coordinates]
            valid_tiles.append((tile, original_index))
    
    # Sort by original index
    valid_tiles.sort(key=lambda x: x[1])
    
    # Create new tiles array with same length as original
    new_tiles = [None] * len(map.tiles)
    
    # Place tiles back in their original positions
    for i, (tile, _) in enumerate(valid_tiles):
        new_tiles[i] = tile
    
    map.tiles = new_tiles
    
    # Update the coord_to_tile mapping
    map.coord_to_tile = {tile.coordinates: tile for tile in map.tiles if tile}
    
    return map
print("Done!")

def noAdjacentSameResources(map):
    """Eliminate adjacent tiles with the same resource using depth-based swapping"""
    sort(map)
    for tile in map.tiles:
        if tile is not None:
            adjacent_same_resources = []
            for adj in tile.adjacent.to_list_no_none():
                if adj is not None and adj.resource == tile.resource:
                    adjacent_same_resources.append(adj)
            
            if adjacent_same_resources:
                swap_candidate = findResourceSwapCandidate(tile, map, 1)
                if swap_candidate is None:
                    swap_candidate = findResourceSwapCandidate(tile, map, 2)
                if swap_candidate is None:
                    swap_candidate = findResourceSwapCandidate(tile, map, 0)
                if swap_candidate is not None:
                    temp_resource = tile.resource
                    tile.resource = swap_candidate.resource
                    swap_candidate.resource = temp_resource
                    map = fillAdjacentNumbers(map)
                    break
    return map

def findResourceSwapCandidate(original_tile, map, search_depth):
    """Find a tile to swap resources with using depth-based search"""
    if search_depth == 0:
        candidates = [tile for tile in map.tiles if tile is not None]
    elif search_depth == 1:
        candidates = original_tile.adjacent.to_list_no_none()
    elif search_depth == 2:
        candidates = []
        for adj in original_tile.adjacent.to_list_no_none():
            if adj is not None:
                candidates.extend(adj.adjacent.to_list_no_none())
        candidates = list(set([c for c in candidates if c is not None]))
    
    for candidate in candidates:
        if (candidate is not None and 
            candidate.resource != original_tile.resource and
            candidate.resource != "Desert"):  # Don't swap with desert
            is_safe = True
            # Check if swapping would create new adjacent same resources
            for other_tile in map.tiles:
                if (other_tile is not None and 
                    other_tile.resource == original_tile.resource and 
                    other_tile != original_tile):
                    for adj in other_tile.adjacent.to_list_no_none():
                        if adj == candidate:
                            is_safe = False
                            break
                    if not is_safe:
                        break
            
            # Also check if the candidate's new resource would conflict with its neighbors
            if is_safe:
                for adj in candidate.adjacent.to_list_no_none():
                    if adj is not None and adj.resource == original_tile.resource:
                        is_safe = False
                        break
            
            if is_safe:
                return candidate
    return None

def checkForAdjacentSameResources(map):
    """Check if any adjacent tiles have the same resource type"""
    for tile in map.tiles:
        if tile is not None:
            for adj in tile.adjacent.to_list_no_none():
                if adj is not None and adj.resource == tile.resource:
                    return True  # Found adjacent same resources
    return False  # No adjacent same resources found

def rerandomizeResourcesUntilNoAdjacentSame(map, max_attempts=100):
    """Keep randomizing resources until no adjacent same resources or max attempts reached"""
    attempts = 0
    
    while checkForAdjacentSameResources(map) and attempts < max_attempts:
        # Rerandomize the resources
        resources = map.resources[:]
        random.shuffle(resources)
        
        # Create new tiles with shuffled resources
        for i in range(len(map.resources)):
            if map.tiles[i] is not None:
                map.tiles[i].resource = resources[i]
        
        # Update adjacent relationships
        map = fillAdjacentNumbers(map)
        attempts += 1
    
    if attempts >= max_attempts:
        print(f"Warning: Could not eliminate adjacent same resources after {max_attempts} attempts")
    else:
        print(f"Successfully eliminated adjacent same resources after {attempts} attempts")
    
    return map

print("Done!")