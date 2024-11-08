# Assembler for my custom minecraft redstone computer

![whole computer](./imgs/whole-computer.png "Whole computer")
![user input](./imgs/user-input.png "User input")
![displays](./imgs/displays.png "Displays")

### Minecraft version: 1.15.2
### Python version: 3.11

## Installation

Clone the repository with git
```bash
git clone https://github.com/BartoszLipinskiSzyb/assemblerv2_0
```

Extract file "THIS_IS_COMPUTER_WORLD.zip" into your minecraft saves folder

## Running the assembler

Windows

```bash
python assemblerv2_0.py path/to/source
```

Linux/MacOS

```bash
python3 assemblerv2_0.py path/to/source
```

You can place -v option at the end of the command for verbose mode

## Loading compiled code into minecraft world

If you don't have one, obtain command_block by typing into minecraft console

```minecraft
/give @p minecraft:command_block
```

Place the command block anywhere in the world so that 3x3 block cube above the block is air, and paste into it command that assemblerv2_0.py script created. Then power the command block with any redstone signal

## Assembly syntax

### References

References can be used to assign a value to string. Note that references are replaced in code during its preprocessing, so it really works like #DEFINE in C or macro in Rust.

#### Register references

These are used to point to the computer's "cache" which consists of 16 16-bit words. The syntax for register X is

```assembly
reg.X
```

where X is any value from 0 to 15 representing register address.

You can use register reference assigning by using following syntax

```assembly
*name = X
```

where name is any string without whitespaces and X is a register address.

You can then use the reference anywhere in code (even before the declaration!) by typing

```assembly
*name
```

#### IO references

The computer has 8-bit IO address bus, so it can address 256 different devices and read from or write to them. Syntax for them is

```assembly
io.Y
```

where Y is any value from 0 to 255, representing IO address.

You can use IO reference assigning by using following syntax

```assembly
io name = Y
```

where name is any string without whitespaces and Y is an IO address.

You can then use the reference anywhere in code (even before the declaration!) by typing

```assembly
name
```

Currently connected devices with their addresses are:

```
0-31 additional memory
32-35 - pixel display (takes 4 least significant bits): 32 - X position, 33 - Y position, 34 - data/command 
128 - decimal display and input
129 - 4 informational lamps on user interface (takes 4 least significant bits)
```

#### Program memory references

These are used to create points in program it can jump to. The simplest example is an infinite loop

```assembly
name:
   go name
```

where name is any string without whitespaces

The assembler automatically assigns value to them, so you don't have to worry about their value. Just place them in code before instruction you want to be able to jump to.

You can then use the reference anywhere in code (even before the declaration!) by typing

```assembly
name
```

### Instruction syntax

Instructions are directly translated to machine instructions 1:1. Each instruction line equals one instruction that the computer will execute

```assembly
input -> output ifcondition go goto
```

where

input is input from 0-2 locations, combined with an operator if needed

output is 0-2 locations, separated by "," to which operation result will be written

condition is the condition under which the computer will perform jump to instruction specified by goto

goto is instruction address to jump to if condition is true


Example line of code that adds 1 to register 0 and writes the result into register 0

```assembly
reg.0 + 1 -> reg.0
```

Example line of code that performs OR on register 5 and register 12 and writes the result into IO address 128 (a. k. a. decimal display)

```assembly
reg.5 | reg.12 -> io.128
```

Example line of code that checks if register 7 is equal to register 8 by XORing and checking if result is 0. If result is 0 it jumps to instruction 0

```assembly
reg.7 ^ reg.8 -> _ if0 go 0
```

### Operators

Operators are used to combine one or two inputs

- \+ adds two values:
    a + b
- \- subtracts two values:
    a - b
- \& performs bitwise AND on two values:
    a & b
- \| performs bitwise OR on two values:
    a | b
- \^ performs bitwise XOR on two values:
    a ^ b
- \! performs bitwise NOT on one value:
    ! b
- \>\> performs right bitshift on one value:
    a \>\>

### Conditions

Conditions are used to test result of operation in different ways

- true - always true, always jumps to goto instruction:
    iftrue
- false - always false, never jumps to got instruction:
    iffalse
- 0 - true if result is 0:
    if0
- \- - true if result is negative:
    if-
- overflow - true if operation resulted in 16-bit overflow:
    ifoverflow
- !0 - true if result is not 0:
    if!0
- !- - true if result is non-negative:
    if!-
- !overflow - true if operation didn't result in 16-bit overflow:
    if!overflow

### Import statements

Import statement are used to include code from other files in a program. They work by directly putting content of a specified file in program. That means if they contain any intructions, they will be executed

```assembly
use path/to/file.a
```

It both handles relative and absolute paths

## Examples

For example programs, check out [programs](https://github.com/BartoszLipinskiSzyb/assemblerv2_0/tree/main/programs) directory. Some of them are already loaded into the world.