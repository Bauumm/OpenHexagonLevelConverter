import chardet
import log
import os


class BaseFile:
    def __init__(self, path=None):
        self.path = path
        self.saved = False
        if path is None:
            self._text = ""
        else:
            with open(path, "rb") as file:
                encoding = chardet.detect(file.read())["encoding"]
            with open(path, encoding=encoding) as file:
                self._text = file.read()

    def mixin(self, text, pos):
        self._text = self._text[:pos] + text + self._text[pos:]

    def _get_pos_from_line(self, line, text):
        pos = 0
        lines = text.split("\n")
        if line < 0:
            line = len(lines) + line + 1
        for i in range(len(lines)):
            if line == i:
                break
            pos += len(lines[i]) + 1
        return pos

    def set_text(self, text):
        self._text = text

    def mixin_line(self, text, line=0):
        self.mixin(text + "\n", self._get_pos_from_line(line, self._text))

    def replace(self, text, newtext):
        self._text = self._text.replace(text, newtext)

    def save(self, path):
        if self.saved:
            log.warn("Saving", os.path.basename(self.path), "twice!")
        if "/" in path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            file.write(self._text)
        self.saved = True
