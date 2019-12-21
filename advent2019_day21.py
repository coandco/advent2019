from utils import read_data
from advent2019_day21_intcode import run_tape

DATA = [int(x) for x in read_data().split(",")]


def part_one(data):
    input = """NOT A J
NOT B T
OR T J
NOT C T
OR T J
AND D J
WALK
    """
    _, _, output, _ = run_tape(DATA, [ord(x) for x in input])
    return output


def part_two(data):
    input = """NOT A J
NOT B T
OR T J
NOT C T
OR T J
AND D J
NOT H T
NOT T T
OR E T
AND T J
RUN
    """
    _, _, output, _ = run_tape(data, [ord(x) for x in input])
    return output


print(f"Hull damage from part one: {part_one(DATA)}")
print(f"Hull damage from part two: {part_two(DATA)}")

