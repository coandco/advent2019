from utils import read_data
from collections import defaultdict, namedtuple
from typing import List, DefaultDict, Dict


# Convenience class to parse instruction strings and provide friendly names for their components
class Instruction(object):
    def __init__(self, instruction_string):
        self.direction = instruction_string[0]
        self.amount = int(instruction_string[1:])


# NamedTuples are hashable, so they're suitable for dict keys
Coord = namedtuple('Coord', ['y', 'x'])
DIRECTIONS = {'U': Coord(-1, 0), 'R': Coord(0, 1), 'D': Coord(1, 0), 'L': Coord(0, -1)}


def go_in_direction(coord: Coord, direction: str) -> Coord:
    return Coord(x=coord.x+DIRECTIONS[direction].x, y=coord.y+DIRECTIONS[direction].y)


def process_instruction(grid: DefaultDict[Coord, Dict], thread_id: int, curpos: Coord,
                        steps: int, instruction: Instruction) -> Coord:
    for _ in range(instruction.amount):
        curpos = go_in_direction(curpos, instruction.direction)
        steps += 1
        if thread_id not in grid[curpos]:
            grid[curpos][thread_id] = steps
    return curpos



def process_data(data: List[List[str]]) -> DefaultDict[Coord, Dict]:
    """
    This will return a defaultdict of visited coordinates and the number of steps each thread took to get there
    For example, if only thread 0 had visited location (4,5) and it took 9 steps to get there:
    grid[Coord(y=4,x=5)] = {0: 9}

    If both threads have visited coordinate (25,100), with one taking 322 steps and the other 453:
    grid[Coord(y=25,x=100)] = {0: 322, 1: 453}
    """
    grid = defaultdict(dict)
    for thread_id, instruction_list in enumerate(data):
        current_pos = Coord(y=0, x=0)
        steps = 0
        for instruction_str in instruction_list:
            instruction = Instruction(instruction_str)
            current_pos = process_instruction(grid, thread_id, current_pos, steps, instruction)
            steps += instruction.amount
    return grid


if __name__ == '__main__':
    DATA = [x.split(",") for x in read_data().split("\n")]
    filled_grid = process_data(DATA)
    # Any dict value that has more than one thread's steps recorded is an intersection
    intersections = [key for (key, value) in filled_grid.items() if len(value) > 1]
    distances = [abs(coord.y)+abs(coord.x) for coord in intersections]
    print(f'Smallest Manhattan Distance: {min(distances)}')

    # Each grid location has the number of steps each thread took to get there
    combined_steps = [sum(filled_grid[intersection].values()) for intersection in intersections]
    print(f'Smallest Combined Steps: {min(combined_steps)}')
