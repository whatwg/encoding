import json
filename = "encodings.json"
data = json.loads(open(filename, "r").read())

handle = open(filename, "w")
handle.write(json.dumps(data, sort_keys=True, allow_nan=False, indent=2, separators=(',', ': ')))
handle.write("\n")
