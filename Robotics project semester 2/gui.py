# The following file contains code written by ROB2 - B223
# 2. Semester AAU 2021.

from tkinter import *
from tkinter import filedialog, StringVar, OptionMenu
from config import CaseConfig

class gui:

    def __init__(self):
        """
        Constructor
        Contains the basic setup of the GUI
        """

        # Creates a window to add widgets to and sets it's size
        self.root = Tk(None, None, "Order selection")
        self.root.geometry("900x400")

        # Allowed options for given variables
        COLOR_OPTIONS = ["black", "white", "blue"]
        BOOL_OPTIONS = ["no", "yes"]
        CURVE_OPTIONS = ["none", "edge", "curved"]

        # Creates variables containing the selection in the GUI
        self.color_top = StringVar(self.root)
        self.color_top.set(COLOR_OPTIONS[0])
        self.color_bottom = StringVar(self.root)
        self.color_bottom.set(COLOR_OPTIONS[0])
        self.engraving_bool = StringVar(self.root)
        self.engraving_bool.set(BOOL_OPTIONS[0])
        self.curve_type = StringVar(self.root)
        self.curve_type.set(CURVE_OPTIONS[0])
        self.text_frame = Frame(self.root, height=60)
        self.text_frame.pack()
        self.button_frame = Frame(self.root)
        self.button_frame.pack()
        self.info_frame = Frame(self.root)
        self.info_frame.pack()
        self.close_frame = Frame(self.root)
        self.close_frame.pack(side=BOTTOM)

        # Introtext variable
        INTROTEXT = Label(self.text_frame, text="Hello and Welcome to Smart lab Inc! \n The following options are available for your order:", font='Helvetica 16')
        INTROTEXT.grid(row=1, column=4)

        # Header for Cover variables
        header1_label = Label(self.button_frame, text="Cover", font='Helvetica 14 bold')
        header1_label.grid(row=2, column=4)

        # Dropdown menus for variables related to the cover with descriptive labels
        self.top_color = Label(self.button_frame, text="Top cover color:", font=40)
        self.top_color.grid(row=3, column=2)
        color_top_drop = OptionMenu(self.button_frame, self.color_top, *COLOR_OPTIONS)
        color_top_drop.grid(row=3, column=3)
        self.bottom_color = Label(self.button_frame, text="Bottom cover color:", font=40)
        self.bottom_color.grid(row=3, column=4)
        color_bottom_drop = OptionMenu(self.button_frame, self.color_bottom, *COLOR_OPTIONS)
        color_bottom_drop.grid(row=3, column=5)
        self.curve_label = Label(self.button_frame, text="Curvature type:", font=40)
        self.curve_label.grid(row=5, column=2)
        curve_selection_drop = OptionMenu(self.button_frame, self.curve_type, *CURVE_OPTIONS)
        curve_selection_drop.grid(row=5, column=3)

        # Header for engraving variables
        header2_label = Label(self.button_frame, text="Engraving", font='Helvetica 14 bold')
        header2_label.grid(row=6, column=4)

        # Dropdown menu and filepath menu for variables related to engraving
        self.engraving_label = Label(self.button_frame, text="Do you want it engraved?", font=40)
        self.engraving_label.grid(row=7, column=2)
        engraving_selection = OptionMenu(self.button_frame, self.engraving_bool, *BOOL_OPTIONS)
        engraving_selection.grid(row=7, column=3)
        self.ent1 = Entry(self.button_frame, font=40)
        self.ent1.grid(row=7, column=6)
        b1_label = Label(self.button_frame, text="file*:", font=40)
        b1_label.grid(row=7, column=4)
        b1 = Button(self.button_frame, text="Browse for file", font=40, command=self.browsefunc)
        b1.grid(row=7, column=5)

        # Info label with information regarding the svg file used
        info_label = Label(self.info_frame, text="\n*: File must be an svg and: \n - Must be cropped to content \n - Must be in black and white contrast", font=40)
        info_label.pack(side=LEFT)
        # info_label.grid(row=9, column=1)

        # Order buttom to assign variables in the .ini file and close the window
        b2 = Button(self.close_frame, text="Order", font=40, command=self.ok)
        b2.grid(row=1, column=4)

        # Main loop for window
        self.root.mainloop()

    def browsefunc(self):
        """
        Creates the filedialog window and allows user to pick a file in their system
        :return: Assigns the value given by filedialog to the variable containing the selection
        """
        filename = filedialog.askopenfilename(filetypes=(("svg files", "*.svg"), ("All files", "*.*")))
        self.ent1.delete(0, END)
        self.ent1.insert(END, filename)

    def ok(self):
        """
        Sends the variables to the configParser and closes the window
        :return: Sends variables to ConfigParser
        """
        CaseConfig.set_var('colour', self.color_top.get())
        CaseConfig.set_var('bottom', self.color_bottom.get())
        CaseConfig.set_var('engrave', self.engraving_bool.get())
        CaseConfig.set_var('file', self.ent1.get())
        CaseConfig.set_var('curve_style', self.curve_type.get())
        self.root.destroy()









