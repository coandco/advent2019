from utils import read_data

DATA = read_data().split("-")


def has_repeated_char(num):
    numstr = str(num)
    previous_digit = None
    for char in numstr:
        if char == previous_digit:
            return True
        else:
            previous_digit = char
    return False


def meets_part1_criteria(num):
    digits = [int(x) for x in str(num)]
    if not len(digits) == 6:
        return False
    if not has_repeated_char(num):
        return False
    lowest_digit = 0
    for digit in digits:
        if digit < lowest_digit:
            return False
        else:
            lowest_digit = digit
    return True


def meets_part2_criteria(number):
    numstr = str(number)
    previous_digit = None
    current_count = 0
    for char in numstr:
        if char == previous_digit:
            current_count += 1
        else:
            if current_count == 2:
                return True
            current_count = 1
            previous_digit = char
    if current_count == 2:
        return True
    return False


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
