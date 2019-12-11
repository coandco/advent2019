from utils import read_data
from pathlib import Path
from typing import NamedTuple, List
from advent2019_day11_intcode import run_tape_generator
from collections import defaultdict
import numpy as np


class Coord(NamedTuple):
    y: int
    x: int


DATA = [int(x) for x in read_data().split(",")]

PANEL_BLACK = 0
PANEL_WHITE = 1

TURN_LEFT = 0
TURN_RIGHT = 1
DIRECTIONS = {'^': Coord(-1, 0), '>': Coord(0, 1), 'v': Coord(1, 0), '<': Coord(0, -1)}
TURN_DIRECTIONS = [{'^': '<', '<': 'v', 'v': '>', '>': '^'}, {'^': '>', '>': 'v', 'v': '<', '<': '^'}]


def go_in_direction(coord: Coord, direction: str) -> Coord:
    return Coord(x=coord.x+DIRECTIONS[direction].x, y=coord.y+DIRECTIONS[direction].y)


def run_painter(tape: List[int], initial_square=PANEL_BLACK):
    field = defaultdict(int)
    painted_locations = set()
    curloc = Coord(0, 0)
    curdir = '^'
    field[curloc] = initial_square
    program = run_tape_generator(tape)
    # Initialize the generator so it's ready to accept input
    next(program)
    while True:
        try:
            color, direction = program.send(field[curloc])
        except StopIteration:
            break
        field[curloc] = color
        painted_locations.add(curloc)
        curdir = TURN_DIRECTIONS[direction][curdir]
        curloc = go_in_direction(curloc, curdir)
    return field, painted_locations


if __name__ == '__main__':
    _, touched_locs = run_painter(DATA)
    print(f"Number of painted locations with black initial square: {len(touched_locs)}")
    completed_field, _ = run_painter(DATA, PANEL_WHITE)
    just_white_panels = [x for x in completed_field if completed_field[x] == PANEL_WHITE]
    # Ordinarily I'd need to worry about min values as well, but I eyeballed just_white_panels
    # and it doesn't have any negative values
    max_x = max([coord.x for coord in just_white_panels])
    max_y = max([coord.y for coord in just_white_panels])
    # Using numpy just for convenient output
    field = np.zeros((max_y+1, max_x+1), dtype=np.int)
    for coord in just_white_panels:
        field[coord.y, coord.x] = 1
    with np.printoptions(linewidth=2000, threshold=2000, formatter={'int': lambda x: "#" if x == 1 else "."}):
        print(field)
