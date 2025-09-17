import os

lineTable = []

with open(os.path.join(os.getcwd(), 'exits.txt'), 'r') as file:
    for line in file:
        lineTable.append(line)

lineTableLength = len(lineTable) - 1
i = 0

while i < lineTableLength:
    if lineTable[i].find('\n'):
        lineTable[i] = lineTable[i].rstrip(',\n') + ''
    
    lineTable[i] = f'"{lineTable[i]}",\n'
    i += 1

with open(os.path.join(os.getcwd(), 'exits_comma.txt'), 'w') as file:
    for line in lineTable:
        file.write(line)