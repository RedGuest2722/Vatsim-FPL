import tkinter as tk
import importlib

def selectRunway(self, selectRunwayButton: tk.Button):
    
    runwayWindow: tk.Toplevel = tk.Toplevel(master=self.root, bg="#000000", pady=40, padx=150)
    
    
    runwayList: tk.Listbox = tk.Listbox(master=runwayWindow, fg="#ffffff", bg="#000000", justify="center", width=4, height=len(self.airport.RUNWAYS), font=(20))
    for runway in self.airport.RUNWAYS.keys():
        runwayList.insert(tk.END, runway)
        
    runwayList.pack(anchor="center")
    
    while not runwayList.curselection():
        self.root.update()
    
    self.runway.set(runwayList.get(runwayList.curselection()))
    selectRunwayButton.configure(text=f"Change selected")
    runwayWindow.destroy()
#end

# Inside Airports/__init__.py
def loadAirport(userLocation: tk.StringVar, root: tk.Tk, runway: tk.StringVar):
    self = type("AirportModule", (), {})()
    self.runway = runway
    self.airport = importlib.import_module(f"Airports.{userLocation.get()}")
    self.root = root
    
    # Call the __init__ function from the airport module
    if hasattr(self.airport, "__init__"):
        self.airport.__init__(self.runway, self.root)

    # Attach required attributes and functions
    self.DATA = getattr(self.airport, "DATA", {})
    self.RUNWAYS = getattr(self.airport, "RUNWAYS", {})
    self.checkFPL = lambda pilot: self.airport.checkFPL(self, pilot)

    selectRunwayButton = tk.Button(master=root, width=20, font=(20), command=lambda:selectRunway(self, selectRunwayButton), text="Select runway", fg="#ffffff", bg="#808080")
    selectRunwayButton.pack(side="top", pady=5)

    return self