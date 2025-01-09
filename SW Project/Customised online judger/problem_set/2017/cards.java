/*
 * Solution to cards
 * The idea of this solution is to consider the problem in the following way:
 * Each time a card needs to be drawn, there are two options: Move everything above it to the bottom
 * or move everything below it and itself to the top.  The problem is to find the set of these options
 * which minimizes the total cost of all moves.
 * A key observation is that regardless of which option we choose, the deck will end up in the same configuration
 * after the current card is drawn.  For example, if the deck is 3 5 1 4 2, we can do either of the following sequences:
 * 35142 -> 51423 -> 14235 -> 4235 or 35142 -> 23514 -> 42351 -> 14235 -> 4235.  Either way, the deck after card 1 is drawn is 4235.
 * Because of this, we can use a greedy algorithm, using whichever option gives a lower cost for the current card.
 * The cost of each option corresponds to the sum of elements within a range of the deck, which could normally be done with a cumulative sum array.
 * However, in this case, we are removing cards as we go, so a binary indexed tree is needed (removing a card can be represented by setting the cost of that card to 0).
 */

import java.util.*;

public class cards
{
	public static void main(String[] args)
	{
		Scanner input = new Scanner(System.in);
		int T = input.nextInt();
		for(int t = 0; t<T; t++)
		{
			// Take in input and store the position of each number.
			int n = input.nextInt();
			int[] a = new int[n];
			int[] pos = new int[n+1];
			for(int i = 0; i<n; i++)
			{
				a[i] = input.nextInt();
				pos[a[i]] = i+1;
			}
			// Initialize the cost of each card to that card's value.
			BIT cards = new BIT(n);
			for(int i = 0; i<n; i++) cards.upd(i+1, a[i]);
			// Handle the first card on its own because we don't have a position from which our last card came.
			long costToReachFirst = cards.csum(pos[1]-1);
			long res = Math.min(costToReachFirst, cards.csum(n) - costToReachFirst);
			int lastPos = pos[1];
			// Remove the first card by setting its cost back to 0.
			cards.upd(pos[1], -1);
			// Now, handle cards 2 through n.
			for(int i = 2; i<=n; i++)
			{
				// Get the cost of both options, and take the minimum.
				long costToDrawFromTop = 0;
				if(pos[i] > lastPos) costToDrawFromTop = cards.csum(lastPos, pos[i] - 1);
				else costToDrawFromTop = cards.csum(lastPos, n) + cards.csum(pos[i] - 1);
				long costToDrawFromBottom = 0;
				if(pos[i] > lastPos) costToDrawFromBottom = cards.csum(lastPos) + cards.csum(pos[i], n);
				else costToDrawFromBottom = cards.csum(pos[i], lastPos);
				res += Math.min(costToDrawFromTop, costToDrawFromBottom);
				cards.upd(pos[i], -i);
				lastPos = pos[i];
			}
			System.out.println(res);
		}
	}
	/*
	 * Binary Indexed Tree - used for updates and range queries.  Every operation is O(log(n)).
	 */
	static class BIT
	{
		long[] tree;
		int n;
		BIT(int n)
		{
			tree = new long[n+1];
			this.n = n;
		}
		/*
		 * Increases the value at x by v.
		 */
		void upd(int x, int v)
		{
			int i = x;
			while(i<=n)
			{
				tree[i]+=v;
				i += (i&-i);
			}
		}
		/*
		 * Returns the sum of the first x elements.
		 */
		long csum(int x)
		{
			long s = 0;
			while(x>0)
			{
				s += tree[x];
				x -= (x&-x);
			}
			return s;
		}
		/*
		 * Returns the sum of elements x through y, inclusive.
		 */
		long csum(int x, int y)
		{
			return csum(y) - csum(x-1);
		}
	}
}