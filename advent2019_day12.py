from utils import read_data
from typing import List, NamedTuple
from itertools import combinations
from functools import reduce
import math
import re

MOON_REGEX = re.compile(r'<x=(?P<x>[^,]*), y=(?P<y>[^,]*), z=(?P<z>[^>]*)>')


class MoonAxis(NamedTuple):
    pos: int
    vel: int

    @classmethod
    def velocity_change(cls, my_attr, other_attr):
        if my_attr < other_attr:
            return 1
        elif my_attr > other_attr:
            return -1
        else:
            return 0

    def update_velocity(self, other_moon: 'MoonAxis'):
        return MoonAxis(self.pos, self.vel + self.velocity_change(self.pos, other_moon.pos))

    def apply_velocity(self):
        return MoonAxis(self.pos + self.vel, self.vel)

    def __str__(self):
        return f"<{self.pos}, {self.vel}>"


class SystemAxis(object):
    def __init__(self, moons: List[MoonAxis]):
        self.moons = moons
        self.seen_configurations = set()
        self.seen_configurations.add(tuple(self.moons))

    def apply_gravity(self):
        for moon1, moon2 in combinations(range(len(self.moons)), 2):
            self.moons[moon1] = self.moons[moon1].update_velocity(self.moons[moon2])
            self.moons[moon2] = self.moons[moon2].update_velocity(self.moons[moon1])

    def update_positions(self):
        for i, moon in enumerate(self.moons):
            self.moons[i] = moon.apply_velocity()

    def tick(self):
        self.apply_gravity()
        self.update_positions()
        new_configuration = tuple(self.moons)
        if new_configuration in self.seen_configurations:
            return len(self.seen_configurations)
        else:
            self.seen_configurations.add(new_configuration)
            return None

    @property
    def positions(self):
        return [abs(moon.pos) for moon in self.moons]

    @property
    def velocities(self):
        return [abs(moon.vel) for moon in self.moons]

    def __str__(self):
        return "\n".join([str(x) for x in self.moons])


DATA = read_data().split("\n")

moon_list_x = []
moon_list_y = []
moon_list_z = []

for line in DATA:
    match = MOON_REGEX.match(line)
    moon_list_x.append(MoonAxis(pos=int(match.group('x')), vel=0))
    moon_list_y.append(MoonAxis(pos=int(match.group('y')), vel=0))
    moon_list_z.append(MoonAxis(pos=int(match.group('z')), vel=0))

axes = {'x': SystemAxis(moon_list_x), 'y': SystemAxis(moon_list_y), 'z': SystemAxis(moon_list_z)}
for _ in range(1000):
    for axis in axes:
        axes[axis].tick()

position_sums = [sum(x) for x in zip(*[axis.positions for axis in axes.values()])]
velocity_sums = [sum(x) for x in zip(*[axis.velocities for axis in axes.values()])]
total_energies = [pos*vel for pos, vel in zip(position_sums, velocity_sums)]
print(f'total energy after 1000 ticks is {sum(total_energies)}')

axes = {'x': SystemAxis(moon_list_x), 'y': SystemAxis(moon_list_y), 'z': SystemAxis(moon_list_z)}
repeat_values = []

for axis in axes:
    while True:
        repeat_seen = axes[axis].tick()
        if repeat_seen:
            print(f"Axis {axis} repeats at {repeat_seen} ticks")
            repeat_values.append(repeat_seen)
            break


# Cribbed from https://stackoverflow.com/a/147539
def lcm(a, b):
    return a * b // math.gcd(a, b)


print(f"Total repeat pattern is {reduce(lcm, repeat_values)}")
