from utils import read_data
import numpy as np
from scipy.signal import convolve2d
from typing import NamedTuple, Dict, Tuple


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other) -> 'Coord':
        return Coord(self.y+other.y, self.x+other.x)


DIRECTIONS = {
    'U': Coord(-1, 0),
    'L': Coord(0, -1),
    'D': Coord(1, 0),
    'R': Coord(0, 1)
}


def make_grid(data):
    grid = np.zeros((len(data), len(data[0])), dtype=np.bool)
    for y, line in enumerate(data):
        for x, char in enumerate(line):
            if char == '#':
                grid[y, x] = True
    return grid


def print_grid(grid):
    with np.printoptions(linewidth=2000, threshold=20000,
                         formatter={'bool': lambda x: "#" if x else "."}):
        print(grid)


def in_bounds(shape: Tuple[int, int], coord: Coord):
    return (0 <= coord.y < shape[0]) and (0 <= coord.x < shape[1])


def get_relative(grid_stack: Dict[int, np.ndarray], requested_level: int) -> np.ndarray:
    try:
        return grid_stack[requested_level]
    except KeyError:
        return np.zeros(grid_stack[0].shape, dtype=np.bool)


def evolve_board(grid, neighbor_grid):
    empty_with_new_bugs = ((neighbor_grid == 1) | (neighbor_grid == 2)) & np.invert(grid)
    bugs_still_there = (neighbor_grid == 1) & grid
    return empty_with_new_bugs | bugs_still_there


def evolve_board_part_one(grid: np.ndarray):
    adjacency = np.array([[0, 1, 0],
                          [1, 1, 1],
                          [0, 1, 0]], dtype=np.int)
    neighbor_grid = convolve2d(grid, adjacency, mode='same', boundary='fill', fillvalue=0) - grid

    return evolve_board(grid, neighbor_grid)


def calc_neighbor_part_two(grid_stack: Dict[int, np.ndarray], lvl: int, coord: Coord):
    neighbors = 0
    shape = grid_stack[0].shape

    # The middle coordinate isn't technically part of the set, so we want to make sure it stays dead for when we count
    if coord == Coord(2, 2):
        return 0

    # left neighbor
    test_coord = coord + DIRECTIONS['L']
    # If it would try to go off the edge, get one level higher
    if not in_bounds(shape, test_coord):
        neighbors += get_relative(grid_stack, lvl-1)[Coord(2, 2)+DIRECTIONS['L']]
    # If the coord would be the center of the square, get the side of one level lower
    elif test_coord == Coord(2, 2):
        neighbors += get_relative(grid_stack, lvl+1)[:, -1].sum()
    else:
        neighbors += get_relative(grid_stack, lvl)[test_coord]

    # top neighbor
    test_coord = coord + DIRECTIONS['U']
    # If it would try to go off the edge, get one level higher
    if not in_bounds(shape, test_coord):
        neighbors += get_relative(grid_stack, lvl - 1)[Coord(2, 2)+DIRECTIONS['U']]
    # If the coord would be the center of the square, get the side of one level lower
    elif test_coord == Coord(2, 2):
        neighbors += get_relative(grid_stack, lvl + 1)[-1, :].sum()
    else:
        neighbors += get_relative(grid_stack, lvl)[test_coord]

    # right neighbor
    test_coord = coord + DIRECTIONS['R']
    # If it would try to go off the edge, get one level higher
    if not in_bounds(shape, test_coord):
        neighbors += get_relative(grid_stack, lvl - 1)[Coord(2, 2)+DIRECTIONS['R']]
    # If the coord would be the center of the square, get the side of one level lower
    elif test_coord == Coord(2, 2):
        neighbors += get_relative(grid_stack, lvl + 1)[:, 0].sum()
    else:
        neighbors += get_relative(grid_stack, lvl)[test_coord]

    # bottom neighbor
    test_coord = coord + DIRECTIONS['D']
    # If it would try to go off the edge, get one level higher
    if not in_bounds(shape, test_coord):
        neighbors += get_relative(grid_stack, lvl - 1)[Coord(2, 2)+DIRECTIONS['D']]
    # If the coord would be the center of the square, get the side of one level lower
    elif test_coord == Coord(2, 2):
        neighbors += get_relative(grid_stack, lvl + 1)[0, :].sum()
    else:
        neighbors += get_relative(grid_stack, lvl)[test_coord]

    return neighbors


def cull_grid_stack(grid_stack: Dict[int, np.ndarray]):
    for level in grid_stack.keys():
        if np.all(grid_stack[level] is False):
            del grid_stack[level]


def calc_neighbor_test(grid_stack, level):
    def _calc_neighbor_test(y, x):
        return calc_neighbor_part_two(grid_stack, level, Coord(y=y, x=x))
    return _calc_neighbor_test


def make_neighbor_stack_part_two(grid_stack: Dict[int, np.ndarray]) -> Dict[int, np.ndarray]:
    neighbor_stack = {}
    possible_growth_levels = set()

    for level in grid_stack.keys():
        neighbor_stack[level] = np.fromfunction(np.vectorize(calc_neighbor_test(grid_stack, level)),
                                                shape=grid_stack[0].shape, dtype=np.int)
        possible_growth_levels.add(level + 1)
        possible_growth_levels.add(level - 1)

    for level in possible_growth_levels.difference(grid_stack.keys()):
        neighbor_stack[level] = np.fromfunction(np.vectorize(calc_neighbor_test(grid_stack, level)),
                                                grid_stack[0].shape, dtype=np.int)

    return neighbor_stack


SCORE_MATRIX = np.full((25,), 2, dtype=np.int)
POWER_MATRIX = np.arange(25, dtype=np.int)
SCORE_MATRIX = np.power(SCORE_MATRIX, POWER_MATRIX)
SCORE_MATRIX = np.reshape(SCORE_MATRIX, (5, 5))


def score_board(grid: np.ndarray):
    return int(np.sum(SCORE_MATRIX, where=grid))


def part_one(data):
    grid = make_grid(data)
    seen_states = set()
    seen_states.add(int(score_board(grid)))
    while True:
        grid = evolve_board_part_one(grid)
        score = score_board(grid)
        if score in seen_states:
            return score
        else:
            seen_states.add(score)


def evolve_board_part_two(grid_stack: Dict[int, np.ndarray]):
    neighbor_stack = make_neighbor_stack_part_two(grid_stack)
    for level in neighbor_stack:
        grid_stack[level] = evolve_board(get_relative(grid_stack, level), neighbor_stack[level])


def part_two(data, num_iterations):
    grid_stack = {0: make_grid(data)}
    for i in range(num_iterations):
        print(f"Running generation {i+1}/{num_iterations}...")
        evolve_board_part_two(grid_stack)

    return sum(grid_stack[x].sum() for x in grid_stack)


SAMPLE_ONE = """....#
#..#.
#..##
..#..
#....""".split("\n")

SAMPLE_TWO = """.....
.....
.....
#....
.#...""".split("\n")


SAMPLE_THREE = """....#
#..#.
#..##
..#..
#....""".split("\n")

if __name__ == '__main__':
    DATA = read_data().split("\n")
    print(f"Biodiversity score for first repeat state is {part_one(DATA)}")
    print(f"Total count for part two after 200 generations is {part_two(DATA, 200)}")

