# The following file contains code made by ROB2 - B223
# 2. Semester AAU 2021.

import os
from configparser import ConfigParser


class CaseConfig:
    # Global variables
    # Set allowed values for covers
    _ALLOWED_COLOURS = ['white', 'blue', 'black']
    _ALLOWED_CURVES = ['none', 'edge', 'curved']

    @classmethod
    def __open_config(cls) -> ConfigParser:
        """
        Accesses the config file and creates a ConfigParser object to read the file
        :return: The ConfigParser object
        """
        cfg = ConfigParser()
        cfg.read('config.ini')
        return cfg

    @classmethod
    def colour(cls, type_='customer'):
        """
        Static class method
        Checks the value at 'colour' from the config file
        :param type_: string default 'customer' can be 'default'
        :return: string contained in key 'colour'
        """
        colour_id = cls.__open_config().get(type_, 'colour')

        # if we decide to use hex strings instead of colour names, use re to ensure it is valid
        # import re
        #
        # if not re.match('[a-fA-F0-9]', colour_id'):
        #     raise KeyError('Error, colour code not valid.')
        #
        # and append the # when returning
        # return f'#{colour_id}'

        if colour_id not in cls._ALLOWED_COLOURS:
            raise KeyError('Error, colour is not available.')

        # ... other error handling, validation, or mutation

        return colour_id

    @classmethod
    def curve_style(cls, type_='customer'):
        """
        Static class method
        Checks the value at 'curve_style' from the config file
        :param type_: string default 'customer' can be 'default'
        :return: string contained in key 'curve_style'
        """
        curve_style_id = cls.__open_config().get(type_, 'curve_style')

        if curve_style_id not in cls._ALLOWED_CURVES:
            raise KeyError('Error, curve style is not available.')

        # ... other error handling, validation, or mutation

        return curve_style_id

    @classmethod
    def file(cls, type_='customer'):
        """
        Static class method
        Checks the value at 'file' from the config file
        :param type_: string default 'customer' can be 'default'
        :return: string contained in key 'file'
        """
        file_path = cls.__open_config().get(type_, 'file')

        if not os.path.isfile(file_path) and not file_path == '':
            raise FileNotFoundError('Error, file does not exist.')

        # ... other error handling, validation, or mutation

        return file_path

    @classmethod
    def engrave(cls, type_='customer'):
        """
        Static class method
        Checks the value 'engrave' from the config file
        :param type_: string default 'customer' can be 'default'
        :return: boolean value in key 'engrave'
        """
        engrave_bool = cls.__open_config().getboolean(type_, 'engrave')

        if type(engrave_bool) != bool:
            raise KeyError('Error, not a boolean type')

        return engrave_bool

    @classmethod
    def bottom_colour(cls, type_='customer'):
        """
        Static class method
        Checks the value at 'bottom' from the config file
        :param type_: string default 'customer' can be 'default'
        :return: string contained in key 'bottom'
        """
        bottom_colour_id = cls.__open_config().get(type_, 'bottom')

        # if we decide to use hex strings instead of colour names, use re to ensure it is valid
        # import re
        #
        # if not re.match('[a-fA-F0-9]', colour_id'):
        #     raise KeyError('Error, colour code not valid.')
        #
        # and append the # when returning
        # return f'#{colour_id}'

        if bottom_colour_id not in cls._ALLOWED_COLOURS:
            raise KeyError('Error, colour is not available.')

        # ... other error handling, validation, or mutation

        return bottom_colour_id

    @classmethod
    def set_var(cls, key_, value, type_='customer'):
        """
        Static class method
        Sets the value of the given key in the header(type) to the given parameter "value"
        :param key_: The key to set
        :param value: The value to give the key
        :param type_: The type, default set to customer
        :return: A rewritten config file
        """
        if key_ == 'file':
            if not os.path.isfile(value) and value != '':
                raise FileNotFoundError('Error, file does not exist')
        config = cls.__open_config()
        config.set(type_, key_, value)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

