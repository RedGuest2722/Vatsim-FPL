import json, os

with open(os.path.join(os.getcwd(), 'SRD.json'), 'r') as file:
    data: dict = json.load(file)

i = 0
while i != 1:
    for ADEP in data.get('ADEP'):
        for ADES in ADEP.get('ADES'):
            for ADES_K, ADES_V in ADES.items():
                if not len(ADES_K) == 4:
                    print(ADES_K)
            

#for ADEP in data.get('ADEP'):
    #for ADES in ADEP.get('ADES'):
        #if len(ADES):
