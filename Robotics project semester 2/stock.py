# The following file contains code made by ROB2 - B223
# 2. Semester AAU 2021.

import json
import os


class Stock:
    # Global variables
    STOCK_FILE = 'stock.json'
    FIELDS = ['type', 'stock']
    INITIAL_STOCK = 10
    TYPES = ['black_none', 'black_edge', 'black_curved', 'white_none', 'white_edge', 'white_curved', 'blue_none',
             'blue_edge', 'blue_curved']

    def __init__(self):
        """
        Constructor
        Checks if a stock file exists, if not creates one
        """
        if not os.path.isfile(self.STOCK_FILE):
            self.__create_stock()

    def __create_stock(self):
        """
        Creates json file and prints the initial stock values into it
        """
        stock = {type_: self.INITIAL_STOCK for type_ in self.TYPES}

        with open(self.STOCK_FILE, 'w') as f:
            f.write(json.dumps(stock, indent=4))

    def __get_stock(self):
        """
        Opens and reads the current stock from the stock file
        :return: Returns the contents of the stock file
        """
        with open(self.STOCK_FILE, 'r') as f:
            return json.loads(f.read())

    def __update_stock(self, stock: json):
        """
        Prints the given stock to the file
        :param stock: object with type hint json
        """
        with open(self.STOCK_FILE, 'w') as f:
            f.write(json.dumps(stock, indent=4))

    def get(self, type_: str):
        """
        Accesses the file and reads the current stock of a specific type
        :param type_: The type of cover called for
        :return: the value of the given type
        """

        stock_ = self.__get_stock()
        return stock_[type_]

    def set(self, type_: str, count: int):
        """
        Updates the stock of a given type with a given count
        :param type_: Type of cover
        :param count: The amount that is left
        """
        stock_ = self.__get_stock()
        stock_[type_] = count
        self.__update_stock(stock_)

    def add(self, type_: str, count: int):
        """
        Updates the stock of a given type with a given count
        :param type_: Type of cover
        :param count: The amount that is left
        """
        stock_ = self.__get_stock()
        stock_[type_] += count
        self.__update_stock(stock_)

    def sub(self, type_: str, count: int):
        """
        Updates the stock of a given type with a given count
        :param type_: Type of cover
        :param count: The amount that is left
        """
        stock_ = self.__get_stock()
        stock_[type_] -= count
        self.__update_stock(stock_)

    @classmethod
    def get_init(cls):
        """
        Access to the initial stock count
        :return: The initial value for all covers
        """
        return cls.INITIAL_STOCK
