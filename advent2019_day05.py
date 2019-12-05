from utils import read_data
from typing import List, Tuple


def interpret_opcode(opcode: int) -> Tuple[int, List[int]]:
    base_opcode = opcode % 100
    modes = opcode // 100
    modes_array = []
    while modes > 0:
        modes_array.append(modes % 10)
        modes = modes // 10
    return base_opcode, modes_array


MODE_POSITION = 0
MODE_IMMEDIATE = 1


class OpCodeBase(object):
    length = 0

    def __init__(self, tape, index, input):
        self.tape = tape
        self.index = index
        self.instruction = tape[index:index+self.length]
        self.input = input
        self.opcode, self.modes = interpret_opcode(tape[index])

    def read_value(self, value, position):
        if position < len(self.modes):
            mode = self.modes[position]
        else:
            mode = MODE_POSITION

        if mode == MODE_POSITION:
            return self.tape[value]
        else:
            return value

    def run(self):
        pass


class OpcodeAdd(OpCodeBase):
    length = 4

    def run(self):
        pos_one, pos_two, result_pos = self.instruction[1:self.length]
        self.tape[result_pos] = self.read_value(pos_one, 0) + self.read_value(pos_two, 1)
        return self.index + self.length


class OpcodeMultiply(OpCodeBase):
    length = 4

    def run(self):
        pos_one, pos_two, result_pos = self.instruction[1:self.length]
        self.tape[result_pos] = self.read_value(pos_one, 0) * self.read_value(pos_two, 1)
        return self.index + self.length


class OpcodeInput(OpCodeBase):
    length = 2

    def run(self):
        position_to_store = self.instruction[1]
        self.tape[position_to_store] = self.input
        return self.index + self.length


class OpcodeOutput(OpCodeBase):
    length = 2

    def run(self):
        value_to_output = self.instruction[1]
        actual_value = self.read_value(value_to_output, 0)
        print(f"OUTPUT VALUE: {actual_value}")
        return self.index + self.length


class OpcodeJumpIfTrue(OpCodeBase):
    length = 3

    def run(self):
        test_value = self.read_value(self.instruction[1], 0)
        jump_location = self.read_value(self.instruction[2], 1)
        if test_value != 0:
            return jump_location
        else:
            return self.index + self.length


class OpcodeJumpIfFalse(OpCodeBase):
    length = 3

    def run(self):
        test_value = self.read_value(self.instruction[1], 0)
        jump_location = self.read_value(self.instruction[2], 1)
        if test_value == 0:
            return jump_location
        else:
            return self.index + self.length


class OpcodeLessThan(OpCodeBase):
    length = 4

    def run(self):
        pos_one = self.read_value(self.instruction[1], 0)
        pos_two = self.read_value(self.instruction[2], 1)
        output_pos = self.instruction[3]
        if pos_one < pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0
        return self.index + self.length


class OpcodeEqual(OpCodeBase):
    length = 4

    def run(self):
        pos_one = self.read_value(self.instruction[1], 0)
        pos_two = self.read_value(self.instruction[2], 1)
        output_pos = self.instruction[3]
        if pos_one == pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0
        return self.index + self.length


class OpcodeHalt(OpCodeBase):
    length = 1

    def run(self):
        return None  # Halt processing


OPCODES = {
    1: OpcodeAdd,
    2: OpcodeMultiply,
    3: OpcodeInput,
    4: OpcodeOutput,
    5: OpcodeJumpIfTrue,
    6: OpcodeJumpIfFalse,
    7: OpcodeLessThan,
    8: OpcodeEqual,
    99: OpcodeHalt
}


def process_instruction(tape, index, input_value):
    opcode = tape[index] % 100

    if opcode in OPCODES:
        return OPCODES[opcode](tape, index, input_value).run()
    else:
        raise Exception(f"Unknown opcode {opcode} at position {index} on {tape}")


def run_tape(tape, input):
    tmptape = tape[:]
    curpos = 0
    while curpos is not None:
        curpos = process_instruction(tmptape, curpos, input)
    return tape


DATA = [int(x) for x in read_data().split(",")]

if __name__ == '__main__':
    # part one
    my_input = 1
    run_tape(DATA, my_input)

    # part 2
    my_input = 5
    run_tape(DATA, my_input)