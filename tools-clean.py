import json
filename = "encodings.json"
data = json.loads(open(filename, "r").read())

# Sorting and duplicate check
labelsseen = []
for set in data:
    for encoding in set["encodings"]:
        labels = encoding["labels"]
        labels.sort()
        encoding["labels"] = labels
        for label in labels:
            if label in labelsseen:
                raise "Duplicate label: ", label
            labelsseen.append(label)

handle = open(filename, "w")
handle.write(json.dumps(data, sort_keys=True, allow_nan=False, indent=2, separators=(',', ': ')))
handle.write("\n")
