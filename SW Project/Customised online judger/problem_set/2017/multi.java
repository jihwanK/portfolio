// Arup Guha
// 8/25/2017
// Alternate Solution to 2017 UCF Locals Problem: Multiples

import java.util.*;

public class multi {

	// We don't have to worry about numbers bigger than this.
	final public static long MAX = 1000000000000000L;

	// Lists are created so products of each list fit in a long...
	final public static int[] primes = {3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127};
	final public static int[] primes1 = {3,5,7,11,13,17,19,23,29,31,37,41,43,47,53};
	final public static int P1LEN = primes1.length;
	final public static int PLEN = primes.length;
	final public static int[] primes2 = {59,61,67,71,73,79,83,89,97,101,103,107,109,113,127};

	public static void main(String[] args) {

		// Here is our pre-comp we are doing a "divide and conquer" strategy to try to speed up our work...
		ArrayList<item> list1 = formList(primes1);
		ArrayList<item> list2 = formList(primes2);
		Collections.sort(list1);
		Collections.sort(list2);

		Scanner stdin = new Scanner(System.in);
		int numCases = stdin.nextInt();

		// Process each case.
		for (int loop=0; loop<numCases; loop++) {

			// Get input.
			int maxD = stdin.nextInt();
			long n = stdin.nextLong();

			// count # of primes <= maxD.
			int numP = 0;
			while (numP < primes.length && primes[numP] <= maxD) numP++;

			long res = n/2;

			// Try each factor from list 1.
			for (int i=0; i<list1.size(); i++) {

				// Match with each from list 2.
				for (int j=0; j<list2.size(); j++) {

					// Calculate this product - if it's too big, get out!
					long prod = list1.get(i).div*list2.get(j).div;
					if (prod > n) break;

					// Trivially we can cut out of list 2, since it doesn't get used for this numP limit.
					if (j>0 && numP <= P1LEN) break;

					// Not in our count!
					if (i+j == 0) continue;

					// Calculate our full mask - if this subset isn't in it, skip it.
					int fullM = list1.get(i).mask + (list2.get(j).mask << P1LEN);
					if (numP < 31 && fullM >= (1<<numP)) continue;

					// Based on parity of the subset, add or subtract...
					int bits = list1.get(i).numBits + list2.get(j).numBits;
					if (bits%2 == 0) 	res -= (n/prod+1)/2;
					else				res += (n/prod+1)/2;
				}
			}

			// Ta da!
			System.out.println(res);
		}
	}

	// Just forms a list of terms storing products and their associated subsets as a bitmask.
	public static ArrayList<item> formList(int[] p) {
		int n = p.length;
		item[] res = new item[1<<n];
		Arrays.fill(res, null);
		res[0] = new item(1L,0);

		// Go through each product.
		for (int i=1; i<(1<<n); i++) {
			int bit = bitOn(i);
			int prevM = i - (1<<bit);

			// We only form the product if it's not too big.
			if (res[prevM] != null && res[prevM].div*p[bit] <= MAX)
				res[i] = new item(res[prevM].div*p[bit], i);
		}

		// Add the valid products of primes.
		ArrayList<item> ans = new ArrayList<item>();
		for (int i=0; i<res.length; i++)
			if (res[i] != null)
				ans.add(res[i]);

		return ans;
	}

	// Returns the index/location of the lowest bit on.
	public static int bitOn(int mask) {
		int loc = 0;
		while ((mask & (1<<loc)) == 0) loc++;
		return loc;
	}
}

class item implements Comparable<item> {

	public long div;
	public int mask;
	public int numBits;

	public item(long x, int mymask) {
		div = x;
		mask = mymask;
		numBits = Integer.bitCount(mask);
	}

	public int compareTo(item other) {
		if (this.div < other.div) return -1;
		if (this.div > other.div) return 1;
		return 0;
	}
}