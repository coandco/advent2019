from aocd import get_data
from pathlib import Path

# This is a standalone script meant to be run to automatically grab my data
# for a given year/day and dump it into an automatically-named file.

YEAR_NUM = 2019
DAY_NUM = 1

data = get_data(year=YEAR_NUM, day=DAY_NUM)

file_location = Path(f'inputs/advent{YEAR_NUM}_day{DAY_NUM:02d}_input.txt')
file_location.write_text(data)
