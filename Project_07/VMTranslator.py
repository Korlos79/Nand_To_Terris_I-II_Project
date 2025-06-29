#!/usr/bin/python
import os, sys


class Parser:
  def __init__(self, source):
    self.infile = open(source) # Mở file chứa code VM
    self.command = ["nada"] # Lệnh hiện tại (khởi tạo mặc định)
    self.advanceReachedEOF = False # Kiểm tra đã đến cuối file chưa

# Xác định loại lệnh
    self.cType = {
        "sub" : "math", # Các phép toán số học
        "add" : "math",
        "neg" : "math",
        "eq"  : "math",
        "gt"  : "math",
        "lt"  : "math",
        "and" : "math",
        "or"  : "math",
        "not" : "math",
        "push" : "push", # Lệnh push
        "pop"  : "pop", # Lệnh pop
        "EOF"  : "EOF", # Cuối file
        }

  def hasMoreCommands(self):
    position = self.infile.tell() # Lưu vị trí hiện tại trong file
    self.advance() # Thử đọc tiếp
    self.infile.seek(position) # Quay lại vị trí cũ
    return not self.advanceReachedEOF # Nếu EOF thì không còn lệnh

  def advance(self):
    thisLine = self.infile.readline() # Đọc một dòng từ file
    if thisLine == '':
      self.advanceReachedEOF = True # Nếu hết file, đặt cờ EOF
    else:
      splitLine = thisLine.split("/")[0].strip() # Loại bỏ comment
      if splitLine == '':
        self.advance() # Nếu dòng rỗng, đọc tiếp
      else:
        self.command = splitLine.split() # Lưu lệnh vào `self.command`

  def commandType(self):
    return self.cType.get(self.command[0], "invalid cType")
#Kiểm tra lệnh đầu tiên trong self.command.
#Nếu khớp với cType, trả về loại lệnh ("math", "push", "pop").
#Nếu không có trong danh sách, trả về "invalid cType".
  def arg1(self):
    return self.command[1]
#Lấy đối số đầu tiên (thường là segment hoặc điều kiện so sánh).
  def arg2(self):
    return self.command[2]
#Lấy đối số thứ hai (thường là index trong push/pop).

class CodeWriter:
  def __init__(self, dest):
    self.root = dest[:-4].split('/')[-1] # Lấy tên file không có phần mở rộng
    self.outfile = open(dest, "w") # Mở file đích dest để ghi Assembly code
    self.nextLabel = 0 # Biến đếm cho nhãn nhảy (jump labels)

  def setFileName(self, source):
    self.fileName = source[:-3] #đặt tên file hiện tại không có phần mở rộng .vm

  def writeArithmetic(self, command):
    trans = ""
    if command == "add":
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
    #M=M-1: Giảm giá trị của SP xuống 1, tức là di chuyển con trỏ stack xuống 1 đơn vị.
    #A=M: Sau khi giảm SP, A sẽ chứa giá trị mới của SP, tức là trỏ đến phần tử trên cùng mới của stack.
      trans += "D=M\n" 
      trans += "@SP\n" # pop second value into M
      trans += "AM=M-1\n" 
      trans += "M=D+M\n" # push sum onto M
      trans += "@SP\n"
      trans += "M=M+1\n" 
    elif command == "sub":
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # pop second value into M
      trans += "AM=M-1\n" 
      trans += "M=M-D\n" # push difference onto M
      trans += "@SP\n"
      trans += "M=M+1\n" 
    elif command == "neg":
      trans += "@SP\n" # get (not pop) value into M
      trans += "A=M-1\n" 
      trans += "M=-M\n" # and negate it 
    elif command == "not":
      trans += "@SP\n" # get (not pop) value into M
      trans += "A=M-1\n" 
      trans += "M=!M\n" # and negate it 
    elif command == "or":
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # get second value into M
      trans += "A=M-1\n"
      trans += "M=D|M\n" # put result back on stack
    elif command == "and":
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # get second value into M
      trans += "A=M-1\n"
      trans += "M=D&M\n" # put result back on stack
    elif command == "eq":
      label = str(self.nextLabel)
      self.nextLabel += 1
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # get second value into M
      trans += "A=M-1\n"
      trans += "D=M-D\n" # D = older value - newer
      trans += "M=-1\n" # tentatively put true on stack
      trans += "@eqTrue" + label + "\n" # and jump to end if so
      trans += "D;JEQ\n"
      trans += "@SP\n" # set to false otherwise
      trans += "A=M-1\n"
      trans += "M=0\n" 
      trans += "(eqTrue" + label + ")\n"
    elif command == "gt":
      label = str(self.nextLabel)
      self.nextLabel += 1
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # get second value into M
      trans += "A=M-1\n"
      trans += "D=M-D\n" # D = older value - newer
      trans += "M=-1\n" # tentatively put true on stack
      trans += "@gtTrue" + label + "\n" # and jump to end if so
      trans += "D;JGT\n"
      trans += "@SP\n" # set to false otherwise
      trans += "A=M-1\n"
      trans += "M=0\n" 
      trans += "(gtTrue" + label + ")\n"
    elif command == "lt":
      label = str(self.nextLabel)
      self.nextLabel += 1
      trans += "@SP\n" # pop first value into D
      trans += "AM=M-1\n"
      trans += "D=M\n" 
      trans += "@SP\n" # get second value into M
      trans += "A=M-1\n"
      trans += "D=M-D\n" # D = older value - newer
      trans += "M=-1\n" # tentatively put true on stack
      trans += "@ltTrue" + label + "\n" # and jump to end if so
      trans += "D;JLT\n"
      trans += "@SP\n" # set to false otherwise
      trans += "A=M-1\n"
      trans += "M=0\n" 
      trans += "(ltTrue" + label + ")\n"
    else:
      trans = command + " not implemented yet\n"
    self.outfile.write("// " + command + "\n" + trans)

  def writePushPop(self, command, segment, index):
    trans = ""
    if command == "push":
      trans += "// push " + segment + index + "\n"
      if segment == "constant":
        trans += "@" + index + "\n" # load index into A
        trans += "D=A\n" # move it to D
        trans += "@SP\n" # load 0 into A (M[0] contains stack pointer)
        trans += "A=M\n" # load stack pointer
        trans += "M=D\n" # put D onto stack
        trans += "@SP\n" # load stack pointer address into A
        trans += "M=M+1\n" # increment stack pointer
      elif segment == "static":
        trans += "@" + self.root + "." + index + "\n"
        trans += "D=M\n"
        trans += "@SP\n" 
        trans += "A=M\n" 
        trans += "M=D\n"
        trans += "@SP\n"
        trans += "M=M+1\n"
      elif segment == "this":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n" # Đưa giá trị vào D
        trans += "@THIS\n" # Load địa chỉ của THIS segment
        trans += "A=M+D\n"  #A trỏ đến `THIS[index]`
        trans += "D=M\n" #Lấy giá trị `THIS[index]` vào D
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      elif segment == "that":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n"
        trans += "@THAT\n"
        trans += "A=M+D\n" 
        trans += "D=M\n"
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      elif segment == "argument":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n"
        trans += "@ARG\n"
        trans += "A=M+D\n" 
        trans += "D=M\n"
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      elif segment == "local":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n"
        trans += "@LCL\n"
        trans += "A=M+D\n" 
        trans += "D=M\n"
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      elif segment == "temp":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n"
        trans += "@5\n"
        trans += "A=A+D\n" 
        trans += "D=M\n"
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      elif segment == "pointer":
        trans += "@" + index + "\n" # get value into D
        trans += "D=A\n"
        trans += "@3\n"
        trans += "A=A+D\n" 
        trans += "D=M\n"
        trans += "@SP\n" # put it onto the stack
        trans += "A=M\n"
        trans += "M=D\n"
        trans += "@SP\n" # increment the stack pointer
        trans += "M=M+1\n"
      else:
        trans += segment + " not implemented yet, can't push\n"
    elif command == "pop":
      trans += "// pop " + segment + index + "\n"
      if segment == "static":
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@" + self.root + "." + index + "\n"
        trans += "M=D\n"
      elif segment == "this":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@THIS\n"
        trans += "D=M+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      elif segment == "that":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@THAT\n"
        trans += "D=M+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      elif segment == "argument":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@ARG\n"
        trans += "D=M+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      elif segment == "local":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@LCL\n"
        trans += "D=M+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      elif segment == "pointer":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@3\n"
        trans += "D=A+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      elif segment == "temp":
        trans += "@" + index + "\n" # get address into R13
        trans += "D=A\n"
        trans += "@5\n"
        trans += "D=A+D\n" 
        trans += "@R13\n"
        trans += "M=D\n"
        trans += "@SP\n" # pop value into D
        trans += "AM=M-1\n"
        trans += "D=M\n"
        trans += "@R13\n" # address back in A (no touchy D)
        trans += "A=M\n"
        trans += "M=D\n"
      else:
        trans += segment + " not implemented yet, can't pop\n"
    self.outfile.write(trans)

  def writeError(self):
    self.outfile.write("Whoopsie, command not recognized\n")
    
def main():
  root = sys.argv[1] # Đọc tên tệp gốc từ tham số dòng lệnh
  parser = Parser(root + ".vm") # Tạo đối tượng Parser để xử lý tệp .vm
  writer = CodeWriter(root + ".asm") # Tạo đối tượng CodeWriter để ghi mã Assembly vào tệp .asm
    
  
  while parser.hasMoreCommands(): # Tiến hành đọc và xử lý từng lệnh trong tệp VM
    parser.advance() # Đọc lệnh tiếp theo
    cType = parser.commandType() # Lấy kiểu lệnh
    if cType == "push" or cType == "pop":
      writer.writePushPop(cType, parser.arg1(), parser.arg2())
    elif cType == "math":
      writer.writeArithmetic(parser.command[0])
    else:
      writer.writeError()

if __name__ == "__main__":
  main()

  

