from utils import read_data
from advent2019_day09_intcode import run_tape

DATA = [int(x) for x in read_data().split(",")]
SAMPLE_ONE = [int(x) for x in "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99".split(",")]
SAMPLE_TWO = [int(x) for x in "1102,34915192,34915192,7,4,7,99,0".split(",")]
SAMPLE_THREE = [int(x) for x in "104,1125899906842624,99".split(",")]

if __name__ == '__main__':
    run_tape(DATA, [1])
    run_tape(DATA, [2])
