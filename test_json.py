import json

data = {
    "normal_str_2": "\\\\(",
    "normal_str_4": "\\\\\\\\\[",
    "raw_str_2": r"\\(",
    "raw_str_4": r"\\\\["
}

with open("test.json", "w") as f:
    json.dump(data, f, indent=4)

