#!/usr/bin/env python3

"""
CSV and JSON writers

Version : 0.3alpha
"""

import sys
import csv, json

class JSONWriter():

    def __init__(self, filepath):
        # Error handling is done in basic_ingester.py
        self.__json_fd = open(filepath, 'w')

    def close(self):
        self.__json_fd.close()

    def write(self, data):
        # data is dictionary
        json.dump(data, self.__json_fd, indent=4)
        self.__json_fd.write("\n") # nice file format


class ESWriter():

    def __init__(self, host, port, index):

        if 'elasticsearch' not in sys.modules: # Prevent loading module multiple times...
            # Import ES module only if ESWriter is used (it is not a std module...)
            try:
                from elasticsearch import Elasticsearch
            except ImportError:
                print("Elasticsearch module for python is not installed.")
                print("It is required to use elasticsearch output.")
                print("Try: pip3 install elasticsearch")
                sys.exit(2)

        # Create ES objet
        self.__es = Elasticsearch([
                                  {'host': host, 'port': port}
                                  ])
        self.__es_index = index

        if not self.__es.ping():
            print("Elasticsearch is not reachable, exiting...")
            print("Check host and port.")
            sys.exit(2)

    def write(self, data):
        try:
            self.__es.index(index=self.__es_index, doc_type="ebdo_data", body=data)
        except Exception as e:
            # Don't hard fail for dev use
            print("Error while importing data to ES...")
            print(data)

    def close(self):
        # No explicit way to close ES socket (AFAIK)
        pass
