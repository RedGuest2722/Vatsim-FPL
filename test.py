import tkinter as tk
root = tk.Tk()

def ls(sid):
    lsWindow.destroy()
    aircrafts = {}
    aircrafts["A20N"] = sid
    
    print(f"{list(aircrafts.keys())[0]}\n{aircrafts["A20N"]}")
    root.destroy()

lsWindow: tk.Toplevel = tk.Toplevel(master=root, bg="#000000")
lsFrame: tk.Frame = tk.Frame(master=lsWindow, bg="#000000")
lsFrame.pack(anchor="center", pady=10)
lsLabel1: tk.Label = tk.Label(master=lsFrame, text=f'Is A20N a ', fg="#ffffff", bg="#808080")
lsLabel1.pack(side="left")
listoButton: tk.Button = tk.Button(master=lsFrame, text="LISTO", command=lambda:ls("LISTO"))
listoButton.pack(side="left", padx=5)
lsLabel2: tk.Label = tk.Label(master=lsFrame, text=f'or a', fg="#ffffff", bg="#808080")
lsLabel2.pack(side="left", padx=5)
sanbaButton: tk.Button = tk.Button(master=lsFrame, text="SANBA", command=lambda:ls("SANBA"))
sanbaButton.pack(side="left", padx=5)
lsLabel3: tk.Label = tk.Label(master=lsFrame, text=f'departure.', fg="#ffffff", bg="#808080")
lsLabel3.pack(side="left", padx=5)

root.mainloop()