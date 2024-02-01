import sys
import json
import re
from os import path
import linter

def flatten(lst: []) -> []:
    """Flattens a multi-dimensional array"""
    flattened=[]
    #print 'argument to main loop:', lst
    for i in lst:
        if  isinstance(i, list):
            for j in i:
                #print 'passing %r for nested lists' % j
                if isinstance(j, list):
                    flattened+=flatten(j)
                else:
                    flattened.append(j)
        else:
            flattened.append(i)
    return flattened


def import_imports(filepath):
    """Replaces import statements with code"""
    with open(filepath, "r") as f:
        content = f.readlines()
        for i, line in enumerate(content):
            splitted = line.split(" ")
            if splitted[0] == "use":
                lib_path = path.join(path.dirname(filepath), splitted[1].strip("\n"))
                # print("opening " + lib_path)
                with open(lib_path, "r") as lib:
                    content[i] = "\n" + lib.read()
                    if "\nuse" in content[i]:
                        content[i] = import_imports(lib_path)
                    # todo: recursive imports

    return flatten(content)


def preprocess(lines: list[str]) -> list[str]:
    """Removes comments and empty lines and replaces references with values (macro)"""
    references = {}

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
            linesCommandsOnly[i] = re.sub(r"\," + re.escape(key) + r"$", "," + references[key], linesCommandsOnly[i])

    # print("Code:")
    # for i, line in enumerate(linesCommandsOnly):
        # print(f"{i}: {line}")
    # print()

    # print("References:")
    # print(references)
    # print()

    return linesCommandsOnly


def tokenize(assembly: list[str]) -> list[str]:
    """Finds input, output, condition and goto address in instructions"""
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
            "line": line,
            "input": input,
            "output": output,
            "condition": condition,
            "goto": goto
        })

    return tokenized


def bindigits(n: int, bits: int) -> str:
    """Converts n to binary representations string of length bits"""
    s = bin(n & int("1"*bits, 2))[2:]
    return list(map(int, list(("{0:0>%s}" % (bits)).format(s))))


memory_layout = json.load(open("./memory/program_memory_layout.json"))
memory_parts = memory_layout['parts']


def write_number_to_memory(number: int | str, layout_part: dict, binary: [int]):
    """Writes a number to layout_part in binary"""
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

def error_msg(line: str | dict, msg: str) -> None:
    """Presents error with line on which it occured"""
    error_line = f"In {line}: {msg}"
    print()
    print("~" * len(error_line))
    print()
    print(f"{ bcolors.header }in {line}{bcolors.endc}: {bcolors.fail}{msg}{bcolors.endc}")
    print()
    print("~" * len(error_line))
    sys.exit(-1)


def to_binary(line: dict) -> [int]:
    """Converts line to final binary representation of the instruction"""
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

        elif "io." in input_arg:
            io = input_arg.replace("io.", "")
            io_operation = "r"

            binary = write_number_to_memory(io, memory_parts['io'], binary)

        elif "reg." in input_arg:
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
                        sys.exit(-1)
                else:
                    is_reg_a_set = True
                    binary = write_number_to_memory(reg, memory_parts['reg_a'], binary)
                    binary[memory_parts['reg_a_enable']['range'][0]] = 1

            # tylko na rejestrze b lub operandzie
            elif operation in ['!']:
                if i - 1 == operation_idx:
                    if is_reg_b_set or is_operand_set:
                        error_msg(line, "NOT operation can only be used with one value")
                        sys.exit(-1)
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

        elif not (input_arg in operations or input_arg == '_'):
            error_msg(line["line"], "undefined variable: " + input_arg)

    # setting output register and output IO
    is_reg_out_set = False
    for output in line['output']:
        if "reg." in output:
            if is_reg_out_set:
                error_msg(line, "can only have one output register")
                sys.exit(-1)

            value = output.replace("reg.", "")
            binary = write_number_to_memory(value, memory_parts['reg_out'], binary)
            binary[memory_parts['reg_out_enable']['range'][0]] = 1
            is_reg_out_set = True

        elif "io." in output:
            if io_operation is not None:
                error_msg(line, "cannot read and write to IO at the same time and can only use one IO address")
                sys.exit(-1)

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
        'true': ["not"],
        '0': ["zero"],
        'overflow': ["overflow"],
        '-': ["negative"],
        '!-': ["negative", "not"],
        "!0": ["zero", "not"],
        "!overflow": ["overflow", "not"]
    }
    # setting condition
    condition = line['condition']

    if condition != "false":
        if condition != "true":
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

def color_binary(line: str) -> str:
    """Colors binary output of to_binary function based on memory_layout"""
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
def to_points_in_world(binary: [[int]]) -> [[int]]:
    """Converts binary representation of instructions to corresponding point in Minecraft world where redstone torches will be placed"""
    zero_point = position_config["zero_point"]
    points = []
    for (line_idx, line) in enumerate(binary):
        for (digit_idx, digit) in enumerate(line):
            if digit == 1:
                points.append([zero_point[0] + ((line_idx % position_config["memory_dimensions"]["length"]) * 2),  zero_point[1] - (line_idx // position_config["memory_dimensions"]["length"]) * 4, zero_point[2] + (digit_idx * 2)])

    return points

commands = json.load(open("./memory/minecraft_commands.json"))
def to_minecraft_command(points: [[int]]) -> str:
    """Converts points in Minecraft world to single Minecraft command that will spawn redstone torches"""
    zero_point = position_config["zero_point"]
    command = commands["start"]
    # cleaning all redstone torches
    command += "{id:command_block_minecart,Command:'fill " + str(zero_point[0]) + " " + str(zero_point[1]) + " " + str(zero_point[2]) + " " + str(zero_point[0] + (position_config["memory_dimensions"]["length"] - 1) * 2) + " " + str(zero_point[1] - (position_config["memory_dimensions"]["height"] - 1) * 2) + " " + str(zero_point[2] + (position_config["memory_dimensions"]["width"] - 1) * 2) + " air replace redstone_wall_torch'},"

    for point in points:
        command += "{id:command_block_minecart,Command:'setblock " + str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + " redstone_wall_torch[facing=" + position_config["facing"] + "]'},"

    command += commands["end"]
    return command


def main():
    lint_errors = linter.lint_file(sys.argv[1])

    if not len(lint_errors) == 0:
        for i, line in lint_errors:
            print("Line " + str(i + 1) + " : \n" + line.strip("\n") + "\n : bad syntax\n")
        return -1

    lines = import_imports(sys.argv[1])
    assembly = preprocess(lines)
    tokenized = tokenize(assembly)
    binary = list(map(to_binary, tokenized))
    points_in_world = to_points_in_world(binary)
    minecraft_command = to_minecraft_command(points_in_world)

    if "-v" in sys.argv:
        print("".join(lines))
        print()
        print("\n".join(assembly))
        print()
        print("\n".join(map(str, tokenized)))
        print()
        print("\n".join(map(color_binary, binary)))
        print()
        print(points_in_world)
        print()

    print(minecraft_command)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: python {path.basename(__file__)} <file input> -v")
        print()
        print("options:")
        print("-v - verbose mode, show more information")
        sys.exit(-1)
    sys.exit(main())
