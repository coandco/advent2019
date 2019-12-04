from utils import read_data
from collections import Counter

DATA = read_data().split("-")


def has_repeated_char(num):
    counts = Counter(str(num))
    return any((x > 1) for x in counts.values())


def meets_part1_criteria(num):
    digits = [int(x) for x in str(num)]
    lowest_digit = 0
    for digit in digits:
        if digit < lowest_digit:
            return False
        else:
            lowest_digit = digit

    # Once we hit this point, we know that the number is "sorted",
    # which means if there are two of a digit they're guaranteed to be next to each other
    if not has_repeated_char(num):
        return False
    return True


def meets_part2_criteria(num):
    counts = Counter(str(num))
    return 2 in counts.values()


if __name__ == '__main__':
    low = int(DATA[0])
    high = int(DATA[1])
    part1_passwords = []
    part2_passwords = []
    for number in range(low, high+1):
        if meets_part1_criteria(number):
            part1_passwords.append(number)
    for number in part1_passwords:
        part2_passwords = [x for x in part1_passwords if meets_part2_criteria(x)]
    print(len(part1_passwords))
    print(len(part2_passwords))
