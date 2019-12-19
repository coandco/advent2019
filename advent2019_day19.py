from utils import read_data
from advent2019_day19_intcode import run_tape_generator
from typing import NamedTuple, Dict, Union, Set
import numpy as np

DATA = [int(x) for x in read_data().split(",")]


class Coord(NamedTuple):
    y: int
    x: int


def print_grid(to_print):
    with np.printoptions(linewidth=2000, threshold=20000,
                         formatter={'int': lambda x: "#" if x else "."}):
        test = str(to_print)
        print(test)


def get_value_at_location(loc):
    detector = run_tape_generator(DATA, num_outputs=1)
    next(detector)
    return detector.send([loc.x, loc.y])[0]


def part_one():
    grid = np.zeros((50, 50), dtype=int)

    for y, x in np.ndindex(grid.shape):
        grid[y, x] = get_value_at_location(Coord(y=y, x=x))
    #print_grid(grid)
    return np.count_nonzero(grid == 1)


PRINT_DICT = {
    0: '.',
    1: '#'
}


# Borrowed from peter200lx's point-cloud-print function
def print_cloud(map: Set[Coord]) -> str:
    min_x = min(key.x for key in map)
    min_y = min(key.y for key in map)
    max_x = max(key.x for key in map)
    max_y = max(key.y for key in map)
    lines = []
    for row in range(min_y, max_y + 1):
        line = (1 if Coord(row, x) in map else 0 for x in range(min_x, max_x + 1))
        lines.append(f"{row:0>3}: " + "".join(PRINT_DICT[i] for i in line))
    return "\n".join(lines)


def follow_beam(starting_line, start_guess=0, end_guess=None):
    beam_start = start_guess
    beam_end = end_guess
    current_line = starting_line
    while True:
        while not get_value_at_location(Coord(y=current_line, x=beam_start)):
            beam_start += 1
        if beam_end is None:
            beam_end = beam_start
        while get_value_at_location(Coord(y=current_line, x=beam_end)):
            beam_end += 1
        yield beam_start, beam_end, current_line
        current_line += 1


def part_two():
    # grid = np.zeros((50, 50), dtype=int)
    desired_difference = 100
    start_line = 970

    # For debugging purposes
    #
    # printer = follow_beam(start_line)
    # pointcloud = set()
    # for _ in range(desired_difference):
    #     beam_start, beam_end, current_line = next(printer)
    #     for x in range(beam_start, beam_end):
    #         pointcloud.add(Coord(y=current_line, x=x))
    # print(print_cloud(pointcloud))

    beam_top = follow_beam(start_line)
    # We use desired_difference-1 because this is inclusive -- lines 100-109 are 10 tall
    beam_bottom = follow_beam(start_line+(desired_difference-1))

    while True:
        top_start, top_end, current_top_line = next(beam_top)
        bottom_start, bottom_end, current_bottom_line = next(beam_bottom)
        # print(f"top line {current_top_line} starts at {top_start} and ends at {top_end}, for width {top_end-top_start}")
        # print(f"bottom line {current_bottom_line} starts at {bottom_start} and ends at {bottom_end}, for width {bottom_end-bottom_start}")
        # print(f"difference is {top_end-bottom_start}")
        # print(f"Origin coord would be {Coord(y=current_top_line, x=top_end-desired_difference)}")
        if top_end-bottom_start == desired_difference:
            return Coord(y=current_top_line, x=top_end-desired_difference)



print(f"Number of beam squares in a 50x50 grid: {part_one()}")
ship_origin = part_two()
print(f"Ship origin coord is {ship_origin}, which results in output {(ship_origin.x*10000 + ship_origin.y)}")
