
from AST import ASTInternalNode, ASTExternalNode
from yacc import parser
import os


INDENT_STRING = '  '


def formatIndent(item, rank=-1):
    print(item)
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
        if tree.key == 'selection_statement':
            if len(tree.children) == 5:
                return ['if '+code_list[2][0]+':', code_list[4]]
            if len(tree.children) == 7:
                return ['if '+code_list[2][0]+':', code_list[4], 'else:', code_list[6]]
        elif tree.key == 'block_item_list':
            lst = []
            #print(code_list, tree.key, tree.children)
            for code in code_list:
                for c in code:
                    lst.append(c)
            return lst
        else:
            lst = []
            s = ''
            for code in code_list:
                for c in code:
                    if isinstance(c, str):
                        s += c
                    else:
                        lst.append(s)
                        lst.append(c)
                        s = ''
            if len(s) != 0:
                lst.append(s)
            return lst

    def leaf_string(self, tree):
        if tree.value == ';':
            return ['']
        elif tree.value == '&&':
            return ['and']
        elif tree.value == '||':
            return ['or']
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
        print(code_list)
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
    translator.translate('1.txt', '1.out')