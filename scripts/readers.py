#!/usr/bin/env python3

"""
CSV and JSON readers

Version : 0.3alpha
"""

import sys
import csv, json

class CSVReader():
    """
    This reader is iterable.

    Parameters:
        - filepath : path to csv file
        - config_converters: dictionary where keys are column names specified in config file
        - delimiter : csv delimiter (optional)

    Return:
        data():
            - an iterable object,
              each iteration returns a dictionary {valueName: value, ...}
        close():
            - Close fd

    """

    def __init__(self, filepath, config_converters, csv_delimiter=','):

        # Open fd
        try:
            self.__csv_fd = open(filepath, mode='rt', newline='')
        except Exception as e:
            print(e)
            print("Failed to open CSV source file.")
            sys.exit(2)

        # Open csv reader
        self.__csv_reader = csv.reader(self.__csv_fd, delimiter=csv_delimiter)

        # Get header (only used in __init__)
        csv_header = next(self.__csv_reader) # List

        # Find indexes of useful columns (column name are keys of config_converters)
        self.__columns_indexes = {}
        for inputName in config_converters.keys():
            if inputName in csv_header:
                self.__columns_indexes[inputName] = csv_header.index(inputName)
            else:
                print(inputName+" was set in config file but was not found in CSV file header, exiting...")
                sys.exit(2)

    def data(self):
        for row in self.__csv_reader:
            values = {}
            for inputName in self.__columns_indexes.keys():
                values[inputName] = row[self.__columns_indexes[inputName]]
            yield values

    def close(self):
        self.__csv_fd.close()


class JSONReader():
    """
    This reader is iterable.

    Parameters:
        - filepath : path to json file
        - config_converters: dictionary where keys are column names configured in config file

    Return:
        data():
            - an iterable object,
              each iteration returns a dictionary {valueName: value, ...}
        close():
            - Close fd

    """

    def __init__(self, filepath, config_converters):

        # Open fd
        try:
            self.__json_fd = open(filepath, mode='rt')
        except Exception as e:
            print(e)
            print("Failed to open JSON source file.")
            sys.exit(2)

        # Store config_converters (it will be used in data() to return only valueNames specified in config file)
        self.__config_converters = config_converters

    def data(self):
        for line in self.__json_fd:

            try:
                json_reader = json.loads(line)
            except Exception as e:
                print(e)
                print("Failed to parse JSON source file.")
                sys.exit(2)

            values = {}
            for inputName in self.__config_converters.keys():
                try:
                    values[inputName] = json_reader[inputName]
                except KeyError as e:
                    print(inputName+" was set in config file but was not found in JSON input file, exiting...")
                    sys.exit(2)

            yield values

    def close(self):
        self.__json_fd.close()
