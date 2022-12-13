from base_file import BaseFile
from luaparser import astnodes
from luaparser import ast
import luaparser
import fix_utils
import shutil
import log
import os


class LuaFile(BaseFile):
    def __init__(self, path=None):
        super().__init__(path)
        self.rebuild_ast = True
        parse_error_split = self._text.split("^-")
        if len(parse_error_split) == 1:
            parse_error_split = self._text.split("^ -")
        if len(parse_error_split) != 1:
            count = 1
            try:
                while float(parse_error_split[1][:count]):
                    count += 1
            except ValueError:
                count -= 1
            self._text = parse_error_split[0] + "^(-" + \
                parse_error_split[1][:count] + ")" + \
                parse_error_split[1][count:]
        self._text = fix_utils.fix_lua(self._text)
        try:
            self._ast_tree = ast.parse(self._text)
        except luaparser.builder.SyntaxException as error:
            # Try inserting an end if the luaparser is missing one,
            # this is a hacky faulty lua fix
            if "Expecting one of 'end' at line" in str(error):
                log.warn("Auto inserting missing end!")
                line = int(str(error)
                           .split("Expecting one of 'end' at line ")[1]
                           .split(",")[0])
                self.mixin_line("end", line=line)
            else:
                raise error
        fix_utils.fix_recursion(self)

    def build_ast(self):
        self._ast_tree = ast.parse(self._text)

    def set_text(self, text):
        self._text = text
        if self.rebuild_ast:
            self._ast_tree = ast.parse(self._text)

    def _get_assign_nodes(self, name):
        nodes = []
        for node in ast.walk(self._ast_tree):
            if isinstance(node, astnodes.Assign):
                for target in node.targets:
                    if isinstance(target, astnodes.Name) and target.id == name:
                        nodes.append(target)
                for value in node.values:
                    if isinstance(value, astnodes.Name) and value.id == name:
                        nodes.append(value)
        return nodes

    def _get_function_node(self, name):
        if name is None:
            return
        for node in ast.walk(self._ast_tree):
            if isinstance(node, astnodes.Function):
                if isinstance(node.name, astnodes.Index):
                    continue
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
        if self.rebuild_ast:
            self._ast_tree = ast.parse(self._text)

    def mixin_line(self, code, function=None, line=0):
        if function is None:
            pos = self._get_pos_from_line(line, self._text)
        else:
            source = self.get_function(function, with_definition=False)
            if source is None:
                return
            pos = self._get_pos_from_line(line, source)
        self.mixin("\n" + code, function, pos)

    def _get_function_call_nodes(self, name):
        nodes = []
        for node in ast.walk(self._ast_tree):
            if isinstance(node, astnodes.Call) and \
                    isinstance(node.func, astnodes.Name):
                if type(name) == str:
                    if node.func.id == name:
                        nodes.append(node)
                else:
                    if node.func.id in name:
                        nodes.append(node)
        return nodes

    def replace_assigns(self, variable, new_variable):
        nodes = self._get_assign_nodes(variable)
        if len(nodes) > 0:
            nodes.reverse()
            for node in nodes:
                self._text = self._text[:node.start_char] + new_variable + \
                    self._text[node.stop_char + 1:]
        if self.rebuild_ast:
            self._ast_tree = ast.parse(self._text)

    def replace_function_calls_multiple(self, function_dict):
        nodes = self._get_function_call_nodes(function_dict.keys())
        if len(nodes) > 0:
            nodes.reverse()
            for node in nodes:
                self._text = self._text[:node.func.start_char] + \
                    function_dict[node.func.id] + \
                    self._text[node.func.stop_char + 1:]
            if self.rebuild_ast:
                self._ast_tree = ast.parse(self._text)

    def replace_function_calls(self, function, new_function):
        nodes = self._get_function_call_nodes(function)
        if len(nodes) > 0:
            nodes.reverse()
            for node in nodes:
                self._text = self._text[:node.func.start_char] + \
                    new_function + self._text[node.func.stop_char + 1:]
            if self.rebuild_ast:
                self._ast_tree = ast.parse(self._text)

    def replace(self, text, newtext):
        old_text = self._text
        super().replace(text, newtext)
        if old_text != self._text and self.rebuild_ast:
            self._ast_tree = ast.parse(self._text)

    def save(self, path):
        super().save(path)
        if shutil.which("stylua") is None:
            log.warn("stylua is not installed, skipping code prettifying!")
        else:
            if os.system("stylua \"" + path + "\"") != 0:
                log.warn("stylua failed to prettify code, this likely means \
that something went wrong during conversion!")
