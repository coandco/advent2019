from utils import read_data


def calc_fuel_stage_one(mass):
    return (mass // 3) - 2


def calc_fuel_stage_two(mass):
    current_amount = mass
    total_fuel = 0
    # The parenthesis here are needed so it doesn't try to assign
    # the boolean (adjusted_calc(foo) > 0) to new_amount
    while (new_amount := calc_fuel_stage_one(current_amount)) > 0:
        current_amount = new_amount
        total_fuel += new_amount
    return total_fuel


DATA = read_data(__file__).split("\n")

STAGE_ONE = [calc_fuel_stage_one(int(x)) for x in DATA]
total = sum(STAGE_ONE)
print(f'Stage one: {total}')

STAGE_TWO = [calc_fuel_stage_two(int(x)) for x in DATA]
total_two = sum(STAGE_TWO)
print(f'Stage two: {total_two}')
