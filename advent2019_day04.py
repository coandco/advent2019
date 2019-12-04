from utils import read_data
from collections import Counter

DATA = read_data().split("-")


def has_repeated_char(numstr):
    counts = Counter(numstr)
    return any((x > 1) for x in counts.values())


def meets_part1_criteria(numstr):
    digits = [int(x) for x in numstr]
    lowest_digit = 0
    for digit in digits:
        if digit < lowest_digit:
            return False
        else:
            lowest_digit = digit

    # Once we hit this point, we know that the number is "sorted",
    # which means if there are two of a digit they're guaranteed to be next to each other
    if not has_repeated_char(numstr):
        return False
    return True


def meets_part2_criteria(numstr):
    counts = Counter(numstr)
    return 2 in counts.values()


if __name__ == '__main__':
    low = int(DATA[0])
    high = int(DATA[1])
    part1_passwords = []
    part2_passwords = []
    for number in range(low, high+1):
        if meets_part1_criteria(str(number)):
            part1_passwords.append(str(number))
    for number in part1_passwords:
        part2_passwords = [x for x in part1_passwords if meets_part2_criteria(x)]
    print(len(part1_passwords))
    print(len(part2_passwords))
