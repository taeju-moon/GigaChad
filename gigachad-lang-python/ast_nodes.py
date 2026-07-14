from dataclasses import dataclass, field


@dataclass
class Program:
    statements: list


@dataclass
class VarDecl:
    var_type: type
    name: str


@dataclass
class Assign:
    name: str
    expr: object


@dataclass
class Input:
    name: str
    prompt: str


@dataclass
class Output:
    expr: object


@dataclass
class NewlinePrint:
    pass


@dataclass
class Loop:
    index_name: str
    count_expr: object
    body: list


# --- expression nodes ---

@dataclass
class Concat:
    parts: list = field(default_factory=list)


@dataclass
class BinOp:
    op: str
    left: object
    right: object


@dataclass
class IntLiteral:
    value: int


@dataclass
class StringLiteral:
    value: str


@dataclass
class VarRef:
    name: str
