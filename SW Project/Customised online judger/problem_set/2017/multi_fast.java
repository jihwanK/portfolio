// Arup Guha
// 8/25/2017
// Alternate Solution to 2017 UCF Locals Problem: Multiples

import java.util.*;

public class multi_fast {

	// We don't have to worry about numbers bigger than this.
	final public static long MAX = 1000000000000000L;

	// Lists are created so products of each list fit in a long...
	final public static int[] primes = {3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127};
	final public static int PLEN = primes.length;

	// Stores all necessariy divisors and their associated parity (parity of # of prime factors)
	public static long[][] div;
	public static boolean[][] parity;
	public static long[] master;
	public static boolean[] masterp;

	public static void main(String[] args) {

		div = new long[PLEN][];
		parity = new boolean[PLEN][];
		div[0] = new long[1];
		div[0][0] = 3;
		parity[0] = new boolean[1];
		parity[0][0] = true;
		master = div[0];
		masterp = parity[0];

		// Pre-calculate all of our possible divisors.
		for (int i=1; i<PLEN; i++) {
			formList(i);
			merge(i);
		}

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

			// Go through all valid prime lists.
			for (int i=0; i<numP; i++) {

				// Go through each number that has this prime in it.
				for (int j=0; j<div[i].length; j++) {

					// Too big, get out.
					if (div[i][j] > n) break;

					// Do appropriate inclusion/exclusion.
					if (parity[i][j])	res += (n/div[i][j]+1)/2;
					else				res -= (n/div[i][j]+1)/2;
				}
			}

			// Ta da!
			System.out.println(res);
		}
	}

	public static void formList(int index) {

		// Find max val.
		int i = master.length-1;
		int p = primes[index];
		while (master[i]*p > MAX) i--;

		// Copy rest of the list and multiply by p.
		div[index] = new long[i+2];
		parity[index] = new boolean[i+2];
		for (int j=i; j>=0; j--) {
			div[index][j+1] = master[j]*p;
			parity[index][j+1] = !masterp[j];
		}
		div[index][0] = p;
		parity[index][0] = true;
	}

	// Merges list index into the master list and updates it.
	public static void merge(int index) {

		int len = master.length + div[index].length;
		long[] res = new long[len];
		boolean[] sign = new boolean[len];
		int i=0, j=0, resi=0;

		while (i<master.length || j<div[index].length) {
			if (i == master.length) {
				res[resi] = div[index][j];
				sign[resi++] = parity[index][j++];
			}
			else if (j == div[index].length)	{
				res[resi] = master[i];
				sign[resi++] = masterp[i++];
			}
			else if (master[i] < div[index][j]) {
				res[resi] = master[i];
				sign[resi++] = masterp[i++];
			}
			else {
				res[resi] = div[index][j];
				sign[resi++] = parity[index][j++];
			}
		}

		// Reassign to master list.
		master = res;
		masterp = sign;
	}
}
