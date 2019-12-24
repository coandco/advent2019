from utils import read_data
from typing import NamedTuple, Set, DefaultDict, Union, Dict
import string
from collections import deque
import numpy as np


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other) -> 'Coord':
        return Coord(y=self.y+other.y, x=self.x+other.x)


class KeyDoorPair(NamedTuple):
    key: Union[Coord, None] = None
    door: Union[Coord, None] = None

    def set_key(self, key):
        return KeyDoorPair(key=key, door=self.door)

    def set_door(self, door):
        return KeyDoorPair(key=self.key, door=door)


DIRECTIONS = {
    'N': Coord(-1, 0),
    'W': Coord(0, -1),
    'S': Coord(1, 0),
    'E': Coord(0, 1),
}

GRID_WALL = '#'
GRID_ENTRANCE = '@'
GRID_FLOOR = '.'


def parse_data(data):
    grid_size = Coord(y=len(data)+1, x=len(data[0])+1)
    grid = np.zeros((grid_size.y, grid_size.x), dtype=np.str)
    keys = dict()
    doors = dict()
    starting_loc = Coord(0, 0)
    for y, line in enumerate(data):
        for x, char in enumerate(line):
            current_loc = Coord(y=y, x=x)
            grid[current_loc.y, current_loc.x] = char
            if char == '@':
                starting_loc = current_loc
            if char.isupper():
                doors[char] = current_loc
            elif char.islower():
                keys[char] = current_loc
    return grid, keys, doors, starting_loc


# Don't need to check boundaries because there are walls all around the outside
def valid_adjacent(grid: np.ndarray, coord: Coord, found_keys: str = "") -> Set[Coord]:
    possibilities = set(coord+x for x in DIRECTIONS.values())
    for loc in list(possibilities):
        char = grid[loc]
        if char == "#" or (char.isupper() and char.lower() not in found_keys):
            possibilities.remove(loc)
    return possibilities


def make_heatmap(grid: np.ndarray, start_loc: Coord, found_keys: str = "") -> np.ndarray:
    heatmap = np.full(grid.shape, fill_value=-1, dtype=np.int)
    check_list = next_locations = {start_loc}
    current_value = 0

    while next_locations:
        next_locations = set()
        for coord in check_list:
            char = grid[coord]
            existing_value = heatmap[coord]
            if existing_value == -1 or (0 <= current_value < existing_value):
                heatmap[coord] = current_value
                # Can't pass through keys without getting them, but still want to record distance to them
                if char in string.ascii_lowercase and char not in found_keys:
                    continue
                next_locations.update(valid_adjacent(grid, coord, found_keys))
        check_list = next_locations
        current_value += 1
    return heatmap


class KeyPath(NamedTuple):
    path: str
    cost: int

    def __str__(self):
        return self.path


def get_reachable_keys(grid: np.ndarray, keys: Dict[str, Coord],
                       starting_loc: Coord, already_gotten: str = ""):
    heatmap = make_heatmap(grid, starting_loc, already_gotten)
    return {k: heatmap[v] for k, v in keys.items()
            if heatmap[v] != -1 and k not in already_gotten}


def find_shortest_path(grid: np.ndarray, keys: Dict[str, Coord], starting_loc):
    initial_keys = get_reachable_keys(grid, keys, starting_loc)
    known_paths = deque(initial_keys.items())
    shortest_path = None
    cached_results = {}

    while known_paths:
        path = known_paths.pop()
        # If your cost is already greater than the known shortest path, cut this tree off
        if shortest_path and path[1] > shortest_path[1]:
            continue
        path_loc = keys[path[0][-1]]
        cache_key = (path_loc, frozenset(path[0]))
        if cache_key in cached_results:
            reachable_keys = cached_results[cache_key]
        else:
            reachable_keys = get_reachable_keys(grid, keys, path_loc, path[0])
            cached_results[cache_key] = reachable_keys
        # If the new paths created will have gotten all of the keys)
        if len(path[0]) == len(keys) - 1:
            if shortest_path is None or path[1] < shortest_path[1]:
                shortest_path = path
                print(f"Found new shortest path: {path[0]} with cost {path[1]}")
        else:
            for key in reachable_keys:
                known_paths.append((f"{path[0]}{key}", path[1]+reachable_keys[key]))
            # known_paths.extend((path[0]+k, path[1]+v) for k, v in reachable_keys.items())
    return shortest_path


DATA = read_data().split("\n")
SAMPLE_ONE = """########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################""".split("\n")
SAMPLE_TWO = """########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################""".split("\n")
SAMPLE_THREE = """#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################""".split("\n")
my_grid, keys, doors, start = parse_data(SAMPLE_THREE)
#reachable_keys = get_reachable_keys(my_grid, keys, start)
#print(reachable_keys)
best_path = find_shortest_path(my_grid, keys, start)
print(best_path)