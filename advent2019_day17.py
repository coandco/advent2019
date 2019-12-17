from utils import read_data
from advent2019_day17_intcode import run_tape_generator, run_tape
from typing import NamedTuple


class Coord(NamedTuple):
    y: int
    x: int

    def calibration(self):
        return self.y * self.x


def get_view(program):
    outstr = ""
    while True:
        try:
            outstr += chr(program.send(0)[0])
        except StopIteration:
            break
    return outstr


def detect_intersections(picture):
    intersections = []
    for y, line in enumerate(picture):
        for x, char in enumerate(line):
            if char == "#":
                try:
                    above = picture[y-1][x]
                    below = picture[y+1][x]
                    left = picture[y][x-1]
                    right = picture[y][x+1]
                    if above == below == left == right == "#":
                        intersections.append(Coord(y=y, x=x))
                except IndexError:
                    # If one of the squares adjacent to a # is out of bounds, obviously this isn't an intersection
                    continue
    return intersections


DATA = [int(x) for x in read_data().split(",")]

camera = run_tape_generator(DATA, num_outputs=1)
next(camera)

camera_view = get_view(camera).split("\n")
all_intersections = detect_intersections(camera_view)
print("\n".join(camera_view))
print(f"calibration value is {sum(x.calibration() for x in all_intersections)}")

# Turn on vacuum robot
DATA[0] = 2
# Full path:
# L,10,L,12,R,6,R,10,L,4,L,4,L,12,L,10,L,12,R,6,R,10,L,4,L,4,L,12,L,10,L,12,R,6,L,10,R,10,R,6,L,4,R,10,
# L,4,L,4,L,12,L,10,R,10,R,6,L,4,L,10,L,12,R,6,L,10,R,10,R,6,L,4
#
# Factoring program A out:
# L,10,L,12,R,6,R,10,L,4,L,4,L,12,L,10,L,12,R,6,R,10,L,4,L,4,L,12,L,10,L,12,R,6,<A>,R,10,
# L,4,L,4,L,12,<A>,L,10,L,12,R,6,<A>
#
# Factoring program B out:
# <B>,R,10,L,4,L,4,L,12,<B>,R,10,L,4,L,4,L,12,<B>,<A>,R,10,L,4,L,4,L,12,<A>,<B>,<A>
#
# Factoring program C out:
# <B>,<C>,<B>,<C>,<B>,<A>,<C>,<A>,<B>,<A>
part2_input = [ord(x) for x in """B,C,B,C,B,A,C,A,B,A
L,10,R,10,R,6,L,4
L,10,L,12,R,6
R,10,L,4,L,4,L,12
n
"""]
_, _, dust_amount, _ = run_tape(DATA, part2_input)
print(f"Dust amount: {dust_amount}")



