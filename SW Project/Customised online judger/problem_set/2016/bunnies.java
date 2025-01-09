/*
 * Solution to Bouncing Bunnies from 2016 UCF Local Programming Contest
 * Author: Michael Kirsche
 * A bunny can be jump from hill a to hill b if |Ta - Tb| = |Ha - Hb|
 * Case 1: Ta - Tb = Ha - Hb -> Ta - Ha = Tb - Hb
 * Case 2: Ta - Tb = -(Ha - Hb) -> Ta + Ha = Tb + Hb
 * Therefore, if we transform each hill from (T, H) to (T + H, T - H),
 * a bunny can jump between two hills if they have at least one of their two values in common.
 * We will construct a graph where the nodes are values for T + H and values for T - H (one node for each distinct value)
 * A hill is then treated as an edge between its sum (T + H) value and its difference (T - H) value.
 * Then, we run a breadth-first search (or other shortest path algorithm) 
 * starting at the sum and difference values for the first hill.
 * As soon as we reach the sum or difference value for the last hill, we are one hop away from the last hill,
 * so the answer is 1 + min(shortest path to last sum, shortest path to last difference).
 */
import java.io.*;
import java.util.*;
public class bunnies {
	@SuppressWarnings("unchecked")
public static void main(String[] args) throws IOException {
	long startTime = System.currentTimeMillis();
        Scanner input = new Scanner(System.in);
	int T = input.nextInt();
	for(int t = 0; t<T; t++)
	{
		/*
		 * Read in the input
		 */
		int n = input.nextInt();
		int[] ts = new int[n], hs = new int[n];
		for(int i = 0; i<n; i++) ts[i] = input.nextInt();
		for(int i = 0; i<n; i++) hs[i] = input.nextInt();
		
		/*
		 * Create sets of the distinct sum and difference values.
		 */
		HashSet<Integer> sums = new HashSet<Integer>(), diffs = new HashSet<Integer>();
		for(int i = 0; i<n; i++)
		{
			sums.add(ts[i] + hs[i]);
			diffs.add(ts[i] - hs[i]);
		}
		
		/*
		 * Map each sum and difference value to a node number in our graph.
		 */
		HashMap<Integer, Integer> sumMap = new HashMap<Integer, Integer>(), diffMap = new HashMap<Integer, Integer>();
		int nodes = 0;
		for(int x : sums) sumMap.put(x, nodes++);
		for(int x : diffs) diffMap.put(x, nodes++);
		
		/*
		 * Construct a graph with each hill as an undirected edge between its sum and difference values.
		 */
		ArrayList<Integer>[] g = new ArrayList[nodes];
		for(int i = 0; i<g.length; i++) g[i] = new ArrayList<Integer>();
		int[] dist = new int[nodes];
		int oo = 987654321;
		Arrays.fill(dist, oo);
		Queue<Integer> q = new LinkedList<Integer>();
		for(int i = 0; i<n; i++)
		{
			int sumNode = sumMap.get(ts[i] + hs[i]);
			int diffNode = diffMap.get(ts[i] - hs[i]);
			g[sumNode].add(diffNode);
			g[diffNode].add(sumNode);
			if(i == 0)
			{
				q.add(sumNode);
				q.add(diffNode);
				dist[sumNode] = dist[diffNode] = 0;
			}
		}
		
		/*
		 * Run breadth-first search
		 */
		while(!q.isEmpty())
		{
			int at = q.poll();
			for(int e : g[at])
			{
				if(dist[e] > 1 + dist[at])
				{
					dist[e] = 1 + dist[at];
					q.add(e);
				}
			}
		}
		
		/*
		 * Get the shortest path to the last hill and print the answer.
		 */
		int endSumNode = sumMap.get(ts[n-1] + hs[n-1]);
		int endDiffNode = diffMap.get(ts[n-1] - hs[n-1]);
		int res = Math.min(dist[endSumNode], dist[endDiffNode]) + 1;
		if(res >= oo) res = -1;
		System.out.printf("Field #%d: %d\n\n", t+1, res);
	}
	long endTime = System.currentTimeMillis();
	//System.out.println(1.0 * (endTime - startTime) / 1000 + " seconds");
}
}
