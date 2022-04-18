import argparse
from sys import stderr, stdin, exit
import re
import xml.etree.ElementTree as ET

source_file = ""
input_file = ""
instructions = list()
position = 0
labels = dict()
GF = dict()
TF = None
LF = list()
# ##CLASSES


class Instruction:
    def __init__(self, instr_opcode, number):
        self.instr_opcode = instr_opcode
        self.number = number
        self.args = []

    def add_argument(self, arg_type, value):
        self.args.append(Argument(arg_type, value))


class Argument:
    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value


class Variable:
    def __init__(self, var_type, value):
        self.var_type = var_type
        self.value = value

# def check_argument_count():

def check_instruction(i):
    print("instrukce checknuta\n"+str(i))

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
        # chceck var existence
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


def move(var, symb):
    split = var.value.split("@")


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

def interpret_instruction(instruction):
    global position
    global TF
    global LF
    if instruction.instr_opcode == "MOVE":
        var = instruction.args[0]
        symb = instruction.args[1]
        move(var)
    elif instruction.instr_opcode == "CREATEFRAME":
        createframe()
    elif instruction.instr_opcode == "PUSHFRAME":
        pushframe()
    elif instruction.instr_opcode == "POPFRAME":
        popframe()
    elif instruction.instr_opcode == "DEFVAR":
        var = instruction.args[0]
        defvar(var)

# # ###argumenty


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

# ########XML parse

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

# ##sort
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
for element in root:
    instructions.append(Instruction(element.attrib['opcode'].upper(), instruction_count))
    for subelement in element:
        instructions[instruction_count-1].add_argument(subelement.attrib['type'].lower(), subelement.text)
    instruction_count += 1

for i in instructions:
    check_instruction(i)

for i in instructions:
    if i.instr_opcode == "LABEL":
        labels.update({i.args[0].value: i.number})



while position != len(instructions):
    print("pocet: "+str(len(instructions)))
    interpret_instruction(instructions[position])
    position += 1