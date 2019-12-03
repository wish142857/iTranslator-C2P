import re
def scanf(format):
    s = input()
    format = format.replace(r'%d', r'([-+]?\d+)')
    format = format.replace(r'%s', r'(\S+)')
    format = format.replace(r'%c', r'(.)')
    print(format, s)
    match_objs = re.match(format, s, re.M|re.I)
    if match_objs:
        args = []
        i = 1
        while True:
            try:
                print(match_objs)
                args.append(match_objs.group(i))
            except:
                break
            i += 1
        return args


#print(scanf('%d%d%d'))

scanf_py = '''
def scanf(format, *args):
    pass
'''

gets_py='''
def gets(s):
    s_in = input()
    for i, c in enumerate(s_in):
        s[i] = c
'''

printf_py = '''
def printf(format, *args):
    print(format % args, end='')
'''

system_py = '''
def system(s):
    if not isinstance(s, str):
        s = filter(lambda x: x != 0, s)
        s = ''.join(s)
    import os
    os.system(s)
'''

def strlen(s):
    if isinstance(s, str):
        return len(s)
    else:
        _len = 0
        for i in s:
            if i == 0:
                break
            _len += 1
        return _len

strlen_py = '''
def strlen(s):
    if isinstance(s, str):
        return len(s)
    else:
        _len = 0
        for i in s:
            if i == 0:
                break
            _len += 1
        return _len
'''

c_utils = [strlen_py, gets_py, printf_py, scanf_py, system_py]