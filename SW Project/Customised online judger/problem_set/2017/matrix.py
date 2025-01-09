# Arup Guha
# 8/8/2017
# Solution to 2011 UCF Locals Problem Matrix - ported from Java.

numCases = int(input(""))

# Process each case.
for loop in range(1,numCases+1):

    # Read in dimensions.
    toks = input("").split()
    r = int(toks[0])
    c = int(toks[1])
    evenSum = 0
    oddSum = 0

    # Read in row by row.
    for i in range(r):
        toks = input("").split()

        # Add each item to the appropriate sum.
        for j in range(c):
            item = int(toks[j])
            if (i+j)%2 == 0:
                evenSum += item
            else:
                oddSum += item
                
    # Ta da!
    if evenSum == oddSum:
        print("0")
    else:
        print("1")
