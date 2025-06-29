import os,sys

dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "DM": "011",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "AMD": "111",
    "DMA": "111",
    "MDA": "111",
    "MAD": "111",
    "DAM": "111",
    "ADM": "111"
}

comp={
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "1+D": "0011111",
    "A+1": "0110111",
    "1+A": "0110111",
    "D-1": "0001110",
    "-1+D": "0001110",
    "A-1": "0110010",
    "-1+A": "0110010",
    "D+A": "0000010",
    "A+D": "0000010",
    "D-A": "0010011",
    "-A+D": "0010011",
    "A-D": "0000111",
    "-D+A": "0000111",
    "D&A": "0000000",
    "A&D": "0000000",
    "D|A": "0010101",
    "A|D": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "1+M": "1110111",
    "M-1": "1110010",
    "-1+M": "1110010",
    "D+M": "1000010",
    "M+D": "1000010",
    "D-M": "1010011",
    "-M+D": "1010011",
    "M-D": "1000111",
    "-D+M": "1000111",
    "D&M": "1000000",
    "M&D": "1000000",
    "D|M": "1010101",
    "M|D": "1010101"    
}

jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

table={
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576    
}

for i in range(0,16):
    reg="R"+str(i)
    table[reg]=i

variablepointer=16
filename = sys.argv[1]

def strip(line):
    char = line[0]
    if char == "\n" or char =="/":
        return ""
    elif char == " ":
        return strip(line[1:])
    else:
        return char + strip(line[1:])

def normalize(line):
    line = line[:-1]
    if not "=" in line:
        line = "null=" + line
    if not ";" in line:
        line = line + ";null"
    return line

def addVariables(symbol):
    global variablepointer
    table[symbol]=variablepointer
    variablepointer+=1
    return table[symbol]

def aTranslate(line):
    if line[1].isalpha():
        value=line[1:-1]
        aValue=table.get(value,-1)
        if aValue == -1:
            aValue=addVariables(value)
    else:
        aValue=int(line[1:])
    bValue=bin(aValue)[2:].zfill(16)
    return bValue

def cTranslate(line):
    line = normalize(line)
    temp=line.split("=")
    destCode = dest.get(temp[0],"destfail")
    temp=temp[1].split(";")
    compCode=comp.get(temp[0],"compfail")
    jumpCode=jump.get(temp[1],"jumpfail")
    return compCode, destCode, jumpCode

def translate(line):
    if line[0] == "@":
        return aTranslate(line)
    else:
        codes=cTranslate(line)
        return "111"+codes[0]+codes[1]+codes[2]

def firstPass():
    infile=open(filename+".asm")
    outfile=open(filename+".inter","w")
    lineNumber = 0
    for line in infile:
        sline = strip(line)
        if sline != "":
            if sline[0] == "(":
                label=sline[1:-1]
                table[label]=lineNumber
                sline=""
            else:
                lineNumber+=1
                outfile.write(sline+"\n")
    infile.close()
    outfile.close()

def secondPass():
    infile=open(filename+".inter")
    outfile=open(filename+".hack","w")
    for line in infile:
        tline=translate(line)
        outfile.write(tline+"\n")
    infile.close()
    outfile.close()
    os.remove(filename+".inter")

firstPass()
secondPass()
