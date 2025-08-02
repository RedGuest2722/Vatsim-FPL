import requests, sys, tkinter as tk, threading, json, time, os
from geopy.distance import distance


root = tk.Tk()
root.geometry("1000x500")


with open(os.path.join(os.getcwd(), 'Airport Coords.json'), 'r') as file:
    airportCoords: dict = json.load(file)


def endProgram():
    root.quit()
    sys.exit()

def getPilots(airportCoords):
    while True:
        vatsimData: dict = requests.get("https://data.vatsim.net/v3/vatsim-data.json").json()
        filtered_pilots: list = []
        for pilot in vatsimData.get('pilots', []):
            pilot: list
            
            if pilot.get('flight_plan', {}) and distance(
                (airportCoords['EGCC'].get('latt'), airportCoords['EGCC'].get('long')),
                (pilot.get('latitude'), pilot.get('longitude'))
                ) <= 2 and pilot.get('flight_plan', {}).get('departure') == 'EGCC':
                    list.append(filtered_pilots, pilot)

        linePilot = ""
        for pilot in filtered_pilots:
            if pilot.get('flight_plan', {}):
                linePilot += f"\n\n{pilot.get('callsign')}: {pilot.get('flight_plan', {}).get('route', '')}"
            else:
                linePilot += f"\n\n{pilot.get('callsign')}: No FPL"
        
        pilotLabel.configure(text=linePilot)
        vatsimTime: str = vatsimData.get("general").get("update_timestamp")
        pilotTime.configure(text=f'Updated: {vatsimTime.split("T")[1].split(".")[0]} UTC')

def timeUpdate():
    while True:
        timeZuluLabel.configure(text=f'Current: {time.strftime("%H : %M : %S", time.gmtime())} UTC')

def update_wraplength(event):
    # Subtract a little for padding if desired
    pilotLabel.config(wraplength=event.width - 20)


endProgramButton: tk.Button = tk.Button(master=root, command=lambda:endProgram(), text="End Program", width=10)
endProgramButton.pack(side='bottom', pady=5)



pilotLabel: tk.Label = tk.Label(root, justify='left', wraplength=960)
pilotLabel.pack(side='top', expand=True, fill='x', pady=5)

pilotTime: tk.Label = tk.Label(root, justify='right')
pilotTime.pack(side='top', pady=5)

timeZuluLabel: tk.Label = tk.Label(root, text=time.strftime('%H : %M : %S'), width=20)
timeZuluLabel.pack(side='bottom', pady=5)

threading.Thread(target=lambda:getPilots(airportCoords), daemon=True, name="Pilot Thread").start()
threading.Thread(target=timeUpdate, daemon=True, name="Time Thread").start()

root.mainloop()