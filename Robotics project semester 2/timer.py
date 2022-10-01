from datetime import datetime, timedelta
from statistics import Statistics

# Class for adding times to the statistics

class Timer:

    # Types of covers
    COVER_TYPES = ['black_none', 'black_edge', 'black_curved', 'white_none', 'white_edge', 'white_curved', 'blue_none',
                   'blue_edge', 'blue_curved']

    def __init__(self):
        """
        Constructor
        Initializes the statistics object
        """
        self.stat = Statistics()

    def end(self, type_, start_):
        """
        Adds the time to the average of the type_ given
        :param type_: The type of time variable
        :param start_: The starting time object
        :return:
        """

        # Get the amount of seconds from datetime
        end = datetime.now()
        diff = end - start_
        diff = diff.total_seconds()

        # Set the time average variable to 0
        self.time_avg = 0

        if type_ == 'average_production_time':

            # Take in the full amount of covers produced
            for types in self.COVER_TYPES:
                self.time_avg =+ self.stat.get(types)

            # Set the value in statistics
            self.stat.set(type_, self.addtoaverage(self.time_avg, self.stat.get(type_), diff))

            # Reset the time average variable
            self.time_avg = 0
        if type_ == 'average_engraving_time':

            # Take in the full amount of covers engraved
            for types in self.COVER_TYPES:
                self.time_avg =+ self.stat.get(f'{types}_engraved')

            # Set the value in statistics
            self.stat.set(type_, self.addtoaverage(self.time_avg, self.stat.get(type_), diff))

            # Reset the time average variable
            self.time_avg = 0
        if type_ == 'average_total_time':

            # Take in the full amount of covers produced
            for types in self.COVER_TYPES:
                self.time_avg =+ self.stat.get(types)

            # Set the value in statistics
            self.stat.set(type_, self.addtoaverage(self.time_avg, self.stat.get(type_), diff))

            # Reset the time average variable
            self.time_avg = 0

            # Print the time taken for the entire operation to the operator
            print(f'The operation took {diff} seconds')

    def addtoaverage(self, average, size, value):
        """
        Method to add a new time to an average
        :param average: The existing average
        :param size: The new amount of covers produced
        :param value: The new value to add
        :return: The new average of all the operations
        """
        # Due to the size being calculated before the call of this function, we
        # have to subtract one from the size initially
        # Adds an element to the average
        return (size-1 * average + value) / (size)

