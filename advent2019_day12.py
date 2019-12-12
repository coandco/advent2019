from utils import read_data
from typing import List, NamedTuple
from itertools import combinations
from functools import reduce
import re

MOON_REGEX = re.compile(r'<x=(?P<x>[^,]*), y=(?P<y>[^,]*), z=(?P<z>[^>]*)>')


class Position(NamedTuple):
    x: int
    y: int
    z: int


class Velocity(NamedTuple):
    x: int
    y: int
    z: int


class Moon(NamedTuple):
    pos: Position
    vel: Velocity

    @classmethod
    def velocity_change(cls, my_attr, other_attr):
        if my_attr < other_attr:
            return 1
        elif my_attr > other_attr:
            return -1
        else:
            return 0

    def update_velocities(self, other_moon: 'Moon'):
        new_x = self.vel.x + self.velocity_change(self.pos.x, other_moon.pos.x)
        new_y = self.vel.y + self.velocity_change(self.pos.y, other_moon.pos.y)
        new_z = self.vel.z + self.velocity_change(self.pos.z, other_moon.pos.z)
        return Moon(self.pos, Velocity(x=new_x, y=new_y, z=new_z))

    @property
    def energy(self):
        return (abs(self.pos.x) + abs(self.pos.y) + abs(self.pos.z)) * (abs(self.vel.x) + abs(self.vel.y) + abs(self.vel.z))

    def apply_velocity(self):
        new_x = self.pos.x + self.vel.x
        new_y = self.pos.y + self.vel.y
        new_z = self.pos.z + self.vel.z
        return Moon(Position(x=new_x, y=new_y, z=new_z), self.vel)

    def __str__(self):
        return f"Moon with position <{self.pos.x}, {self.pos.y}, {self.pos.z}> " + \
               f"and velocity <{self.vel.x}, {self.vel.y}, {self.vel.z}>"


class MoonSystem(object):
    def __init__(self, moons: List[Moon]):
        self.moons = moons

    def apply_gravity(self):
        for moon1, moon2 in combinations(range(len(self.moons)), 2):
            self.moons[moon1] = self.moons[moon1].update_velocities(self.moons[moon2])
            self.moons[moon2] = self.moons[moon2].update_velocities(self.moons[moon1])

    def update_positions(self):
        for i, moon in enumerate(self.moons):
            self.moons[i] = moon.apply_velocity()

    @property
    def total_energy(self):
        return sum([moon.energy for moon in self.moons])

    def tick(self):
        self.apply_gravity()
        self.update_positions()

    def __str__(self):
        return "\n".join([str(x) for x in my_moonsystem.moons])


DATA = read_data().split("\n")

moon_list = []
for line in DATA:
    match = MOON_REGEX.match(line)
    moon_position = Position(x=int(match.group('x')), y=int(match.group('y')), z=int(match.group('z')))
    moon_list.append(Moon(pos=moon_position, vel=Velocity(0, 0, 0)))

my_moonsystem = MoonSystem(moon_list)
#print(str(my_moonsystem) + "\n")
for _ in range(1000):
    my_moonsystem.tick()
    #print(str(my_moonsystem) + "\n")

print(f'total energy after 1000 ticks is {my_moonsystem.total_energy}')


# Second half requires simulating each axis independently to find patterns
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

    def __str__(self):
        return "\n".join([str(x) for x in self.moons])


moon_list_x = []
moon_list_y = []
moon_list_z = []


for line in DATA:
    match = MOON_REGEX.match(line)
    moon_list_x.append(MoonAxis(pos=int(match.group('x')), vel=0))
    moon_list_y.append(MoonAxis(pos=int(match.group('y')), vel=0))
    moon_list_z.append(MoonAxis(pos=int(match.group('z')), vel=0))

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
def lcmm(*args):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    def lcm(a, b):
        return a * b // gcd(a, b)

    return reduce(lcm, args)


print(f"Total repeat pattern is {lcmm(*repeat_values)}")
