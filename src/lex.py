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


# 数字 - 十进制
D = r'[0-9]'
# 数字 - 十六进制
H = r'[0-9a-fA-F]'
# 下划线与字母
L = r'([_a-zA-Z])'
# 科学计数法后缀
E = r'[Ee][+-]?[0-9]+'
# 浮点数修饰符
FS = r'(f|F|l|L)'
# 整型数修饰符
IS = r'(u|U|l|L)*'


# 标识符
identifier = r'(%s(%s|%s)*)' % (L, D, L)
# 布尔
boolean = r'(true|false)'
# 整型数字
integer = r'(0?%s+%s?|0[xX]%s+%s?|%s+%s%s?)' % (D, IS, H, IS, D, E, FS)
# 浮点数字（小数）
decimal = r'((%s+\.%s*(%s)?%s?)|(%s*\.%s+(%s)?%s?))' % (D, D, E, FS, D, D, E, FS)
# 字符
char = r'(\'(\\.|[^\\\'])+\')'
# 常量
constant = r'(%s|%s|%s|%s)' % (decimal, integer, char, boolean)
# 字符串原文
string_literal = r'"(\\.|[^\\"])*"'


@TOKEN(constant)
def t_CONSTANT(t):
    return t

@TOKEN(identifier)
def t_IDENTIFIER(t):
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t


@TOKEN(string_literal)
def t_STRING_LITERAL(t):
    return t


# 行号追踪
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 空白字符定义
t_ignore = ' \t\v\f'


# 注释过滤
def t_COMMENT(t):
    r'//[^\n]*'
    pass


# 错误处理
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Compute column.
#     string is the input text string
#     token is a token instance
def find_column(string, token):
    last_cr = string.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


# 构建词法分析器
lexer = lex.lex()


# 测试程序
if __name__ == '__main__':
    while True:
        try:
            filepath = input('lex > ')
            with open(filepath, 'r') as file:
                data = file.read()
                lex.input(data)
            while True:
                tok = lexer.token()
                if not tok:
                    break
                print(tok, find_column(data, tok))
        except EOFError:
            break
