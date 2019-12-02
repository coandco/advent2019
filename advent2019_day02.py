from utils import read_data

DATA = [int(x) for x in read_data(__file__).split(",")]


def run_tape(tape):
    curpos = 0
    while True:
        if tape[curpos] == 1:
            pos_one = tape[curpos+1]
            pos_two = tape[curpos+2]
            result_pos = tape[curpos+3]
            tape[result_pos] = tape[pos_one] + tape[pos_two]
            curpos += 4
        elif tape[curpos] == 2:
            pos_one = tape[curpos + 1]
            pos_two = tape[curpos + 2]
            result_pos = tape[curpos + 3]
            tape[result_pos] = tape[pos_one] * tape[pos_two]
            curpos += 4
        elif tape[curpos] == 99:
            break
        else:
            print(f'hit invalid opcode, tape looks like {".".join(tape)}')
            exit(1)
    return tape


def run_tape_two(tape, noun, verb):
    tmptape = tape[:]
    tmptape[1] = noun
    tmptape[2] = verb
    return run_tape(tmptape)


part1_data = DATA[:]
part1_data[1] = 12
part1_data[2] = 2
part1_final = run_tape(part1_data)
print(f"Zero pos is {part1_final[0]}")


for i in range(100):
    for j in range(100):
        part2_output = run_tape_two(DATA, i, j)
        if part2_output[0] == 19690720:
            print(f"i is {i}, j is {j}, Answer is {100 * i + j}")
            exit(0)



