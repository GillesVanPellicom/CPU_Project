#!/usr/bin/python

import re

debug = False


def prepareFile(fileSrc):
    file = open(fileSrc, 'r')
    arr = file.readlines()
    toRemove = []
    # for every line
    for i in range(len(arr)):

        # mark comments for removal
        if '#' in arr[i]:
            toRemove.append(i)

        # remove possible newline escapes
        arr[i] = arr[i].replace("\n", '')

        # mark empty lines for removal
        if len(arr[i]) == 0:
            toRemove.append(i)

    for i in range(len(toRemove) - 1, -1, -1):
        del arr[toRemove[i]]

    return arr


def parse(preparedFile):
    labels = {}
    for i in range(len(preparedFile)):
        s = preparedFile[i]
        if s.find(':') != -1:
            # label
            labels.update({s: i - len(labels)})
    instrl = []
    for i in range(len(preparedFile)):
        # FIXME correct line numbers
        s = preparedFile[i]

        if s.find(':') != -1:
            # label already processed
            continue

        elif s.replace(' ', '') == "noop":
            # noop - 00000 (nullary)
            # Append to instruction list
            instrl.append("00000 000000000 000000000 000000000")

        elif s.find('add ') != -1:
            # add - 00001 (binary)
            # Generate instruction and append to instruction list
            instrl.append(generateBinaryInstr(s, "00001", 3, i + 1))

        elif s.find('addi ') != -1:
            # addi - 00010 (immediate)
            # append to instruction list
            instrl.append(generateImmediateInstr(s, "00010", 4, i + 1))

        elif s.find('xor ') != -1:
            # check for xor before or since find() is used
            # xor - 00011 (binary)
            # Generate instruction and append to instruction list
            instrl.append(generateBinaryInstr(s, "00011", 3, i + 1))

        elif s.find('ori ') != -1:
            # ori - 00100 (immediate)
            # Generate instruction and append to instruction list
            instrl.append(generateImmediateInstr(s, "00100", 3, i + 1))

        elif s.find('or ') != -1:
            # or - 00101 (binary)
            # Generate instruction and append to instruction list
            instrl.append(generateBinaryInstr(s, "00101", 2, i + 1))

        elif s.find('and ') != -1:
            # and - 00110 (binary)
            # Generate instruction and append to instruction list
            instrl.append(generateBinaryInstr(s, "00110", 3, i + 1))

        elif s.find('inv ') != -1:
            # inv - 00111 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "00111", 3, i + 1))

        elif s.find('not ') != -1:
            # not - 01000 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01000", 3, i + 1))

        elif s.find('sll ') != -1:
            # sll - 01001 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01001", 3, i + 1))

        elif s.find('sla ') != -1:
            # sla - 01010 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01010", 3, i + 1))

        elif s.find('srl ') != -1:
            # srl - 01011 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01011", 3, i + 1))

        elif s.find('sra ') != -1:
            # sra - 01100 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01100", 3, i + 1))

        elif s.find('lmb ') != -1:
            # lmb - 01101 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01101", 3, i + 1))

        elif s.find('smb ') != -1:
            # smb - 01110 (unary)
            # Generate instruction and append to instruction list
            instrl.append(generateUnaryInstr(s, "01110", 3, i + 1))

    print(instrl)
    print(labels)


def generateBinaryInstr(s, opcode, instrLength, line):
    ins = opcode
    args = s[instrLength + 1:].replace(' ', '').split(',')

    # check argument count
    if len(args) != 3:
        raise SyntaxError(consolePrefix(line) + "Invalid argument(s).")

    # generate instruction
    ins += ' ' + regNameToAddress(args[0], line) + ' ' + regNameToAddress(args[1],
                                                                          line) + ' ' + regNameToAddress(
        args[2], line)

    # return instruction
    return ins


def generateUnaryInstr(s, opcode, instrLength, line):
    ins = opcode
    args = s[instrLength + 1:].replace(' ', '').split(',')

    # check argument count
    if len(args) != 2:
        raise SyntaxError(consolePrefix(line) + "Invalid argument(s).")

    # generate instruction
    ins += ' ' + regNameToAddress(args[0], line) + ' ' + regNameToAddress(args[1], line) + ' ' + '0' * 9

    # return instruction
    return ins


def generateImmediateInstr(s, opcode, instrLength, line):
    ins = opcode
    args = s[instrLength + 1:].replace(' ', '').split(',')

    # check argument count
    if len(args) != 3:
        raise SyntaxError(consolePrefix(line) + "Invalid argument(s).")

    # FIXME 2's complement
    # check if immediate is too large
    if int(args[2]) > pow(2, 16) - 1:
        raise SyntaxError(consolePrefix(line) + "Immediate too large")

    # FIXME 2's complement
    # generate instruction
    ins += ' ' + regNameToAddress(args[0], line) + ' ' + regNameToAddress(args[1], line) + ' ' + format(int(args[2]),
                                                                                                        '018b')

    # return instruction
    return ins


def regNameToAddress(s, lineNumber):

    match = re.match(r"([a-z])([0-9]?[0-9])", s, re.I)
    error = False
    offset = 0
    regId = 0

    if not match:
        # possible register by name
        regType = s
        match regType:
            case "zero":
                # zero register (0x000)
                offset = 0
            case "hff":
                # hardware failure flag register (0x031)
                offset = 49
            case "cdb":
                # current data bank register (0x032)
                offset = 50
            case "cpb":
                # current program bank register (0x033)
                offset = 51
            case "lar":
                # link address register (0x034)
                offset = 52
            case _:
                # invalid register designation
                error = True
    else:
        split = match.groups()

        regType = split[0]
        if len(split[1]) != 0:
            regId = int(split[1])

        match regType:
            case 'r':
                # normal registers r0-r31 (0x001 - 0x020)
                offset = 1
                # registry id must be [0; 31]
                if not (0 <= regId <= 31):
                    raise SyntaxError(consolePrefix(lineNumber) + "Registers of type 'r' must be [0; 31].")

            case 'v':
                # result registers v0-v7 (0x021 - 0x028)
                offset = 33
                # registry id must be [0; 7]
                if not (0 <= regId <= 7):
                    raise SyntaxError(consolePrefix(lineNumber) + "Registers of type 'v' must be [0; 7].")

            case 'a':
                # argument registers a0-a7 (0x029 - 0x030)
                offset = 41
                # registry id must be [0; 7]
                if not (0 <= regId <= 7):
                    raise SyntaxError(consolePrefix(lineNumber) + "Registers of type 'a' must be [0; 7].")

            case _:
                # invalid register designation
                raise SyntaxError(consolePrefix(lineNumber) + "Register designation \"" + str(s) + "\" is invalid.")

    result = offset + regId
    if debug:
        print(consolePrefix(lineNumber) + "Reg " + str(s) + " is addressed " + str(hex(result)))
    return format(result, '09b')


def consolePrefix(lineNumber):
    return "[Line " + str(lineNumber) + "] "


def main():
    a = prepareFile("../resources/test.asm")
    print(a)
    parse(a)


if __name__ == '__main__':
    main()
