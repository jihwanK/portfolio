// Arup Guha
// 8/17/2016
// Solution to 2016 UCF Locals Problem: Dominoes

import java.util.*;

public class dominoes {

    final public static int MAXDOMINOES = 20;
    final public static long MOD = 1000000007L;

    public static int n;
    public static int[][] list;

    public static void main(String[] args) {

    	// Stores result when all orderings are possible.
    	long[] fact = new long[MAXDOMINOES+1];
    	fact[0] = 1;
    	for (int i=1; i<=MAXDOMINOES; i++)
    		fact[i] = (fact[i-1]*i)%MOD;

        Scanner stdin = new Scanner(System.in);
        int numCases = stdin.nextInt();

        // Process each case.
        for (int loop=0; loop<numCases; loop++) {

            // Read in this case.
            n = stdin.nextInt();
            list = new int[n][2];
            for (int i=0; i<n; i++)
                for (int j=0; j<2; j++)
                    list[i][j] = stdin.nextInt();

            // Special case - if all the dominoes are the same, all orderings work.
            if (same(list)) {
            	System.out.println(fact[n]);
            	continue;
            }

            // dp[mask][last][orientation] will store the number of permutations using the dominoes indicated by
            // mask, with the last domino last facing in the direction dictated by orientation. If orientation is 0,
            // this is the original input orientation, if it is 1, it's flipped.
            long[][][] dp = new long[1<<n][n][2];

            // Always 1 way to place one domino in a fixed orientation.
            for (int i=0; i<n; i++) {
                dp[1<<i][i][0] = 1;
                dp[1<<i][i][1] = 1;
            }

            // Outer DP loop, solve all problem instances for each subset of dominoes.
            for (int mask=3; mask<(1<<n); mask++) {

                // Now, try each domino as the last domino in mask.
                for (int last=0; last<n; last++) {

                    // Not a valid state.
                    if ((mask&(1<<last)) == 0) continue;

                    int prevmask = mask - (1<<last);

                    for (int i=0; i<n; i++) {

                        if ((prevmask&(1<<i)) == 0) continue;

                        // Both i and last are in regular orientation.
                        if (list[i][1] == list[last][0])
                            dp[mask][last][0] = (dp[mask][last][0]+dp[prevmask][i][0])%MOD;

                        // Here i is flipped and last is regular.
                        else if (list[i][0] == list[last][0])
                            dp[mask][last][0] = (dp[mask][last][0]+dp[prevmask][i][1])%MOD;

                        // i is regular but last is flipped.
                        if (list[i][1] == list[last][1])
                            dp[mask][last][1] = (dp[mask][last][1]+dp[prevmask][i][0])%MOD;

                        // Both i and last are flipped.
                        else if (list[i][0] == list[last][1])
                            dp[mask][last][1] = (dp[mask][last][1]+dp[prevmask][i][1])%MOD;
                    }
                } // end last loop
            } // end mask loop

            // Sum up result - all ways to place all dominoes over all possible last dominoes in either orientation.
            // Since we screened out our special case, no over-counting will occur here.
            long res = 0L;
            for (int last=0; last<n; last++) {
            	res = (res + dp[(1<<n)-1][last][0])%MOD;
            	if (list[last][0] != list[last][1])
            		res = (res + dp[(1<<n)-1][last][1])%MOD;
            }
            System.out.println(res);
        }
    }

    // Returns true iff each dominoe in list is the same.
    public static boolean same(int[][] list) {
    	for (int i=1; i<list.length; i++)
    		if (!same(list[0], list[i]))
    			return false;
    	return true;
    }

    // Pre-condition: a and b are length 2.
    // Post-condition: Returns true iff a and b store the same pair (order doesn't matter).
    public static boolean same(int[] a, int[] b) {
    	return (a[0] == b[0] && a[1] == b[1]) || (a[0] == b[1] && a[1] == b[0]);
    }

}
