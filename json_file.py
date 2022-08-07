from extended_dict import ExtendedDict
import chardet
import json
import log
import os


class JsonFile(ExtendedDict):
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

        self.saved = False
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
        json_dict = json.loads(content)
        for key in json_dict:
            self[key] = json_dict[key]

    def save(self, path):
        if self.saved:
            log.warn("Saving", os.path.basename(self.path), "twice!")
        if "/" in path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(self, file, indent=4)
