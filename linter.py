import re
import sys

def verify_line(line: str) -> bool:
    if line.isspace():
        return True

    return re.match(r"^[^\S\n]*(\S{1,} *(([+-|&^]{1}) *\S{1,} *)?-> *[^\s\,]{1,} *(, *\S{1,})? *(if(true|false|0|-|overflow|!0|!-|!overflow) {1,}go {1,}\S{1,})?)|(\/{2}.*$)|(^io {1,}\S* {0,}= {0,}\d*$)|(^\S{1,} *= *\d{1,}$)|(\S*:)|(go *\S{1,})|(use( {1,}\S{1,}){1,})$", line.strip(" \t")) is not None

def lint_file(path):
    errors = []

    file_contents = None
    with open(path) as f:
        file_contents = f.readlines()

    for l_num, line in enumerate(file_contents):
        if not verify_line(line):
            errors.append([l_num, line])

    return errors

if __name__ == "__main__":
    exit(0 if len(lint_file(sys.argv[1])) == 0 else -1)
