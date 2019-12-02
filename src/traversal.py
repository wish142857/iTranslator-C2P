
from AST import ASTInternalNode, ASTExternalNode
from yacc import parser
import os


INDENT_STRING = '    '


def formatIndent(item, rank=-1):
    #print(item)
    if type(item) == str:
        return INDENT_STRING * rank + item
    if type(item) == list:
        lines = []
        for i in item:
            lines.append(formatIndent(i, rank + 1))
        return '\n'.join(lines)


class Translator:
    def __init__(self):
        self.functions = []
        self.declarations = []

    def translate(self, input_file_name, output_file_name):
        try:
            with open(input_file_name, 'r') as input_file:
                file_content = self.remove_sharp(input_file)
                tree = parser.parse(file_content)
                with open(output_file_name, 'w+') as output_file:
                    output_file.write(formatIndent(self.filter(tree)))
                print('{} was translated to {} successfully.'.format(
                    input_file_name, output_file_name))
        except Exception as e:
            print(e)

    def remove_sharp(self, input_file):
        while True:
            line = input_file.readline()
            if line.find('#') < 0:
                return line + input_file.read()

    def compose(self, tree, code_list):
        # ++i
        if tree.key == 'unary_expression' and isinstance(tree.children[0], ASTExternalNode)\
                and tree.children[0].value == '++':
            res = [code_list[1][0]+' = '+code_list[1][0]+' + 1']
            print(res)
            return res
        # return
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return' and len(tree.children) == 2:
            return ['return']
        elif tree.key == 'jump_statement' and tree.children[0].key == 'return' and len(tree.children) == 3:
            return [code_list[0][0] + ' '+ code_list[1][0]]
        # struct
        elif tree.key == 'struct_or_union_specifier' and len(tree.children) == 5:
            print(code_list[1])
            print(code_list[3])
            mstr = ''
            for item in code_list[3]:
                mstr += item
            print(code_list[1][0] + '={' + mstr + '}')
            return [code_list[1][0] + '={' + mstr + '}']
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
                return ['def '+code_list[1][0]+':', code_list[2]]
        # in x = 1 中int的去除
        elif tree.key == 'declaration':
            if len(tree.children) == 3:
                return code_list[1]
            elif len(tree.children) == 2:
                return code_list[0]
        # int s[10]; ==> s = [0]*10
        elif tree.key == 'direct_declarator' and len(tree.children) == 4 and \
                isinstance(tree.children[2], ASTInternalNode) and \
                    tree.children[2].key == 'assignment_expression':
            return [code_list[0][0] + '=[' + '0' + ']*' + code_list[2][0]]
        # int s[10] = {1}; ==>  s = [1]*10
        elif tree.key == 'init_declarator' and len(tree.children) == 3 and code_list[0][0].find('[') >= 0:
            tmp = code_list[0][0]
            index_1 = tmp.find('[')
            index_2 = tmp.find(']')
            code_list[0][0] = tmp[:index_1+1]+code_list[2][0]+tmp[index_2:]
            print(code_list[0][0])
            return [str(code_list[0][0])]
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

    def leaf_string(self, tree):
        if tree.value == ';':
            return ['']
        elif tree.value == '&&':
            return [' and ']
        elif tree.value == '||':
            return [' or ']
        elif tree.value == '!':
            return ['not ']
        else:
            return [tree.value]

    def traversal(self, tree, stack):
        stack.append(tree.key)
        code_list = []

        if isinstance(tree, ASTExternalNode):
            stack.pop()
            return self.leaf_string(tree)
        for child in tree.children:
            code_list.append(self.traversal(child, stack))
        #print(tree.key, code_list)
        pycode = self.compose(tree, code_list)
        stack.pop()
        return pycode

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
        code = []
        for declaration in self.declarations:
            code.extend(self.traversal(declaration, []))
        for function in self.functions:
            code.extend(self.traversal(function, []))
        return code


if __name__ == '__main__':
    translator = Translator()
    translator.translate('1.txt', '2.txt')