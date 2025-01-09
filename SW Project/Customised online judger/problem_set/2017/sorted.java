// correct on all cases I got it to finish on (everything except the max case 10 x 10 with nothing)

import java.util.*;

public class sorted {

	final public static int MOD = 10007;

	public static int r;
	public static int c;
	public static int[][] grid;
	public static boolean[][] canChange;

	public static HashMap<Long,Integer> map;

	public static void main(String[] args) {

		Scanner stdin = new Scanner(System.in);
		int numCases = stdin.nextInt();

		// Process each case.
		for (int loop=1; loop<=numCases; loop++) {

			r = stdin.nextInt();
			c = stdin.nextInt();
			grid = new int[r][c];
			canChange = new boolean[r][c];
			for (int i=0; i<r; i++) {
				String tmp = stdin.next();
				for (int j=0; j<c; j++) {
					grid[i][j] = tmp.charAt(j) == '.' ? -1 : tmp.charAt(j) - 'a';
					canChange[i][j] = tmp.charAt(j) == '.';
				}
			}

			// Run it!
			System.out.println(solve());
		}
	}

	// Wrapper function to get all solutions.
	public static int solve() {
		map = new HashMap<Long,Integer>();
		int[] end = new int[r];
		Arrays.fill(end, c);
		return solve(end, 25);
	}

	public static int solve(int[] state, int letter) {

		// Screen out some cases.
		if (contradiction(state,letter)) return 0;

		// Down to A's either we can do it or we can't.
		if (letter == 0) return 1;

		// We did this already.
		long lookup = getState(state, letter);
		if (map.containsKey(lookup)) return map.get(lookup);

		// Get the corners that stick out.
		ArrayList<Integer> corners = getCorners(state);
		int n = corners.size();

		// Answers without using this letter.
		int without = solve(state, letter-1);

		int with = 0;

		// Do inclusion-exclusion.
		for (int mask=1; mask<(1<<n); mask++) {

			// Naturally sets up adding/subtracting.
			int sign = Integer.bitCount(mask)%2 == 1 ? 1 : -1;

			int[] newstate = getNewState(state, corners, mask, letter);
			if (newstate == null) continue;

			// Set letter.
			for (int bit=1,i=0; bit<=mask; bit<<=1,i++)
				if ((mask & bit) != 0)
					grid[corners.get(i)][state[corners.get(i)]-1] = letter;

			int tmp = solve(newstate, letter);
			with = (with + sign*tmp + 100070)%10007;

			// Change back, if they were changeable.
			for (int bit=1,i=0; bit<=mask; bit<<=1,i++)
				if ((mask & bit) != 0 && canChange[corners.get(i)][state[corners.get(i)]-1])
					grid[corners.get(i)][state[corners.get(i)]-1] = -1;
		}

		// Calculate result, store it and return.
		int res = (with+without)%10007;
		map.put(lookup, res);
		return res;
	}


	public static boolean contradiction(int[] state, int letter) {
		for (int i=0; i<r; i++)
			for (int j=0; j<state[i]; j++) // out of bounds state[i] == c...
				if (grid[i][j] > letter) return true;
		return false;
	}

	public static long getState(int[] state, int letter) {
		long res = letter;
		for (int i=0; i<r; i++) res = (c+1)*res + state[i];
		return res;
	}

	public static ArrayList<Integer> getCorners(int[] state) {
		ArrayList<Integer> res = new ArrayList<Integer>();
		for (int i=0; i<r-1; i++)
			if (state[i] > state[i+1])
				res.add(i);
		if (state[r-1] > 0) res.add(r-1);
		return res;
	}

	public static int[] getNewState(int[] state, ArrayList<Integer> corners, int mask, int letter) {

		// return null if any forced square can't equal letter.
		for (int bit=1,i=0; bit<=mask; bit<<=1,i++) {
			if ((mask & bit) != 0) {
				int cur = grid[corners.get(i)][state[corners.get(i)]-1]; // array out of bounds here...
				if (cur != letter && cur != -1)
					return null;
			}
		}

		int[] res = new int[r];
		for (int i=0; i<r; i++) res[i] = state[i];

		// Otherwise, subtract one from each row where we are forcing letter.
		for (int bit=1,i=0; bit<=mask; bit<<=1,i++)
			if ((mask & bit) != 0)
				res[corners.get(i)]--;
		return res;
	}

}
