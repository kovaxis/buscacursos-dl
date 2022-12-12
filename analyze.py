#!/usr/bin/env python3

from abc import abstractmethod
import sys
import json
import traceback
from typing import Callable, ClassVar, Dict, List, Set

with open("courses.json", "r") as file:
    data = json.load(file)


class Expr:
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def find_unique_leaves(self, unique: dict[str, set[str]]):
        pass

    def recursive_apply(self, f):
        return self


class Const(Expr):
    val: bool

    def __init__(self, val: bool):
        self.val = val

    def __str__(self):
        return str(int(self.val))

    def find_unique_leaves(self, unique: dict[str, set[str]]):
        pass


class Conn(Expr):
    op: ClassVar[str]
    neutral: ClassVar[bool]
    params: list[Expr]

    def __str__(self):
        s = ""
        for x in self.params:
            if s != "":
                s += f" {self.op} "
            if isinstance(x, Conn):
                s += f"({x})"
            else:
                s += str(x)
        return s

    def find_unique_leaves(self, unique: dict[str, set[str]]):
        for x in self.params:
            x.find_unique_leaves(unique)

    def __hash__(self):
        return hash((self.op, tuple(self.params)))

    @abstractmethod
    def dup(self, params: list[Expr]) -> 'Conn':
        pass

    @abstractmethod
    def dupnot(self, params: list[Expr]) -> 'Conn':
        pass

    def recursive_apply(self, f):
        new = self.dup([])
        changed = False
        for x in self.params:
            y = x.recursive_apply(f)
            if y is not x:
                changed = True
            new.params.append(y)
        if not changed:
            new = self
        new = f(new)
        # if new is not self:
        #     print(f"changed from '{self}' -> '{new}'")
        return new

    def simplify(self):
        ops = [Conn.degen, Conn.assoc, Conn.anihil,
               Conn.idem, Conn.ident, Conn.absorp, Conn.factor]
        x = self
        while True:
            prev = x
            for op in ops:
                x = x.recursive_apply(op)
            if prev is x:
                break
        return x

    def mapsimplify(self, ctx, simplify) -> Expr:
        new = self.dup([])
        changed = False
        for x in self.params:
            if simplify(ctx, new, x):
                changed = True
            else:
                new.params.append(x)
        if changed:
            return new
        else:
            return self

    def degen(self):
        if len(self.params) == 0:
            return Const(self.neutral)
        elif len(self.params) == 1:
            return self.params[0]
        else:
            return self

    def assoc(self):
        return self.mapsimplify(None, assoc_rule)

    def anihil(self):
        return self.mapsimplify([False], anihil_rule)

    def idem(self):
        return self.mapsimplify(set(), idem_rule)

    def ident(self):
        return self.mapsimplify(None, ident_rule)

    def absorp(self):
        seen = set()
        for x in self.params:
            seen.add(hash(x))
        return self.mapsimplify(seen, absorp_rule)

    def factor(self):
        cnt_factors = {}
        for x in self.params:
            if isinstance(x, Conn) and x.op != self.op:
                for y in x.params:
                    h = hash(y)
                    cnt_factors[h] = cnt_factors.get(h, 0) + 1
        mx = 0
        mx_h = 0
        for h, c in cnt_factors.items():
            if c > mx:
                mx = c
                mx_h = h
        if mx <= 1:
            return self
        inner = []
        outer = []
        factor = None
        for x in self.params:
            has_factor = False
            if isinstance(x, Conn) and x.op != self.op:
                inner_new = []
                for y in x.params:
                    if mx_h == hash(y):
                        # This inner clause contains the factor
                        has_factor = True
                        factor = y
                    else:
                        inner_new.append(y)
            if has_factor:
                # This clause has the factor
                # Remove the factor and add it to the inner clauses
                inner.append(x.dup(inner_new).degen())
            else:
                # This clause has no factor
                # Add as-is to the outer clauses
                outer.append(x)
        inner = self.dup(inner)
        factor = self.dupnot([factor, inner])
        outer.append(factor)
        outer = self.dup(outer).degen()
        return outer


def assoc_rule(ctx, x: Conn, y: Expr):
    if isinstance(y, Conn) and y.op == x.op:
        for sub in y.params:
            x.params.append(sub)
        return True


def anihil_rule(ctx: list[bool], x: Conn, y: Expr):
    if ctx[0] or (isinstance(y, Const) and y.val != x.neutral):
        ctx[0] = True
        return True


def idem_rule(ctx: set[int], x: Conn, y: Expr):
    h = hash(y)
    if h in ctx:
        return True
    ctx.add(h)


def ident_rule(ctx, x: Conn, y: Expr):
    if isinstance(y, Const) and y.val == x.neutral:
        return True


def absorp_rule(ctx, x: Conn, y: Expr):
    if isinstance(y, Conn) and y.op != x.op:
        for sub in y.params:
            if sub in ctx:
                # Skip the whole clause
                return True


class And(Conn):
    op: str = 'y'
    neutral: bool = True

    def __init__(self, params: List[Expr]):
        self.params = params

    def dup(self, params: list[Expr]):
        return And(params)

    def dupnot(self, params: list[Expr]):
        return Or(params)


class Or(Conn):
    op: str = 'o'
    neutral: bool = False

    def __init__(self, params: List[Expr]):
        self.params = params

    def dup(self, params: list[Expr]):
        return Or(params)

    def dupnot(self, params: list[Expr]):
        return And(params)


class Restr(Expr):
    lhs: str
    rhs: str
    op: str

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __str__(self):
        return f"({self.lhs} {self.op} {self.rhs})"

    def __hash__(self):
        return hash((self.lhs, self.op, self.rhs))

    def find_unique_leaves(self, unique: Dict[str, Set[str]]):
        unique.setdefault(self.lhs, set()).add(f"{self.op} \"{self.rhs}\"")


class Req(Expr):
    code: str
    co: bool

    def __init__(self, code: str, co: bool):
        self.code = code
        self.co = co

    def __str__(self):
        co = "(c)" if self.co else ""
        return f"{self.code}{co}"

    def __hash__(self):
        return hash((self.code, self.co))

    def find_unique_leaves(self, unique: dict[str, set[str]]):
        unique.setdefault(self.code, set()).add(self.co)


class BcParser:
    s: str
    i: int
    is_restr: bool

    def __init__(self, s: str, is_restr: bool):
        self.s = s
        self.i = 0
        self.is_restr = is_restr

    def take(self, cond: Callable[[str], bool]):
        prv = self.i
        while self.i < len(self.s) and cond(self.s[self.i]):
            self.i += 1
        return self.s[prv: self.i]

    def trim(self):
        return self.take(str.isspace)

    def eof(self):
        return self.i >= len(self.s)

    def bail(self, msg: str):
        ty = "restrictions" if self.is_restr else "requirements"
        raise Exception(
            f'invalid {ty} "{self.s}" around character {self.i}: {msg}')

    def ensure(self, cond: bool, msg: str):
        if not cond:
            self.bail(msg)

    def peek(self, n: int = 1):
        n = self.i + n
        if n > len(self.s):
            n = len(self.s)
        return self.s[self.i: n]

    def pop(self, n: int = 1):
        prv = self.i
        self.i += n
        if self.i > len(self.s):
            self.i = len(self.s)
        return self.s[prv: self.i]

    def parse_restr(self) -> Restr:
        lhs = self.take(lambda c: c.isalnum() or c.isspace()).strip()
        self.trim()
        cmp = self.take(lambda c: c in "<=>")
        self.trim()
        rhs = self.take(lambda c: c != ")").strip()
        self.ensure(len(lhs) > 0, "expected an lhs")
        self.ensure(len(cmp) > 0, "expected a comparison operator")
        self.ensure(len(rhs) > 0, "expected an rhs")
        return Restr(lhs, cmp, rhs)

    def parse_req(self) -> Req:
        code = self.take(str.isalnum)
        self.ensure(len(code) > 0, "expected a course code")
        self.trim()
        co = False
        if self.peek() == "(":
            self.pop()
            self.ensure(self.pop(2) == "c)", "expected (c)")
            co = True
        return Req(code=code, co=co)

    def parse_unit(self) -> Expr:
        self.trim()
        self.ensure(not self.eof(), "expected an expression")

        # Parse parenthesized unit
        if self.peek() == "(":
            self.pop()
            inner = self.parse_orlist()
            self.trim()
            self.ensure(self.pop() == ")", "expected a closing parentheses")
            return inner

        # Parse unit
        if self.is_restr:
            return self.parse_restr()
        else:
            return self.parse_req()

    def parse_andlist(self) -> Expr:
        inner: list[Expr] = []
        while True:
            inner.append(self.parse_unit())
            self.trim()
            nxt = self.peek().lower()
            if nxt == "" or nxt == ")" or nxt == "o":
                break
            elif nxt == "y":
                self.pop()
            else:
                self.bail("expected the end of the expression or a connector")
        if len(inner) == 1:
            return inner[0]
        else:
            return And(inner)

    def parse_orlist(self) -> Expr:
        inner: list[Expr] = []
        while True:
            inner.append(self.parse_andlist())
            self.trim()
            nxt = self.peek().lower()
            if nxt == "" or nxt == ")":
                break
            elif nxt == "o":
                self.pop()
            else:
                self.bail("expected the end of the expression or a connector")
        if len(inner) == 1:
            return inner[0]
        else:
            return Or(inner)

    @classmethod
    def parse_requirement(cls, s) -> Expr:
        return BcParser(s, is_restr=False).parse_orlist()

    @classmethod
    def parse_restriction(cls, s) -> Expr:
        return BcParser(s, is_restr=True).parse_orlist()

    @classmethod
    def parse_deps(cls, req, conn, restr) -> Expr:
        deps = None
        if req != "No tiene":
            deps = BcParser.parse_requirement(req)
        if restr != "No tiene":
            restr = BcParser.parse_restriction(restr)
            if deps is None:
                deps = restr
            else:
                if conn == "y":
                    deps = And([deps, restr])
                elif conn == "o":
                    deps = Or([deps, restr])
                else:
                    raise Exception(f"invalid req/restr connector {conn}")
        if deps is None:
            deps = And([])
        return deps


courses = data["2022-2"]
unique = set()
unique_lhs = {}

req_counts = {}

for sigla, c in courses.items():

    # if c['area'] != "":
    #    print(f"{sigla} area = \"{c['area']}\"")
    # if c['category'] != "":
    #    print(f"{sigla} category = \"{c['category']}\"")

    # restr = c['restrictions']
    # if restr not in unique:
    #    #print(f"{sigla} {restr}")
    #    unique.add(restr)
    #    if restr != "No tiene":
    #        try:
    #            restr_obj = BcParser(restr).parse()
    #            #print(f"  {restr_obj}")
    #            restr_obj.find_unique_lhs(unique_lhs)
    #        except:
    #            print(f"parsing restr \"{restr}\" for course {sigla} failed:")
    #            traceback.print_exc()

    try:
        deps = BcParser.parse_deps(
            c['requirements'], c['connector'], c['restrictions'])
        leaves = {}
        deps.find_unique_leaves(leaves)
        cnt = 0
        for code, inst in leaves.items():
            cnt += len(inst)
        req_counts.setdefault(cnt, {})[sigla] = deps
    except:
        print(
            f"parsing deps '{c['requirements']}', '{c['connector']}', '{c['restrictions']}' for course {sigla} failed:")
        traceback.print_exc()
req_counts = dict(sorted(req_counts.items()))

for lhs, rhss in unique_lhs.items():
    print(f"\"{lhs}\":")
    for rhs in rhss:
        print(f"  {rhs}")

for cnt, courses in req_counts.items():
    print(f"{len(courses)} courses with {cnt} requirements")
    if cnt > 10:
        for code, deps in courses.items():
            print(f"  {code}")
            print(f"    original:   {deps}")
            deps = deps.simplify()
            print(f"    simplified: {deps}")
