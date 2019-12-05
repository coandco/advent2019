from utils import read_data

MODE_POSITION = 0
MODE_IMMEDIATE = 1

OPCODE = 0
INPUT_PARAM = 1
OUTPUT_PARAM = 2


class OpCodeBase(object):
    length = 0
    param_types = []

    def __init__(self, tape, index, input_value):
        self.tape = tape
        self.index = index
        self.instruction = tape[index:index+self.length]
        self.input = input_value
        self.params = self.read_params()

    def read_params(self):
        param_list = []
        modes = self.instruction[0] // 100
        for i in range(1, self.length):
            # get mode
            param_mode = modes % 10
            modes = modes // 10
            if param_mode == MODE_POSITION and self.param_types[i] == INPUT_PARAM:
                param_list.append(self.tape[self.instruction[i]])
            else:
                param_list.append(self.instruction[i])
        return param_list

    def run(self):
        pass


class OpcodeAdd(OpCodeBase):
    length = 4
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, result_pos = self.params
        self.tape[result_pos] = pos_one + pos_two
        return self.index + self.length


class OpcodeMultiply(OpCodeBase):
    length = 4
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, result_pos = self.params
        self.tape[result_pos] = pos_one * pos_two
        return self.index + self.length


class OpcodeInput(OpCodeBase):
    length = 2
    param_types = (OPCODE, OUTPUT_PARAM)

    def run(self):
        position_to_store = self.params[0]
        self.tape[position_to_store] = self.input
        return self.index + self.length


class OpcodeOutput(OpCodeBase):
    length = 2
    param_types = (OPCODE, INPUT_PARAM)

    def run(self):
        value_to_output = self.params[0]
        actual_value = value_to_output
        print(f"OUTPUT VALUE: {actual_value}")
        return self.index + self.length


class OpcodeJumpIfTrue(OpCodeBase):
    length = 3
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM)

    def run(self):
        test_value, jump_location = self.params
        if test_value != 0:
            return jump_location
        else:
            return self.index + self.length


class OpcodeJumpIfFalse(OpCodeBase):
    length = 3
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM)

    def run(self):
        test_value, jump_location = self.params
        if test_value == 0:
            return jump_location
        else:
            return self.index + self.length


class OpcodeLessThan(OpCodeBase):
    length = 4
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, output_pos = self.params
        if pos_one < pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0
        return self.index + self.length


class OpcodeEqual(OpCodeBase):
    length = 4
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, output_pos = self.params
        if pos_one == pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0
        return self.index + self.length


class OpcodeHalt(OpCodeBase):
    length = 1
    param_types = (OPCODE,)

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