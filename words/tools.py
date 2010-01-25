import random

# generate a random bit order
# you'll need to save this mapping permanently, perhaps just hardcode it
# map how ever many bits you need to represent your integer space
mapping = range(34)
mapping.reverse()


# alphabet for changing from base 10
chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# shuffle the bits
def encode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << b
        if n & b1:
            result |= b2
    return enbase(result)

# unshuffle the bits
def decode(n):
    result = 0
    for i, b in enumerate(mapping):
        b1 = 1 << i
        b2 = 1 << b
        if n & b2:
            result |= b1
    return debase(result)

# change the base
def enbase(x):
    n = len(chars)
    if x < n:
        return chars[x]
    return enbase(x/n) + chars[x%n]

# go back to base 10
def debase(x):
    n = len(chars)
    result = 0
    for i, c in enumerate(reversed(x)):
        result += chars.index(c) * (n**i)
    return result

