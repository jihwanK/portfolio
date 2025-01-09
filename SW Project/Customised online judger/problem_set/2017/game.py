
# Read in the number of cases
numCases = int(input())

# Compute the probability for each case
for curCase in range(0, numCases):
   # Read in the types of gears
   numGearTypes = int(input())

   # Make arrays for the gear counts and gear probabilities
   gearCounts = []
   gearProbs = []

   # Read in the gear descriptions
   for curGearType in range(0, numGearTypes):
      # Read in the gear description and parse it
      line = input().split()
      curCount = int(line[0])
      curProb = float(line[1])

      # Update the arrays
      gearCounts.append(curCount)
      gearProbs.append(curProb)

   # Read in the total number of tries
   numTries = int(input())

   # Make two large arrays of probabilities
   curProb = [0.0] * (numTries + 1)
   nextProb = [0.0] * (numTries + 1)

   # Start the current probability with zero for acquiring the zero-th gear by
   # the zero-th day
   curProb[0] = 1.0

   # Run through each gear type
   for curGearType in range(0, numGearTypes):
      # Run through each of the needed gears for the current type
      for curGear in range(0, gearCounts[curGearType]):
         # Fill the current array with the failing probabilities
         for curTry in range(0, numTries):
            curProb[curTry + 1] += \
               curProb[curTry] * (1.0 - gearProbs[curGearType])
   
         # Fill the next array with zero
         for curTry in range(0, numTries + 1):
            nextProb[curTry] = 0.0
       
         # Update the array by the probability of successfully acquiring a gear
         for curTry in range(0, numTries):
            nextProb[curTry + 1] += curProb[curTry] * gearProbs[curGearType]
         
         # Update the current probability array by swapping the next and current
         swp = curProb
         curProb = nextProb
         nextProb = swp

   # Sum the current prob as it contains the probabilities of successfulling
   # acquiring all gears
   answer = 0.0
   for curTry in range(0, numTries + 1):
      answer += curProb[curTry]

   # print the answer
   print('{:.3f}'.format(answer))
