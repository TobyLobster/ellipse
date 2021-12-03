import re

# Open the file in read mode
text = open("trace.txt", "r")

# Create an empty dictionary
d = dict()

# Loop through each line of the file
for line in text:
    # Remove the leading spaces and newline character
    line = line.strip()

    match = re.match(r"\d+ +m`\$([0-9a-f][0-9a-f][0-9a-f][0-9a-f])", line)
    if match:
        addr = match.groups(1)[0]

        # Check if the word is already in dictionary
        if addr in d:
            # Increment count of word by 1
            d[addr] = d[addr] + 1
        else:
            # Add the word to dictionary with count 1
            d[addr] = 1

results=dict(sorted(d.items(),key= lambda x:x[1]))

# Print the contents of dictionary
for key in list(results.keys()):
    print(key, ":", results[key])
