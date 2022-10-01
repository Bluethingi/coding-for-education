# The following file contains code made by ROB2 - B223
# 2. Semester AAU 2021.

import json
import os
from robolink import *


class Statistics:
    # Global variables
    STATISTICS_FILE = 'statistics.json'
    FIELDS = ['type', 'created']
    INITIAL_VALUE = 0
    TYPES = ['black_none', 'black_none_engraved', 'black_edge', 'black_edge_engraved', 'black_curved',
             'black_curved_engraved', 'white_none', 'white_none_engraved', 'white_edge', 'white_edge_engraved',
             'white_curved', 'white_curved_engraved', 'blue_none', 'blue_none_engraved', 'blue_edge',
             'blue_edge_engraved', 'blue_curved', 'blue_curved_engraved', 'average_production_time',
             'average_engraving_time', 'average_total_time']
    RDK = Robolink()

    def __init__(self):
        """
        Constructor:
        Checks if file exits, if not then creates it.
        """
        if not os.path.isfile(self.STATISTICS_FILE):
            self.__create_statistics()

    def __str__(self):
        """
        String method:
        Prints a string containing relevant information about the object itself
        """
        statistics_ = self.__get_statistics()
        statistics_ = str(statistics_)
        statistics_ = str(statistics_).replace(', ', '\n').replace('{', '').replace('}', '').replace('\'', '').replace(
            'curved', 'curved covers').replace('_', ' ').replace('none', 'flat covers').replace(
            'edge', 'curved edges covers').replace('covers:', 'covers produced:').replace(
            'average production', '\n\naverage production').replace('time', 'time*')
        statistics_ = str('Current production statistics:\n' + statistics_ + '\n*All times in seconds')
        self.RDK.ShowMessage(statistics_)

    def __create_statistics(self):
        """
        Creates a json file and prints the initial values into it
        """
        statistics = {type_: self.INITIAL_VALUE for type_ in self.TYPES}

        with open(self.STATISTICS_FILE, 'w') as f:
            f.write(json.dumps(statistics, indent=4))

    def __get_statistics(self):
        """
        Opens and reads the current stock from the statistics file
        :return: Returns the contents of the statistics file
        """
        with open(self.STATISTICS_FILE, 'r') as f:
            return json.loads(f.read())

    def __update_statistics(self, stat: json):
        """
        Prints the given statistics to the file
        :param stat: object with type hint json
        """
        with open(self.STATISTICS_FILE, 'w') as f:
            f.write(json.dumps(stat, indent=4))

    def get(self, stat_: str):
        """
        Accesses the file and reads the current statistics of a specific type
        :param stat_: the type to get the value from
        :return: The value contained in the type "stat_"
        """
        statistics_ = self.__get_statistics()
        return statistics_[stat_]

    def add(self, stat_: str, count: int):
        """
        Updates the statistics with the given count
        :param stat_: the type that has to be added to
        :param count: The amount to be added
        """
        statistics_ = self.__get_statistics()
        statistics_[stat_] += count
        self.__update_statistics(statistics_)

    def set(self, stat_: str, amount: float):
        """
        Sets the given statistic to the given amount
        :param stat_: the type that has to be changed
        :param amount: The amount to set it to
        """
        statistics_ = self.__get_statistics()
        statistics_[stat_] = amount
        self.__update_statistics(statistics_)
