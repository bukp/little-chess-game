import tkinter as tk
from tkinter import ttk
import os
import game
import json

def user_settings():
        try :
            with open("config.json" ,"r+") as file:
                return json.load(file)
        except :
            return game.DEFAULT_SETTINGS

def settings_window(parent_window):

    def get_data():
        return {
            "settings" : [liste1.get(liste1.curselection()[0]), liste2.get(liste2.curselection()[0])],
            "bsd" : liste3.get(liste3.curselection()[0]),
            "bsz" : int(size_set.get()),
            "board" : fen_entry.get(),
            "pieces_style" : pieces_style_list.get(),
            "board_style" : board_style_list.get()
        }

    def save():
        with open("config.json" ,"+w") as file:
            json.dump(get_data(), file)
    
    def create():
        parent_window.__init__(get_data())
        window.destroy()

    default = user_settings()

    #Creation of the tkinter setting window
    size = (600, 170)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset/pieces/cburnett/bN.png"))
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight = 1)
    window.rowconfigure(1, weight = 1)
    window.rowconfigure(2, weight = 1)

    row1 = tk.Frame(window)
    row1.grid(row=0, column=0, sticky="ew", padx=5)
    row1.columnconfigure(0, weight=1)
    row1.columnconfigure(1, weight=1)
    row1.columnconfigure(2, weight=1)
    row1.columnconfigure(3, weight=5)

    frame1 = tk.LabelFrame(row1, text = "White player")
    frame1.grid(row=0, column=0, sticky="nsew")

    frame2 = tk.LabelFrame(row1, text = "Black player")
    frame2.grid(row=0, column=1, sticky="nsew")

    frame3 = tk.LabelFrame(row1, text = "View")
    frame3.grid(row=0, column=2, sticky="nsew")

    frame4 = tk.LabelFrame(row1, text = "Board")
    frame4.grid(row=0, column=3, sticky="nsew")
    frame4.columnconfigure(0, weight=1)
    frame4.columnconfigure(1, weight=1)
    frame4.rowconfigure(0, weight=1)
    frame4.rowconfigure(1, weight=1)

    frame5 = tk.Frame(window)
    frame5.grid(row=1, column=0, sticky="ew", padx=5)
    frame5.columnconfigure(1, weight=1)

    frame6 = tk.LabelFrame(window, text = "Style")
    frame6.grid(row=2, column=0, sticky="nsew", padx=5)
    frame6.columnconfigure(0, weight=1)
    frame6.columnconfigure(1, weight=2)
    frame6.columnconfigure(2, weight=1)
    frame6.columnconfigure(3, weight=2)

    liste1 = tk.Listbox(frame1, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste1.pack()
    liste1.insert(1, "player")
    liste1.insert(2, "bot")
    liste1.insert(3, "random")
    liste1.insert(4, "remote player")
    liste1.select_set(liste1.get(0, "end").index(default["settings"][0]))

    liste2 = tk.Listbox(frame2, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste2.pack()
    liste2.insert(1, "player")
    liste2.insert(2, "bot")
    liste2.insert(3, "random")
    liste2.insert(4, "remote player")
    liste2.select_set(liste2.get(0, "end").index(default["settings"][1]))

    liste3 = tk.Listbox(frame3, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste3.pack()
    liste3.insert(1, "white")
    liste3.insert(2, "black")
    liste3.select_set(liste3.get(0, "end").index(default["bsd"]))

    tk.Label(frame4, text = "Board size : ").grid(row=0, column=0, sticky="w")

    size_set = tk.StringVar()
    spinbox = tk.Spinbox(frame4, values = list(range(120, 1320 ,120)), width = 5, textvariable = size_set)
    size_set.set(default["bsz"])
    spinbox.grid(row=0, column=1, sticky="ew")

    tk.Button(frame4, text="Save Settings", command = save).grid(row=1, column=0, sticky="ew")

    tk.Button(frame4, text="Create Board", command = create).grid(row=1, column=1, sticky="ew")

    tk.Label(frame5, text = "Fen : ").grid(row=0, column=0, sticky="w")

    fen_entry = tk.Entry(frame5)
    fen_entry.grid(row=0, column=1, sticky="ew")
    fen_entry.insert(0, default["board"])
    
    tk.Label(frame6, text = "Pieces : ").grid(row=0, column=0, sticky="w")

    pieces_list = os.listdir("asset/pieces")
    pieces_style_list = ttk.Combobox(frame6, values=pieces_list, state="readonly")
    pieces_style_list.grid(row=0, column=1, sticky="ew")
    pieces_style_list.current(pieces_list.index(default["pieces_style"]))

    tk.Label(frame6, text = "Board : ").grid(row=0, column=2, sticky="w")

    board_list = list(map(lambda x: x.split(".")[0], os.listdir("asset/boards")))
    board_style_list = ttk.Combobox(frame6, state="readonly", values=board_list)
    board_style_list.grid(row=0, column=3, sticky="ew")
    board_style_list.current(board_list.index(default["board_style"]))

    window.mainloop()


if __name__ == "__main__":
    settings_window()