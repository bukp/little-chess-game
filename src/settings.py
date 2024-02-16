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

def settings_window(parent_window = None):

    def get_data():
        return {
            "settings" : [liste1.get(liste1.curselection()[0]), liste2.get(liste2.curselection()[0])],
            "options" : [{"address" : white_address_entry.get(), "port" : white_port_entry.get()},
                {"address" : black_address_entry.get(), "port" : black_port_entry.get()}],
            "bsd" : liste3.get(liste3.curselection()[0]),
            "bsz" : int(size_set.get()),
            "board" : fen_entry.get(),
            "pieces_style" : pieces_style_list.get(),
            "board_style" : board_style_list.get()
        }

    def save():
        with open("config.json" ,"+w") as file:
            json.dump(get_data(), file)

    def reset():
        load(game.DEFAULT_SETTINGS)

    def load(default = None):
        if default == None:
            default = user_settings()

        liste1.select_clear(0, "end")
        liste1.select_set(liste1.get(0, "end").index(default["settings"][0]))
        liste2.select_clear(0, "end")
        liste2.select_set(liste2.get(0, "end").index(default["settings"][1]))
        liste3.select_clear(0, "end")
        liste3.select_set(liste3.get(0, "end").index(default["bsd"]))

        fen_entry.delete(0, "end")
        fen_entry.insert(0, default["board"])

        white_address_entry.delete(0, "end")
        white_address_entry.insert(0, default["options"][0]["address"])
        white_port_entry.delete(0, "end")
        white_port_entry.insert(0, default["options"][0]["port"])

        black_address_entry.delete(0, "end")
        black_address_entry.insert(0, default["options"][1]["address"])
        black_port_entry.delete(0, "end")
        black_port_entry.insert(0, default["options"][1]["port"])

        pieces_style_list.current(pieces_list.index(default["pieces_style"]))
        board_style_list.current(board_list.index(default["board_style"]))
        size_set.set(default["bsz"])

        refresh()
    
    def create():
        parent_window.board.delete()
        parent_window.__init__(get_data())
        window.destroy()

    #Creation of the tkinter setting window
    size = (600, 190)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(True, True)
    window.iconphoto(True, tk.PhotoImage(file = "asset/pieces/cburnett/bN.png"))
    window.columnconfigure(0, weight=1)

    window.rowconfigure(0, weight = 1)
    window.rowconfigure(1, weight = 1)
    window.rowconfigure(2, weight = 1)
    window.rowconfigure(3, weight = 1)
    window.rowconfigure(4, weight = 1)

    row1 = tk.Frame(window)
    row1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    row1.columnconfigure(0, weight=1)
    row1.columnconfigure(1, weight=1)
    row1.columnconfigure(2, weight=1)
    row1.columnconfigure(3, weight=1)

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
    
    frame3 = tk.LabelFrame(row1, text = "View")
    frame3.grid(row=0, column=2, sticky="nsew")

    liste3 = tk.Listbox(frame3, height = 4, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste3.pack()
    liste3.insert(1, "white")
    liste3.insert(2, "black")

    frame4 = tk.LabelFrame(row1, text = "Settings")
    frame4.grid(row=0, column=3, sticky="nsew")
    frame4.columnconfigure(0, weight=1)
    frame4.columnconfigure(1, weight=1)
    frame4.rowconfigure(0, weight=1)
    frame4.rowconfigure(1, weight=1)

    tk.Button(frame4, text="Save Settings", command = save).grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    tk.Button(frame4, text="Reset Settings", command = reset).grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

    tk.Button(frame4, text="Load Settings", command = load).grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

    tk.Button(frame4, text="Create Board", command = create).grid(row=1, column=1, sticky="nsew", padx=2, pady=2)

    frame5 = tk.Frame(window)
    frame5.grid(row=1, column=0, sticky="nsew", padx=5)
    frame5.columnconfigure(1, weight=1)

    tk.Label(frame5, text = "Fen : ").grid(row=0, column=0, sticky="w")

    fen_entry = tk.Entry(frame5)
    fen_entry.grid(row=0, column=1, sticky="nsew")

    frame6 = tk.LabelFrame(window, text = "White remote player options")
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
            frame6.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
            extend += 55
        else :
            frame6.grid_forget()
        
        if len(liste2.curselection()) != 0 and liste2.get(liste2.curselection()[0]) == "remote player":
            frame7.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
            extend += 55
        else :
            frame7.grid_forget()
        
        window.geometry(f"{size[0]}x{size[1]+extend}")

    refresh()

    frame8 = tk.LabelFrame(window, text = "Style")
    frame8.grid(row=4, column=0, sticky="new", padx=5, pady=5)
    frame8.columnconfigure(0, weight=1)
    frame8.columnconfigure(1, weight=2)
    frame8.columnconfigure(2, weight=1)
    frame8.columnconfigure(3, weight=2)

    tk.Label(frame8, text = "Pieces : ").grid(row=0, column=0, sticky="w")
    
    pieces_list = os.listdir("asset/pieces")
    pieces_style_list = ttk.Combobox(frame8, values=pieces_list, state="readonly")
    pieces_style_list.grid(row=0, column=1, sticky="nsew")

    tk.Label(frame8, text = "Board : ").grid(row=0, column=2, sticky="w")

    board_list = list(map(lambda x: x.split(".")[0], os.listdir("asset/boards")))
    board_style_list = ttk.Combobox(frame8, state="readonly", values=board_list)
    board_style_list.grid(row=0, column=3, sticky="nsew")

    tk.Label(frame8, text = "Board size : ").grid(row=0, column=5, sticky="w")

    size_set = tk.StringVar()
    spinbox = tk.Spinbox(frame8, values = list(range(120, 1320 ,120)), width = 5, textvariable = size_set)
    spinbox.grid(row=0, column=6, sticky="nsew")

    load()
    window.mainloop()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__))+"\\..")
    settings_window()