// Arup Guha
// 8/22/2016
// Alternate (and slower) solution to 2016 UCF Locals Problem: Wildest Dreams

import java.util.*;

public class dreams2 {

    public static void main(String[] args) {

        Scanner stdin = new Scanner(System.in);
        int numCases = stdin.nextInt();

        // Go through each case.
        for (int loop=1; loop<=numCases; loop++) {

            // Get all info.
            int n = stdin.nextInt();
            int fav = stdin.nextInt()-1;
            int[] lengths = new int[n];
            int sum = 0, preAnya = 0;
            for (int i=0; i<n; i++) {
                lengths[i] = stdin.nextInt();
				sum += lengths[i];
				if (i < fav) preAnya += lengths[i];
            }

            // Hard-code an array with what occurs each second. 1 = anya's song, 0 = not anya's song.
            int[] expand = new int[sum];
            int t = 0;
            for (int i=0; i<n; i++)
            	for (int j=0; j<lengths[i]; j++,t++)
            		expand[t] = i == fav ? 1 : 0;

            // Hard-code which second Arup's segments go to.
            int[] arupForward = new int[sum];
            for (int i=0; i<sum; i++)
            	arupForward[i] = (i+1)%sum;

            // Hard-code which second Anya's segments go to.
            int[] anyaForward = new int[sum];
            Arrays.fill(anyaForward,-1);
            for (int i=preAnya; i<preAnya+lengths[fav]-1; i++)
            	anyaForward[i] = i+1;
            anyaForward[preAnya+lengths[fav]-1] = preAnya;

			// Print header.
            System.out.println("CD #"+loop+":");
            int days = stdin.nextInt();

            // Process each day.
            for (int i=0; i<days; i++) {

                int res = 0, position = preAnya;

                int numSegments = stdin.nextInt();

                // Simulate each segment.
                for (int j=0; j<numSegments; j++) {

                    int length = stdin.nextInt();

                    // Go all but last step.
                    for (int k=0; k<length-1; k++) {
                    	res += expand[position];
                    	position = j%2 == 0 ? anyaForward[position] : arupForward[position];
                    }

            		// Here is what happens in the last time step.
                    res += expand[position];
                    position = j%2 == 0 ? arupForward[position] : preAnya;
                }

				// This drive result.
                System.out.println(res);
            }

			// Between cases.
            System.out.println();
        }
    }
}