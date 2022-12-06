from luaparser import astnodes
from luaparser import ast
from config import CONVERTER_PREFIX
import log
import os


def match_capitalization(path):
    path = os.path.realpath(path)
    parent_folder = os.path.dirname(path)
    if not os.path.exists(parent_folder):
        parent_folder = match_capitalization(parent_folder)
        if parent_folder is None:
            return None
    for entry in os.listdir(parent_folder):
        if entry.upper() == os.path.basename(path).upper():
            return os.path.join(parent_folder, entry)


# This function is specifically aimed at fixing faulty lua files in 1.92 packs,
# so just like the errors in those files, this is a big mess
def fix_lua(code):
    if "os.time" in code.replace("math.randomseed(os.time())", ""):
        log.error("os.time is used!")
        raise Exception("Unsupported function used")
    code = code.replace("if num = ", "if num == ")  # exutils.lua fix

    # token recognition errors
    code = code.replace("\\*", "\\\\*")
    code = code.replace(".\\Â°", ".\\\\Â°")
    return _parse_code(code)


def fix_recursion(lua_file):
    functions = []
    for node in ast.walk(lua_file._ast_tree):
        if isinstance(node, astnodes.Function):
            if isinstance(node.name, astnodes.Index):
                continue
            func_code = lua_file._text[node.start_char:node.stop_char + 1]
            func_ast = ast.parse(func_code)
            for sub_node in ast.walk(func_ast):
                if isinstance(sub_node, astnodes.Call) and \
                        isinstance(sub_node.func, astnodes.Name):
                    if sub_node.func.id == node.name.id and \
                            func_code[sub_node.stop_char - 1:
                                      sub_node.stop_char + 1] == "()":
                        functions.append([node, sub_node])
    functions.reverse()
    for func in functions:
        log.warn("Limiting recursion depth approximately in", func[0].name.id)
        lua_file.mixin_line("if " + CONVERTER_PREFIX +
                            "call_depth >= 16381 then u_haltTime(16) \
                            error(\"stack overflow\") end " +
                            CONVERTER_PREFIX + "call_depth = " +
                            CONVERTER_PREFIX + "call_depth + 1",
                            func[0].name.id)
        lua_file.mixin_line(CONVERTER_PREFIX + "call_depth = " +
                            CONVERTER_PREFIX + "call_depth - 1",
                            func[0].name.id, -1)


OPENING_KEYWORDS = ["if", "for", "while", "function"]
SEPERATORS = [" ", "\t", "\n", ";", ",", "(", ")"]


def _count_keyword(code, keyword):
    match_count = 0
    matches = 0
    last_sep = True
    string_type = None
    for char in code + "\n":
        if char == "\"":
            if string_type is None:
                string_type = char
            elif string_type == char:
                string_type = None
        if char == "'":
            if string_type is None:
                string_type = char
            elif string_type == char:
                string_type = None
        if string_type is None:
            if match_count >= len(keyword):
                if char in SEPERATORS:
                    matches += 1
                else:
                    match_count = 0
                last_sep = False
            if last_sep and keyword[match_count] == char:
                match_count += 1
            else:
                match_count = 0
                last_sep = char in SEPERATORS
        else:
            match_count = 0
            last_sep = False
    return matches


def _parse_line(line, ends, openings, needs_do):
    # Counting openings and end keywords
    end_add = _count_keyword(line, "end")
    opening_add = 0
    for keyword in OPENING_KEYWORDS:
        opening_add += _count_keyword(line, keyword)
    ends += end_add
    openings += opening_add
    has_loop = False
    for loop in "for", "while":
        if _count_keyword(line, loop) > 0:
            has_loop = True
    # Replace elseif without prior opening with if
    if _count_keyword(line, "elseif") > 0 and ends == openings and \
            line.find("end") < line.find("elseif"):
        log.warn("Changing wrong line of lua:", line)
        line = line.replace("elseif", "if")
        openings += 1
        opening_add += 1
    dos = _count_keyword(line, "do")
    if has_loop and dos == 0:
        needs_do = True
    function = _count_keyword(line, "function") > 0
    if function and "(" not in line:
        log.warn("Adding missing brackets to line:", line)
        line = line + "()"
    # Remove lines without loop but with do,
    #              with "elseif >",
    #              with ", )" or
    #              with more ends than openings
    if (not has_loop and not needs_do and dos > 0) \
            or "elseif >" in line or ", )" in line or ends > openings:
        log.warn("Removing wrong line of lua:", line)
        line = ""
        ends -= end_add
        openings -= opening_add
    if dos > 0:
        needs_do = False
    if "io.open(" in line and "\\" in line:
        before, args = line.split("io.open(", 1)
        before += "io.open("
        args, after = args.split(")", 1)
        after = ")" + after
        line = before + args.replace("\\", "/") + after
        log.warn("Fixed \\ in file path")
    return line, ends, openings, needs_do


def _parse_code(code):
    # parsing line by line
    ends = 0
    openings = 0
    lines = code.split("\n")
    code = ""
    is_comment = False
    needs_do = False
    for i in range(len(lines)):
        # Ignoring but readding comments
        swap = False
        line_comment = lines[i].split("--", 1)
        line = line_comment[0]
        if len(line_comment) > 1:
            comment = "--" + line_comment[1]
        else:
            comment = ""
        full_line = line + comment
        for comment_type in "]]--", "]===]--":
            if comment_type in full_line:
                comment, line = full_line.split(comment_type)
                comment += comment_type
                swap = True
                is_comment = False
        if not is_comment:
            line, ends, openings, needs_do = _parse_line(line, ends, openings,
                                                         needs_do)
        if comment[:4] == "--[[" or comment[:7] == "--[===[":
            is_comment = True
        if swap:
            code += comment + line + "\n"
        else:
            code += line + comment + "\n"
    return code
