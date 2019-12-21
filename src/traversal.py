import copy

from AST import ASTInternalNode, ASTExternalNode
from yacc import parser
import os
from C_utils import c_utils
from lint import formatIndent, precompile

# INDENT_STRING = '    '
#
#
# def formatIndent(item, rank=-1):
#     #print(item)
#     if type(item) == str:
#         return INDENT_STRING * rank + item
#     if type(item) == list:
#         lines = []
#         for i in item:
#             lines.append(formatIndent(i, rank + 1))
#         return '\n'.join(lines)


class Translator:
    def __init__(self):
        self.functions = []
        self.declarations = []
        self.global_variables = []
        self.variable_table = {}

    def translate(self, input_file_name, output_file_name):
        try:
            if True:
                success, file_content = precompile(input_file_name)
                if not success:
                    print(file_content)
                    return
            # with open(input_file_name, 'r') as input_file:
                # file_content = self.remove_sharp(input_file)
                tree = parser.parse(file_content)
                with open(output_file_name, 'w+') as output_file:
                    out = formatIndent(self.filter(tree))
                    for c_util in c_utils:
                        out = c_util + out
                    out += '\nif __name__ == "__main__":\n    main()'
                    output_file.write(out)
                print('{} was translated to {} successfully.'.format(
                    input_file_name, output_file_name))
        except Exception as e:
            print(e)

    def remove_sharp(self, input_file):
        while True:
            line = input_file.readline()
            if line.find('#') < 0:
                return line + input_file.read()

    def declaration_compose(self, tree, code_list, flag):
        if tree.key == 'init_declarator':
            pass
            #self.global_variables.append(code_list[0][0].split('=')[0])
        # in x = 1 中int的去除
        if tree.key == 'declaration':
            if len(tree.children) == 3 and flag == '':
                return code_list[1]
            elif len(tree.children) == 3 and flag != '':
                # return [code_list[0][0],
                #         code_list[1][0] + ' = ' + code_list[0][0].split('class ')[1].split(':')[0] + '()'
                #         ]

                if flag != code_list[0][0]:
                    result = code_list[0]
                else:
                    result = []
                for class_obj in code_list[1]:
                    result.append(class_obj + ' = ' + flag + '()')
                print(result)
                if len(result) == 1:
                    tmp = result[0]
                    if tmp.find('=') != tmp.rfind('='):
                        tmp_2 = tmp.split('=')[2]
                        tmp_2 = tmp_2.lstrip()
                        tmp = tmp.split('=')[0] + '=' + tmp.split('=')[1]
                        tmp = tmp[0:tmp.find('[') + 1] + tmp_2 + tmp[tmp.find(']'):]
                        tmp = tmp.rstrip()
                        result = []
                        result.append(tmp)
                return result
            # elif len(tree.children) == 3 and flag == 'no_def':
            #     return [code_list[1][0] + '=None']
            elif len(tree.children) == 2:
                return code_list[0]
        # int s[10]; ==> s = [0]*10
        elif tree.key == 'direct_declarator' and len(tree.children) == 4 and \
                isinstance(tree.children[2], ASTInternalNode) and \
                tree.children[2].key == 'assignment_expression':
            return [code_list[0][0] + '=[' + '0' + ']*' + code_list[2][0]]
        # int s[5] = {1,2,3}; ==>  s = [1,2,3,0,0]
        # char s[5] = "abc"; ==>  s = ['a','b','c',0,0]
        elif tree.key == 'init_declarator' and len(tree.children) == 3 and code_list[0][0].find('[') >= 0:
            tmp = code_list[0][0]  # s[0]*5
            index_1 = tmp.find('[')
            left = tmp[:index_1 - 1]  # s
            length = int(code_list[0][0].split('*')[1])  # 5
            if code_list[2][0].find('"') >= 0:
                # 处理"abc"
                tmp = code_list[2][0]  # "abc"
                mstr = '['
                for i in range(1, len(tmp) - 1):
                    mstr += '\''
                    mstr += tmp[i]
                    mstr += '\''
                    mstr += ','
                for i in range(0, length - len(tmp) + 2):
                    mstr += str(0)
                    mstr += ','
                mstr += ']'
                # s = ['a', 'b', 'c', 0, 0]
                result = left + '=' + mstr
                # print(result)
                return [left + '=' + mstr]
            else:
                # 处理 {1,2,3} code_list[2][0] = 1,2,3
                num = len(code_list[2][0].split(','))  # 3
                for i in range(0, length - num):
                    code_list[2][0] += ','
                    code_list[2][0] += str(0)
                # s = [1,2,3,0,0]
                result = left + '=[' + code_list[2][0] + ']'
                # print(result)
                return [result]
        # elif tree.key == 'init_declarator' and len(tree.children) == 1 and flag == '':
        #     return [code_list[0][0] + '=None']
        elif tree.key == 'init_declarator_list':
            if len(tree.children) == 1:
                print(code_list[0])
                return code_list[0]
            else:
                print([code_list[0][0],
                        code_list[2][0]])
                return [code_list[0][0],
                        code_list[2][0]]
        # elif tree.key == 'init_declarator' and len(tree.children) == 1:
        #     return [code_list[0][0] + '=None']
        # if tree.key == 'declaration':
        #     self.global_variables.append(None)
        #     if len(tree.children) == 3 and flag == '':
        #         return code_list[1]
        #     elif len(tree.children) == 3 and flag == 'class':
        #         return code_list[1]
        #     elif len(tree.children) == 2:
        #         return code_list[0]
        # # elif tree.key == 'struct_or_union':
        # #     return
        elif tree.key == 'struct_or_union_specifier' and len(tree.children) == 2:
            return code_list[1]
        elif tree.key == 'struct_or_union_specifier' and len(tree.children) == 5:
            print(tree.children)
            return [code_list[0][0] + ' ' + code_list[1][0] + ':',
                    code_list[3]]
        elif tree.key == 'struct_declaration_list':
            lst = []
            for code in code_list:
                for c in code:
                    lst.append(c)
            return lst
        elif tree.key == 'struct_declaration':
            return [code_list[1][0] + ' = None']
        elif tree.key == 'initializer' and len(tree.children) == 3:
            return code_list[1]
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

    def function_compose(self, tree, code_list, flag):
        # ++i
        if tree.key == 'unary_expression' and isinstance(tree.children[0], ASTExternalNode)\
                and tree.children[0].value == '++':
            res = [code_list[1][0]+' = '+code_list[1][0]+' + 1']
            # print(res)
            return res
        # --i
        elif tree.key == 'unary_expression' and isinstance(tree.children[0], ASTExternalNode)\
                and tree.children[0].value == '--':
            res = [code_list[1][0]+' = '+code_list[1][0]+' - 1']
            return res
        # i++
        elif tree.key == 'postfix_expression' and len(tree.children)==2:
            if tree.children[1].value == '--':
                res = [code_list[0][0]+' = '+code_list[0][0]+' - 1']
                return res
            if tree.children[1].value == '++':
                res = [code_list[0][0]+' = '+code_list[0][0]+' + 1']
                return res
        # return
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return' and len(tree.children) == 2:
            return ['return']
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return' and len(tree.children) == 3:
            return [code_list[0][0] + ' '+ code_list[1][0]]
        # struct
        elif tree.key == 'struct_or_union_specifier':
            return code_list[1]
        elif tree.key == 'struct_declaration':
            return [ '\''+ code_list[1][0] + '\'' + ':\'\', ']
        elif tree.key == 'selection_statement':
            if len(tree.children) == 5:
                return ['if '+code_list[2][0]+':', code_list[4]]
            if len(tree.children) == 7:
                return ['if '+code_list[2][0]+':', code_list[4], 'else:', code_list[6]]
        # while
        elif tree.key == 'iteration_statement':
            if tree.children[0].value == 'while':
                return ['while '+' '+code_list[2][0]+':', code_list[4]]
            if len(tree.children) == 7:
                return [code_list[2][0], 'while ' + code_list[3][0] + ':', code_list[6], code_list[4]]
        elif tree.key == 'block_item_list':
            lst = []
            for code in code_list:
                for c in code:
                    lst.append(c)
            return lst
        # 函数大括号的去除
        elif tree.key == 'compound_statement':
            if len(tree.children) == 3:
                return code_list[1]
            elif len(tree.children) == 2:
                return ['pass']
        # 函数前加def
        elif tree.key == 'function_definition':
            if len(tree.children) == 4:
                pass
            elif len(tree.children) == 3:
                function_body = []
                for global_var in self.global_variables:
                    function_body.append('global ' + global_var)
                for code in code_list[2]:
                    function_body.append(code)
                return ['def '+code_list[1][0]+':', function_body]#code_list[2]]
        # in x = 1 中int的去除
        elif tree.key == 'declaration':
            if len(tree.children) == 3:
                if flag == 'class':
                    return [code_list[1][0] + ' = ' + code_list[0][0] + '()']
                else:
                    return code_list[1]

            elif len(tree.children) == 2:
                return code_list[0]
        # int s[10]; ==> s = [0]*10
        elif tree.key == 'direct_declarator' and len(tree.children) == 4 and \
                isinstance(tree.children[2], ASTInternalNode) and \
                    tree.children[2].key == 'assignment_expression':
            return [code_list[0][0] + '=[' + '0' + ']*' + code_list[2][0]]
        # int s[5] = {1,2,3}; ==>  s = [1,2,3,0,0]
        # char s[5] = "abc"; ==>  s = ['a','b','c',0,0]
        elif tree.key == 'init_declarator' and len(tree.children) == 3 and code_list[0][0].find('[') >= 0:
            tmp = code_list[0][0] # s[0]*5
            index_1 = tmp.find('[')
            left = tmp[:index_1-1] # s
            length = int(code_list[0][0].split('*')[1]) # 5
            if code_list[2][0].find('"') >= 0:
                # 处理"abc"
                tmp = code_list[2][0] # "abc"
                mstr = '['
                for i in range(1,len(tmp)-1):
                    mstr += '\''
                    mstr += tmp[i]
                    mstr += '\''
                    mstr += ','
                for i in range(0,length-len(tmp)+2):
                    mstr += str(0)
                    mstr += ','
                mstr += ']'
                # s = ['a', 'b', 'c', 0, 0]
                result = left + '=' + mstr
                print(result)
                return [left + '=' + mstr]
            else:
                # 处理 {1,2,3} code_list[2][0] = 1,2,3
                print("array2", code_list[2][0])
                num = len(code_list[2][0].split(',')) # 3
                for i in range(0,length-num):
                    code_list[2][0] += ','
                    code_list[2][0] += str(0)
                # s = [1,2,3,0,0]
                result = left+'=['+code_list[2][0]+']'
                print(result)
                return [result]
        elif tree.key == 'initializer' and len(tree.children) == 3:
            return code_list[1]
        # 函数参数列表中int的去除
        elif tree.key == 'parameter_declaration':
            if len(tree.children) == 2:
                return code_list[1]
            elif len(tree.children) == 1:
                pass
        # 函数列表中s[]的去除
        elif tree.key == 'direct_declarator' and len(tree.children) == 3 and tree.children[1] == '[':
            return [code_list[0][0]]
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
            # lst = []
            # s = ''
            # for code in code_list:
            #     for c in code:
            #         if isinstance(c, str):
            #             s += c
            #         else:
            #             if len(s) != 0:
            #                 lst.append(s)
            #             lst.append(c)
            #             s = ''
            # if len(s) != 0:
            #     lst.append(s)
            # return lst

    def flag_calculate(self, tree, flag_list):
        if tree.key == 'struct_or_union_specifier':
            print("class name", tree.children[1].value)
            return tree.children[1].value#'class'
        # if tree.key == 'init_declarator' and len(tree.children) == 1:
        #     return 'no_def'
        else:
            for flag in flag_list:
                if flag != '':
                    return flag
            return ''


    def leaf_string(self, tree):
        if tree.value == ';':
            return ['']
        elif tree.value == '&&':
            return [' and ']
        elif tree.value == '||':
            return [' or ']
        elif tree.value == '!':
            return ['not ']
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
            code, flag = self.traversal(child, stack, type)
            code_list.append(code)
            flag_list.append(flag)
        #print(tree.key, code_list)
        try:
            flag_to_upper = self.flag_calculate(tree, flag_list)
        except Exception as e:
            print(str(e))

        if type == 'declaration':
            pycode = self.declaration_compose(tree, code_list, flag_to_upper)
        else:
            pycode = self.function_compose(tree, code_list, flag_to_upper)


        stack.pop()
        return pycode, flag_to_upper


    def filter(self, tree):
        """
        this function first picks out the functions and declarations
        and then process them one by one
        """
        def pick_out(tree):
            if tree.key == 'function_definition':
                self.functions.append(tree)
            else:
                self.declarations.append(tree)
        while True:
            if tree.key == 'translation_unit':
                if len(tree.children) == 2:
                    pick_out(tree.children[1].children[0])
                    tree = tree.children[0]
                else:
                    pick_out(tree.children[0].children[0])
                    break

        self.declarations = reversed(self.declarations)
        code_list = []
        for declaration in self.declarations:
            self.declaration_extract(declaration)
            code, flag = self.traversal(declaration, [], 'declaration')
            code_list.extend(code)
        print(self.global_variables)

        for function in self.functions:
            self.name_replacement(function)
            code, flag = self.traversal(function, [], 'function')
            code_list.extend(code)
        return code_list

    def declaration_extract(self, tree):
        if tree.key == 'struct_or_union_specifier':
            return
        if isinstance(tree, ASTExternalNode):
            return
        # if isinstance(tree.children[0], ASTExternalNode):
        #     print(tree.key)
        #     if tree.key == 'IDENTIFIER':
        #         self.global_variables.append(tree.value)
        #     return
        for child in tree.children:
            if child.key == 'IDENTIFIER':
                self.global_variables.append(child.value)
                self.variable_table[child.value] = [(child.value, True)]
            else:
                self.declaration_extract(child)

    def name_replacement(self, tree, is_declarator=False):
        table_copy = copy.deepcopy(self.variable_table)
        if isinstance(tree, ASTInternalNode):
            if tree.key == 'declarator':
                for child in tree.children:
                    self.name_replacement(child, True)
            elif tree.key == 'struct_or_union_specifier':
                return
            elif tree.key == 'postfix_expression' and len(tree.children) == 3 \
                    and isinstance(tree.children[2], ASTExternalNode) and tree.children[2].key == 'IDENTIFIER':
                return
            elif tree.key == 'iteration_statement' or tree.key == 'selection_statement':
                table_copy = copy.deepcopy(self.variable_table)
                for child in tree.children:
                    self.name_replacement(child, is_declarator)
                self.variable_table = table_copy
            else:
                for child in tree.children:
                    self.name_replacement(child, is_declarator)

        else:
            if tree.key != 'IDENTIFIER':
                return
            print(tree.value)
            if tree.value in self.variable_table.keys():
                if is_declarator:
                    table = self.variable_table[tree.value]
                    if len(table) == 0:
                        table.append((tree.value, False))
                    else:
                        last = table[-1][0]
                        table.append((last + '_', False))
                        tree.value = last + '_'
                else:
                    table = self.variable_table[tree.value]
                    if len(table) != 0:
                        last = table[-1][0]
                        tree.value = last
        self.variable_table = table_copy


if __name__ == '__main__':
    translator = Translator()
    translator.translate('test.c', 'test.py')