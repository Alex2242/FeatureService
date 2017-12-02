#!/usr/bin/env python3

"""
Checker and converter

Version : 0.3alpha
"""

import sys


# Better way to do that ?
def strToType(str_type):
    if str_type == "str":
        return type("a")
    elif str_type == "int":
        return type(0)
    elif str_type == "float":
        return type(0.0)
    elif str_type == "list":
        return type([])
    elif str_type == "None":
        return type(None)
    else:
        return None


def typeConverter(value, config):

    # Suppress spaces (FIXME: if value is "human" text, we should not supress spaces... New type ?)
    if isinstance(value, str):
        value = value.strip()

    if len(value) == 0:
        if "defaultValue" in config:
            value = config['defaultValue'] # str
            if value == "None":
                return None
            else:
                return value
        else:
            raise Exception # FIXME: Better way to do that

    output_type_str = config['outputType']
    if output_type_str == "str":
        return str(value)
    elif output_type_str == "int":
        return int(value)
    elif output_type_str == "float":
        return float(value)
    elif output_type_str == "None" or value == "None":
        return None
    else:
        return value


def converter(data, config_converters, debug=False):

    converted_data = {}
    for inputName in data.keys():
        outputName = config_converters[inputName]['outputName']

        # Check input type
        if type(data[inputName]) != strToType(config_converters[inputName]['inputType']):
            print("Type mismatch for input, exiting...")
            print("Expected type: "+config_converters[inputName]['inputType'])
            print("Data type: "+str(type(data[inputName])))
            print(data)
            sys.exit(2)

        # Convert value
        try: # FIXME: Better way than try/except ?
            converted_data[outputName] = typeConverter(data[inputName], config_converters[inputName])
        except Exception:
            print("Error during conversion.")
            print("Value "+inputName+" is empty and no default value was specified, exiting...")
            print(data)
            sys.exit(2)

        if debug:
            print(inputName+' imported to '+outputName+' ('+config_converters[inputName]['inputType']+' --> '+config_converters[inputName]['outputType']+')')

    if debug:
        print('---')

    return converted_data
