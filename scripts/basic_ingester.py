#!/usr/bin/env python3

"""Basic ingester

Usage:
  basic_ingester.py (-c | --config) <config_path>
  basic_ingester.py (-h | --help)
  basic_ingester.py --version

Options:
  -c --config   Path to config file
  -h --help     Show this screen.
  --version     Show version.

Return codes:
0 : successful conversion
1 : config file not found or parsing failed
2 : error during conversion
"""

import sys, os
from docopt import docopt
import yaml

from files_io import *

arguments = docopt(__doc__, version="0.1alpha")

# Open and parse config file
# Warning: It is not safe to call yaml.load with any data received from an untrusted source!
try:
    config_file = open(arguments['<config_path>'], 'rt')
    config = yaml.load(config_file)
except Exception as e:
    print(e)
    sys.exit(1)

print(config) # dev

# Parse input
config_input = config['input']
if config_input['scheme'] == 'local':
    filepath = config_input['local']['path']
    extension = os.path.splitext(filepath)[1]

    if extension == '.csv':
        try:
            # Dictionary reverse search : get column name of timestamp (e.g. "Time of Observsation")
            timestamp_column_name = {v: k for k, v in config['Converter'].items()}['timestamp']
            source = CSVReader(filepath, timestamp_column_name)
        except Exception as e:
            print(e)
            print("Failed to open CSV source file.")
            sys.exit(2)

    elif extension == '.json':
        try:
            source = JSONReader(filepath)
        except Exception as e:
            print(e)
            print("Failed to open JSON source file.")
            sys.exit(2)

    else:
        print("Unknown extension for input file.")
        sys.exit(2)
else:
    print("HDFS backend not yet implemented")
    sys.exit(2)

# Parse output
config_output = config['output']
if config_output['scheme'] == 'local':
    filepath = config_output['local']['path']
    try:
        destination = JSONWriter(filepath)
    except Exception as e:
        print(e)
        print("Failed to open JSON output file.")
        sys.exit(2)
else:
    print("HDFS backend not yet implemented")
    sys.exit(2)

# Loop on values
i = 0; n = source.size
for timestamp in source.AvailableTimestamp():
    i += 1; print('['+str(i)+'/'+str(n)+'] '+timestamp)
    destination.addTimestramp(timestamp)


    for ValueName in source.AvailableValueName():
        # type conversion will be done here
        # all type are str for now, remove spaces.
        value = source.GetValue(timestamp, ValueName).strip()

        try:
            ConverterValueName = config['Converter'][ValueName]
        except KeyError:
            # ValueName does not exist in config file, skip it
            continue

        destination.addValue(timestamp, ConverterValueName, value)
        print(ValueName+' imported to '+ConverterValueName)


# Exiting properly
destination.close()
sys.exit(0)
