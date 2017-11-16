#!/usr/bin/env python3

"""
CSV and JSON readers and writers

Version : 0.1alpha
"""

import sys
import csv, json

class CSVReader():

    def __init__(self, filepath, timestamp_column_name):

        csv_fd = open(filepath, newline='')
        csv_reader = csv.reader(csv_fd, delimiter=',')

        # Get header
        self.__csv_header = next(csv_reader) # List

        # Get index of timestamp column
        try:
            self.__indexOfTimestamp = self.__csv_header.index(timestamp_column_name)
        except ValueError:
            print("No "+timestamp_column_name+" column found in CSV source file.")
            sys.exit(2)

        # Store values in array
        # Not efficient, basic processing for now
        self.__csv_data = []
        for row in csv_reader:
            self.__csv_data.append(row)

        # Close fd
        csv_fd.close()

    #####
    # CSV specific getters
    #####
    @property
    def header(self):
        return self.__csv_header

    @property
    def data(self):
        return self.__csv_data

    @property
    def size(self):
        return len(self.__csv_data)

    @property
    def line(self, i):
        return self.__csv_data[i]

    #####
    # generic getters
    #####

    def AvailableValueName(self):
        return self.__csv_header

    def AvailableTimestamp(self):
        return [line[self.__indexOfTimestamp] for line in self.__csv_data]

    def GetValue(self, timestamp, value_name):
        for line in self.__csv_data: # weak performance
            if line[self.__indexOfTimestamp] == timestamp:
                return line[self.__csv_header.index(value_name)]



class JSONWriter():

    def __init__(self, filepath):

        self.__json_fd = open(filepath, 'w')

        # List to store data (in dictionary, one per timestamp) before writing
        self.__data = []

        # Dictionary to store index (in self.__data) of timestamp
        self.__indexes = {}


    def close(self):
        # Write data to file and close
        for timestamp in self.__data:
            json.dump(timestamp, self.__json_fd, indent=4)
            self.__json_fd.write("\n") # nice file format
        self.__json_fd.close()


    #####
    # generic getters
    #####

    def addTimestramp(self, timestamp):
        if timestamp in self.__indexes:
            print(timestamp+" already exist, don't use addTimestramp() twice...")
            return

        self.__data.append({
        "latitude": None,
        "longitude": None,
        "timestamp": timestamp,
        "wind_speed": None,
        "wind_direction": None,
        "sea_surface_temperature": None
        })

        # Store index
        self.__indexes[timestamp] = len(self.__data) - 1

    def addValue(self, timestamp, value_name, value):
        self.__data[self.__indexes[timestamp]][value_name] = value
