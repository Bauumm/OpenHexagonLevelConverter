from slpp import slpp
import chardet
import json
import os


class JsonFile:
    def __init__(self, path):

        def line_has_symbol(line, symbol):
            pos = 0
            can_find = True
            for part in line.split("\""):
                can_find = not can_find
                if can_find:
                    pos += len(part) + 1
                    continue
                if symbol in part:
                    return pos + len(part.split(symbol)[0])
                pos += len(part) + 1

        self.path = path
        content = ""
        with open(path, "rb") as file:
            encoding = chardet.detect(file.read())["encoding"]
        with open(path, encoding=encoding) as file:
            write = True
            for line in file.read().split("\n"):
                if write:
                    start_comment = line_has_symbol(line, "/*")
                    one_line_comment = line_has_symbol(line, "//")
                    if start_comment is not None:
                        content += line[:start_comment] + "\n"
                        write = False
                    elif one_line_comment is not None:
                        content += line[:one_line_comment] + "\n"
                    else:
                        content += line + "\n"
                else:
                    stop_comment = line_has_symbol(line, "*/")
                    if stop_comment is not None:
                        content += line[stop_comment + 2:] + "\n"
                        write = True
        self._json = json.loads(content)

    def get_keys(self):
        return list(self._json.keys())

    def get(self, value_name):
        return self._json.get(value_name)

    def delete(self, value_name):
        if value_name in self._json:
            del self._json[value_name]

    def as_table(self):
        return slpp.encode(self._json)

    def mixin(self, value_name, value):
        self._json[value_name] = value

    def save(self, path):
        if "/" in path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(self._json, file, indent=4)
