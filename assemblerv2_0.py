import sys
import json
import re


def preprocess(filepath):
    references = {}

    lines = None
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {filepath} not found")
        sys.exit(-1)

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

    for i in range(len(linesCommandsOnly)):
        for key in references:
            linesCommandsOnly[i] = re.sub(r"^" + re.escape(key) + r"\s", references[key] + " ", linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"$", " " + references[key], linesCommandsOnly[i])
            linesCommandsOnly[i] = re.sub(r"\s" + re.escape(key) + r"\s", " " + references[key] + " ", linesCommandsOnly[i])

    print("Code:")
    for i, line in enumerate(linesCommandsOnly):
        print(f"{i}: {line}")
    print()

    print("References:")
    print(references)
    print()

    return linesCommandsOnly


def tokenize(assembly):
    tokenized = []

    for i, line in enumerate(assembly):
        input = re.findall(r"^.*->", line)
        if len(input) == 0:
            input = re.findall(r"^.*if", line)
        if len(input) == 0:
            input = [line]

        input = re.sub(r"(\sif$)|(\s->$)", "", input[0])

        condition = re.findall(r"if.*go", line)
        if len(condition) == 0:
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
    print()
    print("~" * len(error_line))
    print()
    print(f"{ bcolors.header }in {line}{bcolors.endc}: {bcolors.fail}{msg}{bcolors.endc}")
    print()
    print("~" * len(error_line))
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


    operation = None
    operations = ["+", "-", "&", "|", "^", ">>" "!"]
    for op in operations:
        if op in input_args:
            if operation is None:
                operation = op
            else:
                error_msg(line, "cannot have two operators")

    for input_arg in input_args:
        if input_arg.isdigit():
            if is_operand_set:
                error_msg(line, "cannot have two operands")
            else:
                binary = write_number_to_memory(input_arg, memory_parts['operand'], binary)
                is_operand_set = True

        if "reg." in input_arg:
            print(is_operand_set, is_reg_b_set, is_reg_a_set)
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
                else:
                    is_reg_a_set = True
                    binary = write_number_to_memory(reg, memory_parts['reg_a'], binary)
                    binary[memory_parts['reg_a_enable']['range'][0]] = 1

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

def main():
    assembly = preprocess(sys.argv[1])
    tokenized = tokenize(assembly)

    print("\n".join(map(str, tokenized)))

    binary = list(map(to_binary, tokenized))

    print()
    print("\n".join(map(color_binary, binary)))

if __name__ == "__main__":
    main()
