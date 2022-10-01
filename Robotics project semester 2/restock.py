# The following file contains code made by ROB2 - B223
# 2. Semester AAU 2021.


from stock import Stock

"""
Restock script:
Refills the entire stock after hard reset
"""
# All the types of covers
TYPES = ['black_none', 'black_edge', 'black_curved', 'white_none', 'white_edge', 'white_curved', 'blue_none',
         'blue_edge', 'blue_curved']

# Initialize the stock object to access the stock
stock = Stock()

# For each type reset the stock to initial values
for type_cover in TYPES:
    stock.set(type_cover, stock.get_init())
