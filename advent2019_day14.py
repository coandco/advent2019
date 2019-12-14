from utils import read_data
from collections import defaultdict
from typing import Dict, DefaultDict


class Reaction(object):
    def __init__(self, reaction_str: str):
        in_side, out_side = reaction_str.split(" => ")
        in_midpoint = [x.split(" ") for x in in_side.split(", ")]
        self.inputs = {x[1]: int(x[0]) for x in in_midpoint}
        self.output_amount, self.output_type = out_side.split(" ")
        self.output_amount = int(self.output_amount)


def get_ore_for_fuel(reactions_dict: Dict[str, Reaction], extras_dict: DefaultDict[str, int],
                     starting_point="FUEL", amount_needed=1):
    total_ore = 0
    current_reaction = reactions_dict[starting_point]
    if extras_dict[starting_point] < amount_needed:
        amount_actually_needed = amount_needed - extras_dict[starting_point]
        extras_dict[starting_point] = 0
    else:
        amount_actually_needed = 0
        extras_dict[starting_point] -= amount_needed
    multiple = amount_actually_needed // current_reaction.output_amount
    mod = amount_actually_needed % current_reaction.output_amount
    if mod:
        multiple += 1
    extra_produced = current_reaction.output_amount - mod if mod else 0
    extras_dict[starting_point] += extra_produced
    for chem, amount in current_reaction.inputs.items():
        if chem == "ORE":
            total_ore += multiple * amount
        else:
            total_ore += get_ore_for_fuel(reactions_dict, extras_dict, chem, multiple * amount)
    return total_ore


INPUT = [Reaction(x) for x in read_data().split("\n")]
SAMPLE_ONE = [Reaction(x) for x in """10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL""".split("\n")]
SAMPLE_TWO = [Reaction(x) for x in """9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL""".split("\n")]
SAMPLE_THREE = [Reaction(x) for x in """157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""".split("\n")]


reactions_dict = {x.output_type: x for x in INPUT}
extras_dict = defaultdict(int)
total_ore = get_ore_for_fuel(reactions_dict, extras_dict)
print(total_ore)
part_two_ore_left = 1_000_000_000_000
extras_dict = defaultdict(int)


def binary_search(reactions_dict, extras_dict, lo=0, hi=1_000_000_000_000):
    while lo < hi:
        mid = (lo+hi)//2
        midval = 1_000_000_000_000 - get_ore_for_fuel(reactions_dict, extras_dict, amount_needed=mid)
        if midval > 0:
            lo = mid+1
        elif midval < 0:
            hi = mid
        else:
            return mid
    return mid


fuel_produced = binary_search(reactions_dict, extras_dict)
print(fuel_produced)


