from collections import defaultdict

MODE_POSITION = 0
MODE_IMMEDIATE = 1
MODE_RELATIVE = 2

OPCODE = 0
INPUT_PARAM = 1
OUTPUT_PARAM = 2


class OpCodeBase(object):
    pretty_name = ""
    param_types = []

    def __init__(self, tape, index, input_value_iter, relative_base):
        self.tape = tape
        self.index = index
        self.newindex = self.index + self.length
        self.instruction = [tape[x] for x in range(self.index, self.index+self.length)]
        self.input = input_value_iter
        self.relative_base = relative_base
        self.output_value = None
        self.relative_adjustment_amount = None
        self.param_modes = self.get_param_modes()
        self.params = self.read_params()
        #print(f"index: {self.index}, relbase: {self.relative_base}, "
        #      f"instruction: {self.instruction}, 63: {self.tape[63]}, 1k: {self.tape[1000]}")

    @property
    def length(self):
        return len(self.param_types)

    def get_param_modes(self):
        mode_list = []
        modes = self.instruction[0] // 100
        for i in range(1, self.length):
            mode_list.append(modes % 10)
            modes = modes // 10
        return mode_list

    def read_params(self):
        param_list = []
        modes = self.instruction[0] // 100
        for i in range(1, self.length):
            # get mode
            param_mode = modes % 10
            modes = modes // 10
            if param_mode == MODE_POSITION and self.param_types[i] == INPUT_PARAM:
                param_list.append(self.tape[self.instruction[i]])
            elif param_mode == MODE_RELATIVE:
                if self.param_types[i] == INPUT_PARAM:
                    param_list.append(self.tape[self.relative_base+self.instruction[i]])
                # For output params, we're doing the dereference in the run function itself
                elif self.param_types[i] == OUTPUT_PARAM:
                    param_list.append(self.relative_base + self.instruction[i])
            else:
                param_list.append(self.instruction[i])
        return param_list

    def run(self):
        pass


class OpcodeAdd(OpCodeBase):
    pretty_name = "add"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, result_pos = self.params
        self.tape[result_pos] = pos_one + pos_two


class OpcodeMultiply(OpCodeBase):
    pretty_name = "mul"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, result_pos = self.params
        self.tape[result_pos] = pos_one * pos_two


class OpcodeInput(OpCodeBase):
    pretty_name = "input"
    param_types = (OPCODE, OUTPUT_PARAM)

    def run(self):
        position_to_store = self.params[0]
        self.tape[position_to_store] = next(self.input)


class OpcodeOutput(OpCodeBase):
    pretty_name = "output"
    param_types = (OPCODE, INPUT_PARAM)

    def run(self):
        value_to_output = self.params[0]
        print(f"OUTPUT VALUE: {value_to_output}")
        self.output_value = value_to_output


class OpcodeJumpIfTrue(OpCodeBase):
    pretty_name = "jump_true"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM)

    def run(self):
        test_value, jump_location = self.params
        if test_value != 0:
            self.newindex = jump_location


class OpcodeJumpIfFalse(OpCodeBase):
    pretty_name = "jump_false"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM)

    def run(self):
        test_value, jump_location = self.params
        if test_value == 0:
            self.newindex = jump_location


class OpcodeLessThan(OpCodeBase):
    pretty_name = "less_than"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, output_pos = self.params
        if pos_one < pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0


class OpcodeEqual(OpCodeBase):
    pretty_name = "equal"
    param_types = (OPCODE, INPUT_PARAM, INPUT_PARAM, OUTPUT_PARAM)

    def run(self):
        pos_one, pos_two, output_pos = self.params
        if pos_one == pos_two:
            self.tape[output_pos] = 1
        else:
            self.tape[output_pos] = 0


class OpcodeAdjustRelativeBase(OpCodeBase):
    pretty_name = "relbase"
    param_types = (OPCODE, INPUT_PARAM)

    def run(self):
        self.relative_adjustment_amount = self.params[0]


class OpcodeHalt(OpCodeBase):
    pretty_name = "halt"
    length = 1
    param_types = (OPCODE,)

    def run(self):
        self.newindex = None  # Halt processing


OPCODES = {
    1: OpcodeAdd,
    2: OpcodeMultiply,
    3: OpcodeInput,
    4: OpcodeOutput,
    5: OpcodeJumpIfTrue,
    6: OpcodeJumpIfFalse,
    7: OpcodeLessThan,
    8: OpcodeEqual,
    9: OpcodeAdjustRelativeBase,
    99: OpcodeHalt
}

# work in progress
# def pretty_print_instruction(inst: OpCodeBase):
#     outstr = f"i{inst.index} r{inst.relative_base} {inst.pretty_name}"
#     modes = [int(x) for x in list(reversed(f"{inst.instruction[0]:0{inst.length+1}d}"))][2:]
#     for i, param in enumerate(inst.instruction[1:]):
#         if modes[i] == MODE_POSITION:
#             outstr += f" pos({param})"
#         elif modes[i] == MODE_RELATIVE:
#             outstr += f" relpos({param})"
#         elif modes[i] == MODE_IMMEDIATE:
#             outstr += f" {param}"
#         else:
#             outstr += f" UNKNOWN({param})"
#     return outstr


def process_instruction(tape, index, input_value, relative_base):
    opcode = tape[index] % 100

    if opcode in OPCODES:
        instruction = OPCODES[opcode](tape, index, input_value, relative_base)
        instruction.run()
        #print(pretty_print_instruction(instruction))
        return instruction.newindex, instruction
    else:
        raise Exception(f"Unknown opcode {opcode} at position {index} on {tape}")


def run_tape_with_output_stop(tape, input_values, starting_pos=0, relative_base=0):
    tmptape = defaultdict(int, {x[0]: x[1] for x in enumerate(tape)})
    curpos = starting_pos
    input_value_iter = iter(input_values)
    while curpos is not None:
        curpos, completed_instruction = process_instruction(tmptape, curpos, input_value_iter, relative_base)
        if completed_instruction.relative_adjustment_amount is not None:
            relative_base += completed_instruction.relative_adjustment_amount
        # Originally I had just "if output" here, but that failed when output was legitimately 0
        if completed_instruction.output is not None:
            tape_output = completed_instruction.output
            return tmptape, curpos, tape_output, relative_base
    return tmptape, curpos, None, relative_base


def run_tape(tape, input_values, starting_pos=0, relative_base=0):
    tmptape = defaultdict(int, {x[0]: x[1] for x in enumerate(tape)})
    curpos = starting_pos
    tape_output = None
    input_value_iter = iter(input_values)
    while curpos is not None:
        curpos, completed_instruction = process_instruction(tmptape, curpos, input_value_iter, relative_base)
        if completed_instruction.relative_adjustment_amount is not None:
            relative_base += completed_instruction.relative_adjustment_amount
        # Originally I had just "if output" here, but that failed when output was legitimately 0
        if completed_instruction.output_value is not None:
            tape_output = completed_instruction.output_value
    return tmptape, curpos, tape_output, relative_base


def run_sequence(tape, sequence):
    current_input = 0
    amp_output = None
    for amp in sequence:
        _, _, amp_output, _ = run_tape_with_output_stop(tape, [amp, current_input])
        current_input = amp_output
    return amp_output


def run_sequence_with_feedback(tape, sequence):
    tapes = [tape[:] for x in range(5)]
    inputs = [0, None, None, None, None]
    positions = [0]*5
    relative_bases = [0]*5
    # First run, init each with its phase setting
    for i, amp in enumerate(sequence):
        tapes[i], positions[i], inputs[(i+1) % 5], relative_bases[i] = run_tape_with_output_stop(tapes[i],
                                                                                                 [amp, inputs[i]],
                                                                                                 positions[i])
    # After that, only provide existing inputs
    while not all(position is None for position in positions):
        for i, amp in enumerate(sequence):
            tapes[i], positions[i], inputs[(i + 1) % 5], relative_bases[i] = run_tape_with_output_stop(tapes[i],
                                                                                                       [inputs[i]],
                                                                                                       positions[i])
    return inputs[0]
