// Arup Guha
// 7/31/2013
// Solution to 2011 UCF Locals Problem: Matrix
import java.util.*;

public class matrix {

	public static void main(String[] args) {

		Scanner stdin = new Scanner(System.in);
		int numCases = stdin.nextInt();

		// Go through each case.
		for (int loop=1; loop<=numCases; loop++) {

			// Store sums of "even" and "odd" indexes.
			int r = stdin.nextInt();
			int c = stdin.nextInt();
			int evenSum = 0, oddSum = 0;
			for (int i=0; i<r; i++) {
				for (int j=0; j<c; j++) {
					int val = stdin.nextInt();
					if ( (i+j)%2 == 0)
						evenSum += val;
					else
						oddSum += val;
				}
			}

			// Output result - this is the invariant in the given
			// transformation...
			if (evenSum == oddSum)
				System.out.println("0");
			else
				System.out.println("1");
		}
	}
}
