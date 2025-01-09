# Solution to Maximum Non-Overlapping Increasing Subsequences

T = int(input())
for t in range(0, T):

	# Read in the input
	n = int(input())
	a = list(map(int, input().split()))
	
	# The first step is to compute for each subarray what the longest increasing subsequence is within that subarray.
	# Here we will force the last element to be used, since in our later steps we will simply use a smaller subarray if we do not want to use the last element.
	# This is done in O(n^3) time using dynamic programming.
	# lis[i][j] will hold the length of the longest increasing subsequence in {a[i], ..., a[j]} which uses element a[j]
	lis = [[0 for j in range(0, n)] for i in range(0, n)]
	
	for i in range(0, n):
		for j in range(i, n):
			# Any non-empty subarray can have an increasing subsequence of length 1 (just the last element)
			val = 1
			
			# Also, the last element can be appended to any increasing subsequence that ends earlier in the subarray if it is larger than the earlier endpoint's value.
			# So, we will try all possible earlier endpoints and see how long the resulting sequence is, taking the maximum.
			for k in range(i, j):
				if(a[k] < a[j] and 1 + lis[i][k] > val):
					val = 1 + lis[i][k]
			lis[i][j] = val
	ans = ''
	
	# Now, the problem can be solved independently for each value of k using the lis array as a lookup table.
	for k in range(1, n+1):
		# Here, dp[i] will be the highest number of elements that can be used in valid subsequences assuming that a[i] is the end of the last subsequence.
		dp = []
		
		# Initially, we try all possible endpoints for the first subsequence we will use, updating their dp values.
		for i in range(0, n):
			val = 0
			if(lis[0][i] >= k):
				val = lis[0][i]
			dp.append(val)
		res = 0
		
		# Then, for each possible endpoint for a subsequence, we see where we can append on a new subsequence, and update the dp values
		# of the later endpoint to be dp[i] + lis[i+1][j], assuming lis[i+1][j] is large enough for us to make a valid subsequence between
		# the two endpoints.
		for i in range(0, n):
			for j in range(i+1, n):
				if(lis[i+1][j] >= k and lis[i+1][j] + dp[i] > dp[j]):
					dp[j] = lis[i+1][j] + dp[i]
			if(dp[i] > res):
				res = dp[i]
				
		# Append the current answer onto the output string.
		ans = ans + str(res)
		if(k < n):
			ans = ans + ' '
			
	print(ans)
	