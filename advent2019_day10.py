from utils import read_data

from typing import NamedTuple, Set, Union
from math import gcd
import numpy as np


class Coord(NamedTuple):
    y: int
    x: int


def generate_possible_angles(point: Coord, field_size: Coord) -> Set[Coord]:
    possible_angles = set()
    # Add cardinal directions that Fraction can't deal with
    possible_angles.update([Coord(0, 1), Coord(1, 0), Coord(0, -1), Coord(-1, 0)])
    for y in range(field_size.y):
        for x in range(field_size.x):
            if y == point.y or x == point.x:
                continue
            y_slope = y-point.y
            x_slope = x-point.x
            reduction_factor = gcd(y_slope, x_slope)
            possible_angles.add(Coord(y=y_slope//reduction_factor, x=x_slope//reduction_factor))
    return possible_angles


def in_bounds(point: Coord, field_size: Coord) -> bool:
    return 0 <= point.x < field_size.x and 0 <= point.y < field_size.y


def check_angle(from_loc: Coord, field_size: Coord, asteroids: Set[Coord], angle: Coord) -> Union[Coord, None]:
    curloc = from_loc
    while True:
        curloc = Coord(y=curloc.y+angle.y, x=curloc.x+angle.x)
        if in_bounds(curloc, field_size):
            if curloc in asteroids:
                return curloc
        else:
            return None


def count_detected(from_loc: Coord, field_size: Coord, asteroids: Set[Coord], angles: Set[Coord]) -> int:
    detected = 0
    for angle in angles:
        if check_angle(from_loc, field_size, asteroids, angle):
            detected += 1
    return detected


def get_best_asteroid(asteroid_field, field_size):
    highest_score = 0
    best = None
    for asteroid in asteroid_field:
        angles = generate_possible_angles(asteroid, field_size)
        asteroid_score = count_detected(asteroid, field_size, asteroid_field, angles)
        if asteroid_score > highest_score:
            highest_score = asteroid_score
            best = asteroid
    return highest_score, best


def kaboom_asteroids(asteroid_field: Set[Coord], starting_asteroid: Coord, field_size: Coord):
    def get_degrees(coord):
        degrees = np.angle(np.complex(-coord.y, coord.x), deg=True)
        return degrees if degrees >= 0 else degrees + 360
    sorted_angles = sorted(generate_possible_angles(starting_asteroid, field_size), key=get_degrees)
    kabooms = 0
    while True:
        for angle in sorted_angles:
            if doomed_asteroid := check_angle(starting_asteroid, field_size, asteroid_field, angle):
                kabooms += 1
                asteroid_field.remove(doomed_asteroid)
                print(f"OBLITERATED asteroid at {doomed_asteroid}. Doom clock at {kabooms}.")
                if kabooms == 200:
                    return doomed_asteroid


MAPPING = {"#": 1, ".": 0}
DATA = [[MAPPING[y] for y in x] for x in read_data().split("\n")]
SIZE = (Coord(y=len(DATA), x=len(DATA[0])))

data_array = np.array(DATA, dtype=np.int)
asteroids = set([Coord(y=x[0], x=x[1]) for x in np.argwhere(data_array == 1)])
score, best_asteroid = get_best_asteroid(asteroids, SIZE)
final_asteroid = kaboom_asteroids(asteroids, best_asteroid, SIZE)
print(f"highest score is {score} for asteroid at {best_asteroid}")
print(f"Final asteroid was at {final_asteroid}.  Number is {final_asteroid.x*100 + final_asteroid.y}.")

# Debug sanity check to make sure I was reading in correctly
# with np.printoptions(linewidth=2000, threshold=2000, formatter={'int': lambda x: "#" if x == 1 else "."}):
#     print(data_array)

