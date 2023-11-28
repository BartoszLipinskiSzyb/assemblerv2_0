import sys
import json
import re
from os import path

def preprocess(filepath):
    references = {}

    lines = None
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        # print(f"File {filepath} not found")
        sys.exit(-1)

    # removing trailing spaces
    lines = list(map(lambda line: line.strip(), lines))

    # removing empty lines and comments
    linesStripped = []
    for i in range(len(lines)):
        lines[i] = lines[i].strip("\n")
        if not (lines[i] == "" or lines[i][0:2] == "//"):
            linesStripped.append(lines[i])

    # loading definitions
    linesProgram = []
    for i in range(len(linesStripped)):
        if " = " in linesStripped[i]:
            splittedLine = linesStripped[i].split(" = ")
            name = splittedLine[0]
            value = splittedLine[1]

            if name[0] == "*":
                value = "reg." + value

            if name[0:3] == "io ":
                name = name[3:]
                value = "io." + value

            references[name] = value
        else:
            linesProgram.append(linesStripped[i])

    # loading jump definitions
    linesCommandsOnly = []
    sub = 0
    for i in range(len(linesProgram)):
        if linesProgram[i][-1] == ":":
            references[linesProgram[i][0:-1]] = str(i - sub)
            sub += 1
        else:
            linesCommandsOnly.append(linesProgram[i])

    # replacing uses of references in code with values
    for i in range(len(linesCommandsOnly)):
        for key in references:
            linesCommandsOnly[i] = re.sub(r"^" + re.escape(key) + r"\s", references[key] + " ", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"$", " " + references[key], linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"\s", " " + references[key] + " ", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"\,", " " + references[key] + ",", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\," + re.escape(key) + r"\s", "," + references[key] + " ", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\," + re.escape(key) + r"\,", "," + references[key] + ",", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\," + re.escape(key) + r"\,", "," + references[key] + ",", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\," + re.escape(key) + r"$", "," + references[key], linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"$", " " + references[key], linesCommandsOnly[i])

    # print("Code:")
    # for i, line in enumerate(linesCommandsOnly):
        # print(f"{i}: {line}")
    # print()

    # print("References:")
    # print(references)
    # print()

    return linesCommandsOnly


def tokenize(assembly):
    tokenized = []

    for i, line in enumerate(assembly):
        if "->" in line:

            input = re.findall(r"^.*->", line)
            if len(input) == 0:
                input = re.findall(r"^.*if", line)
            if len(input) == 0:
                input = [line]

            input = re.sub(r"(\sif$)|(\s->$)", "", input[0])
        else:
            input = "_"

        condition = re.findall(r"if.*go", line)
        if len(condition) == 0:
            if "go " in line:
                condition = ["true"]
            else:
                condition = ["false"]
        condition = re.sub("(if)|( go)", "", condition[0])

        goto = re.findall(r"go\s\d*$", line)

        if len(goto) == 0:
            goto = "0"
        goto = re.sub("(go )", "", goto[0])

        output = re.findall(r"->\s.*\sif", line)
        if len(output) == 0:
            output = re.findall(r"->\s.*$", line)
        if len(output) == 0:
            output = ["_"]

        output = re.sub(r"(\sif)|(->\s)", "", output[0])
        output = re.sub(r"\s", "", output).split(",")

        tokenized.append({
            "input": input,
            "output": output,
            "condition": condition,
            "goto": goto
        })

    return tokenized


def bindigits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return list(map(int, list(("{0:0>%s}" % (bits)).format(s))))


memory_layout = json.load(open("./memory/program_memory_layout.json"))
memory_parts = memory_layout['parts']


def write_number_to_memory(number, layout_part, binary):
    number_size = layout_part['range'][1] - layout_part['range'][0]
    bin = bindigits(int(number), number_size)
    if layout_part['order'] == "LSB":
        bin = bin[::-1]
    for i in range(number_size):
        binary[i + layout_part['range'][0]] = bin[i]

    return binary

class bcolors:
    header = '\033[95m'
    okblue = '\033[94m'
    okcyan = '\033[96m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    endc = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

def error_msg(line, msg):

    error_line = f"In {line}: {msg}"
    # print()
    # print("~" * len(error_line))
    # print()
    # print(f"{ bcolors.header }in {line}{bcolors.endc}: {bcolors.fail}{msg}{bcolors.endc}")
    # print()
    # print("~" * len(error_line))
    exit(-1)


def to_binary(line):
    binary = [0 for _ in range(memory_layout["length"])]

    # setting goto value
    binary = write_number_to_memory(line['goto'], memory_parts['goto'], binary)

    # parsing input
    input_args = line["input"].split(" ")

    is_operand_set = False
    is_reg_a_set = False
    is_reg_b_set = False

    # setting operation
    operation = None
    operation_idx = None
    operations = ["+", "-", "&", "|", "^", ">>", "!"]
    for op in operations:
        if op in input_args:
            if operation is None:
                operation = op
                operation_idx = input_args.index(op)
            else:
                error_msg(line, "cannot have two operators")

    # setting default operation to let data flow through ALU
    if operation is None:
        operation = '^'

    # setting operation bits
    bits = memory_parts['alu_operation']['bits']
    # setting default operation as XOR to let data flow through ALU

    match operation:
        case "|":
            binary = write_number_to_memory(0x000000 | (1 << bits.index("&")) | (1 << bits.index("^")), memory_parts['alu_operation'], binary)
        case "-":
            binary = write_number_to_memory(0x000000 | (1 << bits.index("+")) | (1 << bits.index("carry") | (1 << bits.index("!"))), memory_parts['alu_operation'], binary)
        case _:
            binary = write_number_to_memory(0x000000 | (1 << bits.index(operation)), memory_parts['alu_operation'], binary)

    io_operation = None
    # setting input values and deciding which value should be loaded to a and b. TODO: selecting registers for all operations
    for (i, input_arg) in enumerate(input_args):
        if input_arg.isdigit():
            if is_operand_set:
                error_msg(line, "cannot have two operands")
            else:
                binary = write_number_to_memory(input_arg, memory_parts['operand'], binary)
                is_operand_set = True

        if "io." in input_arg:
            io = input_arg.replace("io.", "")
            io_operation = "r"

            binary = write_number_to_memory(io, memory_parts['io'], binary)

        if "reg." in input_arg:
            reg = input_arg.replace("reg.", "")

            # przemienne operacje - nieważne jaki bufor będzie użyty
            if operation in ["+", "&", "|", "^"]:
                if is_reg_a_set:
                    if not is_reg_b_set and not is_operand_set:
                        is_reg_b_set = True
                        binary = write_number_to_memory(reg, memory_parts['reg_b'], binary)
                        binary[memory_parts['reg_b_enable']['range'][0]] = 1
                    else:
                        error_msg(line, "both registers already selected")
                        exit(-1)
                else:
                    is_reg_a_set = True
                    binary = write_number_to_memory(reg, memory_parts['reg_a'], binary)
                    binary[memory_parts['reg_a_enable']['range'][0]] = 1

            # tylko na rejestrze b lub operandzie
            elif operation in ['!']:
                if i - 1 == operation_idx:
                    if is_reg_b_set or is_operand_set:
                        error_msg(line, "NOT operation can only be used with one value")
                        exit(-1)
                    else:
                        is_reg_b_set = True
                        binary = write_number_to_memory(reg, memory_parts['reg_b'], binary)
                        binary[memory_parts['reg_b_enable']['range'][0]] = 1

            elif operation in ['-']:
                if i < operation_idx:
                    if is_reg_a_set:
                        error_msg(line, "register A cannot load two values at the same time")
                    else:
                        is_reg_a_set = True
                        binary = write_number_to_memory(reg, memory_parts['reg_a'], binary)
                        binary[memory_parts['reg_a_enable']['range'][0]] = 1
                else:
                    if is_reg_b_set:
                        error_msg(line, "register B cannot load two values at the same time")
                    else:
                        is_reg_b_set = True
                        binary = write_number_to_memory(reg, memory_parts['reg_b'], binary)
                        binary[memory_parts['reg_b_enable']['range'][0]] = 1

            elif operation in ['>>']:
                if is_reg_a_set:
                    error_msg(line, "with right bitshift computer can only load to A register")
                is_reg_a_set = True
                binary = write_number_to_memory(reg, memory_parts['reg_a'], binary)
                binary[memory_parts['reg_a_enable']['range'][0]] = 1

    # setting output register and output IO
    is_reg_out_set = False
    for output in line['output']:
        if "reg." in output:
            if is_reg_out_set:
                error_msg(line, "can only have one output register")
                exit(-1)

            value = output.replace("reg.", "")
            binary = write_number_to_memory(value, memory_parts['reg_out'], binary)
            binary[memory_parts['reg_out_enable']['range'][0]] = 1
            is_reg_out_set = True

        elif "io." in output:
            if io_operation is not None:
                error_msg(line, "cannot read and write to IO at the same time and can only use one IO address")
                exit(-1)

            io = output.replace("io.", "")
            io_operation = "w"
            binary = write_number_to_memory(io, memory_parts['io'], binary)

    # setting io operation
    if io_operation is not None:
        bits = memory_parts['io_operation']['bits']
        binary = write_number_to_memory(0x0000 | (1 << bits.index(io_operation)), memory_parts['io_operation'], binary)

    if (is_reg_b_set or is_operand_set) and is_reg_a_set and operation_idx is None:
        error_msg(line, "cannot combine two values without operator")

    condition_combinations = {
        'true': [],
        '0': ["zero"],
        'overflow': ["overflow"],
        '-': ["negative"],
        '!-': ["negative", "not"],
        "!0": ["zero", "not"],
        "!overflow": ["overflow", "not"]
    }
    # setting condition
    condition = line['condition']

    # special case for when line looks something like
    # go 42
    # TODO: when line looks something like above, make input empty. Currently input will be go 42. It sets operand and it shouldn't

    if condition != "false":
        binary[memory_parts['condition_enable']['range'][0]] = 1
        if condition not in condition_combinations.keys():
            error_msg(line, "not a valid condition")

        combination = condition_combinations.get(condition)
        result_condition = 0x0000
        bits = memory_parts['condition']['bits']
        for bit in combination:
            result_condition |= 1 << bits.index(bit)
        binary = write_number_to_memory(result_condition, memory_parts['condition'], binary)

    return binary

def color_binary(line):
    line = line[::-1]

    def get_current_range(pos):
        pos = memory_layout['length'] - pos - 1
        for i, key in enumerate(memory_parts):
            if pos >= memory_parts[key]['range'][0] and pos < memory_parts[key]['range'][1]:
                return i % 2 == 1

    result = ""
    last_was_colored = False
    for i in range(len(line)):
        should_color = get_current_range(i)
        if not last_was_colored and should_color:
            result += bcolors.okcyan
            last_was_colored = True
        elif last_was_colored and not should_color:
            result += bcolors.endc
            last_was_colored = False

        result += str(line[i])

    return result + bcolors.endc

position_config = json.load(open("./memory/world_position_config.json"))
def to_points_in_world(binary):
    zero_point = position_config["zero_point"]
    points = []
    for (line_idx, line) in enumerate(binary):
        for (digit_idx, digit) in enumerate(line):
            if digit == 1:
                points.append([zero_point[0] + ((line_idx % position_config["memory_dimensions"]["length"]) * 2),  zero_point[1] - (line_idx // position_config["memory_dimensions"]["length"]) * 2, zero_point[2] + (digit_idx * 2)])

    return points

commands = json.load(open("./memory/minecraft_commands.json"))
def to_minecraft_command(points):
    command = commands["start"]
    for point in points:
        command += "{id:command_block_minecart,Command:'setblock " + str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + " redstone_wall_torch[facing=" + position_config["facing"] + "]'},"
    
    command += "{id:command_block_minecart,Command:'setblock ~ ~1 ~ command_block{auto:1,Command:\"fill ~ ~ ~ ~ ~-2 ~ air\"}'},{id:command_block_minecart,Command:'kill @e[type=command_block_minecart,distance=..1]'}]}]}]}"
    return command


def main():
    assembly = preprocess(sys.argv[1])
    tokenized = tokenize(assembly)

    print("\n".join(map(str, tokenized)))

    binary = list(map(to_binary, tokenized))

    print()
    print("\n".join(map(color_binary, binary)))

    points_in_world = to_points_in_world(binary)

    print()
    print(points_in_world)

    minecraft_command = to_minecraft_command(points_in_world)

    print()
    print(minecraft_command)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # print(f"usage: python {path.basename(__file__)} <file input>")
        exit(-1)
    main()
