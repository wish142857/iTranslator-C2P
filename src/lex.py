import ply.lex as lex
from ply.lex import TOKEN

tokens = (
    'CONSTANT',
    'STRING_LITERAL',
    'IDENTIFIER',
    'ELLIPSIS',
    'RIGHT_ASSIGN',
    'LEFT_ASSIGN',
    'ADD_ASSIGN',
    'SUB_ASSIGN',
    'MUL_ASSIGN',
    'DIV_ASSIGN',
    'MOD_ASSIGN',
    'AND_ASSIGN',
    'XOR_ASSIGN',
    'OR_ASSIGN',
    'RIGHT_OP',
    'LEFT_OP',
    'INC_OP',
    'DEC_OP',
    'PTR_OP',
    'AND_OP',
    'OR_OP',
    'LE_OP',
    'GE_OP',
    'EQ_OP',
    'NE_OP',

)

reserved = {
    'auto': 'AUTO',
    'break': 'BREAK',
    'bool': 'BOOL',
    'case': 'CASE',
    'char': 'CHAR',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'float': 'FLOAT',
    'for': 'FOR',
    'goto': 'GOTO',
    'if': 'IF',
    'inline': 'INLINE',
    'int': 'INT',
    'long': 'LONG',
    'register': 'REGISTER',
    'restrict': 'RESTRICT',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'void': 'VOID',
    'volatile': 'VOLATILE',
    'while': 'WHILE',
}
tokens = tokens + tuple(reserved.values())

literals = ';,:=.&![]{}~()+-*/%><^|?'

t_ELLIPSIS = r'\.\.\.'
t_RIGHT_ASSIGN = r'>>='
t_LEFT_ASSIGN = r'<<='
t_ADD_ASSIGN = r'\+='
t_SUB_ASSIGN = r'-='
t_MUL_ASSIGN = r'\*='
t_DIV_ASSIGN = r'/='
t_MOD_ASSIGN = r'%='
t_AND_ASSIGN = r'&='
t_XOR_ASSIGN = r'\^='
t_OR_ASSIGN = r'\|='
t_RIGHT_OP = r'>>'
t_LEFT_OP = r'<<'
t_INC_OP = r'\+\+'
t_DEC_OP = r'--'
t_PTR_OP = r'->'
t_AND_OP = r'&&'
t_OR_OP = r'\|\|'
t_LE_OP = r'<='
t_GE_OP = r'>='
t_EQ_OP = r'=='
t_NE_OP = r'!='


digit = r'([0-9])'
hex_digit = r'[0-9a-fA-F]'
nondigit = r'([_a-zA-Z])'
identifier = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)'
dec_integer = r'(' + digit + r'+)'
hex_integer = r'(0[xX]' + hex_digit + r'+)'
integer = r'(' + dec_integer + r'|' + hex_integer + r')'
char = r'(\'(\\.|[^\\\'])+\')'
number = r'(' + integer + r'|' + char + r')' 

string_literal = r'"(\\.|[^\\"])*"'


@TOKEN(identifier)
def t_IDENTIFIER(t):
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# A regular expression rule with some action code
@TOKEN(number)
def t_CONSTANT(t):
    #t.value = int(t.value)
    return t

@TOKEN(string_literal)
def t_STRING_LITERAL(t):
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\v\f'


# ignore comment
def t_COMMENT(t):
    r'//[^\n]*'
    pass


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


# Build the lexer from my environment and return it
lexer = lex.lex()

"""
test_str = '''
this is a test
't'
"\\""
'''
with open('test.txt', 'r') as fr:
    test_str = fr.read()
lex.input(test_str)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok, find_column(test_str, tok))
"""
