import os
cwd = os.getcwd()
print(cwd)

dictionary = {
    '1': 344,
    '2': 455,
    '3': 566,
    '4': 677,
    '5': 788
}

for key in dictionary:
    value = dictionary[key]
    print(value)
    dictionary[value] = 'Uh oh!'