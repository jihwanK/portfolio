
numSets = int(input())

for _ in range(numSets):
   values = list(map(int, input().split()))

   goodDenom = True
   for j in range(2, values[0] + 1):
      if (values[j] < 2 * values[j - 1]):
         goodDenom = False;

   if goodDenom:
      print("0")
   else:
      print("1")

