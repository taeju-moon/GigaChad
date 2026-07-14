import re
from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    text: str


# Multi-word keyword literals, longest-first so no shorter phrase can
# shadow a longer one that starts with the same words.
KEYWORDS = [
    ("KW_START", "Of Course"),
    ("KW_END", "See you tomorrow My Son"),
    ("KW_NEWLINE", "Go To Next Step, My Son"),
    ("KW_DEFINE", "너는 이제부터"),
    ("KW_IS", "이다"),
    ("TYPE_INT", "FUCKING ASSHOLE"),
    ("TYPE_STR", "FUCKING BADASS"),
    ("KW_OUTPUT", "기적같은 하루가 널 기다려"),
    ("KW_INPUT", "이번엔 또 무슨 pussy같은 고민 때문에 날 부른거지"),
    ("OP_ADD", "HARD TRAINING"),
    ("OP_SUB", "STOP OVER THINKING"),
    ("OP_MUL", "AIM HIGH"),
    ("OP_DIV", "DONT GIVE A SHIT"),
    ("KW_LOOP_START", "만삣삐"),
    ("KW_BY", "by"),
    ("KW_FORWARD", "앞으로 나아가"),
    ("KW_LOOP_END", "큰꿈을 가져 my son"),
]
KEYWORDS.sort(key=lambda kw: len(kw[1]), reverse=True)

TOKEN_REGEX = re.compile(
    "|".join(
        # (?!\w) blocks partial matches, e.g. "by" swallowing the first two
        # letters of an identifier like "bypass" that happens to follow it.
        [r"(?P<%s>%s)(?!\w)" % (kind, re.escape(text)) for kind, text in KEYWORDS]
        + [
            r'(?P<STRING>"[^"\n]*")',
            r"(?P<INT>\d+)",
            r"(?P<COMMA>,)",
            r"(?P<QMARK>\?)",
            r"(?P<WHITESPACE>\s+)",
            r"(?P<IDENT>[^\s,\?\"]+)",
        ]
    )
)


def tokenize(source: str) -> list:
    tokens = []
    pos = 0
    while pos < len(source):
        match = TOKEN_REGEX.match(source, pos)
        if not match:
            raise NotImplementedError(f"lexer가 다음 지점을 해석하지 못했다: {source[pos:pos + 20]!r}")
        kind = match.lastgroup
        text = match.group()
        pos = match.end()
        if kind == "WHITESPACE":
            continue
        tokens.append(Token(kind, text))
    return tokens
