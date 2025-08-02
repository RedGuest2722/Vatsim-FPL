import requests
import tkinter as tk
import threading
import queue
from geopy.distance import distance
import json
import time
import os
import sys


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
root.geometry("400x300")


#Vars
vatsimDataJson: queue.Queue = queue.Queue()
airportPilots: queue.Queue = queue.Queue
endThreads: queue.Queue = queue.Queue()
endThreads.put(item=False)
timeLocal: queue.Queue = queue.Queue()
runwayInUse: tk.StringVar = tk.StringVar(master=root)
userLocation = None

    #file vars
with open(os.path.join(os.getcwd(), r"data.json"), "r") as file:
    data: dict = json.load(file)

with open(r'D:\My Stuff\Coding Projects\Vatsim FPL Checker\Airport Coords.json', 'r') as file:
    airportCoords: dict = json.load(file)

#Functions
def vatsimDataFunc(vatsimDataJson: queue.Queue, airportPilots: queue.Queue, airportCoords: dict):
    '''
    Fetches new VATSIM data every second.
    '''

    vatsimDataJson.put(requests.get("https://data.vatsim.net/v3/vatsim-data.json").json())
    
    airportPilots.put([
        pilot for pilot in vatsimDataJson.get()['pilots']
        if distance((airportCoords[userLocation].get('latt'), airportCoords[userLocation].get('long')), (pilot.get('latitude'), pilot.get('longitude'))) <= 2 and pilot['flight_plan'].get('departure') == userLocation
    ])
    
    for pilot in airportPilots.get():
        
#end

def endProgram():
    root.quit()
    sys.exit()


#Start Threads
threading.Timer(function=lambda:vatsimDataFunc(vatsimDataJson, airportPilots, airportCoords), interval=1).start() #Vatsim Thread


#Find User location
'''
while not userLocation:
    for controller in vatsimDataJson.get()['controllers']:
        if controller.get('cid') == data['USERDATA'].get('CID') and str.find(controller.get('callsign'), "ATIS") < 0:
            userLocation = controller.get('callsign')[:4]
    time.sleep(5)
'''
userLocation = "EGCC"


#Tkinter start buttons
endProgramButton: tk.Button = tk.Button(master=root, command=lambda:endProgram(), text="End Program", width=15)
endProgramButton.pack(side='bottom', pady=5)
messageBox: tk.Label = tk.Label(master=root)
messageBox.pack(side='bottom', pady=5)

root.mainloop()