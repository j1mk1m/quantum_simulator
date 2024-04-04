import sys

if __name__=="__main__":
    file_name = sys.argv[1]

    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            lines.append(line)
