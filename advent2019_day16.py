from utils import read_data
from typing import List, Tuple, Generator
from itertools import islice

BASE_PATTERN = (0, 1, 0, -1)


def rightmost_digit(number: int) -> int:
    return abs(number) % 10


def pattern_gen(repeats: int):
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


def run_phases(input_signal: Tuple[int], phases: int):
    for _ in range(phases):
        input_signal = tuple(apply_pattern(input_signal))
    return input_signal


def run_phases_big(input_signal: Tuple[int], phases: int):
    offset = int("".join([str(x) for x in input_signal[:7]]))
    for i in range(phases):
        input_signal = tuple(apply_pattern(input_signal))
    return input_signal[offset:offset+8]


DATA = tuple(int(x) for x in read_data())
SAMPLE_ONE = tuple(int(x) for x in "12345678")
SAMPLE_TWO = tuple(int(x) for x in "80871224585914546619083218645595")
SAMPLE_THREE = tuple(int(x) for x in "19617804207202209144916044189917")
SAMPLE_FOUR = tuple(int(x) for x in "03036732577212944063491565474664"*10000)

print(run_phases(SAMPLE_TWO, 100))
print(run_phases_big(SAMPLE_FOUR, 100))

print(f"First eight digits of FFT'd data: {''.join(str(x) for x in run_phases(DATA, 100)[:8])}")

