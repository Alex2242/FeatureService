#!/usr/bin/env python3

import sys, os
import csv, json

"""

SUMMARY
This script converts weather data from csv file to json formatted data to be imported in Elasticsearch.


USAGE
./weather_csv_to_ES.py {csv_file} [{json_file}]

{json_file} is optional, if no is given, json data will be printed to stdout


EXIT STATUS
0 : successful conversion
1 : no argument or too many arguments
2 : csv file does not exist

"""

def usage():
	print("Usage: "+sys.argv[0]+" {csv_file} [{json_file}]")
	print("See script header for more information.")

if len(sys.argv) < 2:	# sys.argv[0] is script name
	print("At least 1 argument must be provided, exiting...")
	usage()
	sys.exit(1)

if not os.path.isfile(sys.argv[1]):
	print(sys.argv[1]+" does not exist, exiting...")
	usage()
	sys.exit(2)

if len(sys.argv) == 2:
	# print data to stdout (only data, no warning)
	stdout = True

elif len(sys.argv) == 3:
	stdout = False

	# Open json fd
	if os.path.isfile(sys.argv[2]):
		print("Warning: "+sys.argv[2]+" will be overwritten.")
	else:
		print("json will be stored to "+sys.argv[2])

	json_file = sys.argv[2]
	json_fd = open(json_file, 'w')
else:
	print("Too many arguments, exiting...")
	usage()
	sys.exit(1)

# Open csv file
csv_file = open(sys.argv[1], newline='')
csv_reader = csv.reader(csv_file, delimiter=',')

# Parse header
csv_header = next(csv_reader)
index_latitude = csv_header.index("Latitude")
index_longitude = csv_header.index("Longitude")
index_timestamps = csv_header.index("Time of Observation")
index_sea_surface_T = csv_header.index("Sea Surface Temperature")
index_wind_direction = csv_header.index("Wind Direction")
index_wind_speed = csv_header.index("Wind Speed")
# TODO : parse all values, specify units

# Reading csv
if not stdout:
	print("Processing...")

i = 0
for row in csv_reader:

	# To be determined
	# What action should be taken if some values are empty ? (eg. sea_surface_T)

	# Get values and convert to float
	latitude = float(row[index_latitude])
	longitude = float(row[index_longitude])

	try: # sea_surface_T could be empty...
		sea_surface_T = float(row[index_sea_surface_T])
	except:
		sea_surface_T = ""

	# FIXME : int or float ?
	try:
		wind_direction = int(row[index_wind_direction])
	except:
		wind_direction = ""
	try:
		wind_speed = int(row[index_wind_speed])
	except:
		wind_speed = ""

	# This dictionary will be used by json.dumps
	data = {
		row[index_timestamps]:{
			# Convert values from str to float
			"latitude":latitude,
			"longitude":longitude,
			"sea_surface_T":sea_surface_T,
			"wind_direction":wind_direction,
			"wind_speed":wind_speed
			}
		}

	# Format to json and write to file or print to stdout
	if stdout:
		print(json.dumps(data, indent=4))
	else:
		json.dump(data, json_fd, indent=4)
		json_fd.write("\n") # nice file format

	# Counter
	i += 1

# Closing fd and exiting properly
csv_file.close()

if not stdout:
	json_fd.close()
	print(str(i)+" lines processed with success.")

sys.exit(0)
