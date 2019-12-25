from utils import read_data
from typing import NamedTuple, Set, Tuple, Union, Dict
import string
from collections import deque
import numpy as np


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other) -> 'Coord':
        return Coord(y=self.y+other.y, x=self.x+other.x)

    def __sub__(self, other) -> 'Coord':
        return Coord(y=self.y-other.y, x=self.x-other.x)


DIRECTIONS = {
    'N': Coord(-1, 0),
    'W': Coord(0, -1),
    'S': Coord(1, 0),
    'E': Coord(0, 1),
}

QUADRANTS = [Coord(-1, -1), Coord(-1, 1), Coord(1, -1), Coord(1, 1)]

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
    known_paths = deque(KeyPath(*x) for x in initial_keys.items())
    shortest_path = None
    cached_results = {}
    cached_distances = {}

    while known_paths:
        path = known_paths.pop()
        path_loc = keys[path.path[-1]]
        cache_key = (path_loc, frozenset(path.path))
        # If your cost is already greater than the known shortest path to this location, cut this tree off
        if path.cost > cached_distances.get(cache_key, 99999):
            continue
        if cache_key in cached_results:
            reachable_keys = cached_results[cache_key]
        else:
            reachable_keys = get_reachable_keys(grid, keys, path_loc, path.path)
            cached_results[cache_key] = reachable_keys
        # If the new paths created will have gotten all of the keys)
        for key, distance in reversed(sorted(reachable_keys.items(), key=lambda x: x[1])):
            new_path = KeyPath(path=f"{path.path}{key}", cost=path.cost + distance)
            if len(new_path.path) == len(keys):
                if shortest_path is None or new_path.cost < shortest_path.cost:
                    shortest_path = new_path
                    print(f"Found new shortest path: {new_path.path} with cost {new_path.cost}")
            else:
                known_paths.append(new_path)
                cache_key = (keys[key], frozenset(new_path.path))
                if new_path.cost < cached_distances.get(cache_key, 99999):
                    cached_distances[cache_key] = new_path.cost
    return shortest_path


# This function basically just runs part one on each quadrant individually, assuming that all doors with keys
# not in the quadrant are open, then adds the results and returns them.  It gets the correct answer.
def part_two_cheat(grid: np.ndarray, keys: Dict[str, Coord], doors: Dict[str, Coord], old_starting_loc: Coord):
    split_keys = partition_coords(keys, old_starting_loc)
    split_doors = partition_coords(doors, old_starting_loc)
    actual_starting_locs = tuple(old_starting_loc + x for x in QUADRANTS)
    total_distance = 0
    for bot_num, loc in enumerate(actual_starting_locs):
        # get a list of doors to faux-open in the quadrant
        fake_open_doors = "".join(k for k, v in split_doors.items()
                                  if v.quadrant == bot_num and split_keys[k.lower()].quadrant != bot_num).lower()
        keys_in_quadrant = {k: v for k, v in split_keys.items() if v.quadrant == bot_num}
        initial_keys = get_reachable_keys(grid, keys, loc, fake_open_doors)
        known_paths = deque(KeyPath(*x) for x in initial_keys.items())
        shortest_path = None
        cached_results = {}
        cached_distances = {}

        while known_paths:
            path = known_paths.pop()
            path_loc = keys[path.path[-1]]
            cache_key = (path_loc, frozenset(path.path))
            # If your cost is already greater than the known shortest path to this location, cut this tree off
            if path.cost > cached_distances.get(cache_key, 99999):
                continue
            if cache_key in cached_results:
                reachable_keys = cached_results[cache_key]
            else:
                reachable_keys = get_reachable_keys(grid, keys, path_loc, path.path+fake_open_doors)
                cached_results[cache_key] = reachable_keys
            # If the new paths created will have gotten all of the keys)
            for key, distance in reversed(sorted(reachable_keys.items(), key=lambda x: x[1])):
                new_path = KeyPath(path=f"{path.path}{key}", cost=path.cost + distance)
                if len(new_path.path) == len(keys_in_quadrant):
                    if shortest_path is None or new_path.cost < shortest_path.cost:
                        shortest_path = new_path
                        print(f"Found new shortest path: {new_path.path} with cost {new_path.cost}")
                else:
                    known_paths.append(new_path)
                    cache_key = (keys[key], frozenset(new_path.path))
                    if new_path.cost < cached_distances.get(cache_key, 99999):
                        cached_distances[cache_key] = new_path.cost
        total_distance += shortest_path.cost
        print(f"shortest path for quadrant {bot_num} is {shortest_path.cost}")
    return total_distance


def make_part_two_grid(part_one_grid: np.ndarray, starting_loc):
    part_two_grid = part_one_grid.copy()
    part_two_grid[starting_loc] = GRID_WALL
    for direction in DIRECTIONS.values():
        part_two_grid[starting_loc+direction] = GRID_WALL
    return part_two_grid


class PartitionedKey(NamedTuple):
    location: Coord
    quadrant: int


def partition_coords(keys: Dict[str, Coord], entrance: Coord) -> Dict[str, PartitionedKey]:
    partitioned_keys = {}
    for key, location in keys.items():
        difference = location - entrance
        if difference.x < 0 and difference.y < 0:
            partitioned_keys[key] = PartitionedKey(location, 0)
        elif difference.x > 0 and difference.y < 0:
            partitioned_keys[key] = PartitionedKey(location, 1)
        elif difference.x < 0 and difference.y > 0:
            partitioned_keys[key] = PartitionedKey(location, 2)
        elif difference.x > 0 and difference.y > 0:
            partitioned_keys[key] = PartitionedKey(location, 3)
    return partitioned_keys


def get_bot_positions(entrance: Coord, split_keys: Dict[str, PartitionedKey], keys_gotten: str) -> Tuple[Coord]:
    known_positions = [None, None, None, None]
    for key in reversed(keys_gotten):
        if known_positions[split_keys[key].quadrant] is None:
            known_positions[split_keys[key].quadrant] = split_keys[key].location
    # If we've made it through all of the known keys without finding positions for some bots, fill in the starting locs
    for bot_num, position in enumerate(known_positions):
        if position is None:
            known_positions[bot_num] = entrance + QUADRANTS[bot_num]
    return tuple(known_positions)


class KeyPathMulti(NamedTuple):
    path: str
    cost: int
    bot_positions: Tuple[Coord]

    def __str__(self):
        return self.path


def part_two_shortest_path(grid: np.ndarray, keys: Dict[str, Coord], old_starting_loc: Coord):
    known_paths = deque()
    split_keys = partition_coords(keys, old_starting_loc)
    actual_starting_locs = tuple(old_starting_loc+x for x in QUADRANTS)
    for loc in actual_starting_locs:
        known_paths.extend(KeyPathMulti(path=x[0],
                                        cost=x[1],
                                        bot_positions=get_bot_positions(old_starting_loc, split_keys, ""))
                           for x in get_reachable_keys(grid, keys, loc).items())

    shortest_path = None
    cached_results = {}
    cached_distances = {}

    while known_paths:
        path = known_paths.pop()
        path_locs = path.bot_positions
        cache_key = (path_locs, frozenset(path.path))
        # If your cost is already greater than the known shortest path to this location, cut this tree off
        if path.cost > cached_distances.get(cache_key, 99999):
            continue
        reachable_keys = {}
        for bot_loc in path_locs:
            reachable_cache_key = (bot_loc, cache_key[1])
            if reachable_cache_key not in cached_results:
                cached_results[reachable_cache_key] = get_reachable_keys(grid, keys, bot_loc, path.path)
            reachable_keys.update(cached_results[reachable_cache_key])

        for key, distance in reversed(sorted(reachable_keys.items(), key=lambda x: x[1])):
            new_positions = list(path_locs)
            new_positions[split_keys[key].quadrant] = split_keys[key].location
            new_path = KeyPathMulti(path=f"{path.path}{key}", cost=path.cost + distance, bot_positions=tuple(new_positions))

            if len(new_path.path) == len(keys):
                if shortest_path is None or new_path.cost < shortest_path.cost:
                    shortest_path = new_path
                    print(f"Found new shortest path: {new_path.path} with cost {new_path.cost}")
            else:
                known_paths.append(new_path)
                cache_key = (tuple(new_positions), frozenset(new_path.path))
                if new_path.cost < cached_distances.get(cache_key, 99999):
                    cached_distances[cache_key] = new_path.cost
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
SAMPLE_FOUR = """########################
#@..............ac.GI.b#
###d#e#f################
###A#B#C################
###g#h#i################
########################""".split("\n")
SAMPLE_FIVE = """###############
#d.ABC.#.....a#
######.#.######
#######@#######
######.#.######
#b.....#.....c#
###############""".split("\n")
SAMPLE_SIX = """#############
#g#f.D#..h#l#
#F###e#E###.#
#dCba.#.BcIJ#
######@######
#nK.L.#.G...#
#M###N#H###.#
#o#m..#i#jk.#
#############""".split("\n")

if __name__ == '__main__':
    my_grid, keys, doors, start = parse_data(DATA)
    best_path = find_shortest_path(my_grid, keys, start)
    print(f"Shortest path for part one is {best_path.path} with cost {best_path.cost}")
    part_two_grid = make_part_two_grid(my_grid, start)
    best_path = part_two_cheat(part_two_grid, keys, doors, start)
    print(f"Shortest path cost for part two (gotten by computing individual quarters and adding them) is {best_path}")
