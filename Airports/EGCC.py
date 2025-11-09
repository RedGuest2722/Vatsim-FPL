from geopy.distance import geodesic
import json, tkinter as tk

RUNWAYS: dict = {
    "23R": [
        "EKLAD 1R",
        "KUXEM 1R",
        "LISTO 2R",
        "POL 5R",
        "SANBA 1R",
        "SONEX 1R"
    ],
    "23L": [
        "EKLAD 1Y",
        "KUXEM 1Y",
        "LISTO 1Y",
        "POL 1Y",
        "SANBA 1Y",
        "SONEX 1Y"
    ],
    "05L": [
        "ASMIM 1S",
        "DESIG 1S",
        "LISTO 2S",
        "POL 4S"
    ],
    "05R": [
        "ASMIM 1Z",
        "DESIG 1Z",
        "LISTO 2Z",
        "POL 1Z"
    ]
}

REROUTES: dict = {
    "ASMIM": {
        "EKLAD": "EKLAD Y53 WAL",
        "KUXEM": "KUXEM P17 NOKIN"
        },
    "DESIG": "SONEX UL975 DESIG",
    "LISTO": "SANBA N859 HON",
    "EKLAD": "ASMIM L975 WAL",
    "KUXEM": "ASMIM P16 NOKIN",
    "SANBA": "LISTO L612 HON",
    "SONEX": "DESIG"
}

FLCAPS: dict = [
    {
        "AIRPORT": [
            "EGBB",
            "EGBE",
            "EGNX"
        ],
        "FL": 90
    },
    {
        "AIRPORT": [
            "EGLL",
            "EGLC",
            "EGSC",
            "EGSS",
            "EGGW",
            "EGKK",
            "EGKB"
        ],
        "FL": 190
    },
    {
        "AIRPORT": [
            "EGGD",
            "EGFF",
            "EGSY",
            "EGTE",
            "EGJJ",
            "EGJB",
            "EGJA"
        ],
        "FL": 290
    },
    {
        "AIRPORT": [
            "EGAA",
            "EGAC",
            "EGAD",
            "EGAE",
            "EGAL",
            "EGPF",
            "EGPG",
            "EGPH",
            "EGPK",
            "EGPN",
            "EGQL"
        ],
        "FL": 240
    },
    {
        "AIRPORT": [
            "EHAM",
            "EHBK",
            "EHGG",
            "EHHO",
            "EHLW",
            "EHTE"
        ],
        "FL": 350,
        "RST": [
            "KOLAG",
            "RAVLO",
            "LAMSO"
        ]
    },
    {
        "AIRPORT": "EB",
        "FL": 290
    },
    {
        "AIRPORT": [
            "EIDW",
            "EIDG",
            "EIME",
            "EIWT"
        ],
        "FL": 280
    },
    {
        "AIRPORT": "EI",
        "FL": 160,
        "RST": [
            "LIFFY"
        ]
    },
    {
        "AIRPORT": [
            "LFGA",
            "LFGB",
            "LFSB",
            "LFSM"
        ],
        "FL": 330
    },
    {
        "AIRPORT": [
            "LFBC",
            "LFBD",
            "LFBE",
            "LFBE",
            "LFBG",
            "LFBS",
            "LFBX",
            "LFCH",
            "LFCY",
            "LFDI"
        ],
        "FL": 350
    },
    {
        "AIRPORT": [
            "EDDG",
            "EDDK",
            "EDDL",
            "EDGS",
            "EDKB",
            "EDKL",
            "EDLA",
            "EDLE",
            "EDLM",
            "EDLN",
            "EDLP",
            "EDLV",
            "EDLW",
            "ETNG",
            "ETNN"
        ],
        "FL": 350,
        "RST": [
            "RENEQ",
            "LONAM",
            "TOFFA",
            "GODOS",
            "MOLIX",
            "LAMSO",
            "NAVPI",
            "SOMVA",
            "REDFA",
            "SUMUM",
            "SASKI"
        ]
    },
    {
        "AIRPORT": [
            "LFSD"
        ],
        "FL": 350
    },
    {
        "AIRPORT": [
            "LFPB",
            "LFPG",
            "LFPN",
            "LFPO",
            "LFPT",
            "LFPV"
        ],
        "FL": 290
    }
]

DATA: dict = {
    "Elevation": 257,
    "Long": -2.2749939,
    "Latt": 53.35388947
}

def __init__(runway: tk.StringVar, root: tk.Tk, resource_path):
    self = type("data", (), {})()
    self.runway = runway
    self.root = root
    self.resource_path = resource_path

    return self

def checkRoute(self, pilot: dict):
    pilotRoute: str = pilot["flight_plan"].get("route")
    
    # Remove SID
    for _, rwy in RUNWAYS.items():
        for sid in rwy:
            if pilotRoute.find(sid) > 0:
                pilotRoute = f'{pilotRoute[:pilotRoute.find(sid)]} {pilotRoute[pilotRoute.find(" ", pilotRoute.find(sid)):]}'
            
    invalid = True
    # See if FPL has a valid departure SID
    for sid in RUNWAYS[self.runway.get()]:
        sid: str
        #check to find a valid SID for given route
        if pilotRoute.find(sid.split(" ")[0]) > -1:
            invalid = False
            #Wake category check
            if self.runway.get().find("23") > -1:
                listo_sanba: bool|str = False
                with open(self.resource_path(r"Airports/EGCC.json"), "r") as file:
                    aircrafts: dict = json.load(file)
                
                
                listo_sanba = aircrafts.get(pilot["flight_plan"].get("aircraft_short"), False)
                
                if listo_sanba:
                    if pilotRoute.find("SANBA") > -1 or pilotRoute.find("LISTO") > -1:
                        if pilotRoute.find(listo_sanba) < 0:
                            for lsSID in RUNWAYS[self.runway.get()]:
                                if lsSID.find(listo_sanba) > -1:
                                    return {"callsign": pilot["callsign"], "type": "RR", "Route": REROUTES[listo_sanba], "SID": lsSID, "colour": "#ffA500"}
                else:
                    lsStringVar: tk.StringVar = tk.StringVar(master=self.root, value="False")
                    lsWindow: tk.Toplevel = tk.Toplevel(master=self.root, bg="#000000")
                    lsWindow.attributes("-topmost", True)
                    lsFrame: tk.Frame = tk.Frame(master=lsWindow, bg="#000000")
                    lsFrame.pack(anchor="center", pady=10)
                    lsLabel1: tk.Label = tk.Label(master=lsFrame, text=f'Is {pilot["flight_plan"]["aircraft_short"]} a ', fg="#ffffff", bg="#808080")
                    lsLabel1.pack(side="left")
                    listoButton: tk.Button = tk.Button(master=lsFrame, text="LISTO", command=lambda:lsStringVar.set("LISTO"))
                    listoButton.pack(side="left", padx=5)
                    lsLabel2: tk.Label = tk.Label(master=lsFrame, text=f'or a', fg="#ffffff", bg="#808080")
                    lsLabel2.pack(side="left", padx=5)
                    sanbaButton: tk.Button = tk.Button(master=lsFrame, text="SANBA", command=lambda:lsStringVar.set("SANBA"))
                    sanbaButton.pack(side="left", padx=5)
                    lsLabel3: tk.Label = tk.Label(master=lsFrame, text=f'departure.', fg="#ffffff", bg="#808080")
                    lsLabel3.pack(side="left", padx=5)

                    while lsStringVar.get() == "False":
                        self.root.update()
                    
                    lsWindow.destroy()
                    aircrafts[pilot["flight_plan"]["aircraft_short"]] = lsStringVar.get()
                    
                    with open(self.resource_path(r"Airports/EGCC.json"), "w") as file: 
                        json.dump(aircrafts, file, indent=4)
                    
                    if pilotRoute.find("SANBA") > -1 or pilotRoute.find("LISTO") > -1:
                        if pilotRoute.find(lsStringVar.get()) < 0:
                            for lsSID in RUNWAYS[self.runway.get()]:
                                if lsSID.find(lsStringVar.get()) > -1:
                                    return {"callsign": pilot["callsign"], "type": "RR", "Route": REROUTES[lsStringVar.get()], "SID": lsSID, "colour": "#ffA500"}
                        
    # if FPL departure invalid find correct departure with re-route
    if invalid:
        filed = pilotRoute[:pilotRoute.find(" ")]
        # Checking for ASMIM (2 options for re-route)
        if filed == "ASMIM":
            if pilotRoute.find("WAL") > -1:
                Reroute = {"Route": REROUTES["ASMIM"]["EKLAD"]}
            else:
                Reroute = {"Route": REROUTES["ASMIM"]["KUXEM"]}
        else:
            Reroute = {"Route": REROUTES[filed]}
        
        # Assign correct SID
        for sid in RUNWAYS[self.runway.get()]:
            if sid.find(Reroute["Route"].split()[0]) > -1:
                Reroute["SID"] = sid
        
        # Apply re-route to FPL
        RerouteList = Reroute["Route"].split(" ")
        if pilotRoute.find(RerouteList[2]) > -1:
            return {"callsign": pilot.get("callsign"), **Reroute, "type": "RR", "colour": "#ffA500"}
        else:
            # More complicated re-route required
            if pilotRoute.find(RerouteList[1]) > -1:
                return {"callsign": pilot["callsign"], "type": "RR", "Route": f"{RerouteList[0]} {RerouteList[1]} {pilotRoute[pilotRoute.find(' ', pilotRoute.find(RerouteList[1])):pilotRoute.find(' ', pilotRoute.find(RerouteList[1])+7)]}","SID": Reroute.get("SID"), "colour": "#ffA500"}
            else:
                return {"callsign": pilot["callsign"], "type": "FPL", "colour": "#ff0000"}
    else:
        return False