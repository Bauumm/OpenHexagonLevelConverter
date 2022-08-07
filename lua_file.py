from base_file import BaseFile
from luaparser import astnodes
from luaparser import ast
import shutil
import log
import os


class LuaFile(BaseFile):
    def __init__(self, path):
        super().__init__(path)
        self._ast_tree = ast.parse(self._text)

    def _get_function_node(self, name):
        for node in ast.walk(self._ast_tree):
            if isinstance(node, astnodes.Function):
                if node.name.id == name:
                    return node

    def get_function(self, name, with_definition=True):
        node = self._get_function_node(name)
        if node is not None:
            if not with_definition:
                function = self._text[node.start_char:node.stop_char + 1]
                source = function.split(")", 1)[1].rsplit("end", 1)[0]
                if source.startswith("\n"):
                    source = source[1:]
                if source.endswith("\n"):
                    source = source[:-1]
                return source
            return self._text[node.start_char:node.stop_char + 1]

    def mixin(self, code, function=None, pos=0):
        node = self._get_function_node(function)
        start_pos = 0
        if node is not None:
            if pos < 0:
                start_pos = node.stop_char - 1
            else:
                start_pos = node.start_char + \
                    len(self.get_function(function).split(")")[0]) + 1
        super().mixin(code, start_pos + pos)
        self._ast_tree = ast.parse(self._text)

    def mixin_line(self, code, function=None, line=0):
        source = self.get_function(function, with_definition=False)
        if source is None:
            source = self._text
        pos = self._get_pos_from_line(line, source)
        self.mixin("\n" + code, function, pos)

    def _get_function_call_nodes(self, name):
        nodes = []
        for node in ast.walk(self._ast_tree):
            if isinstance(node, astnodes.Call) and \
                    isinstance(node.func, astnodes.Name):
                if node.func.id == name:
                    nodes.append(node)
        return nodes

    def replace_function_calls(self, function, new_function):
        nodes = self._get_function_call_nodes(function)
        nodes.reverse()
        for node in nodes:
            self._text = self._text[:node.func.start_char] + \
                new_function + self._text[node.func.stop_char + 1:]
        self._ast_tree = ast.parse(self._text)

    def replace(self, text, newtext):
        super().replace(text, newtext)
        self._ast_tree = ast.parse(self._text)

    def save(self, path):
        super().save(path)
        if shutil.which("stylua") is None:
            log.warn("stylua is not installed, skipping code prettifying!")
        else:
            if os.system("stylua \"" + path + "\"") != 0:
                log.warn("stylua failed to prettify code, this likely means \
that something went wrong during conversion!")
