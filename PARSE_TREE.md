# 기가차드 Parse Tree

`gigachad-lang-python`은 세 단계로 `.chad` 소스를 실행한다.

```
source(.chad) --tokenize()--> tokens --Parser.parse_program()--> AST(Program) --Interpreter.exec_program()--> 실행
     lexer.py                              parser.py                                interpreter.py
```

## 1. 문법 (EBNF)

```
Program     ::= "Of Course" Statement* "See you tomorrow My Son"

Statement   ::= VarDecl | Assign | Input | Output | NewlinePrint

VarDecl     ::= "너는 이제부터" Type IDENT "이다"
Type        ::= "FUCKING ASSHOLE"      (int)
              | "FUCKING BADASS"       (str)

Assign      ::= IDENT "," "너는 이제부터" Expr "이다"

Input       ::= "이번엔 또 무슨 pussy같은 고민 때문에 날 부른거지" "," IDENT "," Prompt "?"

Output      ::= "기적같은 하루가 널 기다려" "," Expr

NewlinePrint::= "Go To Next Step, My Son"

Expr        ::= Arith (Arith)*          # 공백 나열 = 문자열 concat, 단일이면 타입 그대로
Arith       ::= Term (("HARD TRAINING" | "STOP OVER THINKING") Term)*
Term        ::= Factor (("AIM HIGH" | "DONT GIVE A SHIT") Factor)*
Factor      ::= INT | STRING | IDENT

Loop        ::= "만삣삐" "," IDENT "by" Expr "," "앞으로 나아가"
                Statement*
                "큰꿈을 가져 my son"
```

각 `.chad` 소스 줄(line)이 하나의 `Statement`가 된다 (단, `Loop`는 `LoopStart` 줄부터 `큰꿈을 가져 my son` 줄까지 여러 줄에 걸친 하나의 statement). 연산자 우선순위는 문법 구조 자체에 인코딩되어 있다 (`Arith`가 `+`/`-`, 그 아래 `Term`이 `*`/`/`를 담당하므로 곱셈·나눗셈이 먼저 묶인다).

## 2. AST 노드 (`ast_nodes.py`)

| 종류 | 노드 | 필드 |
|---|---|---|
| Statement | `VarDecl` | `var_type`, `name` |
| | `Assign` | `name`, `expr` |
| | `Input` | `name`, `prompt` |
| | `Output` | `expr` |
| | `NewlinePrint` | (없음) |
| | `Loop` | `index_name`, `count_expr`, `body: list[Statement]` |
| Expression | `Concat` | `parts: list[Expr]` |
| | `BinOp` | `op`, `left`, `right` |
| | `IntLiteral` | `value` |
| | `StringLiteral` | `value` |
| | `VarRef` | `name` |

`Parser`가 statement 노드를, `Parser._parse_arith`/`_parse_term`/`_parse_factor`가 서로 재귀 호출하며 expression 노드를 만든다. `Interpreter.eval_expr`는 이 트리를 그대로 재귀적으로 내려가며 평가한다. `Loop`도 같은 재귀 구조를 한 단계 위(문장 단위)에서 반복한다: `Parser._parse_block`이 `KW_LOOP_START` 토큰을 만나면 자기 자신을 재귀 호출해 본문을 `KW_LOOP_END`가 나올 때까지 파싱하고, `Interpreter._exec_loop`는 그 `body` 리스트를 `count_expr` 평가값만큼 반복하며 각 statement를 `exec_stmt`로 재귀 실행한다 (중첩 반복문도 자연스럽게 지원됨).

## 3. 예시: `examples/근성과노력.chad`의 실제 parse tree

```
Of Course

너는 이제부터 FUCKING ASSHOLE 근성 이다
근성, 너는 이제부터 3 이다

기적같은 하루가 널 기다려, "만삣삐 너의 근성은 다음과 같아: "
기적같은 하루가 널 기다려, 근성
Go To Next Step, My Son

너는 이제부터 FUCKING ASSHOLE 노력 이다
노력, 너는 이제부터 4 이다

기적같은 하루가 널 기다려, "만삣삐 너의 노력은 다음과 같아: "
기적같은 하루가 널 기다려, 노력
Go To Next Step, My Son

너는 이제부터 FUCKING ASSHOLE 총합 이다
총합, 너는 이제부터 근성 HARD TRAINING 노력 이다

기적같은 하루가 널 기다려, "만삣삐 너의 근성과 노력의 총합은 다음과 같아: "
기적같은 하루가 널 기다려, 총합

See you tomorrow My Son
```

이 소스를 `Parser.parse_program()`에 넣으면 다음과 같은 `Program` 트리가 나온다:

```
Program
├─ VarDecl(var_type=int, name="근성")
├─ Assign(name="근성", expr=IntLiteral(3))
├─ Output(expr=StringLiteral("만삣삐 너의 근성은 다음과 같아: "))
├─ Output(expr=VarRef("근성"))
├─ NewlinePrint
├─ VarDecl(var_type=int, name="노력")
├─ Assign(name="노력", expr=IntLiteral(4))
├─ Output(expr=StringLiteral("만삣삐 너의 노력은 다음과 같아: "))
├─ Output(expr=VarRef("노력"))
├─ NewlinePrint
├─ VarDecl(var_type=int, name="총합")
├─ Assign(name="총합", expr=BinOp)
├─ Output(expr=StringLiteral("만삣삐 너의 근성과 노력의 총합은 다음과 같아: "))
└─ Output(expr=VarRef("총합"))
```

12번째 statement `Assign(name="총합", ...)`의 `expr`만 유일하게 재귀적인 expression 트리를 갖는다 (`근성 HARD TRAINING 노력` → `BinOp("+", VarRef, VarRef)`):

```
Assign
├─ name: "총합"
└─ expr: BinOp
         ├─ op: "+"
         ├─ left:  VarRef(name="근성")
         └─ right: VarRef(name="노력")
```

`Interpreter.eval_expr(BinOp)`는 `left`/`right`를 각각 `eval_expr`로 재귀 평가한 뒤(`VarRef` → 환경에서 값 조회) `_apply_op("+", 3, 4)`를 호출해 `7`을 반환한다.

## 4. 리터럴 안의 연산자 키워드 처리

`examples/실패해도괜찮아.chad`에는 문자열 리터럴 안에 연산자 키워드 `AIM HIGH`가 그대로 들어있다:

```
메시지, 너는 이제부터 "하지만 넌 PUSSY처럼 시도도 안한 놈들보다 위에 있어. AIM HIGH My son." 이다
```

`lexer.tokenize()`는 여는 `"`부터 닫는 `"`까지를 통째로 `STRING` 토큰 하나로 소비하므로, 내부의 `AIM HIGH`가 `OP_MUL` 토큰으로 잘못 인식되지 않는다:

```
Assign
├─ name: "메시지"
└─ expr: StringLiteral("하지만 넌 PUSSY처럼 시도도 안한 놈들보다 위에 있어. AIM HIGH My son.")
```

## 5. 반복문 (`Loop`) — `for index in range(n):`

```
Loop        ::= "만삣삐" "," IDENT "by" Expr "," "앞으로 나아가"
                Statement*
                "큰꿈을 가져 my son"
```

`IDENT`(반복 변수)는 별도 선언 없이 루프가 시작될 때 int 타입으로 자동 바인딩되고, `0`부터 `Expr` 평가값 미만까지 1씩 증가하며 본문을 반복 실행한다 (Python의 `for index in range(n):`와 동일한 의미).

예시 (`0`부터 `4`까지 더하기):

```
Of Course

너는 이제부터 FUCKING ASSHOLE 총합 이다
총합, 너는 이제부터 0 이다

만삣삐, i by 5, 앞으로 나아가
총합, 너는 이제부터 총합 HARD TRAINING i 이다
큰꿈을 가져 my son

기적같은 하루가 널 기다려, 총합

See you tomorrow My Son
```

파스 트리:

```
Program
├─ VarDecl(var_type=int, name="총합")
├─ Assign(name="총합", expr=IntLiteral(0))
├─ Loop(index_name="i", count_expr=IntLiteral(5))
│  └─ body:
│     └─ Assign(name="총합", expr=BinOp("+", VarRef("총합"), VarRef("i")))
└─ Output(expr=VarRef("총합"))
```

`Interpreter._exec_loop`는 `i`를 `0, 1, 2, 3, 4` 순서로 `self.datas["i"]`에 대입하면서 매 반복마다 `body`의 `Assign` statement를 재귀 실행한다 → `총합`은 `0+0, 1+1, 2+2, 3+3, 4+4`가 아니라 누적합 `0→1→3→6→10`이 되어 최종 출력은 `10`. 실행 결과 확인:

```
$ python -m gigachad-lang-python examples/합계세기.chad
10
```

`Loop` 본문 안에 또 다른 `Loop`가 와도(`만삣삐, j by 2, 앞으로 나아가 ... 큰꿈을 가져 my son`) `_parse_block`과 `exec_stmt`가 그대로 재귀되므로 중첩 반복문이 별도 처리 없이 지원된다.
