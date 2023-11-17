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
            "in": input,
            "out": output,
            "condition": condition,
            "goto": goto
        })

    return tokenized


def bindigits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return list(map(int, list(("{0:0>%s}" % (bits)).format(s))))


memory_layout = json.load(open("../memory/program_memory_layout.json"))
memory_parts = memory_layout['parts']


def to_binary(line):
    binary = [0 for _ in range(memory_layout["length"])]
    
    # setting goto value
    number_size = memory_parts['goto']['range'][1] - memory_parts['goto']['range'][0]
    goto_bin = bindigits(int(line['goto']), number_size)
    if memory_parts['goto']['order'] == "LSB":
        goto_bin = goto_bin[::-1]
    for i in range(number_size):
        binary[i + memory_parts['goto']['range'][0]] = goto_bin[i]

    return binary


def main():
    assembly = preprocess(sys.argv[1])
    tokenized = tokenize(assembly)

    print("\n".join(map(str, tokenized)))

    binary = list(map(to_binary, tokenized))

    print()
    print("\n".join(map(str, binary)))

if __name__ == "__main__":
    main()
