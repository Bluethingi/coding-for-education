# The following file contains code made by ROB2 - B223
# 2. Semester AAU 2021.

from robolink.robolink import Robolink

from config import CaseConfig
from cover import Cover
from engrave import Engrave
from stock import Stock
from gui import gui
from timer import Timer
from datetime import datetime

# Main function for the handling of new covers in the Smart lab project
# This begins by calling the gui class for customer product selection and ordering
# Then checks the remaining stock, if there is still covers left, runs the cover
# retrieval and application and then checks whether the customer selected and engraving
# If the customer has selected engraving, it will start an engraving process based
# upon the chosen type and colour of the cover and then retrieves it.


gui()
RDK = Robolink()
RDK.setSimulationSpeed(1)
stock = Stock()  # For simulating stock
time = Timer()
start = datetime.now() # For timing simulation
#Creates a new cover object, and checks whether a cover previously used is existant, if it is it deletes it
cover = Cover(CaseConfig.colour(), CaseConfig.curve_style(), stock)
cover.new_cover_check()

# If the stock is empty tell the system
if stock.get(f'{CaseConfig.colour()}_{CaseConfig.curve_style()}') == 0:
    none_flat_str = CaseConfig.curve_style().replace('none', 'flat', -1)
    error_str = f'Stock depleted of {CaseConfig.colour()} {none_flat_str} covers'
    RDK.RunMessage(error_str)
# Else run the program
else:
    cover.give_top(time)
    if CaseConfig.engrave():
        pattern = Engrave(RDK)
        if CaseConfig.curve_style() == 'none':
            pattern.begin_flat(time)
        if CaseConfig.curve_style() == 'edge':
            pattern.begin_edge(time)
        if CaseConfig.curve_style() == 'curved':
            pattern.begin_curved(time)
        cover.retrieve()
    # End the timer and add it to the total average time
    time.end('average_total_time', start)
