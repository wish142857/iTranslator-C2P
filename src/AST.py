# coding=utf-8


class ASTNode:
    def __init__(self, key):
        self.key = key


class ASTInternalNode(ASTNode):
    def __init__(self, key, children):
        ASTNode.__init__(self, key)
        for item in children:
            if not isinstance(item, ASTNode):
                item = ASTExternalNode(str(item), str(item))
        self.children = children

    def __str__(self):
        buffer = ''
        for i in self.children:
            buffer += (str(i).strip() + ' ')
        return buffer


class ASTExternalNode(ASTNode):
    def __init__(self, key, value):
        ASTNode.__init__(self, key)
        self.value = str(value)

    def __str__(self):
        return self.value




