#!/bin/python3

import subprocess
import re

# Group 1: Process property
# Group 2: Property value
PATTERN = r"application\.process\.(\w*).?=.?\"(.*)\""

PREFIX_NONE = ""
PREFIX_DETECTED = ""
#PREFIX_DISABLED = "" # TODO!

MAX_OUTPUTS = 2
MAX_OUTPUT_LEN = 16

def get_output_str() -> str:
    try:
        return subprocess.check_output(["listmic"]).decode("utf-8")  
    except FileNotFoundError:
        print("err cmd")
        exit(1)
    except subprocess.CalledProcessError:
        # grep got no data
        return ""

def get_outputs() -> list[dict]:
    lines = get_output_str().split("\n")
    ln = len(lines)

    if ln == 0:
        return []
    
    current: dict = None
    res = []

    for i in range(ln):
        line = lines[i]

        if line.startswith("Source Output"):
            if current:
                res.append(current)
            
            current = dict()
        else:
            matched = re.search(PATTERN, line)
            
            if not matched:
                continue

            if current == None:
                exit()

            [property, value] = matched.groups()            
            current[property] = value

    if current:
        res.append(current)

    return res

def remove_duplicates(outputs: list[dict]) -> list[dict]:
    ln = len(outputs)
    res = []
    
    for i in range(ln):
        duplicate = False

        for j in range(i, ln):
            if i != j and outputs[i]["id"] == outputs[j]["id"]:
                duplicate = True
                break

        if not duplicate:
            res.append(outputs[i])
    
    return res

def main():
    outputs = remove_duplicates(get_outputs())
    count = len(outputs)
    iterations = min(count, MAX_OUTPUTS)
    outputs_str = ""

    for i in range(iterations):
        output = outputs[i]
        binary: str = output["binary"]
        outputs_str += binary[0:MAX_OUTPUT_LEN]

        if len(binary) > MAX_OUTPUT_LEN:
            outputs_str += "..."
            
        if i != iterations - 1:
            outputs_str += ", "

    if count > MAX_OUTPUTS:
        outputs_str += " (...)"

    if count == 0:
        print(PREFIX_NONE, "0")
    else:
        print(f"{PREFIX_DETECTED} {count}: {outputs_str}")

if __name__ == "__main__":
    main()