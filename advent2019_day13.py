from utils import read_data
from advent2019_day13_intcode import run_tape_generator
import numpy as np
import curses


DATA = [int(x) for x in read_data().split(",")]
DATA_PART_TWO = DATA[:]
DATA_PART_TWO[0] = 2

TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4

TILE_PRINT_DICT = {
    TILE_EMPTY: ' ',
    TILE_WALL: '#',
    TILE_BLOCK: '=',
    TILE_PADDLE: '_',
    TILE_BALL: 'o'
}


def print_screen(screen, score=0):
    with np.printoptions(linewidth=2000, threshold=2000, formatter={'int': lambda x: TILE_PRINT_DICT[x]}):
        test = str(screen)
        print(test)
    print(f"Score: {score}")


def print_screen_curses(curses_screen, screen, score):
    with np.printoptions(linewidth=2000, threshold=2000, formatter={'int': lambda x: TILE_PRINT_DICT[x]}):
        board_str = str(screen)
    curses_screen.addstr(0, 0, board_str)
    curses_screen.addstr(26, 2, f"Score: {score}")
    curses_screen.refresh()


def part_one(data, size):
    screen = np.zeros(size, dtype=np.int)
    program = run_tape_generator(data, num_outputs=3)
    next(program)  # Run generator to first yield
    pos_x = pos_y = tile_id = 0
    while True:
        try:
            pos_x, pos_y, tile_id = program.send(0)
        except StopIteration:
            break
        screen[pos_y, pos_x] = tile_id
    return screen


def get_next_input(ball_xpos, paddle_xpos):
    if ball_xpos > paddle_xpos:
        return 1
    elif ball_xpos < paddle_xpos:
        return -1
    else:
        return 0


def part_two(data):
    score = 0
    current_paddle_position = 0
    curses_screen = curses.initscr()
    program = run_tape_generator(data, num_outputs=3)
    next(program)  # Run generator to first yield

    paddle_input = 0
    while True:
        try:
            pos_x, pos_y, tile_id = program.send(paddle_input)
        except StopIteration:
            break
        if pos_x == -1 and pos_y == 0:
            score = tile_id
            curses_screen.addstr(26, 1, f"Score: {score}")
        else:
            if tile_id == TILE_PADDLE:
                current_paddle_position = pos_x
                paddle_input = 0
            elif tile_id == TILE_BALL:
                paddle_input = get_next_input(pos_x, current_paddle_position)
            curses_screen.addstr(pos_y, pos_x, TILE_PRINT_DICT[tile_id])
        curses_screen.refresh()
    return score


part_one_screen = part_one(DATA, (26, 40))
print(f"Number of block tiles: {np.count_nonzero(part_one_screen == TILE_BLOCK)}")

part_two_score = part_two(DATA_PART_TWO)
print(f"Score once game is finished: {part_two_score}")