from .lexer import tokenize
from .ast_nodes import (
    Program, VarDecl, Assign, Input, Output, NewlinePrint, Loop,
    Concat, BinOp, IntLiteral, StringLiteral, VarRef,
)

ARITH_OPS = {"OP_ADD": "+", "OP_SUB": "-"}
TERM_OPS = {"OP_MUL": "*", "OP_DIV": "/"}


class Parser:
    """Recursive-descent parser: one .chad line -> one Statement node.

    Statements stay line-delimited (as the grammar always has been) so a bare
    identifier ending one line's Expr can never be mistaken for the next
    line's Assign target.
    """

    def __init__(self, error_message):
        self.error = error_message

    def parse_program(self, code: str) -> Program:
        lines = code.rstrip("\n").split("\n")
        if not lines or lines[0].strip() != "Of Course" or lines[-1].strip() != "See you tomorrow My Son":
            raise SyntaxError(self.error.get_format_exception())
        body = [line.strip() for line in lines[1:-1]]
        statements, _ = self._parse_block(body, 0, closing_kind=None)
        return Program(statements)

    def _parse_block(self, lines, idx, closing_kind):
        """Recursively parses lines[idx:] into a statement list.

        A Loop statement spans multiple lines, so this recurses to gather
        its body up to the matching KW_LOOP_END line, then resumes at the
        block's own level -- the same recursive-descent shape as expressions,
        just one level up (statements instead of Arith/Term/Factor).
        """
        statements = []
        while idx < len(lines):
            line = lines[idx]
            if not line:
                idx += 1
                continue
            tokens = tokenize(line)
            if not tokens:
                idx += 1
                continue
            if closing_kind is not None and len(tokens) == 1 and tokens[0].kind == closing_kind:
                return statements, idx + 1
            if tokens[0].kind == "KW_LOOP_START":
                index_name, count_expr = self._parse_loop_header(line, tokens)
                body, idx = self._parse_block(lines, idx + 1, "KW_LOOP_END")
                statements.append(Loop(index_name, count_expr, body))
                continue
            statements.append(self._parse_statement_line(line))
            idx += 1
        if closing_kind is not None:
            raise NotImplementedError(self.error.get_interpret_fail_exception("만삣삐 반복문이 닫히지 않았다"))
        return statements, idx

    def _parse_loop_header(self, line, tokens):
        self.tokens = tokens
        self.pos = 0
        self._expect("KW_LOOP_START", line)
        self._expect("COMMA", line)
        index_tok = self._expect("IDENT", line)
        self._expect("KW_BY", line)
        count_expr = self._parse_expr(line)
        self._expect("COMMA", line)
        self._expect("KW_FORWARD", line)
        if self.pos != len(self.tokens):
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        return index_tok.text, count_expr

    def _parse_statement_line(self, line):
        self.tokens = tokenize(line)
        self.pos = 0
        if not self.tokens:
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        stmt = self._parse_statement(line)
        if self.pos != len(self.tokens):
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        return stmt

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _expect(self, kind, line):
        tok = self._peek()
        if tok is None or tok.kind != kind:
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        self.pos += 1
        return tok

    def _parse_statement(self, line):
        tok = self._peek()
        if tok is None:
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        if tok.kind == "KW_DEFINE":
            return self._parse_vardecl(line)
        if tok.kind == "KW_INPUT":
            return self._parse_input(line)
        if tok.kind == "KW_OUTPUT":
            return self._parse_output(line)
        if tok.kind == "KW_NEWLINE":
            self.pos += 1
            return NewlinePrint()
        if tok.kind == "IDENT" and self._assign_ahead():
            return self._parse_assign(line)
        raise NotImplementedError(self.error.get_interpret_fail_exception(line))

    def _assign_ahead(self):
        return (
            self.pos + 2 < len(self.tokens)
            and self.tokens[self.pos + 1].kind == "COMMA"
            and self.tokens[self.pos + 2].kind == "KW_DEFINE"
        )

    def _parse_vardecl(self, line):
        self._expect("KW_DEFINE", line)
        type_tok = self._peek()
        if type_tok is None or type_tok.kind not in ("TYPE_INT", "TYPE_STR"):
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        self.pos += 1
        name_tok = self._expect("IDENT", line)
        self._expect("KW_IS", line)
        var_type = int if type_tok.kind == "TYPE_INT" else str
        return VarDecl(var_type, name_tok.text)

    def _parse_assign(self, line):
        name_tok = self._expect("IDENT", line)
        self._expect("COMMA", line)
        self._expect("KW_DEFINE", line)
        expr = self._parse_expr(line)
        self._expect("KW_IS", line)
        return Assign(name_tok.text, expr)

    def _parse_input(self, line):
        self._expect("KW_INPUT", line)
        self._expect("COMMA", line)
        name_tok = self._expect("IDENT", line)
        self._expect("COMMA", line)
        prompt = self._parse_prompt(line)
        self._expect("QMARK", line)
        return Input(name_tok.text, prompt)

    def _parse_prompt(self, line):
        parts = []
        while self._peek() is not None and self._peek().kind != "QMARK":
            parts.append(self.tokens[self.pos].text)
            self.pos += 1
        if not parts:
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        text = " ".join(parts)
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text

    def _parse_output(self, line):
        self._expect("KW_OUTPUT", line)
        self._expect("COMMA", line)
        return Output(self._parse_expr(line))

    def _parse_expr(self, line):
        parts = [self._parse_arith(line)]
        while self._peek() is not None and self._peek().kind in ("INT", "STRING", "IDENT"):
            parts.append(self._parse_arith(line))
        if len(parts) == 1:
            return parts[0]
        return Concat(parts)

    def _parse_arith(self, line):
        node = self._parse_term(line)
        while self._peek() is not None and self._peek().kind in ARITH_OPS:
            op = ARITH_OPS[self._peek().kind]
            self.pos += 1
            node = BinOp(op, node, self._parse_term(line))
        return node

    def _parse_term(self, line):
        node = self._parse_factor(line)
        while self._peek() is not None and self._peek().kind in TERM_OPS:
            op = TERM_OPS[self._peek().kind]
            self.pos += 1
            node = BinOp(op, node, self._parse_factor(line))
        return node

    def _parse_factor(self, line):
        tok = self._peek()
        if tok is None:
            raise NotImplementedError(self.error.get_interpret_fail_exception(line))
        if tok.kind == "INT":
            self.pos += 1
            return IntLiteral(int(tok.text))
        if tok.kind == "STRING":
            self.pos += 1
            return StringLiteral(tok.text[1:-1])
        if tok.kind == "IDENT":
            self.pos += 1
            return VarRef(tok.text)
        raise NotImplementedError(self.error.get_interpret_fail_exception(line))
