# Arup Guha
# 8/16/2017
# Solution to UCF 2017 Locals Problem: Rotating Cards

def main():

    numCases = int(input(""))

    # Process each case.
    for loop in range(numCases):

        # Get the current stack and store a reverse look up.
        toks = input("").split()
        n = int(toks[0])
        nums = [0]*n
        rev = [0]*(n+1)
        for i in range(1,n+1):
            nums[i-1] = int(toks[i])
            rev[nums[i-1]] = i;

        # Set up my bit.
        mybit = bit(n+1)
        for i in range(1,n+1):
            mybit.add(i, nums[i-1])

        # Initial values.
        cur = 1
        left = n*(n+1)//2
        res = 0

        # Now, go through queries.
        for i in range(1,n+1):

            # Get query range.
            nxt = rev[i]
            low =  min(cur,nxt)
            high = max(cur,nxt)

            # Try both directions and do the best one.
            tot = mybit.totalrange(low,high-1)
            other = left - tot
            res += min(tot, other)

            # Bookkeeping - update all necessary variables.
            left -= nums[nxt-1]
            mybit.add(nxt, -nums[nxt-1])
            cur = nxt

        # Ta da
        print(res)

# Returns the binary value of the lowest 1 bit of n.
def lowestOneBit(n,val):
    if n <= 0:
        return -1
    while (n & val) == 0:
        val <<= 1
    return val;

# Here is the Binary Index Tree/Fenwick Tree...
class bit:

    def __init__(self, n):

        self.cumfreq = []
        size = 1
        while size < n:
            size <<= 1;
        for i in range(size+1):
            self.cumfreq.append(0)

    def add(self, index, value):
        cur = 1
        while index < len(self.cumfreq):
            self.cumfreq[index] += value
            item = lowestOneBit(index, cur)
            index += item
            cur = item
            
            
    def total(self, index):
        ans = 0
        cur = 1
        while index > 0:
            ans += self.cumfreq[index]
            item = lowestOneBit(index, cur)
            index -= item
            cur = item
        return ans

    def totalrange(self, low, high):
        return self.total(high) - self.total(low-1)

# Get it all started.
main()
