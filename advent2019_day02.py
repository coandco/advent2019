from utils import read_data

DATA = [int(x) for x in read_data(__file__).split(",")]


class OpCodeBase(object):
    length = 0

    def __init__(self, tape, index):
        self.tape = tape
        self.index = index
        self.instruction = tape[index:index+self.length]

    def run(self):
        pass


class OpcodeAdd(OpCodeBase):
    length = 4

    def run(self):
        pos_one, pos_two, result_pos = self.instruction[1:self.length]
        self.tape[result_pos] = self.tape[pos_one] + self.tape[pos_two]
        return self.index + self.length


class OpcodeMultiply(OpCodeBase):
    length = 4

    def run(self):
        pos_one, pos_two, result_pos = self.instruction[1:self.length]
        self.tape[result_pos] = self.tape[pos_one] * self.tape[pos_two]
        return self.index + self.length


class OpcodeHalt(OpCodeBase):
    length = 1

    def run(self):
        return None  # Halt processing


OPCODES = {
    1: OpcodeAdd,
    2: OpcodeMultiply,
    99: OpcodeHalt
}


def process_instruction(tape, index):
    opcode = tape[index]
    if opcode in OPCODES:
        return OPCODES[opcode](tape, index).run()
    else:
        raise Exception(f"Unknown opcode {opcode} at position {index} on {tape}")


def run_tape(tape):
    curpos = 0
    while curpos is not None:
        curpos = process_instruction(tape, curpos)
    return tape


def run_tape_with_params(tape, noun, verb):
    tmptape = tape[:]
    tmptape[1] = noun
    tmptape[2] = verb
    return run_tape(tmptape)


def find_part2_combo(tape, desired_output):
    for i in range(100):
        for j in range(100):
            part2_output = run_tape_with_params(tape, i, j)
            if part2_output[0] == desired_output:
                return i, j
    raise Exception(f"Couldn\'t find noun/verb combination that resulted in {desired_output}")


part1_output = run_tape_with_params(DATA, 12, 2)
print(f"Zero pos is {part1_output[0]}")

noun, verb = find_part2_combo(DATA, 19690720)
print(f"noun is {noun}, verb is {verb}, Answer is {100 * noun + verb}")
