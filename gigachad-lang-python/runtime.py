import re


class Data:
    def __init__(self, data: str, type: type):
        self.data = data
        self.type = type


class Util:
    @staticmethod
    def check_type(type: type, data: object):
        if type == int:
            return isinstance(data, int) or data.isdecimal()
        return True


class GigaChad:
    def __init__(self):
        self.datas = {}

    def compile_input(self, line):
        tokens = line.split(",")
        if len(tokens) != 3:
            raise ValueError(f"{line}을 해석할 수 없습니다. 입력 사용 예시")
        des_value = tokens[1].strip()
        if not self.datas.get(des_value):
            raise KeyError(f"{des_value}라는 변수는 정의되지 않았습니다.")
        prompt = tokens[2].strip().strip("?")
        prompt = prompt.strip('"')
        if self.datas[des_value].type == int:
            temp = input(prompt)
            if not Util.check_type(int, temp):
                raise ValueError(
                    f"int type인 변수 {des_value}에 {temp}를 지정할 수 없습니다.")
            self.datas[des_value].data = int(temp)
        else:
            self.datas[des_value].data = str(input(prompt))

    def compile_define(self, line: str):
        tokens = line.replace("너는 이제부터", "").strip().split()
        if len(tokens) == 4 and tokens[1] in ("ASSHOLE", "BADASS"):
            type_, name = tokens[1].strip(), tokens[2].strip()
            if self.datas.get(name):
                raise ValueError(f"{name}은 이미 선언된 변수입니다.")
            self.datas[name] = Data(
                None, int if type_ == "ASSHOLE" else str)
        else:
            raise ValueError(f"Can't Interpret this line: {line}")

    def compile_substitute(self, line: str):
        des_value = line.split(",")[0].strip()
        if not self.datas.get(des_value):
            raise ValueError(f"{des_value}라는 변수는 정의되어있지 않습니다. 변수를 먼저 지정해주세요.")
        tokens = line.split(" ")
        if len(tokens) <= 4:
            raise ValueError(f"{line}에 대입할 변수를 지정하지 않았습니다.")
        tokens = tokens[3:-1]
        insert_value = self.compile_instruction(" ".join(tokens))

        if not Util.check_type(self.datas[des_value].type, insert_value):
            raise ValueError(
                f"{self.datas[des_value].type} 타입의 변수 {des_value}에 {insert_value}를 넣을 수 없습니다.")

        self.datas[des_value].data = insert_value

    def compile_output(self, line: str):
        tokens = line.split("기적같은 하루가 널 기다려,")
        data = self.compile_instruction(tokens[1])
        print(data, end='')

    def compile_instruction(self, line: str):
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            return line.replace('"', '')

        need_eval = False
        if "HARD TRAINING" in line or "STOP OVER THINKING" in line or "AIM HIGH" in line or "DONT GIVE A SHIT" in line:
            need_eval = True
        line = line.replace("HARD TRAINING", "+")
        line = line.replace("STOP OVER THINKING", "-")
        line = line.replace("AIM HIGH", "*")
        line = line.replace("DONT GIVE A SHIT", "/")
        tokens = line.split(" ")
        output = []
        for token in tokens:
            if token.strip() == "":
                continue
            if self.datas.get(token):
                output.append(self.datas[token].data)
            else:
                output.append(token)
        try:
            if need_eval:
                return eval(" ".join(map(str, output)).replace('"', ''))
            else:
                return " ".join(map(str, output)).replace('"', '')
        except:
            raise TypeError(f"표현식 {line}을 해석하지 못하였습니다.")

    def compile(self, code):
        splitter = '\n'
        lines = code.rstrip().split(splitter)
        if lines[0] != "Of Course" or lines[-1] != "See you tomorrow My Son":
            raise ValueError(
                "기가채드는 Of Course로 시작해서 See you tomorrow My Son으로 끝나야해.")
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
                self.compile_input(line)
            # 출력
            elif line.startswith("기적같은 하루가"):
                self.compile_output(line)
            # 줄바꿈
            elif line.startswith("Go To Next Step, My Son"):
                print()
            # 빈 공간
            elif line.strip() == "":
                continue
            else:
                raise NotImplementedError(f"{line}을 읽을 수 없어")
