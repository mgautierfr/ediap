from picoparse import choice, p, one_of, many, many1, tri, eof, not_followed_by, satisfies, string, commit, optional, sep1, sep, desc, not_one_of, compose, pos
from picoparse.text import run_text_parser, newline


from tokens import *

reserved_words = []

as_string = p(compose, lambda iter_: u''.join(iter_))
whitespace_char = p(one_of, " ")
whitespace = as_string(p(many, whitespace_char))
whitespace1 = as_string(p(many1, whitespace_char))

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
    commit()
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

def value():
    return number()

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
    #not_followed_by(p(choice, *[p(reserved, rw) for rw in reserved_words]))
    first = identifier_char1()
    commit()
    rest = many(identifier_char)
    end = pos()
    name = u''.join([first] + rest)
    return Identifier(name, start, end)

def functioncall():
    start = pos()
    name = identifier()
    special('(')
    arguments = sep(value, p(special, ','))
    special(')')
    end = pos()
    return Call(name, arguments, start, end)

def part():
    expr = functioncall()
    many1(p(special,'\n'))
    return expr

def program():
    start = pos()
    prog = many(part)
    whitespace()
    end = pos()
    eof()
    return Program(prog, start, end)

def parse(text):
    return run_text_parser(program, text)[0]
