import tkinter as tk, requests, time, os, sys, math
from geopy.distance import geodesic
import Airports

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    else:
        # Running as a script
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
#end

#Initiate Tkinter
root: tk.Tk = tk.Tk()
root.title("Vatsim UK FPL Checker")
root.geometry("900x600")
root.configure(bg="#000000")

#Vars
runwayInUse: tk.StringVar = tk.StringVar(master=root, value="")
userLocation: tk.StringVar = tk.StringVar(master=root, value="")
pilotFrames: dict = {}
cidStr: tk.StringVar = tk.StringVar()
aircraftCounted: tk.IntVar = tk.IntVar(master=root, value=0)
aircraftErrored: tk.IntVar = tk.IntVar(master=root, value=0)


#Loads Manchester Data
try:
    with open(resource_path(r"cid.txt"), "r") as file:
        cidStr.set(file.readlines()[0])
    #end
except:
    cidWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000")
    cidWindow.attributes("-topmost", True)
    cidLabel: tk.Label = tk.Label(master=cidWindow, font=(8), bg="#000000", fg="#ffffff", text="Enter your vatsim CID:")
    cidLabel.pack(pady=10, side="top")
    cidEntry: tk.Entry = tk.Entry(master=cidWindow, font=(8), bg="#808080", fg="#ffffff", textvariable=cidStr)
    cidEntry.pack(pady=5, side="top")
    while not len(cidStr.get()) == 7:
        root.update()
    #end
    with open(resource_path(r"cid.txt"), "w") as file:
        file.write(cidStr.get())
    #end
    cidWindow.destroy()
#end

def endProgram():
    root.destroy()
    sys.exit()
#end

def quarterTime():
    secsNow: int = int(time.strftime("%S"))
    return 1000*((math.ceil(secsNow/15)*15)-secsNow)
#end

def setCopy(root: tk.Tk, r: str):
    root.clipboard_clear()
    root.clipboard_append(r)
#end

def update_sid_route(frame: dict):
    frame["squawk"].pack_forget()
    
    try:
        frame["fl"].pack_forget()
    except:
        pass
    
    for key in ("sid", "route"):
        try:
            frame[key].destroy()
        except:
            pass

#Functions
def vatsimDataFunc(airportModule: callable, updatedTimeLabel: tk.Label, userLocation: tk.StringVar, pilotFrames: dict):
    """
    MAIN LOOP  
    -
    Fetches new VATSIM data every 15 seconds.
    """
    
    updatedTimeLabel.configure(text=f'Updated: {time.strftime("%H:%M:%S", time.gmtime())}z ({userLocation.get()[2:]} | {runwayInUse.get()})')
    
    #Get vatsim pilots
    pilots: dict|None = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()["pilots"] or None
    
    if pilots is None: # End if lost internet connection.
        raise Exception("Could not fetch VATSIM data.")
    
    # Remove any pilots that have left the ATZ or disconnected
    pilotsInATZ: list = []
    for pilot in pilots:
        if geodesic((Airports.DATA[userLocation.get()]["Latt"], Airports.DATA[userLocation.get()]["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= (Airports.DATA[userLocation.get()]["Elevation"] + 500):
            pilotsInATZ.append(pilot["callsign"])
    
    oldFrames: list = list(pilotFrames.keys())
    
    for callsign in oldFrames:
        if callsign not in pilotsInATZ:
            try:
                pilotFrames[callsign]["frame"].destroy()
                pilotFrames.pop(callsign)
            except:
                pass

    # checks FPL - Route
    if runwayInUse.get() != "":
        aircraftCounted.set(0)
        aircraftErrored.set(0)
        #loop through all pilots
        for pilot in pilots:
            
            # If pilot does not have a FPL, skip.
            if not pilot.get("flight_plan", False):
                continue
            
            # Has pilot departed from user location and still within ATZ?
            isPilotIFR: bool = pilot["flight_plan"]["flight_rules"] == "I"
            isPilotATZ: bool = geodesic((Airports.DATA[userLocation.get()]["Latt"], Airports.DATA[userLocation.get()]["Long"]), (pilot['latitude'], pilot['longitude'])).nautical <= 2 and pilot["altitude"] <= (Airports.DATA[userLocation.get()]["Elevation"] + 500)
            isPilotDepUserLoc: bool = pilot["flight_plan"]["departure"] == userLocation.get()
            
            if isPilotIFR and isPilotATZ and isPilotDepUserLoc:
                aircraftCounted.set(aircraftCounted.get() + 1)
                # Pilot is IFR departing user location within ATZ - Check FPL
                
                # Clean FPL
                pilotRoute: str = pilot["flight_plan"]["route"]
                if userLocation.get() in pilotRoute:
                    pilotRoute = f'{pilotRoute[:pilotRoute.find(userLocation.get())]}{pilotRoute[pilotRoute.find(" ", pilotRoute.find(userLocation.get()))+1:]}'
                
                while "/" in pilotRoute:
                    pilotRoute = f'{pilotRoute[:pilotRoute.find("/")]} {pilotRoute[pilotRoute.find(" ", pilotRoute.find("/"))+1:]}'
                pilot["flight_plan"]["route"] = pilotRoute
                
                sid, route = airportModule.checkFPL(pilot)
                
                altitude = utils.checkFLCAPS(pilot=pilot, FLCAPS=airportModule.FLCAPS)
                if pilot["flight_plan"]["arrival"].find("EG", 0, 1) > -1:
                    altitude = utils.checkOER(pilot["flight_plan"]["arrival"], int(pilot["flight_plan"]["altitude"]))
                
                if pilot["callsign"] in pilotFrames:
                    frame: dict = pilotFrames[pilot["callsign"]]
                else:
                    frame: dict = utils.initPilot(pilot)
                    pilotFrames[pilot["callsign"]] = frame

                if altitude:
                    frame["fl"].configure(text=altitude, fg="#ffa500")
                    aircraftErrored.set(aircraftErrored.get() + 1)
                    errored = True
                else:
                    frame["fl"].configure(text="As filed", fg="#00ff00")
                    errored = False

                if type(route) == type(str()):
                    # pilot route is invalid but has been corrected
                    newRouteText: str = f'Can you accept {sid} departure {runwayInUse.get()} with the reroute: {route} then as filed.'
                    if type(frame["sid"]) == type(tk.Label()) or type(frame["sid"]) == type(None):
                        # Destroy sid and route Labels
                        for key in ("sid", "route"):
                            try:
                                frame[key].destroy()
                            except:
                                pass
                        
                        # Create new sid button and pack it
                        frame["sid"] = tk.Button(frame["frame"], font=(8), fg="#00ff00", bg="#333333", text=sid, command=lambda _s=route: setCopy(root, _s))
                        frame["sid"].grid(column=1, row=0, padx=[5, 5])
                        
                        # Create new route button and pack it
                        frame["route"] = tk.Button(frame["frame"], font=(8), fg="#ffa500", bg="#333333", text="Correction", command=lambda _r=newRouteText: setCopy(root, _r))
                        frame["route"].grid(column=2, row=0, padx=[5, 5])
                        
                    else:
                        frame["sid"].configure(text=sid, command=lambda _s=route: setCopy(root, _s))
                        frame["route"].configure(text="Correction", command=lambda _r=newRouteText: setCopy(root, _r))

                    if not errored:
                        aircraftErrored.set(aircraftErrored.get() + 1)
                else:
                    if route:
                        sidColour: str = "#ffa500"
                        routeText: str = "Unable to correct"
                        routeColour: str = "#ff0000"
                        if not errored:
                            aircraftErrored.set(aircraftErrored.get() + 1)
                    else:
                        if "Err:" in sid:
                            sidColour: str = "#ff0000"
                            routeText: str = "Error"
                            routeColour: str = "#ff0000"
                            
                            if not errored:
                                aircraftErrored.set(aircraftErrored.get() + 1)
                        else:
                            sidColour: str = "#00ff00"
                            routeText: str = "As filed"
                            routeColour: str = "#00ff00"
                    
                    if type(frame["sid"]) == type(tk.Button()) or type(frame["sid"]) == type(None):
                        # Destroy sid and route Buttons
                        for key in ("sid", "route"):
                            try:
                                frame[key].destroy()
                            except:
                                pass
                        
                        frame["sid"] = tk.Label(frame["frame"], font=(8), fg=sidColour, bg="#000000", text=sid)
                        frame["sid"].grid(column=1, row=0, padx=[5, 5])
                        
                        frame["route"] = tk.Label(frame["frame"], font=(8), fg=routeColour, bg="#000000", text=routeText)
                        frame["route"].grid(column=2, row=0, padx=[5, 5])
                    else:
                        frame["sid"].configure(text=sid)
                        frame["route"].configure(text=routeText, fg=routeColour)
                
                squawkColour: str = "#00ff00" if pilot["flight_plan"]["assigned_transponder"] == pilot["transponder"] else "#ff0000"
                frame["squawk"].configure(fg=squawkColour, text=pilot["flight_plan"]["assigned_transponder"])
                
                #pilotFrames[pilot["callsign"]] = frame
            else:
                if pilotFrames.get(pilot["callsign"], False):
                    frame: dict = pilotFrames[pilot["callsign"]]
                    
                    try:
                        frame["route"].destroy()
                        frame["route"] = None
                    except:
                        frame["route"] = None

    root.after(quarterTime(), func=lambda:vatsimDataFunc(airportModule=airportModule, updatedTimeLabel=updatedTimeLabel, userLocation=userLocation, pilotFrames=pilotFrames))

def timeUpdate(localTimeLabel: tk.Label, aircraftErrored: tk.IntVar, aircraftCounted: tk.IntVar):
    localTimeLabel.configure(text=f'Errors {aircraftErrored.get()}/{aircraftCounted.get()} | Current: {time.strftime("%H:%M:%S", time.gmtime())}z')
    root.after(100, func=lambda:timeUpdate(localTimeLabel=localTimeLabel, aircraftErrored=aircraftErrored, aircraftCounted=aircraftCounted))

controllers: dict | None = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json().get("controllers") or None

if controllers:
    for c in controllers:
        if str(c["cid"]) == cidStr.get() and "OBS" not in str(c["callsign"]):
            userLocation.set(c["callsign"][:4])
            break
else:
    raise Exception("Could not fetch VATSIM data.")


if userLocation.get() == "":
    airportWindow: tk.Toplevel = tk.Toplevel(master=root)
    locationVar: tk.StringVar = tk.StringVar()
    locationEntry: tk.Entry = tk.Entry(master=airportWindow, width=10, font=(8), fg="#ffffff", bg="#000000", textvariable=userLocation)
    locationEntry.pack()
    
    while not len(userLocation.get()) == 4:
        root.update()
    #end
    airportWindow.destroy()
    userLocation.set(userLocation.get().upper())
#end

#Tkinter start buttons
bottomBanner: tk.Frame = tk.Frame(master=root, bg="#000000")
bottomBanner.pack(fill="x", side="bottom", pady=[5, 5])
bottomBanner.columnconfigure([0, 1, 2], weight=1, uniform="bottomBanner")

endProgramButton: tk.Button = tk.Button(master=bottomBanner, font=(8), command=lambda:endProgram(), text="End Program", width=15, fg="#ffffff", bg="#808080")
endProgramButton.grid(row=0, column=1, padx=[5, 5])

updatedTimeLabel: tk.Label = tk.Label(master=bottomBanner, font=(8), width=25, fg="#ffffff", bg="#000000")
updatedTimeLabel.grid(row=0, column=0, padx=[5, 5])

localTimeLabel: tk.Label = tk.Label(master=bottomBanner, font=(8), width=25, fg="#ffffff", bg="#000000")
localTimeLabel.grid(row=0, column=2, padx=[5, 5])

pilotsFrame: tk.Frame = tk.Frame(master=root, bg="#000000")

root.attributes("-topmost", True)

utils: Airports.utils = Airports.utils(root=root, runway=runwayInUse, userLocation=userLocation, pilotsFrame=pilotsFrame)
airportModule: callable = getattr(Airports, userLocation.get())(root, runwayInUse, resource_path)

utils.setRunwayButton(airportModule.RUNWAYS)

topBanner: tk.Frame = tk.Frame(master=root, bg="#000000")
topBanner.pack(fill="x", side="top")
topBanner.columnconfigure([0, 1, 2, 3, 4,], weight=1, uniform="topBanner")

tk.Label(master=topBanner, text="Callsign", font=(8), fg="#ffffff", bg="#000000").grid(row=0, column=0)
tk.Label(master=topBanner, text="SID", font=(8), fg="#ffffff", bg="#000000").grid(row=0, column=1)
tk.Label(master=topBanner, text="Route", font=(8), fg="#ffffff", bg="#000000").grid(row=0, column=2)
tk.Label(master=topBanner, text="FL", font=(8), fg="#ffffff", bg="#000000").grid(row=0, column=3)
tk.Label(master=topBanner, text="Squawk", font=(8), fg="#ffffff", bg="#000000").grid(row=0, column=4)

pilotsFrame.pack(fill="both", side="top")

#Start Threads
timeUpdate(localTimeLabel, aircraftErrored, aircraftCounted)
vatsimDataFunc(airportModule, updatedTimeLabel, userLocation, pilotFrames)
root.mainloop()