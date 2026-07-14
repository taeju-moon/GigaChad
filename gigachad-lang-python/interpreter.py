from .ast_nodes import (
    VarDecl, Assign, Input, Output, NewlinePrint, Loop,
    Concat, BinOp, IntLiteral, StringLiteral, VarRef,
)


class Data:
    def __init__(self, data, type):
        self.data = data
        self.type = type


def _matches_type(var_type, value):
    if var_type is int:
        return isinstance(value, int)
    return True


class Interpreter:
    """Tree-walking evaluator: exec_stmt/eval_expr recurse over the AST."""

    def __init__(self, error_message):
        self.error = error_message
        self.datas = {}

    def exec_program(self, program):
        for stmt in program.statements:
            self.exec_stmt(stmt)

    def exec_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            self._exec_vardecl(stmt)
        elif isinstance(stmt, Assign):
            self._exec_assign(stmt)
        elif isinstance(stmt, Input):
            self._exec_input(stmt)
        elif isinstance(stmt, Output):
            self._exec_output(stmt)
        elif isinstance(stmt, NewlinePrint):
            print()
        elif isinstance(stmt, Loop):
            self._exec_loop(stmt)
        else:
            raise NotImplementedError(self.error.get_interpret_fail_exception(str(stmt)))

    def _exec_vardecl(self, stmt):
        if stmt.name in self.datas:
            raise KeyError(self.error.get_value_already_defined_exception(stmt.name))
        self.datas[stmt.name] = Data(None, stmt.var_type)

    def _exec_assign(self, stmt):
        if stmt.name not in self.datas:
            raise NameError(self.error.get_value_not_defined_exception(stmt.name))
        value = self.eval_expr(stmt.expr)
        if not _matches_type(self.datas[stmt.name].type, value):
            raise ValueError(self.error.get_invalid_value_exception(stmt.name, str(value)))
        self.datas[stmt.name].data = value

    def _exec_input(self, stmt):
        if stmt.name not in self.datas:
            raise KeyError(self.error.get_value_not_defined_exception(stmt.name))
        entry = self.datas[stmt.name]
        raw = input(stmt.prompt)
        if entry.type == int:
            if not raw.isdecimal():
                raise ValueError(self.error.get_invalid_value_exception(stmt.name, raw))
            entry.data = int(raw)
        else:
            entry.data = raw

    def _exec_output(self, stmt):
        print(self.eval_expr(stmt.expr), end="")

    def _exec_loop(self, stmt):
        count = self.eval_expr(stmt.count_expr)
        if not isinstance(count, int):
            raise ValueError(self.error.get_invalid_value_exception(stmt.index_name, str(count)))
        self.datas[stmt.index_name] = Data(None, int)
        for i in range(count):
            self.datas[stmt.index_name].data = i
            for inner in stmt.body:
                self.exec_stmt(inner)

    def eval_expr(self, node):
        if isinstance(node, Concat):
            return " ".join(str(self.eval_expr(part)) for part in node.parts)
        if isinstance(node, BinOp):
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)
            return self._apply_op(node.op, left, right)
        if isinstance(node, IntLiteral):
            return node.value
        if isinstance(node, StringLiteral):
            return node.value
        if isinstance(node, VarRef):
            if node.name in self.datas:
                return self.datas[node.name].data
            return node.name
        raise NotImplementedError(self.error.get_interpret_fail_exception(str(node)))

    def _apply_op(self, op, left, right):
        try:
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right
        except Exception:
            pass
        raise NotImplementedError(self.error.get_interpret_fail_exception(f"{left} {op} {right}"))
