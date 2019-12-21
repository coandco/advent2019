from utils import read_data
from typing import NamedTuple, Dict, Tuple, List, Set
import numpy as np

DATA = read_data().split("\n")


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other):
        return Coord(y=self.y+other.y, x=self.x+other.x)


class Portal(NamedTuple):
    dest: Coord
    leveldiff: int


DIRECTIONS = {
    'N': Coord(-1, 0),
    'W': Coord(0, -1),
    'S': Coord(1, 0),
    'E': Coord(0, 1),
}


def make_numpy_array(data):
    grid = np.full((len(data), len(data[0])), fill_value=" ", dtype=np.str)
    for y, line in enumerate(data):
        for x, char in enumerate(line):
            grid[y, x] = char
    return grid


def find_inner_ring(grid):
    center_coord = Coord(y=grid.shape[0]//2, x=grid.shape[1]//2)
    # Find left edge
    current_coord = center_coord
    while grid[current_coord+Coord(y=0, x=-1)] not in (".", "#"):
        current_coord += Coord(y=0, x=-1)
    left_x = current_coord.x

    # Find right edge
    current_coord = center_coord
    while grid[current_coord] not in (".", "#"):
        current_coord += Coord(y=0, x=1)
    width = current_coord.x - left_x

    # find top edge
    current_coord = center_coord
    while grid[current_coord+Coord(y=-1, x=0)] not in (".", "#"):
        current_coord += Coord(y=-1, x=0)
    top_y = current_coord.y

    # find bottom edge
    current_coord = center_coord
    while grid[current_coord] not in (".", "#"):
        current_coord += Coord(y=1, x=0)
    height = current_coord.y - top_y

    return top_y, height, left_x, width


# This code is ugly, but functional
def read_portals(grid: np.ndarray) -> Tuple[Dict[str, List[Coord]], Dict[Coord, Portal]]:
    known_portals = {}
    adjacent_map = {}
    # Top edge
    portal_line = grid[0:2,:]
    for x in range(portal_line.shape[1]):
        possible_portal = "".join(portal_line[:,x])
        if possible_portal.isalpha():
            known_portals[possible_portal] = [Coord(y=2, x=x)]

    # Bottom edge
    portal_line = grid[-2:,:]
    for x in range(portal_line.shape[1]):
        possible_portal = "".join(portal_line[:,x])
        if possible_portal.isalpha():
            known_portals[possible_portal] = [Coord(y=grid.shape[0]-3, x=x)]

    # Left edge
    portal_line = grid[:, 0:2]
    for y in range(portal_line.shape[0]):
        possible_portal = "".join(portal_line[y,:])
        if possible_portal.isalpha():
            known_portals[possible_portal] = [Coord(y=y, x=2)]

    # Right edge
    portal_line = grid[:, -2:]
    for y in range(portal_line.shape[0]):
        possible_portal = "".join(portal_line[y,:])
        if possible_portal.isalpha():
            known_portals[possible_portal] = [Coord(y=y, x=grid.shape[1]-3)]

    top_y, height, left_x, width = find_inner_ring(grid)

    # Inner top edge
    portal_line = grid[top_y:top_y+2, left_x:left_x+width]
    for x in range(portal_line.shape[1]):
        possible_portal = "".join(portal_line[:,x])
        if possible_portal.isalpha():
            portal_location = Coord(y=top_y-1, x=left_x+x)
            known_portals[possible_portal].append(portal_location)
            adjacent_map[known_portals[possible_portal][0]] = Portal(dest=portal_location, leveldiff=-1)
            adjacent_map[portal_location] = Portal(dest=known_portals[possible_portal][0], leveldiff=1)

    # Inner bottom edge
    portal_line = grid[top_y+height-2:top_y+height, left_x:left_x+width]
    for x in range(portal_line.shape[1]):
        possible_portal = "".join(portal_line[:, x])
        if possible_portal.isalpha():
            portal_location = Coord(y=top_y+height, x=left_x+x)
            known_portals[possible_portal].append(portal_location)
            adjacent_map[known_portals[possible_portal][0]] = Portal(dest=portal_location, leveldiff=-1)
            adjacent_map[portal_location] = Portal(dest=known_portals[possible_portal][0], leveldiff=1)

    # Inner left edge
    portal_line = grid[top_y:top_y+height, left_x:left_x+2]
    for y in range(portal_line.shape[0]):
        possible_portal = "".join(portal_line[y, :])
        if possible_portal.isalpha():
            portal_location = Coord(y=top_y+y, x=left_x-1)
            known_portals[possible_portal].append(portal_location)
            adjacent_map[known_portals[possible_portal][0]] = Portal(dest=portal_location, leveldiff=-1)
            adjacent_map[portal_location] = Portal(dest=known_portals[possible_portal][0], leveldiff=1)

    # Inner right edge
    portal_line = grid[top_y:top_y+height, left_x+width-2:left_x+width]
    for y in range(portal_line.shape[0]):
        possible_portal = "".join(portal_line[y, :])
        if possible_portal.isalpha():
            portal_location = Coord(y=top_y+y, x=left_x+width)
            known_portals[possible_portal].append(portal_location)
            adjacent_map[known_portals[possible_portal][0]] = Portal(dest=portal_location, leveldiff=-1)
            adjacent_map[portal_location] = Portal(dest=known_portals[possible_portal][0], leveldiff=1)

    return known_portals, adjacent_map


# Don't need to check boundaries because there are walls all around the outside
def valid_adjacent_non_recursive(grid: np.ndarray, adjacents: Dict[Coord, Portal], coord: Coord) -> Set[Coord]:
    possibilities = set(coord+x for x in DIRECTIONS.values())
    for loc in list(possibilities):
        char = grid[loc]
        if char != ".":
            possibilities.remove(loc)
    if coord in adjacents:
        possibilities.add(adjacents[coord].dest)
    return possibilities


def make_heatmap(grid: np.ndarray, adjacents: Dict[Coord, Portal], start_loc: Coord) -> np.ndarray:
    heatmap = np.full(grid.shape, fill_value=-1, dtype=np.int)
    check_list = next_locations = {start_loc}
    current_value = 0

    while next_locations:
        next_locations = set()
        for coord in check_list:
            existing_value = heatmap[coord]
            if existing_value == -1 or (0 <= current_value < existing_value):
                heatmap[coord] = current_value
                next_locations.update(valid_adjacent_non_recursive(grid, adjacents, coord))
        check_list = next_locations
        current_value += 1
    return heatmap


# Don't need to check boundaries because there are walls all around the outside
def valid_adjacent_recursive(grid: np.ndarray, adjacents: Dict[Coord, Portal],
                             coord: Coord, current_level: int) -> Set[Coord]:
    possibilities = set((coord+x, current_level) for x in DIRECTIONS.values())
    for loc, _ in list(possibilities):
        char = grid[loc]
        if char != ".":
            possibilities.remove((loc, current_level))
    if coord in adjacents and current_level+adjacents[coord].leveldiff >= 0:
        possibilities.add((adjacents[coord].dest, current_level+adjacents[coord].leveldiff))
    return possibilities


def make_heatmap_recursive(grid: np.ndarray, adjacents: Dict[Coord, Portal],
                           start_loc: Coord, end_loc: Coord) -> Dict[int, np.ndarray]:
    heatmaps = {}
    heatmaps[0] = np.full(grid.shape, fill_value=-1, dtype=np.int)
    check_list = next_locations = {(start_loc, 0)}
    current_value = 0

    while next_locations:
        next_locations = set()
        for coord, level in check_list:
            if level not in heatmaps:
                heatmaps[level] = np.full(grid.shape, fill_value=-1, dtype=np.int)
            existing_value = heatmaps[level][coord]
            if existing_value == -1 or (0 <= current_value < existing_value):
                heatmaps[level][coord] = current_value
                if coord == end_loc and level == 0:
                    return heatmaps
                next_locations.update(valid_adjacent_recursive(grid, adjacents, coord, level))
        check_list = next_locations
        current_value += 1


def completed_map_to_string(grid, heatmap):
    output = []
    for y in range(grid.shape[0]):
        output_line = ""
        for x in range(grid.shape[1]):
            char = grid[y, x]
            if char == '.':
                output_line += f"{heatmap[y, x]:^5}"
            elif char == '#':
                output_line += " ### "
            else:
                output_line += f"{char:^5}"
        output.append(output_line)
    return "\n".join(output)


def part_one(data) -> int:
    grid = make_numpy_array(data)
    portals, adjacency = read_portals(grid)
    heatmap = make_heatmap(grid, adjacency, portals['AA'][0])
    return heatmap[portals['ZZ'][0]]


def part_two(data) -> int:
    grid = make_numpy_array(data)
    portals, adjacency = read_portals(grid)
    heatmaps = make_heatmap_recursive(grid, adjacency, portals['AA'][0], portals['ZZ'][0])
    return heatmaps[0][portals['ZZ'][0]]


SAMPLE_DATA = """         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       """.split("\n")

SAMPLE_TWO = """             Z L X W       C                 
             Z P Q B       K                 
  ###########.#.#.#.#######.###############  
  #...#.......#.#.......#.#.......#.#.#...#  
  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  
  #.#...#.#.#...#.#.#...#...#...#.#.......#  
  #.###.#######.###.###.#.###.###.#.#######  
  #...#.......#.#...#...#.............#...#  
  #.#########.#######.#.#######.#######.###  
  #...#.#    F       R I       Z    #.#.#.#  
  #.###.#    D       E C       H    #.#.#.#  
  #.#...#                           #...#.#  
  #.###.#                           #.###.#  
  #.#....OA                       WB..#.#..ZH
  #.###.#                           #.#.#.#  
CJ......#                           #.....#  
  #######                           #######  
  #.#....CK                         #......IC
  #.###.#                           #.###.#  
  #.....#                           #...#.#  
  ###.###                           #.#.#.#  
XF....#.#                         RF..#.#.#  
  #####.#                           #######  
  #......CJ                       NM..#...#  
  ###.#.#                           #.###.#  
RE....#.#                           #......RF
  ###.###        X   X       L      #.#.#.#  
  #.....#        F   Q       P      #.#.#.#  
  ###.###########.###.#######.#########.###  
  #.....#...#.....#.......#...#.....#.#...#  
  #####.#.###.#######.#######.###.###.#.#.#  
  #.......#.......#.#.#.#.#...#...#...#.#.#  
  #####.###.#####.#.#.#.#.###.###.#.###.###  
  #.......#.....#.#...#...............#...#  
  #############.#.#.###.###################  
               A O F   N                     
               A A D   M                     """.split("\n")


print(f"Part one nonrecursive solution is {part_one(DATA)}")
print(f"Part two recursive solution is {part_two(DATA)}")