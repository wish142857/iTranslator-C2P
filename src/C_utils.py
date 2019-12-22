# C 中的gets函数
gets_py='''
def gets_0(s):
    s_in = input()
    for i, c in enumerate(s_in):
        s[i] = c
'''

# C 中的printf函数
printf_py = '''
def printf_0(format, *args):
    new_args = []
    for arg in args:
        if type(arg) == list:
            s = ''
            for c in arg:
                if c == None:
                    break
                s += c
            arg = s
        new_args.append(arg) 
    print(format % tuple(new_args), end='')
'''

# C中的system函数
system_py = '''
def system_0(s):
    if not isinstance(s, str):
        s = filter(lambda x: x != 0, s)
        s = ''.join(s)
    import os
    os.system(s)
'''

# C 中的strlen函数，这里通过None判断数组末尾
strlen_py = '''
def strlen_0(s):
    if isinstance(s, str):
        return len(s)
    else:
        _len = 0
        for i in s:
            if i is None:
                break
            _len += 1
        return _len
'''

# C 中的atoi函数
atoi_py = '''
def atoi_0(s):
    if isinstance(s, str):
        return int(s)
    else:
        sum = 0
        for i in s:
            if i is None:
                break
            sum *= 10
            sum += int(i)
        return sum
'''

# C 中的atof函数
atof_py = '''
def atof_0(s):
    if isinstance(s, str):
        return int(s)
    else:
        mstr = ''
        for i in s:
            if i is None:
                break
            mstr += i
        return float(mstr)
'''

c_utils = [strlen_py, gets_py, printf_py, system_py, atoi_py, atof_py]