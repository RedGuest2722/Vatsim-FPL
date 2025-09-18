import tkinter as tk
import requests
import queue
from geopy.distance import geodesic
import json
import time
import os
import sys
import pyperclip as clip

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


'''
pilot: {
    callsign: string,
    altitude: integer,
    flight_plan: {
        
    }
}
'''
#Initiate Tkinter
root: tk.Tk = tk.Tk()
root.geometry("1500x700")
root.title("Vatsim UK FPL Checker")
root.configure(bg="#000000")


#Vars
baseDir = os.getcwd()
vatsimDataJson: queue.Queue = queue.Queue()
airportPilots: queue.Queue = queue.Queue()
endThreads: queue.Queue = queue.Queue()
endThreads.put(item=False)
timeLocal: queue.Queue = queue.Queue()
runwayInUse: tk.StringVar = tk.StringVar(master=root, value="None")
userLocation: str = ""
pilotFrames: list = []

    #file vars
#Loads Manchester Data
with open(resource_path(r"data.json"), "r") as file:
    data: dict = json.load(file)

def endProgram():
    root.destroy()
    sys.exit()

if not data['USERDATA'].get('CID'):
    
    exitButton: tk.Button = tk.Button(master=root, command=lambda:endProgram(), text="End Program", width=15, font=(20), fg="#ffffff", bg="#808080", anchor="s")
    exitButton.pack(pady=10)
    cidWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000")
    cidWindow.attributes("-topmost", True)
    cidLabel: tk.Label = tk.Label(master=cidWindow, bg="#000000", fg="#ffffff", text="Enter your vatsim CID:")
    cidLabel.pack(pady=10)
    cidVar: tk.StringVar = tk.StringVar(master=cidWindow)
    cidEntry: tk.Entry = tk.Entry(master=cidWindow, bg="#808080", fg="#ffffff", textvariable=cidVar)
    cidEntry.pack(pady=5)
    
    while not len(cidVar.get()) == 7:
        root.update()
    
    data["USERDATA"] = {"CID": int(cidVar.get())}
    with open(resource_path(r"data.json"), "w") as file:
        json.dump(data, file, indent=4)
    cidWindow.destroy()
    exitButton.destroy()

#Loads airport data
with open(resource_path(r"UK Airports Database.json"), "r") as file:
    airportData: dict = json.load(file)
    airportData.keys

#Functions
def vatsimDataFunc(vatsimDataJson: queue.Queue, airportPilots: queue.Queue, airportData: dict, reRouteFrame: tk.Frame, updatedTimeLabel: tk.Label, userLocation: str, pilotFrames: list):
    '''
    MAIN THREAD  
    -
    Fetches new VATSIM data every 15 seconds.
    '''

    #Get vatsim pilots
    pilots = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()['pilots']
    #with open(resource_path(r"vatsimdata.json"), "r") as file:
    #    pilots = json.load(file)
    
    airportPilots: list = []
    
    #remove any pilots that have left the ATZ
    
    newPilotFrame: list = []
    for pilotFrame in pilotFrames:
        keep = False
        for pilot in pilots:
            if geodesic((airportData[userLocation]["Latt"], airportData[userLocation]["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= 2000:
                if pilotFrame["name"] == pilot["callsign"]:
                    keep = True
                    break
        if keep:
            newPilotFrame.append(pilotFrame)
        else:
            pilotFrame["frame"].destroy()
            
    pilotFrames[:] = newPilotFrame
    
    #Main run, checks FPL - Route
    for pilot in pilots:
        #Check in ATZ
        if geodesic((airportData[userLocation]["Latt"], airportData[userLocation]["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= 2000:
            if pilot["flight_plan"]:
                #Checks runway has been chosen and the flight is departing from the user airport
                if runwayInUse.get() != "None" and pilot["flight_plan"]["departure"] == userLocation and pilot["flight_plan"]["flight_rules"] == "I":
                    pilotRoute: str = pilot["flight_plan"]["route"]
                    # Remove FL and Coords e.g(F290N5132)
                    while True:
                        if pilotRoute.find("/") > -1:
                            slashBeginning = pilotRoute.find("/")
                            slashEnding = pilotRoute.find(" ", slashBeginning)
                            pilotRoute = pilotRoute[:slashBeginning] + pilotRoute[slashEnding:]
                        else:
                            break
                    
                    # Remove departure airport
                    if pilotRoute.find(userLocation) > -1:
                        pilotRoute =  pilotRoute[:pilotRoute.find(userLocation)] + pilotRoute[pilotRoute.find(" ", pilotRoute.find(userLocation)):]
                    
                    # Remove SID
                    for _, rwy in data["AIRPORTS"][userLocation]["RUNWAYS"].items():
                        for sid in rwy:
                            if pilotRoute.find(sid) > -1:
                                pilotRoute = f'{pilotRoute[:pilotRoute.find(sid)]} {pilotRoute[pilotRoute.find(" ", pilotRoute.find(sid)):]}'
                            
                    invalid = True
                    # See if FPL has a valid departure SID
                    for sid in data["AIRPORTS"][userLocation][runwayInUse.get()]["SIDS"]:
                        sid: str
                        #check to find a valid SID for given route
                        if pilotRoute.find(sid.split(" ")[0]) > -1:
                            invalid = False
                            #Wake category check
                            if runwayInUse.get().find("23") > -1:
                                listo_sanba: bool|str = False
                                with open(resource_path(r"LISTO re_routes.json"), "r") as file:
                                    aircrafts: dict = json.load(file)
                                
                                while True:
                                    listo_sanba = aircrafts.get(pilot["flight_plan"]["aircraft_short"], False)
                                    
                                    if listo_sanba:
                                        if pilot["flight_plan"]["route"].find(listo_sanba) > 0:
                                            for lsSID in data["AIRPORTS"][userLocation][runwayInUse.get()]:
                                                if lsSID.find(listo_sanba) > -1:
                                                    airportPilots.append({"callsign": pilot["callsign"], "type": "RR", "Route": data["AIRPORTS"][userLocation]["REROUTES"][listo_sanba], "SID": lsSID, "colour": "#ffA500"})
                                        
                                        break
                                    else:
                                        lsStringVar: tk.StringVar = tk.StringVar(master=root, value="False")
                                        lsWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000")
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
                                            root.update()
                                        lsWindow.destroy()
                                        aircrafts[pilot["flight_plan"]["aircraft_short"]] = lsStringVar.get()
                                        
                                        with open(resource_path(r"LISTO re_routes.json"), "w") as file: 
                                            json.dump(aircrafts, file, indent=4)
                                    
                    # if FPL departure invalid find correct departure with re-route
                    if invalid:
                        filed = pilotRoute[:pilotRoute.find(" ")]
                        # Checking for ASMIM (2 options for re-route)
                        if filed == "ASMIM":
                            if pilotRoute.find("WAL") > -1:
                                Reroute = {"Route": data["AIRPORTS"][userLocation]["REROUTES"]["ASMIM"]["EKLAD"]}
                            else:
                                Reroute = {"Route": data["AIRPORTS"][userLocation]["REROUTES"]["ASMIM"]["KUXEM"]}
                        else:
                            Reroute = {"Route": data["AIRPORTS"][userLocation]["REROUTES"][filed]}
                        
                        # Assign correct SID
                        for sid in data["AIRPORTS"][userLocation][runwayInUse.get()]["SIDS"]:
                            if sid.find(Reroute["Route"].split()[0]) > -1:
                                Reroute["SID"] = sid
                        
                        # Apply re-route to FPL
                        RerouteList = Reroute["Route"].split(" ")
                        if pilotRoute.find(RerouteList[2]) > -1:
                            airportPilots.append({"callsign": pilot.get("callsign"), **Reroute, "type": "RR", "colour": "#ffA500"})
                        else:
                            # More complicated re-route required
                            if pilotRoute.find(RerouteList[1]) > -1:
                                airportPilots.append({"callsign": pilot["callsign"], "type": "RR", 
                                    "Route": f"{RerouteList[0]} {RerouteList[1]} {pilotRoute[pilotRoute.find(' ', pilotRoute.find(RerouteList[1])):pilotRoute.find(' ', pilotRoute.find(RerouteList[1])+7)]}", "SID": Reroute["SID"], "colour": "#ffA500"})
                            else:
                                airportPilots.append({"callsign": pilot["callsign"], "SRD": "Needs SRD", "colour": "#ff0000"})
                        
            else:
                airportPilots.append({"callsign": pilot["callsign"], "type": "FPL", "colour": "#ff0000"})
    for pilotReRoute in airportPilots:
        callsign = pilotReRoute["callsign"]
        buttoned = False
        for buttonedCallsign in pilotFrames:
            if buttonedCallsign["name"] == callsign:
                buttoned = True
                buttonedCallsign["labelCall"].configure(fg=pilotReRoute["colour"])
                if pilotReRoute["type"] == "RR":
                    try:
                        buttonedCallsign["labelMsg"].forget()
                    except:
                        pass
                    buttonedCallsign["sid"].configure(text=pilotReRoute["SID"], command=lambda:clip.copy(pilotReRoute["Route"]))
                    buttonedCallsign["route"].configure(text="Re-Route", command=lambda:clip.copy(f'{pilotReRoute["SID"].replace(" ", "")} departure. Runway {runwayInUse.get()}. Re-Route: {pilotReRoute["Route"]} Then as filed.'))
                    buttonedCallsign["sid"].pack(side="left")
                    buttonedCallsign["route"].pack(side="left")
                else:
                    try:
                        buttonedCallsign["sid"].forget()
                        buttonedCallsign["route"].forget()
                    except:
                        pass
                    buttonedCallsign["labelMsg"].configure(text="No flight Plan" if pilotReRoute["type"] == "FPL" else "Needs SRD")
                    buttonedCallsign["labelMsg"].pack(side="left")
                break
            
        if not buttoned:
            
            pilotReRoute["name"] = callsign
            pilotReRoute["Runway"] = runwayInUse.get()
            pilotReRoute["frame"] = tk.Frame(reRouteFrame, bg="#000000")
            pilotReRoute["labelCall"] = tk.Label(pilotReRoute["frame"], text=f"{callsign}:", font=(20), fg=pilotReRoute["colour"], bg="#000000")
            
            pilotReRoute["frame"].pack(side="top", pady=5)
            pilotReRoute["labelCall"].pack(side="left")
            
            pilotReRoute["sid"] = tk.Button(pilotReRoute["frame"], font=(20), fg="#ffffff", bg="#808080")
            pilotReRoute["route"] = tk.Button(pilotReRoute["frame"], font=(20), fg="#ffffff", bg="#808080")
            pilotReRoute["labelMsg"] = tk.Label(pilotReRoute["frame"], font=(20), fg="#ffffff", bg="#808080")
            
            if pilotReRoute["type"] == "RR":
                pilotReRoute["sid"].configure(text=pilotReRoute["SID"], command=lambda:clip.copy(pilotReRoute["Route"]))
                pilotReRoute["route"].configure(text="Re-Route", command=lambda:clip.copy(f'{pilotReRoute["SID"].replace(" ", "")} departure. Runway {runwayInUse.get()}. Re-Route: {pilotReRoute["Route"]} Then as filed.'))
                
                pilotReRoute["sid"].pack(side="left", padx=5)
                pilotReRoute["route"].pack(side="left", padx=5)
            else:
                pilotReRoute["labelMsg"] = tk.Label(pilotReRoute["frame"], text="No flight Plan" if pilotReRoute["type"] == "FPL" else "VFR Traffic" if pilotReRoute["type"] == "VFR" else "As Filed" if pilotReRoute["type"] == "AF" else "Needs SRD", font=(20), fg=pilotReRoute["colour"], bg="#000000")
                pilotReRoute["labelMsg"].pack(side="left")
            
            
            
            pilotFrames.append(pilotReRoute)
    
    updatedTimeLabel.configure(text=f'Updated: {time.strftime("%H:%M:%S", time.gmtime())}z (RWY: {runwayInUse.get()})')

    root.after(ms=1000, func=lambda:vatsimDataFunc(vatsimDataJson, airportPilots, airportData, reRouteFrame, updatedTimeLabel, userLocation, pilotFrames))


def timeUpdate(localTimeLabel: tk.Label):
    localTimeLabel.configure(text=f'Current: {time.strftime("%H:%M:%S", time.gmtime())}z')
    root.after(100, func=lambda:timeUpdate(localTimeLabel))


def selectRunway(runwayInUse: tk.StringVar, data: dict, userLocation: str, selectRunwayButton: tk.Button):
    
    runwayWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000", pady=40, padx=150)
    
    
    runwayList: tk.Listbox = tk.Listbox(master=runwayWindow, fg="#ffffff", bg="#000000", justify="center", width=4, height=len(list(data["AIRPORTS"][userLocation]["RUNWAYS"].keys())), font=("TkDefaultFont", 25))
    for runway in data["AIRPORTS"][userLocation]["RUNWAYS"].keys():
        runwayList.insert(tk.END, runway)
        
    runwayList.pack(anchor="center")
    
    while not runwayList.curselection():
        root.update()
    
    runwayInUse.set(runwayList.get(runwayList.curselection()))
    selectRunwayButton.configure(text=f"Change selected")
    runwayWindow.destroy()
#end

#Find User location
#with open(resource_path(r"vatsimdata.json"), "r") as file:
#    controllers = json.load(file)['controllers']

location, userLocation = True, "EGCC"
#location = False
while not location:
    controllers = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()['controller']
    for controller in controllers:
        if controller['cid'] == data['USERDATA']['CID']:
            userLocation = controller['callsign'][:4]
            location = True
    time.sleep(1)


#Tkinter start buttons
selectRunwayButton: tk.Button = tk.Button(master=root, width=20, font=(20), command=lambda:selectRunway(runwayInUse, data, userLocation, selectRunwayButton), text="Select runway", fg="#ffffff", bg="#808080")
selectRunwayButton.pack(side="top", pady=5)

bottomBanner: tk.Frame = tk.Frame(master=root, bg="#000000")
bottomBanner.pack(side="bottom", pady=5, fill="x")

updatedTimeLabel: tk.Label = tk.Label(master=bottomBanner, width=30, font=(20), anchor="w", fg="#ffffff", bg="#000000")
updatedTimeLabel.pack(side="left", padx=10)

bottomBannercenter: tk.Frame = tk.Frame(master=bottomBanner, bg="#000000")
bottomBannercenter.pack(side="left", expand=True)

endProgramButton: tk.Button = tk.Button(master=bottomBannercenter, command=lambda:endProgram(), text="End Program", width=15, font=(20), fg="#ffffff", bg="#808080")
endProgramButton.pack()

localTimeLabel: tk.Label = tk.Label(master=bottomBanner, width=30, font=(20), anchor="e", fg="#ffffff", bg="#000000")
localTimeLabel.pack(side="right", padx=10)


reRouteFrame: tk.Frame = tk.Frame(master=root, bg="#000000")
reRouteFrame.pack(pady=5, anchor="center")
root.attributes("-topmost", True)

#Start Threads
timeUpdate(localTimeLabel)
vatsimDataFunc(vatsimDataJson, airportPilots, airportData, reRouteFrame, updatedTimeLabel, userLocation, pilotFrames)

root.attributes("-topmost", False)
root.mainloop()