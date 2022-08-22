COLOR_OBJECTS = [
    "main",
    "player_color",
    "text_color",
    "wall_color"
]


def convert_color(color):
    color["dynamic_darkness"] = color.get("dynamic_darkness", 0)
    return color


def convert(style_json):
    for color in COLOR_OBJECTS:
        if color in style_json:
            style_json[color] = convert_color(style_json[color])
    for i in range(len(style_json.get("colors", []))):
        style_json["colors"][i] = convert_color(style_json["colors"][i])
