from utils import read_data
from typing import List


def cut_stack(stack, cut_location):
    return stack[cut_location:] + stack[:cut_location]


def deal_increment(stack, increment):
    new_stack = [None]*len(stack)
    i = 0
    for value in stack:
        if new_stack[i] is not None:
            raise Exception(f"deal increment hit already-filled value {new_stack[i]} at position {i}")
        new_stack[i] = value
        i += increment
        i %= len(stack)
    return new_stack


def deal_new(stack):
    return list(reversed(stack))


def part_one(data: List[str], deck_size: int):
    stack = list(range(deck_size))
    for line in data:
        print(line)
        if line.startswith("deal into new stack"):
            stack = deal_new(stack)
        elif line.startswith("deal with increment "):
            increment = int(line[len("deal with increment "):])
            stack = deal_increment(stack, increment)
        elif line.startswith("cut "):
            cut_location = int(line[len("cut "):])
            stack = cut_stack(stack, cut_location)
        else:
            raise Exception(f"Unknown instruction {line}")

    return stack.index(2019)


def part_two(data: List[str], deck_size: int, repetitions: int, final_card_position: int):
    # I don't actually understand this logic.  This part had zero chance of being solved by programming techniques --
    # the numbers are so huge that understanding data structures or good algorithms was completely, ridiculously
    # insufficient for the task of completing it.  Instead, you have to recognize that the operations correspond to
    # linear equations and apply arcane mathematical transforms to them to get your answer.  I copied the essential
    # parts of this function from peter200lx's solution (and he got it from reddit).
    offset = 0
    increment = 1
    for line in data:
        if line.startswith("deal into new stack"):
            increment *= -1
            offset += increment
        elif line.startswith("deal with increment "):
            increment_param = int(line[len("deal with increment "):])
            increment *= pow(increment_param, deck_size - 2, deck_size)
        elif line.startswith("cut "):
            cut_location = int(line[len("cut "):])
            offset += increment * cut_location
        else:
            raise Exception(f"Unknown instruction {line}")
    offset *= pow(1 - increment, deck_size - 2, deck_size)
    increment = pow(increment, repetitions, deck_size)
    return (final_card_position * increment + (1 - increment) * offset) % deck_size


if __name__ == '__main__':
    DATA = read_data().split("\n")
    print(f"Index of item 2019 is {part_one(DATA, 10007)}")
    print(f"Card at index 2019 is {part_two(DATA, 119315717514047, 101741582076661, 2020)}")