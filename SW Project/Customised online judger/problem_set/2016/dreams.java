// Arup Guha
// 8/12/2016
// Solution to 2016 UCF Locals Problem: Wildest Dreams

import java.util.*;

public class dreams {

    public static void main(String[] args) {

        Scanner stdin = new Scanner(System.in);
        int numCases = stdin.nextInt();

        // Go through each case.
        for (int loop=1; loop<=numCases; loop++) {

            // Get all info.
            int n = stdin.nextInt();
            int fav = stdin.nextInt()-1;
            int[] lengths = new int[n];
            for (int i=0; i<n; i++)
                lengths[i] = stdin.nextInt();

			// Cumulative frequency information is useful to know where you are in the whole CD.
            int[] cumfreq = new int[n+1];
            for (int i=1; i<=n; i++)
                cumfreq[i] = cumfreq[i-1] + lengths[i-1];

			// Print CD header.
            System.out.println("CD #"+loop+":");
            int days = stdin.nextInt();

            // Process each day.
            for (int i=0; i<days; i++) {

                int res = 0, position = 0;

                int numSegments = stdin.nextInt();

                // Simulate each segment.
                for (int j=0; j<numSegments; j++) {

                    int length = stdin.nextInt();

                    // Anya's in the car - add all the time and update the position of the CD.
                    if (j%2 == 0) {
                        res += length;

                        // Ends up in the middle of the song.
                        if (length%lengths[fav] != 0)
                            position = cumfreq[fav] + length%lengths[fav];

                        // Tricky case, song completed, so CD doesn't go back to the beginning of the track.
                        else
                            position = cumfreq[fav+1];
                    }

                    else {

                        // Count how many times Arup listened to the whole CD.
                        int wholeCD = length/cumfreq[n];
                        res += lengths[fav]*wholeCD;

                        // Now, deal with the leftover time.
                        int left = length - wholeCD*cumfreq[n];

                        // Case where in the last partial listen, Arup doesn't go past Anya's favorite song.
                        if (position + left <= cumfreq[fav+1])
                            res += left;

                        // Arup finishes listening to Anya's song after she gets out, but doesn't wrap back to it.
                        else if (position + left <= cumfreq[n] + cumfreq[fav])
                            res += (lengths[fav]-(position-cumfreq[fav]));

                        // This is tricky, just see how many seconds shy of a complete revolution we are, and that's
                        // how much of Anya's favorite song we missed.
                        else
                            res += lengths[fav] - (position - (position+length)%cumfreq[n]);

                    }
                }

				// The result for this day of driving.
                System.out.println(res);
            }

			// Between CDs.
            System.out.println();
        }
    }
}