import json, time

with open("D:\Google Drive Offline\MSFS\VATSIM\Vatsim-FPL\SRD_routes.json", "r") as file:
    data: dict = json.load(file)

#

with open("D:\Google Drive Offline\MSFS\VATSIM\Vatsim-FPL\SRD_routes.json", "w") as file:
    json.dump(data, file, indent=4)