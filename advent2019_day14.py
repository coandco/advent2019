from utils import read_data
from collections import defaultdict
from typing import Dict, DefaultDict, Union
import math


class Reaction(object):
    def __init__(self, reaction_str: str):
        in_side, out_side = reaction_str.split(" => ")
        in_midpoint = [x.split(" ") for x in in_side.split(", ")]
        self.inputs = {x[1]: int(x[0]) for x in in_midpoint}
        self.output_amount, self.output_type = out_side.split(" ")
        self.output_amount = int(self.output_amount)


def get_ore_for_fuel(reactions: Dict[str, Reaction], extras_dict: Union[DefaultDict[str, int], None] = None,
                     starting_point="FUEL", amount_needed=1):
    if not extras_dict:
        extras_dict = defaultdict(int)
    total_ore = 0
    current_reaction = reactions[starting_point]
    if extras_dict[starting_point] < amount_needed:
        amount_actually_needed = amount_needed - extras_dict[starting_point]
        extras_dict[starting_point] = 0
    else:
        amount_actually_needed = 0
        extras_dict[starting_point] -= amount_needed
    multiple = math.ceil(amount_actually_needed / current_reaction.output_amount)
    mod = amount_actually_needed % current_reaction.output_amount
    extra_produced = current_reaction.output_amount - mod if mod else 0
    extras_dict[starting_point] += extra_produced
    for chem, amount in current_reaction.inputs.items():
        if chem == "ORE":
            total_ore += multiple * amount
        else:
            total_ore += get_ore_for_fuel(reactions, extras_dict, chem, multiple * amount)
    return total_ore


def binary_search(reactions, lo=0, hi=1_000_000_000_000):
    mid = (lo + hi) // 2
    while lo < hi:
        mid = (lo+hi)//2
        midval = 1_000_000_000_000 - get_ore_for_fuel(reactions, amount_needed=mid)
        if midval > 0:
            lo = mid+1
        elif midval < 0:
            hi = mid
        else:
            return mid
    return mid


if __name__ == '__main__':
    INPUT = [Reaction(x) for x in read_data().split("\n")]
    reactions_dict = {x.output_type: x for x in INPUT}
    total_ore = get_ore_for_fuel(reactions_dict, amount_needed=1)
    print(f"Ore required to produce one fuel: {total_ore}")
    fuel_produced = binary_search(reactions_dict)
    print(f"Most fuel that can be produces from one trillion ore: {fuel_produced}")


