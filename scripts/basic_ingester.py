#!/usr/bin/env python3

"""Basic ingester

Usage:
  basic_ingester.py (-c | --config) <config_paths>...
  basic_ingester.py (-p | --progress) (-c | --config) <config_paths>...
  basic_ingester.py (-v | --verbose) (-c | --config) <config_paths>...
  basic_ingester.py (-h | --help)
  basic_ingester.py (-V |--version)

Options:
  -c --config    Paths to config files (separated by spaces or wildcard)
  -p --progress  Show progress
  -v --verbose   Verbose mode (show conversion details)
  -h --help      Show this screen.
  -V --version   Show version.

Return codes:
0 : successful conversion
1 : config file not found or parsing failed
2 : error during conversion
"""

version = "0.3alpha"

import sys, os
from docopt import docopt
import yaml

from readers import *
from writers import *
from converter import converter

arguments = docopt(__doc__, version=version)
progress = arguments['--progress']
verbose = arguments['--verbose']

c = 1; n_conf = len(arguments['<config_paths>'])
for config_path in arguments['<config_paths>']:
    print("["+str(c)+"/"+str(n_conf)+"] Processing config file "+config_path+"...")
    c += 1

    # Open and parse config file
    # Warning: It is not safe to call yaml.load with any data received from an untrusted source!
    try:
        config_file = open(config_path, 'rt')
        config = yaml.load(config_file)
        config_file.close()
    except Exception as e:
        print(e)
        print("Can't parse YAML file.")
        sys.exit(1)

    # Store config of converters in a nice format (searchable by inputName...)
    config_converters = {}
    for definition in config['converters']:
        config_converters[definition['inputName']] = definition


    # Parse input and open reader
    config_input = config['input']
    if config_input['scheme'] == 'local':
        filepath = config_input['local']['path']
        extension = os.path.splitext(filepath)[1]

        if extension == '.csv':
            try:
                source = CSVReader(filepath, config_converters, csv_delimiter=',') # TODO : add csv_delimiter in config file
            except Exception as e:
                print(e)
                print("Failed to parse CSV source file.")
                sys.exit(2)

        elif extension == '.json':
            try:
                source = JSONReader(filepath, config_converters)
            except Exception as e:
                print(e)
                print("Failed to parse JSON source file.")
                sys.exit(2)

        else:
            print("Unknown extension for input file.")
            sys.exit(2)

    elif config_input['scheme'] == 'hdfs':
        print("HDFS backend not yet implemented")
        sys.exit(2)

    else:
        print("Unknown input scheme: "+config_input['scheme'])
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

    elif config_output['scheme'] == 'elasticsearch':
        print("elasticsearch backend is EXPERIMENTAL. Use with caution !")
        es_config = config_output['elasticsearch']
        destination = ESWriter(host=es_config['host'], port=es_config['port'], index=es_config['index'])

    elif config_output['scheme'] == 'hdfs':
        print("HDFS backend not yet implemented")
        sys.exit(2)

    else:
        print("Unknown output scheme: "+config_output['scheme'])
        sys.exit(2)


    # Loop on data
    i = 0
    for data in source.data():
        # data is a dictionary: {inputName: value, ...}

        # Convert and write data
        destination.write(converter(data, config_converters, debug=verbose))

        # Print progress
        if progress:
            print(i, end='\r')
        i += 1

    # Exiting properly
    source.close()
    destination.close()
    print("Done: "+str(i)+" lines processed with success.")

print(str(n_conf)+" config files processed with success.")
sys.exit(0)
