from picoparse import choice, p, one_of, many, many1, tri, eof, not_followed_by, satisfies, string, commit, optional, sep1, sep, desc, not_one_of, compose, EndOfFile
from picoparse.text import run_text_parser, newline

from picoparse import pos as _pos


from .tokens import *
from . import instructions

reserved_words = ['if', 'while', 'do', 'define']
binary_operator_chars = ['+', '-', '/', '*', '==', '<', '>', '!=', '<=', '>=']

as_string = p(compose, lambda iter_: u''.join(iter_))
whitespace_char = p(one_of, " ")
whitespace = as_string(p(many, whitespace_char))
whitespace1 = as_string(p(many1, whitespace_char))

textLen = None

def pos():
    p = _pos()
    if p is EndOfFile:
        return textLen
    return p.col-1

def operator_char(operator_chars):
    ret = choice(*(p(string, op) for op in operator_chars))
    ret = u''.join(ret)
    return ret

def identifier_char1():
    return satisfies(lambda l: l.isalpha() or l == "_")

def identifier_char():
    return choice(identifier_char1, digit)

def digit():
    return satisfies(lambda l: l.isdigit())

@tri
def special(name):
    whitespace()
    string(name)
    return name

@tri
def number():
    type_ = Int
    whitespace()
    start = pos()
    sign = optional(p(one_of, "+-"), "+")
    lead = u''.join(many1(digit))
    if optional(p(one_of, '.')):
        trail = u''.join(many1(digit))
        end = pos()
        type_ = Float
        v = float(lead + '.' + trail)
    else:
        v = int(lead)
    if sign == "-":
        v *= -1
    end = pos()
    return type_(v, start, end)

@tri
def operator(chars):
  whitespace()
  start = pos()
  #not_followed_by(p(choice, *[p(reserved_op, op) for op in reserved_operators]))
  name = operator_char(chars)
  end = pos()
  return Identifier(name, start, end)

@tri
def binaryOp():
    start = pos()
    arg1 = term()
    name = operator(binary_operator_chars)
    arg2 = expr()
    end = pos()
    return BinaryOp(name, arg1, arg2, start, end).merge()

def parenthetical():
    start = pos()
    special("(")
    n = expr()
    special(")")
    end = pos()
    return Paren(n, start, end)

def term():
    return choice(parenthetical, number, identifier)

@tri
def expr():
    return choice(binaryOp, functioncall, term)

@tri
def reserved(name):
    assert name in reserved_words
    whitespace()
    string(name)
    not_followed_by(identifier_char)
    return name

@tri
def identifier():
    whitespace()
    start = pos()
    not_followed_by(p(choice, *[p(reserved, rw) for rw in reserved_words]))
    first = identifier_char1()
    commit()
    rest = many(identifier_char)
    end = pos()
    name = u''.join([first] + rest)
    return Identifier(name, start, end)

@tri
def functioncall():
    special('do')
    name = identifier()
    special('(')
    arguments = sep(expr, p(special, ','))
    special(')')
    return instructions.Call(name, arguments)

@tri
def builtincall():
    name = identifier()
    special('(')
    arguments = sep(expr, p(special, ','))
    special(')')
    return instructions.Builtin(name, arguments)

@tri
def assignement():
    name = identifier()
    special('=')
    value = expr()
    return instructions.Assignement(name, value)

@tri
def ifstmt():
    special('if')
    test = expr()
    return instructions.If(test)

@tri
def whilestmt():
    special('while')
    test = expr()
    return instructions.While(test)

@tri
def functionstmt():
    special('define')
    name = identifier()
    special('(')
    arguments = sep(identifier, p(special, ','))
    special(')')
    return instructions.FunctionDef(name, arguments)

@tri
def comment():
    special("#")
    text = many(p(satisfies, lambda l: l is not EndOfFile))
    return instructions.Comment(text)

def part():
    expr = choice(comment, functionstmt, functioncall, builtincall, assignement, ifstmt, whilestmt)
    eof()
    return expr

def get_level(text):
    stripped = text.lstrip()
    return len(text)-len(stripped)

def parse_instruction(text):
    global textLen
    textLen = len(text)
    statement = run_text_parser(part, text)[0]
    statement.level = get_level(text)
    return statement

