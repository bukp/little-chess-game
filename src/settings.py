import tkinter as tk
from tkinter import ttk
import os
import game
import json

def user_settings(category = "all"):
    try :
        with open("config.json" ,"r+") as file:
            if category == "all":
                return json.load(file)
            else :
                return json.load(file)[category]
    except :
        if category == "all":
            return game.DEFAULT_SETTINGS
        else :
            return game.DEFAULT_SETTINGS[category]

def graphics_settings_window():
    
    def get_data():
        return {
            "pieces_style" : pieces_style_list.get(),
            "board_style" : board_style_list.get(),
            "bsd" : view_liste.get(view_liste.curselection()[0]),
            "bsz" : int(size_set.get()),
        }

    def save():
        data = user_settings()
        data["graphics"] = get_data()
        with open("config.json" ,"+w") as file:
            json.dump(data, file, indent=2)

    def reset():
        load(game.DEFAULT_SETTINGS["graphics"])

    def load(default = None):
        if default == None:
            default = user_settings("graphics")

        view_liste.select_clear(0, "end")
        view_liste.select_set(view_liste.get(0, "end").index(default["bsd"]))

        pieces_style_list.current(pieces_list.index(default["pieces_style"]))
        board_style_list.current(board_list.index(default["board_style"]))
        size_set.set(default["bsz"])

    def apply():
        save()
        window.quit()

    #Creation of the tkinter setting window
    size = (500, 100)
    window = tk.Tk()
    window.title("Graphics settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset/pieces/cburnett/bN.png"))
    window.columnconfigure(0, weight=1)

    window.rowconfigure(0, weight = 1)

    frame1 = tk.LabelFrame(window, text = "Style")
    frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    frame1.columnconfigure(0, weight=1)
    frame1.columnconfigure(1, weight=3)
    frame1.rowconfigure(0, weight=1)
    frame1.rowconfigure(1, weight=1)
    frame1.rowconfigure(2, weight=1)

    tk.Label(frame1, text = "Pieces : ").grid(row=0, column=0, sticky="w")
    
    pieces_list = os.listdir("asset/pieces")
    pieces_style_list = ttk.Combobox(frame1, values=pieces_list, state="readonly")
    pieces_style_list.grid(row=0, column=1, sticky="ew", padx=15)

    tk.Label(frame1, text = "Board : ").grid(row=1, column=0, sticky="w")

    board_list = list(map(lambda x: x.split(".")[0], os.listdir("asset/boards")))
    board_style_list = ttk.Combobox(frame1, state="readonly", values=board_list)
    board_style_list.grid(row=1, column=1, sticky="ew", padx=15)

    tk.Label(frame1, text = "Board size : ").grid(row=2, column=0, sticky="w")

    size_set = tk.StringVar()
    spinbox = tk.Spinbox(frame1, values = list(range(120, 1320 ,120)), width = 5, textvariable = size_set)
    spinbox.grid(row=2, column=1, sticky="ew", padx=15)

    frame2 = tk.LabelFrame(window, text = "View")
    frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    view_liste = tk.Listbox(frame2, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    view_liste.pack()
    view_liste.insert(1, "auto")
    view_liste.insert(2, "white")
    view_liste.insert(3, "black")
    view_liste.insert(4, "alternate")

    frame3 = tk.Frame(window)
    frame3.grid(row=0, column=2, sticky="nse", pady=5, padx=5)
    frame3.rowconfigure(0, weight=1)
    frame3.rowconfigure(1, weight=1)

    tk.Button(frame3, text="Reset Settings", command = reset).grid(row=0, column=0, sticky="nsew", padx=2, pady=8)

    tk.Button(frame3, text="Apply Settings", command = apply).grid(row=1, column=0, sticky="nsew", padx=2, pady=8)

    load()
    window.mainloop()
    try :
        data = get_data()
        window.destroy()
    except :
        data = None
    return data

def game_settings_window():

    def get_data():
        return {
            "settings" : [liste1.get(liste1.curselection()[0]), liste2.get(liste2.curselection()[0])],
            "clock" : str(enable_clock.get()),
            "times" : [white_time.get(),black_time.get()],
            "address" : [white_address_entry.get(), black_address_entry.get()], 
            "port" : [white_port_entry.get(),black_port_entry.get()],
            "board" : fen_entry.get(),
        }

    def save():
        data = user_settings()
        data["game"] = get_data()
        with open("config.json" ,"+w") as file:
            json.dump(data, file, indent=2)

    def reset():
        load(game.DEFAULT_SETTINGS["game"])

    def load(default = None):
        if default == None:
            default = user_settings("game")

        liste1.select_clear(0, "end")
        liste1.select_set(liste1.get(0, "end").index(default["settings"][0]))
        liste2.select_clear(0, "end")
        liste2.select_set(liste2.get(0, "end").index(default["settings"][1]))

        enable_clock.set(default["clock"] == "True")
        white_time.set(default["times"][0])
        black_time.set(default["times"][1])

        fen_entry.delete(0, "end")
        fen_entry.insert(0, default["board"])

        white_address_entry.delete(0, "end")
        white_address_entry.insert(0, default["address"][0])
        white_port_entry.delete(0, "end")
        white_port_entry.insert(0, default["port"][0])

        black_address_entry.delete(0, "end")
        black_address_entry.insert(0, default["address"][1])
        black_port_entry.delete(0, "end")
        black_port_entry.insert(0, default["port"][1])

        refresh()
    
    def create(lan = False):
        global post_on_lan
        post_on_lan = lan
        if "remote player" not in get_data()["settings"] and lan:
            return
        save()
        window.quit()

    #Creation of the tkinter setting window
    size = (480, 130)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset/pieces/cburnett/bN.png"))
    window.columnconfigure(0, weight=1)

    window.rowconfigure(0, weight = 1)
    window.rowconfigure(1, weight = 1)
    window.rowconfigure(2, weight = 1)
    window.rowconfigure(3, weight = 1)

    row1 = tk.Frame(window)
    row1.grid(row=0, column=0, sticky="nsew", padx=5)
    row1.columnconfigure(0, weight=1, uniform="r")
    row1.columnconfigure(1, weight=1, uniform="r")
    row1.columnconfigure(2, weight=1, uniform="r")
    row1.columnconfigure(3, weight=1, uniform="r")

    frame1 = tk.LabelFrame(row1, text = "White player")
    frame1.grid(row=0, column=0, sticky="nsew")

    liste1 = tk.Listbox(frame1, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste1.pack()
    liste1.insert(1, "player")
    liste1.insert(2, "bot")
    liste1.insert(3, "random")
    liste1.insert(4, "remote player")
    liste1.bind("<ButtonRelease>", lambda x: refresh())

    frame2 = tk.LabelFrame(row1, text = "Black player")
    frame2.grid(row=0, column=1, sticky="nsew")

    liste2 = tk.Listbox(frame2, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste2.pack()
    liste2.insert(1, "player")
    liste2.insert(2, "bot")
    liste2.insert(3, "random")
    liste2.insert(4, "remote player")
    liste2.bind("<ButtonRelease>", lambda x: refresh())

    frame3 = tk.LabelFrame(row1, text="Time mode")
    frame3.grid(row=0, column=2, sticky="nsew")
    sub_frame = tk.Frame(frame3)
    sub_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
    enable_clock = tk.BooleanVar()
    tk.Checkbutton(sub_frame, variable=enable_clock).grid(row=0, column=0,  sticky="w")
    
    tk.Label(sub_frame, text="Enable time").grid(row=0, column=1, sticky="e")

    frame3.columnconfigure(0, weight=3, uniform="e")
    frame3.columnconfigure(1, weight=1, uniform="e")
    frame3.columnconfigure(2, weight=3, uniform="e")

    tk.Label(frame3, text="white").grid(row=1, column=0, sticky="ew")
    tk.Label(frame3, text=" : ").grid(row=1, column=1, sticky="ew")
    tk.Label(frame3, text="black").grid(row=1, column=2, sticky="ew")

    white_time = tk.StringVar()
    spinbox = tk.Spinbox(frame3, values = ["10", "30", "60", "3m", "5m", "10m", "15m", "30m", "60m"], textvariable = white_time)
    spinbox.grid(row=2, column=0, sticky="ew")
    
    tk.Label(frame3, text=":").grid(row=2, column=1, sticky="ew")
    
    black_time = tk.StringVar()
    spinbox = tk.Spinbox(frame3, values = ["10", "30", "60", "3m", "5m", "10m", "15m", "30m", "60m"], textvariable = black_time)
    spinbox.grid(row=2, column=2, sticky="ew")

    frame4 = tk.Frame(window)
    frame4.grid(row=3, column=0, sticky="nsew", padx=5)
    frame4.columnconfigure(1, weight=1)

    tk.Label(frame4, text = "Fen : ").grid(row=0, column=0, sticky="w")

    fen_entry = tk.Entry(frame4)
    fen_entry.grid(row=0, column=1, sticky="nsew")
    
    frame5 = tk.Frame(row1)
    frame5.grid(row=0, column=3, sticky="nsew", pady=2, padx=5)

    tk.Button(frame5, text="Reset Settings", command = reset).grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    tk.Button(frame5, text="Create Board", command = create).grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

    tk.Button(frame5, text="Create LAN Game", command = lambda: create(True)).grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

    frame6 = tk.LabelFrame(window, text = "White remote player options")
    frame6.rowconfigure(1, weight=1)
    frame6.columnconfigure(0, weight=2)
    frame6.columnconfigure(1, weight=1)
    frame6.columnconfigure(2, weight=2)
    frame6.columnconfigure(3, weight=5)
    frame6.columnconfigure(4, weight=2)
    frame6.columnconfigure(5, weight=3)
    
    tk.Label(frame6, text="Address : ").grid(row = 0, column = 0, sticky="ew")
    white_address_entry = tk.Entry(frame6)
    white_address_entry.grid(row = 0, column = 1, sticky="ew", padx = 5)
    tk.Label(frame6, text="Port : ").grid(row = 0, column = 2, sticky="ew")
    white_port_entry = tk.Entry(frame6)
    white_port_entry.grid(row = 0, column = 3, sticky="ew", padx = 5)

    frame7 = tk.LabelFrame(window, text = "Black remote player options")
    frame7.rowconfigure(1, weight=1)
    frame7.columnconfigure(0, weight=2)
    frame7.columnconfigure(1, weight=1)
    frame7.columnconfigure(2, weight=2)
    frame7.columnconfigure(3, weight=5)
    frame7.columnconfigure(4, weight=2)
    frame7.columnconfigure(5, weight=3)

    tk.Label(frame7, text="Address : ").grid(row = 0, column = 0, sticky="ew")
    black_address_entry = tk.Entry(frame7)
    black_address_entry.grid(row = 0, column = 1, sticky="ew", padx = 5)
    tk.Label(frame7, text="Port : ").grid(row = 0, column = 2, sticky="ew")
    black_port_entry = tk.Entry(frame7)
    black_port_entry.grid(row = 0, column = 3, sticky="ew", padx = 5)

    def refresh():
        extend = 0
        if len(liste1.curselection()) != 0 and liste1.get(liste1.curselection()[0]) == "remote player":
            frame6.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            extend += 50
        else :
            frame6.grid_forget()
        
        if len(liste2.curselection()) != 0 and liste2.get(liste2.curselection()[0]) == "remote player":
            frame7.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
            extend += 50
        else :
            frame7.grid_forget()
        
        window.geometry(f"{size[0]}x{size[1]+extend}")

    refresh()

    load()
    window.mainloop()
    try :
        data = get_data()
        data = (data, post_on_lan)
        window.destroy()
    except :
        data = None
    return data

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__))+"\\..")
    print(game_settings_window())