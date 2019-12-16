from utils import read_data
from typing import List, Tuple, Generator
import time

BASE_PATTERN = (0, 1, 0, -1)


def rightmost_digit(number: int) -> int:
    return abs(number) % 10


def original_pattern_gen(repeats: int):
    first_run = True
    while True:
        for item in BASE_PATTERN:
            for _ in range(repeats-1 if first_run else repeats):
                yield item
            first_run = False


def chunk_gen(pattern: Tuple[int], repeats: int) -> Generator[int, None, None]:
    starting_location = repeats - 1
    current_location = starting_location
    current_multiplier = 1
    while current_location < len(pattern):
        yield sum(pattern[current_location:current_location+repeats])*current_multiplier
        current_location += 2*repeats
        current_multiplier *= -1


def apply_pattern(input_signal: Tuple[int]) -> Generator[int, None, None]:
    current_multiplier = 1
    num_digits = len(input_signal)
    for _ in range(num_digits):
        digit = rightmost_digit(sum(chunk_gen(input_signal, current_multiplier)))
        yield digit
        current_multiplier += 1


# For any given offset, you can ignore all digits before that offset when calculating the digits for said offset,
# because the pattern for those digits will always have 0 as its modifier
def apply_pattern_cheat(input_signal: Tuple[int], offset: int) -> Generator[int, None, None]:
    num_digits = len(input_signal)
    for _ in range(offset):
        yield 0
    current_multiplier = offset + 1
    for _ in range(offset, num_digits):
        digit = rightmost_digit(sum(chunk_gen(input_signal, current_multiplier)))
        yield digit
        current_multiplier += 1


# For any offset past half, each digit is calculated by summing all the digits after it and modding by 10.
# We can thus calculate backwards from the end by keeping a running total of the last digit of the sums.
def apply_pattern_extra_cheat(input_signal: Tuple[int]):
    num_digits = len(input_signal)
    new = list(input_signal[:])
    for i in range(num_digits-2, -1, -1):
        new[i] = (input_signal[i] + new[i+1]) % 10
    return tuple(new)


def run_phases(input_signal: Tuple[int], phases: int):
    for _ in range(phases):
        input_signal = tuple(apply_pattern(input_signal))
    return input_signal


def run_phases_big(input_signal: Tuple[int], offset: int, phases: int):
    for i in range(phases):
        print(f"starting phase {i}")
        start_time = time.time()
        input_signal = tuple(apply_pattern_cheat(input_signal, offset))
        end_time = time.time()
        print(f"phase {i}/{phases} took {end_time-start_time} seconds")
    return input_signal[offset:offset+8]


def run_phases_extra_cheat(input_signal: Tuple[int], offset:int, phases:int):
    if offset < len(input_signal)//2:
        raise Exception("Extra cheat method only works on the latter half of the array")
    working_set = tuple(input_signal[offset:])
    for i in range(phases):
        start_time = time.time()
        working_set = apply_pattern_extra_cheat(working_set)
        end_time = time.time()
        print(f"phase {i}/{phases} took {end_time - start_time} seconds")
    return working_set[:8]


DATA = tuple(int(x) for x in read_data())
DATA_BIG = tuple(int(x) for x in read_data()*10000)
SAMPLE_ONE = tuple(int(x) for x in "12345678")
SAMPLE_TWO = tuple(int(x) for x in "80871224585914546619083218645595")
SAMPLE_THREE = tuple(int(x) for x in "19617804207202209144916044189917")
SAMPLE_FOUR = tuple(int(x) for x in "03036732577212944063491565474664"*10000)


print(f"First eight digits of FFT'd data: {''.join(str(x) for x in run_phases(DATA, 100)[:8])}")
offset = int("".join([str(x) for x in DATA_BIG[:7]]))
message = ''.join(str(x) for x in run_phases_extra_cheat(DATA_BIG, offset, 100))
print(f"Part two message at offset {offset}: {message}")
