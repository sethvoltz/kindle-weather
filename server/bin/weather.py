#!/usr/bin/python2

# Kindle Weather Display
# Matthew Petroff (http://www.mpetroff.net/)
# September 2012
#
# Date and time added Nov 2012. Notes can be found here:
# http://www.shatteredhaven.com/2012/11/1347365-kindle-weather-display.html
# no other changes made
#
# Modified by Seth Voltz (http://seth.to)
# May 2018

import os
import json
import urllib2
from xml.dom import minidom
import datetime
import codecs

# Get paths for files
base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

#
# Download and parse weather data
#

# Fetch data (change lat and lon in config.json)
with open(os.path.join(base_dir, 'config.json')) as f:
    config = json.load(f)

weather_url = (
    'http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=%s&lon=%s&format=24+hourly&numDays=4&Unit=e'
    % (config['latitude'], config['longitude'])
)
weather_xml = urllib2.urlopen(weather_url).read()
dom = minidom.parseString(weather_xml)

# Parse temperatures
xml_temperatures = dom.getElementsByTagName('temperature')
highs = [None]*4
lows = [None]*4
for item in xml_temperatures:
    if item.getAttribute('type') == 'maximum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            highs[i] = int(values[i].firstChild.nodeValue)
    if item.getAttribute('type') == 'minimum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            lows[i] = int(values[i].firstChild.nodeValue)

# Parse icons
xml_icons = dom.getElementsByTagName('icon-link')
icons = [None]*4
for i in range(len(xml_icons)):
    icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')

# Parse dates
xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')

#
# Preprocess SVG
#

# Open SVG to process
output = codecs.open(os.path.join(base_dir, 'source', 'weather.svg'), 'r', encoding='utf-8').read()

# calculate current date and time
now = datetime.datetime.now()
dtnow = now.strftime('%m/%d/%Y %H:%M')

# Insert icons and temperatures
output = output\
    .replace('ICON_ONE',icons[0])\
    .replace('ICON_TWO',icons[1])\
    .replace('ICON_THREE',icons[2])\
    .replace('ICON_FOUR',icons[3])

output = output\
    .replace('HIGH_ONE',str(highs[0]))\
    .replace('HIGH_TWO',str(highs[1]))\
    .replace('HIGH_THREE',str(highs[2]))\
    .replace('HIGH_FOUR',str(highs[3]))

output = output\
    .replace('LOW_ONE',str(lows[0]))\
    .replace('LOW_TWO',str(lows[1]))\
    .replace('LOW_THREE',str(lows[2]))\
    .replace('LOW_FOUR',str(lows[3]))

# Insert date and time of last update
output = output.replace('DATE_VALPLACE',str(dtnow))

# Insert days of week
one_day = datetime.timedelta(days=1)
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

output = output\
    .replace('DAY_THREE',days_of_week[(day_one + 2*one_day).weekday()])\
    .replace('DAY_FOUR',days_of_week[(day_one + 3*one_day).weekday()])

# Write output
codecs.open(os.path.join(base_dir, 'output', 'weather.svg'), 'w', encoding='utf-8').write(output)
