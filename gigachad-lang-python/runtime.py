from .error import ErrorMessage
from .parser import Parser
from .interpreter import Interpreter
import json
import os


class GigaChad:
    def __init__(self):
        json_path = os.path.join(os.path.dirname(__file__), "../gigachad.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                error_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "기가차드 에러 메시지 JSON이 사라졌다. 그건 마치 체육관에 벤치 없는 꼴이다.")
        self.errorMessage = ErrorMessage(**error_data)

    def compile(self, code):
        program = Parser(self.errorMessage).parse_program(code)
        Interpreter(self.errorMessage).exec_program(program)
