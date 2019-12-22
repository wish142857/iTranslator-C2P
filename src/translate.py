import copy

from AST import ASTInternalNode, ASTExternalNode
from yacc import parser
import os
from C_utils import c_utils
from pre_post_process import formatIndent, precompile

TAIL = """
if __name__ == "__main__":
    main_0()
"""


class Translator:
    def __init__(self):
        self.functions = []
        self.declarations = []
        self.global_variables = []
        self.variable_table = {}
        self.head = ""
        for c_util in c_utils:
            self.head += c_util
        self.head += '\n'
        self.tail = TAIL

    def translate(self, input_file_name, output_file_name):
        try:
            # 模拟预编译
            success, file_content = precompile(input_file_name)
            if not success:
                print(file_content)
                return
            # 解析得到语法树
            tree = parser.parse(file_content)

            # 语义处理
            raw_outcome = self.process(tree)

            # 转化为正确格式，优化代码风格，加上首尾代码
            out = formatIndent(raw_outcome)
            out = self.head + out + self.tail

            # 输出
            with open(output_file_name, 'w+', encoding='utf-8') as output_file:
                output_file.write(out)
            print('{} 成功翻译为 {} 。'.format(input_file_name, output_file_name))
        except Exception as e:
            print(str(e))

    # 属性flag：是否是结构体，如果是，返回结构体名；如果否，返回空串
    def flag_calculate(self, tree, flag_list):
        if tree.key == 'struct_or_union_specifier':
            # print("class name", tree.children[1].value)
            return tree.children[1].value
        else:
            for flag in flag_list:
                if flag != '':
                    return flag
            return ''

    # 叶子节点的值翻译
    def leaf_string(self, tree):
        if tree.value == ';':
            return ['']
        elif tree.value == '&&':
            return [' and ']
        elif tree.value == '||':
            return [' or ']
        elif tree.value == '!':
            return ['not ']
        elif tree.value == 'true':
            return ['True']
        elif tree.value == 'false':
            return ['False']
        elif tree.value == 'struct':
            return ['class']
        else:
            return [tree.value]

    def traversal(self, tree, stack, type):
        stack.append(tree.key)
        code_list = []
        flag_list = []

        if isinstance(tree, ASTExternalNode):
            stack.pop()
            return self.leaf_string(tree), ''
        for child in tree.children:
            # 遍历树
            code, flag = self.traversal(child, stack, type)
            code_list.append(code)
            flag_list.append(flag)
        try:
            # 计算flag属性的值
            flag_to_upper = self.flag_calculate(tree, flag_list)
        except Exception as e:
            print(str(e))

        # 通过子节点的code属性和计算得到的flag属性计算此节点的code属性
        pycode = self.code_compose(tree, code_list, flag_to_upper)

        stack.pop()
        return pycode, flag_to_upper

    # 取出所有声明和函数定义并依次序处理之
    def process(self, tree):
        def pick_out(tree):
            if tree.key == 'function_definition':
                self.functions.append(tree)
            else:
                self.declarations.append(tree)

        # 分离函数和全局变量、结构体声明等
        while True:
            if tree.key == 'translation_unit':
                if len(tree.children) == 2:
                    pick_out(tree.children[1].children[0])
                    tree = tree.children[0]
                else:
                    pick_out(tree.children[0].children[0])
                    break

        # 恢复从上到下的顺序
        self.declarations = reversed(self.declarations)
        code_list = []
        for declaration in self.declarations:
            is_function = self.is_function_declaration(declaration)
            if is_function:
                continue
            self.declaration_extract(declaration)
            code, flag = self.traversal(declaration, [], 'declaration')
            code_list.extend(code)
            code_list.append('')  # 空行

        for function in self.functions:
            # 进入函数（作用域），备份变量表
            table_copy = copy.deepcopy(self.variable_table)
            self.name_replacement(function)
            # 离开函数（作用域），恢复变量表
            self.variable_table = table_copy
            code, flag = self.traversal(function, [], 'function')
            code_list.extend(code)
            code_list.append('')
        return code_list

    # 判断一个声明是否为函数声明
    def is_function_declaration(self, tree):
        for child in tree.children:
            if isinstance(child, ASTExternalNode):
                return False
            if child.key == 'direct_declarator':
                if len(child.children) > 1 and isinstance(child.children[1], ASTExternalNode) \
                        and child.children[1].value == '(':
                    return True
                else:
                    return False
            else:
                if self.is_function_declaration(child):
                    return True
        return False

    # 提取所有的全局变量
    def declaration_extract(self, tree):
        # 结构体定义内部直接返回
        if tree.key == 'struct_or_union_specifier':
            return
        # 外部节点直接返回
        if isinstance(tree, ASTExternalNode):
            return
        for child in tree.children:
            # 如果是变量
            if child.key == 'IDENTIFIER':
                # 在变量表中记录该变量
                alias = child.value + '_0'
                self.global_variables.append(alias)
                self.variable_table[child.value] = [(alias, True)]
                child.value = alias
            else:
                self.declaration_extract(child)

    # 对可能发生覆盖的变量进行重命名
    def name_replacement(self, tree, is_declarator=False):

        if isinstance(tree, ASTInternalNode):
            # 进入声明语句
            if tree.key == 'declarator':
                for child in tree.children:
                    self.name_replacement(child, True)
            # 声明语句中的表达式部分不算声明
            elif tree.key == 'primary_expression':
                for child in tree.children:
                    self.name_replacement(child, False)
            # 结构体内部变量直接跳过
            elif tree.key == 'struct_or_union_specifier':
                return
                # for child in tree.children:
                #     self.name_replacement(child, False)
            #
            elif tree.key == 'postfix_expression' and len(tree.children) == 3 \
                    and isinstance(tree.children[2], ASTExternalNode) and tree.children[2].key == 'IDENTIFIER':
                for child in tree.children[:2]:
                    self.name_replacement(child, False)
            # 选择或循环语句，进入新一层作用域
            elif tree.key == 'iteration_statement' or tree.key == 'selection_statement':
                # 进入作用域，保存副本
                table_copy = copy.deepcopy(self.variable_table)
                for child in tree.children:
                    self.name_replacement(child, is_declarator)
                # 离开作用域，恢复变量表
                self.variable_table = table_copy
            else:
                for child in tree.children:
                    self.name_replacement(child, is_declarator)
        else:
            # 不是变量
            if tree.key != 'IDENTIFIER':
                return
            # 变量在变量表中
            if tree.value in self.variable_table.keys():
                # 是声明
                if is_declarator:
                    table = self.variable_table[tree.value]
                    # 不需要重命名
                    if len(table) == 0:
                        alias = tree.value + '_0'
                        table.append((alias, False))
                        tree.value = alias
                    # 需要重命名并修改变量表
                    else:
                        alias = tree.value + '_' + str(len(table))
                        table.append((alias, False))
                        tree.value = alias
                # 不是声明
                else:
                    table = self.variable_table[tree.value]
                    # 需要重命名
                    if len(table) != 0:
                        last = table[-1][0]
                        tree.value = last
                    else:
                        tree.value = tree.value + '_0'
            else:
                alias = tree.value + '_0'
                self.variable_table[tree.value] = [(alias, False)]
                tree.value = alias


    # 自下而上的翻译函数
    # 每个节点的code属性为子节点的code属性的函数
    def code_compose(self, tree, code_list, flag):
        # 前置 ++/--
        if tree.key == 'unary_expression' and isinstance(tree.children[0], ASTExternalNode):
            if tree.children[0].value == '++':
                res = [code_list[1][0] + ' = ' + code_list[1][0] + '+1']
                """
                变量 += 1
                """
                return res
            if tree.children[0].value == '--':
                res = [code_list[1][0] + '=' + code_list[1][0] + '-1']
                """
                变量 -= 1
                """
                return res

        # 后置 ++/--
        elif tree.key == 'postfix_expression' and len(tree.children) == 2:
            if tree.children[1].value == '--':
                res = [code_list[0][0] + '=' + code_list[0][0] + '-1']
                """
                变量 += 1
                """
                return res
            if tree.children[1].value == '++':
                res = [code_list[0][0] + '=' + code_list[0][0] + '+1']
                """
                变量 -= 1
                """
                return res

        # return 语句
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return':
            if len(tree.children) == 2:
                """
                return
                """
                return ['return']
            elif len(tree.children) == 3:
                """
                return 返回值
                """
                return [code_list[0][0] + ' ' + code_list[1][0]]

        # 选择语句
        elif tree.key == 'selection_statement':
            if len(tree.children) == 5:
                """
                if 条件:
                    代码块（缩进+1）
                """
                return ['if ' + code_list[2][0] + ':', code_list[4]]
            if len(tree.children) == 7:
                """
                if 条件:
                    代码块（缩进+1）
                else:
                    代码块（缩进+1）
                """
                return ['if ' + code_list[2][0] + ':', code_list[4], 'else:', code_list[6]]

        # 循环语句
        elif tree.key == 'iteration_statement':
            #  while {
            #      ...
            #  }
            if tree.children[0].value == 'while':
                """
                while 条件:
                    代码块（缩进+1）
                """
                return ['while ' + code_list[2][0] + ':', code_list[4]]
            #  for (...; ...; ...) {
            #      ...
            #  }
            if len(tree.children) == 7:
                """
                初始条件
                while 终止条件:
                    代码块（缩进+1）
                    迭代（缩进+1）
                """
                return [code_list[2][0], 'while ' + code_list[3][0] + ':', code_list[6], code_list[4]]

        # 语句块的换行
        elif tree.key == 'block_item_list':
            lst = []
            for code in code_list:
                for c in code:
                    lst.append(c)
            """
            语句1
            语句2
            ...
            """
            return lst

        # {}作用域 去除{}
        elif tree.key == 'compound_statement':
            if len(tree.children) == 3:
                """
                    代码块（缩进+1）
                """
                return code_list[1]
            # {}内为空，Python需要有 pass
            elif len(tree.children) == 2:
                """
                    pass（缩进+1）
                """
                return ['pass']

        # 函数声明, 返回值类型变为def,
        elif tree.key == 'function_definition':
            if len(tree.children) == 4:
                pass
            elif len(tree.children) == 3:
                function_body = []
                # 无脑加入所有全局变量
                for global_var in self.global_variables:
                    function_body.append('global ' + global_var)
                for code in code_list[2]:
                    function_body.append(code)
                """
                def 函数名:
                    函数体（缩进+1）
                """
                return ['def ' + code_list[1][0] + ':',
                        function_body]

        # 函数参数列表中参数类型的去除
        elif tree.key == 'parameter_declaration' and len(tree.children) == 2:
            """
            变量（没有类型）
            """
            return code_list[1]

        # 函数列表中数组“[]”的去除
        elif tree.key == 'direct_declarator' and len(tree.children) == 3 and tree.children[1].value == '[':
            """
            数组变量名
            """
            return [code_list[0][0]]

        # 形如int x, y=2;的声明中的x, y=2 , Python中需要分行
        elif tree.key == 'init_declarator_list':
            if len(tree.children) == 1:
                """
                变量名（=初始值）
                """
                return code_list[0]
            else:
                """
                变量名1（=初始值1）
                变量名2（=初始值2）
                """
                return [code_list[0][0],
                        code_list[2][0]]

        # 结构体变量的声明（形如struct A a;)
        elif tree.key == 'struct_or_union_specifier' and len(tree.children) == 2:
            """
            结构体名称
            """
            return code_list[1]

        # 结构体的定义（形如 struct A { int x; int y; };
        elif tree.key == 'struct_or_union_specifier' and len(tree.children) == 5:
            """
            class 结构体名称:
                成员变量（缩进+1）
            """
            return [code_list[0][0] + ' ' + code_list[1][0] + ':',
                    code_list[3]]

        # 结构体定义内的语句列表
        elif tree.key == 'struct_declaration_list':
            lst = []
            for code in code_list:
                for c in code:
                    lst.append(c)
            """
            成员变量1 = 初始值1
            成员变量2 = 初始值2
            ...
            """
            return lst

        # 声明语句
        if tree.key == 'declaration' or tree.key == 'struct_declaration':

            # 变量（非结构体）声明，去除变量类型和分号
            if len(tree.children) == 3 and flag == '':
                """
                变量名
                """
                return code_list[1]

            # 结构体变量声明
            elif len(tree.children) == 3 and flag != '':
                # flag 为结构体名称
                if flag != code_list[0][0]:
                    result = code_list[0]
                else:
                    result = []
                for class_obj in code_list[1]:
                    result.append(class_obj + '=' + flag + '()')

                # 结构体数组的处理
                if len(result) == 1:
                    tmp = result[0]
                    if tmp.find('=') != tmp.rfind('='):
                        tmp_2 = tmp.split('=')[2]
                        tmp_2 = tmp_2.lstrip()
                        tmp = tmp.split('=')[0] + '=' + tmp.split('=')[1]
                        tmp = tmp[0:tmp.find('[') + 1] + tmp_2 + ' for i in range(' + tmp[tmp.find('*') + 1:] + ')]'
                        tmp = tmp.rstrip()
                        result = []
                        result.append(tmp)
                # print(result)
                return result

            #
            elif len(tree.children) == 2:
                return code_list[0]
        #

        # 数组的声明与定义，如：
        # int s[10]; == > s = [0] * 10
        # int s[5] = {1,2,3}; ==>  s = [1,2,3,0,0]
        # char s[5] = "abc"; ==>  s = ['a','b','c',0,0]
        elif tree.key == 'direct_declarator' and len(tree.children) == 4 and \
                isinstance(tree.children[2], ASTInternalNode) and \
                tree.children[2].key == 'assignment_expression':
            """
            数组名 = [None] * 长度
            """
            return [code_list[0][0] + '=[' + 'None' + ']*' + code_list[2][0]]

        elif tree.key == 'init_declarator' and len(tree.children) == 3 and code_list[0][0].find('[') >= 0:
            tmp = code_list[0][0]  # s[0]*5
            index_1 = tmp.find('[')
            left = tmp[:index_1 - 1]  # s
            length = code_list[0][0].split('*')[1]  # 5

            # 字符数组 "..."初始化
            if code_list[2][0].find('"') >= 0:
                tmp = code_list[2][0].strip('"')  # "abc"
                result = [left + '=[None]*' + length]
                for i, c in enumerate(tmp):
                    result.append(left + '[' + str(i) + ']="' + c + '"')
                """
                数组名 = [None] * 长度
                数组名[0] = 初始值1 ("字符")
                数组名[1] = 初始值2
                ...
                """
                return result

            # 其他类型的数组 {...}初始化
            else:
                tmp = code_list[2][0].split(',')
                result = [left + '=[None]*' + length]
                for i, c in enumerate(tmp):
                    result.append(left + '[' + str(i) + ']=' + c)
                """
                数组名 = [None] * 长度
                数组名[0] = 初始值1
                数组名[1] = 初始值2
                ...
                """
                return result

        # 去除数组的[]
        elif tree.key == 'initializer' and len(tree.children) == 3:
            """
            []中的值
            """
            return code_list[1]

        # 其他情况
        else:
            lst = []
            flag = True
            for code in code_list:
                if len(code) != 1:
                    flag = False
            if flag:
                s = ''
                for code in code_list:
                    s += code[0]
                lst.append(s)
            else:
                for code in code_list:
                    lst.extend(code)
            return lst
