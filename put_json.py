#!/usr/bin/python3.4
import json
data = {'date':'2/8/2015', 'day': 'tuesday', 'timestamp':'4:02', 'items':{"gun1":"$4.25","gun2":"$3.00"}}
print(json.dumps(data))