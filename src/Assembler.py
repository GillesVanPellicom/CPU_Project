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
        if "\n" in arr[i]:
            arr[i] = arr[i].replace("\n", '')

        # mark empty lines for removal
        if len(arr[i]) == 0:
            toRemove.append(i)

    for i in range(len(toRemove) - 1, -1, -1):
        del arr[toRemove[i]]

    return arr


def lexer(preparedFile):
    labels = []
    instrl = []
    for i in range(len(preparedFile)):
        error = False

        if preparedFile[i][-1] == ':':
            # label
            labels.append(preparedFile[i])

        elif preparedFile[i] == "noop":
            # noop - 00000
            instrl.append("00000 000000000 000000000 000000000")

        elif preparedFile[i][0:4] == "add ":
            # add - 00001
            ins = "00001"
            args = preparedFile[i][4:].replace(' ', '').split(',')

            # check argument count
            if len(args) != 3:
                error = True

            # generate instruction
            ins += ' ' + regNameToAddress(args[0], i + 1) + ' ' + regNameToAddress(args[1],
                                                                                   i + 1) + ' ' + regNameToAddress(
                args[2], i + 1)
            # append to instruction list
            instrl.append(ins)

        elif preparedFile[i][0:5] == "addi ":
            # addi - 00010
            ins = "00010"
            args = preparedFile[i][5:].replace(' ', '').split(',')

            # check argument count
            if len(args) != 2:
                error = True

            # FIXME 2's complement
            # check if immediate is too large
            if int(args[1]) > pow(2, 16) - 1:
                raise SyntaxError(consolePrefix(i + 1) + "Immediate too large")

            # FIXME 2's complement
            # generate instruction
            ins += ' ' + regNameToAddress(args[0], i + 1) + ' ' + format(int(args[1]), '018b')

            # append to instruction list
            instrl.append(ins)

        elif preparedFile[i][0:3] == "or ":
            # or - 00011
            ins = "00011"
            args = preparedFile[i][3:].replace(' ', '').split(',')

            # check argument count
            if len(args) != 3:
                error = True

            # generate instruction
            ins += ' ' + regNameToAddress(args[0], i + 1) + ' ' + regNameToAddress(args[1],
                                                                                   i + 1) + ' ' + regNameToAddress(
                args[2], i + 1)

            # append to instruction list
            instrl.append(ins)

        if error:
            raise SyntaxError(consolePrefix(i + 1) + "Invalid argument(s).")
    print(instrl)



def regNameToAddress(s, lineNumber):
    # FIXME better regex
    match = re.match(r"([a-z]+)([0-9]+)", s, re.I)
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
                    error = True
            case 'v':
                # result registers v0-v7 (0x021 - 0x028)
                offset = 33
                # registry id must be [0; 7]
                if not (0 <= regId <= 7):
                    error = True
            case 'a':
                # argument registers a0-a7 (0x029 - 0x030)
                offset = 41
                # registry id must be [0; 7]
                if not (0 <= regId <= 7):
                    error = True
            case _:
                # invalid register designation
                error = True

    if error:
        raise SyntaxError(consolePrefix(lineNumber) + "Register designation \"" + str(s) + "\" is invalid.")
    result = offset + regId
    if debug:
        print(consolePrefix(lineNumber) + "Register " + str(s) + " is on address " + str(hex(result)))
    return format(result, '09b')


def consolePrefix(lineNumber):
    return "[Line " + str(lineNumber) + "] "


def main():
    a = prepareFile("../resources/test.asm")
    print(a)
    lexer(a)


if __name__ == '__main__':
    main()
