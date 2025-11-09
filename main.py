import tkinter as tk, pyperclip as clip, requests, queue, time, os, sys, math
from geopy.distance import geodesic
from Airports import loadAirport

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    else:
        # Running as a script
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


#Initiate Tkinter
root: tk.Tk = tk.Tk()
root.geometry("700x400")
root.title("Vatsim UK FPL Checker")
root.configure(bg="#000000")


#Vars
vatsimDataJson: queue.Queue = queue.Queue()
airportPilots: queue.Queue = queue.Queue()
endThreads: queue.Queue = queue.Queue()
endThreads.put(item=False)
timeLocal: queue.Queue = queue.Queue()
runwayInUse: tk.StringVar = tk.StringVar(master=root, value="")
userLocation: tk.StringVar = tk.StringVar(master=root)
pilotFrames: list = []
cidStr: tk.StringVar = tk.StringVar()
aircraftCounted: tk.IntVar = tk.IntVar(master=root, value=0)
aircraftErrored: tk.IntVar = tk.IntVar(master=root, value=0)

    #file vars
#Loads Manchester Data
try:
    with open(resource_path(r"cid.txt"), "r") as file:
        cidStr.set(file.readlines()[0])
except:

    exitButton: tk.Button = tk.Button(master=root, command=lambda:endProgram(), text="End Program", width=15, font=(20), fg="#ffffff", bg="#808080", anchor="s")
    exitButton.pack(pady=10)
    cidWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000")
    cidWindow.attributes("-topmost", True)
    cidLabel: tk.Label = tk.Label(master=cidWindow, bg="#000000", fg="#ffffff", text="Enter your vatsim CID:")
    cidLabel.pack(pady=10)
    
    cidEntry: tk.Entry = tk.Entry(master=cidWindow, bg="#808080", fg="#ffffff", textvariable=cidStr)
    cidEntry.pack(pady=5)
    
    while not len(cidStr.get()) == 7:
        root.update()
    
    
    with open(resource_path(r"cid.txt"), "w") as file:
        file.write(cidStr.get())
    cidWindow.destroy()
    exitButton.destroy()

def endProgram():
    root.destroy()
    sys.exit()

def quarterTime():
    secsNow: int = int(time.strftime("%S"))

    return 1000*((math.ceil(secsNow/15)*15)-secsNow)

#Functions
def vatsimDataFunc(vatsimDataJson: queue.Queue, airportPilots: queue.Queue, airportModule: loadAirport, reRouteFrame: tk.Frame, updatedTimeLabel: tk.Label, userLocation: tk.StringVar, pilotFrames: list):
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
    
    #remove any pilots that have left the ATZ or disconnected
    
    newPilotFrame: list = []
    for pilotFrame in pilotFrames:
        keep = False
        for pilot in pilots:
            if geodesic((airportModule.DATA["Latt"], airportModule.DATA["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= (airportModule.DATA["Elevation"] + 1000):
                if pilotFrame["name"] == pilot["callsign"]:
                    keep = True
                    break
        if keep:
            newPilotFrame.append(pilotFrame)
        else:
            pilotFrame["frame"].destroy()
            
    pilotFrames[:] = newPilotFrame
    
    #Main run, checks FPL - Route
    if runwayInUse.get() != "":
        pilotCount = 0
        pilotError = 0
        for pilot in pilots:
            if geodesic((airportModule.DATA["Latt"], airportModule.DATA["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= (airportModule.DATA["Elevation"] + 1000):
                if pilot["flight_plan"]:
                    if pilot["flight_plan"]["departure"] == userLocation.get():
                        pilotCount += 1
                        if pilot["flight_plan"]["flight_rules"] == "I":
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
                            if pilotRoute.find(userLocation.get()) > -1:
                                pilotRoute =  pilotRoute[:pilotRoute.find(userLocation.get())] + pilotRoute[pilotRoute.find(" ", pilotRoute.find(userLocation.get())):]

                            pilot["flight_plan"]["route"] = pilotRoute
                        
                            result = airportModule.checkRoute(pilot)
                            if result:
                                airportPilots.append(result)
                                pilotError += 1
                            else:
                                for pilotFrame in pilotFrames:
                                    if pilotFrame["name"] == pilot["callsign"]:
                                        pilotFrame["frame"].destroy()
                        else:
                            airportPilots.append({"callsign": pilot["callsign"], "type": "VFR", "colour": "#00ff00"})
                else:
                    airportPilots.append({"callsign": pilot["callsign"], "type": "FPL", "colour": "#ff0000"})
                    pilotError += 1
                    pilotCount += 1

        
        aircraftCounted.set(pilotCount)
        aircraftErrored.set(pilotError)


    for pilotReRoute in airportPilots:
        pilotReRoute: dict
        callsign: str = pilotReRoute["callsign"]
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
                    buttonedCallsign["sid"].configure(text=f'ATC: {pilotReRoute.get("SID")}', command=lambda:clip.copy(pilotReRoute["Route"]))
                    buttonedCallsign["route"].configure(text="Pilot", command=lambda:clip.copy(f'{pilotReRoute["SID"]} departure. Runway {runwayInUse.get()}. Re-Route: {pilotReRoute["Route"]} Then as filed.'))
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
                ## ^^ Fix this copy thing as not working properly.

                pilotReRoute["sid"].pack(side="left", padx=5)
                pilotReRoute["route"].pack(side="left", padx=5)
            else:
                pilotReRoute["labelMsg"] = tk.Label(pilotReRoute["frame"], text="No flight Plan" if pilotReRoute["type"] == "FPL" else "VFR Traffic" if pilotReRoute["type"] == "VFR" else "As Filed" if pilotReRoute["type"] == "AF" else "Needs SRD", font=(20), fg=pilotReRoute["colour"], bg="#000000")
                pilotReRoute["labelMsg"].pack(side="left")
            
            
            
            pilotFrames.append(pilotReRoute)
    
    updatedTimeLabel.configure(text=f'Updated: {time.strftime("%H:%M:%S", time.gmtime())}z ({userLocation.get()[2:]} | {airportModule.runway.get()})')

    root.after(quarterTime(), func=lambda:vatsimDataFunc(vatsimDataJson, airportPilots, airportModule, reRouteFrame, updatedTimeLabel, userLocation, pilotFrames))

def timeUpdate(localTimeLabel: tk.Label):
    localTimeLabel.configure(text=f'Errors {aircraftErrored.get()}/{aircraftCounted.get()} | Current: {time.strftime("%H:%M:%S", time.gmtime())}z')
    root.after(100, func=lambda:timeUpdate(localTimeLabel))



location = False
controllers = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()['controllers']
for controller in controllers:
    if str(controller['cid']) == cidStr.get():
        if str(controller['callsign']).find("OBS") < 0:
            userLocation.set(controller['callsign'][:4])
            location = True
    
if not location:
    airportWindow: tk.Toplevel = tk.Toplevel(master=root)
    airportWindow.attributes("-topmost", True)
    locationVar: tk.StringVar = tk.StringVar()

    locationEntry = tk.Entry(master=airportWindow, width=10, font=(20), fg="#ffffff", bg="#000000", textvariable=userLocation)
    locationEntry.pack()

    while not len(userLocation.get()) == 4:
        root.update()
    
    airportWindow.destroy()
    userLocation.set(userLocation.get().upper())


airportModule = loadAirport(userLocation, root, runwayInUse, resource_path)

#Tkinter start buttons
bottomBanner: tk.Frame = tk.Frame(master=root, bg="#000000")
bottomBanner.pack(side="bottom", pady=5, fill="x")

updatedTimeLabel: tk.Label = tk.Label(master=bottomBanner, width=25, font=(20), anchor="w", fg="#ffffff", bg="#000000")
updatedTimeLabel.pack(side="left", padx=10)

bottomBannercenter: tk.Frame = tk.Frame(master=bottomBanner, bg="#000000")
bottomBannercenter.pack(side="left", expand=True)

endProgramButton: tk.Button = tk.Button(master=bottomBannercenter, command=lambda:endProgram(), text="End Program", width=15, font=(20), fg="#ffffff", bg="#808080")
endProgramButton.pack()

localTimeLabel: tk.Label = tk.Label(master=bottomBanner, width=25, font=(20), anchor="e", fg="#ffffff", bg="#000000")
localTimeLabel.pack(side="right", padx=10)


reRouteFrame: tk.Frame = tk.Frame(master=root, bg="#000000")
reRouteFrame.pack(pady=5, anchor="center")
root.attributes("-topmost", True)

#Start Threads
timeUpdate(localTimeLabel)
vatsimDataFunc(vatsimDataJson, airportPilots, airportModule, reRouteFrame, updatedTimeLabel, userLocation, pilotFrames)
root.mainloop()