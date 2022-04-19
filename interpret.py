#VUT FIT IPP PROJ2 interpret.py
#autor: Stepan Bilek
#login: xbilek25

import argparse
from sys import stderr, stdin, exit
import re
import xml.etree.ElementTree as ET


# globalni promenne
source_file = ""
input_file = ""
instructions = list()
position = 0
labels = dict()
GF = dict()
TF = None
LF = list()
calls = list()

# definice trid
class Instruction:
    def __init__(self, instr_opcode, number):
        self.instr_opcode = instr_opcode
        self.number = number
        self.args = []

    def add_argument(self, type, value):
        self.args.append(Argument(type, value))


class Argument:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Variable:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# definice funkci pro kontrolu chyb

# funkce bere jako parametr instrukci a kontroluje zda ma spravny pocet argumentu, pokud nema, vraci chybu
def check_arguments_count(instruction):
    if (instruction.instr_opcode == "CREATEFRAME" or
        instruction.instr_opcode == "PUSHFRAME" or
        instruction.instr_opcode == "POPFRAME" or
        instruction.instr_opcode == "RETURN" or
        instruction.instr_opcode == "BREAK"):
        if len(instruction.args) != 0:
            stderr.write("error wrong amount of arguments")
            exit(32)
    elif (instruction.instr_opcode == "DEFVAR" or
          instruction.instr_opcode == "CALL" or
          instruction.instr_opcode == "PUSHS" or
          instruction.instr_opcode == "POPS" or
          instruction.instr_opcode == "WRITE" or
          instruction.instr_opcode == "LABEL" or
          instruction.instr_opcode == "JUMP" or
          instruction.instr_opcode == "EXIT"):
            if len(instruction.args) != 1:
                stderr.write(("error wrong amount of arguments"))
                exit(32)
    elif (instruction.instr_opcode == "MOVE" or
          instruction.instr_opcode == "INT2CHAR" or
          instruction.instr_opcode == "READ" or
          instruction.instr_opcode == "STRLEN" or
          instruction.instr_opcode == "TYPE" or
          instruction.instr_opcode == "NOT"):
            if len(instruction.args) !=2:
                stderr.write("error wrong amount of arguments")
                exit(32)
    elif (instruction.instr_opcode == "ADD" or
          instruction.instr_opcode == "SUB" or
          instruction.instr_opcode == "MUL" or
          instruction.instr_opcode == "IDIV" or
          instruction.instr_opcode == "LT" or
          instruction.instr_opcode == "GT" or
          instruction.instr_opcode == "EQ" or
          instruction.instr_opcode == "AND" or
          instruction.instr_opcode == "OR" or
          instruction.instr_opcode == "STRI2INT" or
          instruction.instr_opcode == "CONCAT" or
          instruction.instr_opcode == "GETCHAR" or
          instruction.instr_opcode == "SETCHAR" or
          instruction.instr_opcode == "JUMPIFEQ" or
          instruction.instr_opcode == "JUMPIFNEQ"):
            if len(instruction.args) != 3:
                stderr.write("error wrong amount of arguments")
                exit(32)


def check_instruction(i):
    check_arguments_count(i)

# funkce bere jako parametry zpusob ulozeni promenne a samotnou pormennou,
# zkontroluje zda byla inicializovana, pokud ne, tak skonci chybou
def check_var_init(frame, var):
    if frame == "GF":
        if not (var in GF.keys()):
            stderr.write("error not initialized variable\n")
            exit(54)
    elif frame == "TF":
        if TF is None:
            stderr.write("erron not initialized TF\n")
            exit(55)

        if not (var in TF.keys()):
            stderr.write("error not initialized variable\n")
            exit(54)
    elif frame == "LF":
        if len(LF) == 0:
            stderr.write("error no LF\n")
            exit(55)

        if not (var in LF[len(LF) - 1].keys()):
            stderr.write("error not initialized variable\n")
            exit(54)
    else:
        stderr.write("error wrong frame\n")
        exit(99)

# funkce bere jako parametry zpusob ulozeni promenne a jeji nazev, vraci promennou
def get_variable(frame, name):
    global TF
    global LF
    if frame == "GF":
        if not name in GF.keys():
            stderr.write("error variable doesnt exist\n")
            exit(54)
        return GF[name]
    elif frame == "TF":
        if TF is None:
            stderr.write("error no TF\n")
            exit(55)
        if not name in TF.keys():
            stderr.write("error varieable doesnt exist\n")
            exit(54)
        return TF[name]
    elif frame == "LF":
        if len(LF) == 0:
            stderr.write("error no LF\n")
            exit(55)
        if not name in LF[len(LF)-1].keys():
            stderr.write("Variable doesnt exist\n")
            exit(54)
        return LF[len(LF)-1][name]

# funkce bere jako parametry zpusob ulozeni, nazev a argument(hodnotu) promenne, do promenne s nazvem ulozi hodnotu
def save_var(frame, name, arg):
    if re.match(r"(int|string|bool|nil)", arg.type):
        if frame == "GF":
            GF[name] = Variable(arg.type, arg.value)
        elif frame == "TF":
            if TF is None:
                stderr.write("error TF does not exits \n")
                exit(55)
            TF[name] = Variable(arg.type, arg.value)
        elif frame == "LF":
            if len(LF) == 0:
                stderr.write("error LF does not exist \n")
                exit(55)
            LF[len(LF)-1][name] = Variable(arg.type, arg.value)
        else:
            stderr.write("error wrong frame \n")
            exit(55)
    elif arg.type == var:
        var = arg.value.split("@")
        hold = get_variable(var[0], var[1]) #276
        if frame == "GF":
            GF[name] = Variable(hold.type, hold.value)
        elif frame == "TF":
            if TF is None:
                stderr.write("error no TF")
                exit(55)
            TF[name] = Variable(hold.type, hold.value)
        elif frame == "LF":
            if len(LF) == 0:
                stderr.write("error no LF")
                exit(55)
            LF[len(LF-1)][name] = Variable(hold.type, hold.value)
        else:
            stderr.write("error wrong frame\n")
            exit(55)
    else:
        stderr.write("error saving variable\n")
        exit(99)

# ################### funkce vykonavajici instrukce jazyka IPPcode22 ################3
def move(var, symb):
    split = var.value.split("@")
    check_var_init(split[0], split[1])
    save_var(split[0], split[1], symb)


def createframe():
    global TF
    TF = dict()

def pushframe():
    global TF
    global LF
    LF.append(TF)
    TF = None

def popframe():
    global TF
    global LF
    TF = LF.pop()         # todo error handle

def defvar(par1):
    split = par1.value.split("@")
    var = Variable(None, None)
    if split[0] == "GF":
        if split[1] in GF.keys():
            stderr.write("ereor variable already exists \n")
            exit(52)
        GF.update({split[1]: var})
    elif split[0] == "TF":
        if TF is None:
            stderr.write("error no TF")
            exit(52)
        if split [1] in TF.keys():
            stderr.write("error variable already exists \n")
            exit(52)
        TF.update({split[1]: var})
    elif split[0] == "LF":
        if LF.count() == 0:
            stderr.write("error no LF in stack \n")
            exit(52)
        if split[1] in LF[len(LF)-1].keys():
            stderr.write("error variable already exists")
            exit(52)
        LF[len(LF)-1].update({split[1]: var})


def call(pos, label):
    global position
    calls.append(pos)
    if not(label.value in labels.keys()):
        stderr.write("error label doesnt exist \n")
        exit(52)
    position = int(labels[label.value]-1)

def instruction_return():
    global calls
    global position
    if len(calls) == 0:
        stderr.write("error no call\n")
        exit(56)
    tmp = calls.pop()
    position = int(tmp-1)


def pushs(symb):
    print("TODO push ")


def pops(var):
    print("TODO pop ")


def add(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if symb1.type != "int" or symb2.type != "int":
        stderr.write("error arithmetic non-int")
        exit(53)
    tmp1 = Argument("int", int(symb1.value) + int(symb2.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def sub(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])

    if symb1.type != "int" or symb2.type != "int":
        stderr.write("error arithmetic non-int")
        exit(53)

    tmp1 = Argument("int", int(symb1.value) - int(symb2.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def mul(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])

    if symb1.type != "int" or symb2.type != "int":
        stderr.write("error arithmetic non-int")
        exit(53)

    tmp1 = Argument("int", int(symb1.value) * int(symb2.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def idiv(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])

    if int(symb2.value) == 0:
        stderr.write("error, division by zero")
        exit(57)

    if symb1.type != "int" or symb2.type != "int":
        stderr.write("error arithmetic non-int")
        exit(53)

    tmp1 = Argument("int", int(int(symb1.value) / int(symb2.value)))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def lt(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if (symb1.value or symb2.value) == "nil":
       stderr.write("error cant compare nill variable")
       exit(53)

    tmp1 = Argument("bool", symb1.value < symb2.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)

def gt(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if (symb1.value or symb2.value) == "nil":
       stderr.write("error cant compare nill variable")
       exit(53)

    tmp1 = Argument("bool", symb1.value > symb2.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)

def eq(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    tmp1 = Argument("bool", symb1.value == symb2.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)

def instruction_and(var, symb1, symb2):                 # todo kontrola ze jde o bool, same u or
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if symb1.type != "bool" or symb2.type != "bool":
        stderr.write("error logical operator on non-bool")
        exit(53)
    tmp1 = Argument("bool", symb1.value and symb2.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def instruction_or(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if symb1.type != "bool" or symb2.type != "bool":
        stderr.write("error logical operator on non-bool")
        exit(53)
    tmp1 = Argument("bool", symb1.value or symb2.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def instruction_not(var, symb):
    if symb.type == "var":
        tmp = symb.value.split("@")
        symb = get_variable(tmp[0], tmp[1])
    tmp1 = Argument("bool", not symb.value)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def int2char(var, symb):
    if symb.type == "var":
        tmp = symb.value.split("@")
        symb = get_variable(tmp[0], tmp[1])
    tmp1 = Argument("string", chr(symb.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def stri2int(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if int(symb2.value) < 0 or int(symb2.value) > len(symb1.value)-1:
        stderr.write("error out of bounds")
        exit(58)
    tmp1 = Argument("int", ord(symb1.value[int(symb2.value)]))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)

def write(var):
    global TF, LF
    if var.type == "nil":
        print("", end = '')
    elif var.type == "bool":
        print(var.value, end = '')
    elif var.type == "var":
        tmp = var.value.split("@")
        var = get_variable(tmp[0], tmp[1])
        if var.value is None:
            print("", end = '')
        else:
            print(var.value, end = '')
    else:
        tmp = re.split(r"\\", var.value)
        out = ""
        for i in range (0, len(tmp)):
            if (i == 0):
                out += tmp[i]
            else:
                out += chr(int(tmp[i]))
        print(out, end = '')


def concat(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if symb1.type != "string" or symb2.type != "string":
        stderr.write("error can't concat non-strings")
        exit(53)
    tmp1 = Argument("string", str(symb1.value)+str(symb2.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def strlen(var, symb):
    if symb.type == "var":
        tmp = symb.value.split("@")
        symb = get_variable(tmp[0], tmp[1])
    if symb.type != "string":
        stderr.write("error can't strlen non-strings")
        exit(53)
    tmp1 = Argument("string", len(symb.value))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def getchar(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if (int(symb2.value) < 0) or (int(symb2.value) > len(symb1.value)-1):
        stderr.write("error out of bounds")
        exit(58)
    tmp1 = Argument("string", str(symb1.value[int(symb2.value)]))
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def setchar(var, symb1, symb2):
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])
    if (int(symb2.value) < 0) or (int(symb2.value) > len(symb1.value)-1):
        stderr.write("error out of bounds")
        exit(58)
    tmp1 = Argument("int", str(symb1.value[int(symb2.value)])) #todo zmenit na setchar, ted aspon funguji erroy
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def instruction_type(var, symb):
    if symb.type == "var":
        tmp = symb.value.split("@")
        symb = get_variable(tmp[0], tmp[1])
    tmp1 = Argument("string", symb.type)
    tmp2 = var.value.split("@")
    check_var_init(tmp2[0], tmp2[1])
    save_var(tmp2[0], tmp2[1], tmp1)


def jump(label):
    global labels, position
    if label in labels.keys():
        position = int(labels[label]-1)
    else:
        stderr.write("error wrong label")
        exit(52)


def jumpifeq(label, symb1, symb2):
    global labels, position
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])

    if (symb1.type != symb2.type):
        if ((symb1.type == "nil") or (symb2.type == "nil")):
            return
        stderr.write("Variables are of different type, exiting...\n")
        exit(53)
    if int(symb1.value) == int(symb2.value):
        jump(label)


def jumpifneq(label, symb1, symb2):
    global labels, position
    if symb1.type == "var":
        tmp = symb1.value.split("@")
        symb1 = get_variable(tmp[0], tmp[1])
    if symb2.type == "var":
        tmp = symb2.value.split("@")
        symb2 = get_variable(tmp[0], tmp[1])

    if (symb1.type != symb2.type):
        if ((symb1.type == "nil") or (symb2.type == "nil")):
            return
        stderr.write("Variables are of different type, exiting...\n")
        exit(53)
    if int(symb1.value) != int(symb2.value):
        jump(label)

def instruction_exit(symb):
    if symb.type == "var":
        tmp = symb.value.split("@")
        symb = get_variable(tmp[0], tmp[1])
    if symb.type != "int":
        stderr.write("wrong error code type\n")
        exit(57)
    if (symb.value < 0) or (symb.value > 49):
        stderr.write("wrong error code\n")
        exit(57)
    exit(symb.value)

# funkce bere jako parametr instrukci, podle jejiho opcodu zavola odpovidajici funkci a ta instrukci vykona
def interpret_instruction(instruction):
    if instruction.instr_opcode == "MOVE":
        var = instruction.args[0]
        symb = instruction.args[1]
        move(var, symb)
    elif instruction.instr_opcode == "CREATEFRAME":
        createframe()
    elif instruction.instr_opcode == "PUSHFRAME":
        pushframe()
    elif instruction.instr_opcode == "POPFRAME":
        popframe()
    elif instruction.instr_opcode == "DEFVAR":
        var = instruction.args[0]
        defvar(var)
    elif instruction.instr_opcode == "CALL":
        label = instruction.args[0]
        call(instruction.number, label)
    elif instruction.instr_opcode == "RETURN":
        instruction_return()
    elif instruction.instr_opcode == "PUSHS":
        symb = instruction.args[0]
        pushs(symb)
    elif instruction.instr_opcode == "ADD":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        add(var, symb1, symb2)
    elif instruction.instr_opcode == "SUB":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        sub(var, symb1, symb2)
    elif instruction.instr_opcode == "MUL":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        mul(var, symb1, symb2)
    elif instruction.instr_opcode == "IDIV":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        idiv(var, symb1, symb2)
    elif instruction.instr_opcode == "LT":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        lt(var, symb1, symb2)
    elif instruction.instr_opcode == "GT":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        gt(var, symb1, symb2)
    elif instruction.instr_opcode == "EQ":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        eq(var, symb1, symb2)
    elif instruction.instr_opcode == "AND":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        instruction_and(var, symb1, symb2)
    elif instruction.instr_opcode == "OR":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        instruction_or(var, symb1, symb2)
    elif instruction.instr_opcode == "WRITE":
        var = instruction.args[0]
        write(var)
    elif instruction.instr_opcode == "CONCAT":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        concat(var, symb1, symb2)
    elif instruction.instr_opcode == "STRLEN":
        var = instruction.args[0]
        symb = instruction.args[1]
        strlen(var, symb)
    elif instruction.instr_opcode == "GETCHAR":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        getchar(var, symb1, symb2)
    elif instruction.instr_opcode == "INT2CHAR":
        var = instruction.args[0]
        symb = instruction.args[1]
        int2char(var, symb)
    elif instruction.instr_opcode == "STRI2INT":
        var = instruction.args[0]
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        stri2int(var, symb1, symb2)
    elif instruction.instr_opcode == "LABEL":
        pass
    elif instruction.instr_opcode == "JUMP":
        label = instruction.args[0].value
        jump(label)
    elif instruction.instr_opcode == "JUMPIFEQ":
        label = instruction.args[0].value
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        jumpifeq(label, symb1, symb2)
    elif instruction.instr_opcode == "JUMPIFNEQ":
        label = instruction.args[0].value
        symb1 = instruction.args[1]
        symb2 = instruction.args[2]
        jumpifneq(label, symb1, symb2)
    elif instruction.instr_opcode == "EXIT":
        symb = instruction.args[0]
        instruction_exit(symb)
    elif instruction.instr_opcode == "TYPE":
        var = instruction.args[0]
        symb = instruction.args[1]
        instruction_type(var, symb)


# zpracovani argumentu pomoci knihovny argparse
arguments = argparse.ArgumentParser()
arguments.add_argument("--source", nargs=1, help="input XML code")
arguments.add_argument("--input", nargs=1, help="input for interpreted code")
args = vars(arguments.parse_args())
if args['input']:
    input_file = args['input'][0]
else:
    input_file = None
if args['source']:
    source_file = args['source'][0]
else:
    source_file = None

# zpracovavani XML stromu pomoci knihovny xml.etree.ElementTree
tree = None
try:
    if source_file:
        tree = ET.parse(source_file)
    else:
        tree = ET.parse(stdin)
except Exception as e:
    stderr.write(str(e)+"\n")
    stderr.write("Error parsing source file \n")
    exit(31)

# serazeni instrukci podle poradi
root = tree.getroot()
if root.tag != 'program':
    stderr.write("not a program\n")
    exit(32)

try:
    root[:] = sorted(root, key=lambda child: (child.tag, int(child.get('order'))))
except Exception as e:
    stderr.write(str(e)+"\n")
    stderr.write("error sorting instructions\n")
    exit(32)

for child in root:
    try:
        child[:] = sorted(child, key=lambda child: (child.tag))
    except Exception as e:
        stderr.write(str(e)+"\n")
        stderr.write("Error occured when sorting argmuents\n")
        exit(32)

instruction_count = 1

# naplneni seznamu instrukci
for element in root:
    instructions.append(Instruction(element.attrib['opcode'].upper(), instruction_count))
    for subelement in element:
        instructions[instruction_count-1].add_argument(subelement.attrib['type'].lower(), subelement.text)
    instruction_count += 1

for child in root:
  dup = set()
  for c in child:
    if c.tag not in dup:
      dup.add(c.tag)
  if len(dup) != len(child):
    stderr.write("error duplicate elements\n")
    exit(32)


# smycka prochazi vsechny instrukce, kontroluje spravne pocty argumentu a uklada navesti do slovniku labels
for i in instructions:
    check_instruction(i)
    if i.instr_opcode == "LABEL":
        labels.update({i.args[0].value: i.number})

# hlavni smycka, vykonava instrukce
while position != len(instructions):
    interpret_instruction(instructions[position])
    position += 1
