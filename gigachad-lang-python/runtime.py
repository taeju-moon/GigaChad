import sys

class Data:
    def __init__(self, data, type):
        self.data = data
        self.type = type

class GigaChad:
    def __init__(self):
        self.datas = {}

    def compile_define(self,line):
        tokens = line.replace("너는 이제부터", "").strip().split()
        if len(tokens) == 3 and tokens[0] in ("FUCKING_ASSHOLE", "FUCKING_BADASS"):
            type_, name = tokens[0], tokens[1]
            if self.datas.contains(name):
                raise ValueError(f"{name}은 이미 선언된 변수입니다.")
            self.datas[name] = Data(None, int if type_ == "FUCKING_ASSHOLE" else str)
        else:
            raise ValueError(f"Can't Interpret this line: {line}")
        
    def compile_substitute(self,line):
        des_value = line.split(",")[0]
        if not self.datas.get(des_value):
            raise ValueError(f"{des_value}라는 변수는 정의되어있지 않습니다. 변수를 먼저 지정해주세요.")
        tokens = line.split(" ")
        if len(tokens) <= 4:
            raise ValueError(f"{line}에 대입할 변수를 지정하지 않았습니다.")
        tokens = tokens[1:]
        insert_value = self.compile_instruction(tokens)
        
        if not self.check_type(self.datas[des_value].type, insert_value):
            raise ValueError(f"{self.datas[des_value].type} 타입의 변수 {des_value}에 {insert_value}를 넣을 수 없습니다.")
        
        self.datas[des_value] = insert_value

    def compile_instruction(self, line:str):
        line = line.replace("HARD TRAINING", "+")
        line = line.replace("STOP OVER THINKING", "-")
        line = line.replace("AIM HIGH", "*")
        line = line.replace("DOMINATE THE WEEK", "/")
        try:
            return eval(line)
        except:
            raise TypeError(f"{line}을 해석하지 못하였습니다.")

    def check_type(self,type, data):
        if type == int:
            return data.isdecimal()
        return True

    def compile(self, code):
        splitter = '\n'
        lines = code.rstrip().split(splitter)
        if lines[0] != "Of Course" or lines[-1] != "See you tomorrow My Son":
            raise ValueError("기가채드는 Of Course로 시작해서 See you tomorrow My Son으로 끝나야해.")
        for line in lines[1:-1]:
            line = line.strip()
            # 정의
            if line.startswith("너는 이제부터"):
                self.compile_define(line)
            # 대입
            elif not line.startswith("너는 이제부터") and "너는 이제부터" in line:
                self.compile_substitute(line)
            # 입력
            elif line.startswith("이번엔 또 무슨"):
                pass
            # 출력
            elif line.startswith("기적같은 하루가"):
                pass
            
    def compilePath(self, path):
        with open(path) as file:
            code = ''.join(file.readlines())
            self.compile(code)