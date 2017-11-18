#!/usr/bin/env python3

"""
CSV and JSON readers and writers

Version : 0.2alpha
"""

import sys
import csv, json

class CSVReader():

    def __init__(self, filepath, timestamp_column_name):

        # Error handling is done in basic_ingester.py
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

        # Store values in array and index of this array in dictionary
        # Not efficient, basic processing for now
        self.__csv_data = []
        self.__indexes = {}
        i = 0
        for row in csv_reader:
            if row[self.__indexOfTimestamp] not in self.__indexes:
                self.__csv_data.append(row)
                self.__indexes[row[self.__indexOfTimestamp]] = i
                i += 1
            else:
                # FIXME : What should we do ?
                print("Warning: timestamp "+row[self.__indexOfTimestamp]+" appears several times in the CSV input file.")
                print("Only data in first timestamp will be considered.")

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
    def line(self, i):
        return self.__csv_data[i]

    #####
    # generic getters
    #####

    @property
    def size(self):
        return len(self.__csv_data)

    def AvailableValueName(self):
        return self.__csv_header

    def AvailableTimestamp(self):
        # Not ordered, it's an issue ?
        return [key for key, elem in self.__indexes.items()]

    def GetValue(self, timestamp, value_name):
        return self.__csv_data[self.__indexes[timestamp]][self.__csv_header.index(value_name)]


class JSONReader():

    def __init__(self, filepath, timestamp_name):

        # Error handling is done in basic_ingester.py
        json_fd = open(filepath)

        # json_data is list of dictionaries
        self.__json_data = json.load(json_fd)

        # Index timestamp and AvailableValueName
        self.__indexes = {}

        self.__AvailableValueName = []
        # Fill self.__AvailableValueName with first element of the list
        # All elements should have same AvailableValueName or json file is declared incoherent.
        for key, elem in self.__json_data[0].items():
                self.__AvailableValueName.append(key)

        for i in range(len(self.__json_data)):
            # timestamp
            self.__indexes[self.__json_data[i][timestamp_name]] = i

            # Check that all elements have same AvailableValueName
            k = 0
            for key, elem in self.__json_data[i].items():
                if key != self.__AvailableValueName[k]:
                    print("JSON input file is incoherent (all elements don't have identical list of ValueName)")
                    sys.exit(2)
                k += 1

        # Close fd
        json_fd.close()

    #####
    # generic getters
    #####

    @property
    def size(self):
        return len(self.__json_data)

    def AvailableValueName(self):
        return self.__AvailableValueName

    def AvailableTimestamp(self):
        return [key for key, elem in self.__indexes.items()]

    def GetValue(self, timestamp, value_name):
        try:
            return self.__json_data[self.__indexes[timestamp]][value_name]
        except KeyError as e:
            print(e)
            print("timestamp or value_name does not exist")
            print("timestamp = "+timestamp+", value_name = "+value_name)
            sys.exit(2) # Hard fail for debugging


class JSONWriter():

    def __init__(self, filepath):

        # Error handling is done in basic_ingester.py
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
    # generic setters
    #####

    def addTimestramp(self, timestamp):
        if timestamp in self.__indexes:
            print(timestamp+" already exist, don't use addTimestramp() twice...")
            return

        # Template of document in ES
        # Some fields name may be added by addValue()
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
        # If value_name does not exist, it will be created
        self.__data[self.__indexes[timestamp]][value_name] = value
