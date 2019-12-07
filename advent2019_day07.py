from utils import read_data
from advent2019_day07_intcode import run_tape, run_sequence, run_sequence_with_feedback
from itertools import permutations

DATA = [int(x) for x in read_data().split(",")]

SAMPLE_ONE = [int(x) for x in "3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0".split(",")]
SAMPLE_TWO = [int(x) for x in "3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0".split(",")]
SAMPLE_THREE = [int(x) for x in "3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,"
                                "33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0".split(",")]
SAMPLE_FOUR = [int(x) for x in "3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,"
                               "28,6,99,0,0,5".split(",")]
SAMPLE_FIVE = [int(x) for x in "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,"
                               "1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,"
                               "56,1005,56,6,99,0,0,0,0,10".split(",")]

if __name__ == '__main__':
    max_output = 0
    # output = run_sequence(SAMPLE_ONE, [4,3,2,1,0])
    # output = run_sequence(SAMPLE_TWO, [0,1,2,3,4])
    # output = run_sequence(SAMPLE_THREE, [1,0,4,3,2])
    # output = run_sequence_with_feedback(SAMPLE_FOUR, [9,8,7,6,5])
    # output = run_sequence_with_feedback(SAMPLE_FIVE, [9,7,8,5,6])

    for amp_order in permutations([0, 1, 2, 3, 4]):
        output = run_sequence(DATA, amp_order)
        if output > max_output:
            max_output = output
    print(f"Stage one max output is {max_output}")

    max_output = 0
    for amp_order in permutations([5, 6, 7, 8, 9]):
        output = run_sequence_with_feedback(DATA, amp_order)
        if output > max_output:
            max_output = output

    print(f"Stage two max output is {max_output}")

