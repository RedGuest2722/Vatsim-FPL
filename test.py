import os
refinedExits = []

with open(os.path.join(os.getcwd(), 'exits.txt'), 'r') as file:
    exits = file.read()

exitList = exits.split(",")

for exit in exitList:
    if refinedExits:
        for refinedExit in refinedExits:
            if exit not in refinedExits:
                refinedExits.append(exit)
    else:
        refinedExits.append(exit)

with open(os.path.join(os.getcwd(), 'exits2.txt'), 'w') as file:
    file.writelines(refinedExits)