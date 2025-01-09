
def isPrime(num):
   for k in range(2, num // 2):
      if (num % k == 0):
         return False

   return True


numSets = int(input())

for _ in range(numSets):
   num = int(input())
   print("%d " % num, end='')

   if (isPrime(num)):
      print("0")
   else:
      i = num - 1
      while True:
         if (isPrime(i)):
            break
         else:
            i = i - 1

      j = num + 1
      while True:
         if (isPrime(j)):
            break
         else:
            j = j + 1

      if num - i <= j - num:
         print("%d" % (num - i))
      else:
         print("%d" % (j - num))

