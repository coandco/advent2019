from utils import read_data
from advent2019_day15_intcode import run_tape_generator
from typing import NamedTuple, Generator, Dict, Tuple, Union
import numpy as np
from readchar import readkey
import os
import sys
import shutil
import curses


SCREEN_TTY = sys.stdout.isatty()
SCREEN_SIZE = shutil.get_terminal_size((0, 0))


class Coord(NamedTuple):
    y: int
    x: int

    def __add__(self, other: 'Coord'):
        return Coord(y=self.y + other.y, x=self.x + other.x)

    def __mul__(self, other: int):
        return Coord(y=self.y*other, x=self.x*other)


DIRECTION_NUMS = {
    '^': 1,
    'v': 2,
    '<': 3,
    '>': 4
}

DIRECTION_DELTAS = {
    '^': Coord(-1, 0),
    'v': Coord(1, 0),
    '<': Coord(0, -1),
    '>': Coord(0, 1),
}

DELTA_DIRECTIONS = {
    Coord(-1, 0): '^',
    Coord(1, 0): 'v',
    Coord(0, -1): '<',
    Coord(0, 1): '>',
}

KEYS_TO_DIRECTIONS = {
    '\x1b[A': '^',
    '\x1b[B': 'v',
    '\x1b[D': '<',
    '\x1b[C': '>',
    'w': '^',
    's': 'v',
    'a': '<',
    'd': '>',
    '^': '^',
    'v': 'v',
    '<': '<',
    '>': '>'
}

GRID_UNKNOWN = 0
GRID_FLOOR = -1
GRID_WALL = -2
GRID_OXY = -3
GRID_DROID = -4

GRID_PRINT_DICT = {
    GRID_UNKNOWN: " ",
    GRID_FLOOR: ".",
    GRID_WALL: "#",
    GRID_OXY: "!",
    GRID_DROID: "@"
}

NUMPY_PRINT_DICT = {
    GRID_UNKNOWN: " ",
    GRID_FLOOR: "...",
    GRID_WALL: "###",
    GRID_OXY: "!!!",
    GRID_DROID: "@"
}

RESULT_WALL = 0
RESULT_FLOOR = 1
RESULT_OXY = 2


def normalize_map(map: Dict[Coord, int], droid_loc: Coord = Coord(0, 0),
                  adjustment: Union[Coord, None] = None) -> Tuple[Dict[Coord, int], Coord, Coord, Union[Coord, None]]:
    max_x = max(key.x for key in map)
    max_y = max(key.y for key in map)
    if not adjustment:
        min_x = min(key.x for key in map)
        min_y = min(key.y for key in map)
        adjustment = Coord(y=-min_y if min_y < 0 else 0, x=-min_x if min_x < 0 else 0)
    new_map = {key+adjustment: map[key] for key in map}
    return new_map, adjustment, Coord(y=max_y+adjustment.y, x=max_x+adjustment.x), droid_loc + adjustment if droid_loc else None


def print_map(map: Dict[Coord, int], droid_loc: Union[Coord, None] = None,
              steps_map: Union[Dict[Coord, int], None] = None):
    normalized_map, adjustment, size, droid_loc = normalize_map(map, droid_loc=droid_loc)
    to_print = np.zeros((size.y+1, size.x+1), dtype=np.int)
    for key, value in normalized_map.items():
        to_print[key.y, key.x] = value
    if steps_map:
        normalized_steps, _, _, _ = normalize_map(steps_map, adjustment=adjustment)
        for key, value in normalized_steps.items():
            to_print[key.y, key.x] = value
    if droid_loc is not None:
        to_print[droid_loc.y, droid_loc.x] = GRID_DROID
    with np.printoptions(linewidth=2000, threshold=2000, formatter={'int': lambda x: f"{NUMPY_PRINT_DICT[x] if x <= 0 else str(x):>3}"}):
        test = str(to_print)
        print(test)


# Borrowed from peter200lx's point-cloud-print function
def map_to_str(map: Dict[Coord, int], droid_loc: Union[Coord, None] = None) -> str:
    if droid_loc:
        map = map.copy()
        map[droid_loc] = GRID_DROID
    min_x = min(key.x for key in map)
    min_y = min(key.y for key in map)
    max_x = max(key.x for key in map)
    max_y = max(key.y for key in map)
    lines = []
    for row in range(min_y, max_y + 1):
        line = (map.get(Coord(row, x), 0) for x in range(min_x, max_x + 1))
        lines.append("".join(GRID_PRINT_DICT[i] for i in line))
    return "\n".join(lines)


def process_result(discovered_map, steps_map, droid_pos, command, result):
    attempted_pos = droid_pos + DIRECTION_DELTAS[command]
    current_steps = steps_map.get(droid_pos, 0)
    if result == RESULT_WALL:
        discovered_map[attempted_pos] = GRID_WALL
        return droid_pos, False
    elif result == RESULT_FLOOR:
        discovered_map[attempted_pos] = GRID_FLOOR
        if attempted_pos not in steps_map:
            steps_map[attempted_pos] = current_steps + 1
        return attempted_pos, False
    elif result == RESULT_OXY:
        discovered_map[attempted_pos] = GRID_OXY
        if attempted_pos not in steps_map:
            steps_map[attempted_pos] = current_steps + 1
        return attempted_pos, True


def execute_command(program: Generator[int, int, None], direction: str) -> int:
    return program.send(DIRECTION_NUMS[direction])


def clear_screen():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')


def stumbler(discovered_map, starting_pos):
    current_pos = starting_pos
    already_traversed = set(starting_pos)
    path = []
    while True:
        successful_move = False
        for key, delta in DIRECTION_DELTAS.items():
            tile = discovered_map.get(current_pos+delta, 0)
            if tile == GRID_WALL or current_pos+delta in already_traversed:
                continue
            else:
                # Try to go in that direction
                new_pos = yield key
                if new_pos == current_pos:
                    continue
                else:
                    current_pos = new_pos
                    path.append(delta)
                    already_traversed.add(current_pos)
                    successful_move = True
                    break
        if successful_move:
            continue
        # If we've reacted this, we've tried to go in all four directions and hit walls or already-traversed spots
        # Try to backtrack if we can
        if len(path) > 0:
            backtrack_direction = path.pop()*-1
            current_pos = current_pos+backtrack_direction
            yield DELTA_DIRECTIONS[backtrack_direction]
        else:
            # If we've tried all four directions and can't backtrack, we've explored the whole map, so stop iteration
            break
    return 'q'


def explore_map(program: Generator[int, int, None],
                discovered_map: Union[Dict[Coord, int], None] = None,
                steps_map: Union[Dict[Coord, int], None] = None,
                starting_pos: Coord = Coord(0, 0),
                manual_explore=True):
    if not discovered_map:
        discovered_map = {Coord(0, 0): GRID_FLOOR}
    if not steps_map:
        steps_map = {Coord(0, 0): 0}
    droid_pos = starting_pos
    if SCREEN_TTY and SCREEN_SIZE[1] >= 40:
        screen = curses.initscr()
        screen.addstr(0, 0, map_to_str(discovered_map, droid_pos))
        screen.refresh()
    else:
        clear_screen()
        #print(map_to_str(discovered_map, droid_pos))
        print_map(discovered_map, droid_pos, steps_map)
    agent = stumbler(discovered_map, droid_pos)
    if manual_explore:
        c = readkey()
    else:
        c = next(agent)

    while c != 'q':
        if c == 'q':
            print(f"Exited at {droid_pos} with step count {steps_map[droid_pos]}")
            exit(1)
        if c not in KEYS_TO_DIRECTIONS:
            continue
        c = KEYS_TO_DIRECTIONS[c]
        result = execute_command(program, c)[0]
        droid_pos, found_oxy = process_result(discovered_map, steps_map, droid_pos, c, result)
        if SCREEN_TTY and SCREEN_SIZE[1] >= 40:
            screen.addstr(0, 0, map_to_str(discovered_map, droid_pos))
            screen.refresh()
        else:
            clear_screen()
            #print(map_to_str(discovered_map, droid_pos))
            print_map(discovered_map, droid_pos, steps_map)

        if found_oxy:
            return discovered_map, steps_map, droid_pos
        if manual_explore:
            c = readkey()
        else:
            try:
                c = agent.send(droid_pos)
            except StopIteration:
                return discovered_map, steps_map, droid_pos


DATA = [int(x) for x in read_data().split(",")]
droid = run_tape_generator(DATA)
next(droid)  # Initialize droid to first input

map, steps, oxy_pos = explore_map(droid, manual_explore=False)
print(f"Oxygen machine is {steps[oxy_pos]} away from start")

final_map, steps, final_pos = explore_map(droid, discovered_map=map, starting_pos=oxy_pos, manual_explore=False)
print(f"Oxygen takes {max(steps.values())} to reach all of the level")

print_map(final_map, final_pos, steps)

