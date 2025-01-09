/*
 * Our first step is to binary search the answer. This results in the subproblem of finding a path through
 * the cave with a minimum ceiling height of at least X. Although the problem states that the length of the
 * path is not important, it is optimal to take the shortest path to a particular cell if it can be reached.
 * This makes it more likely to make it to the end from that cell since the water level hasn't risen as much.
 * To check if a path can be found with minimum ceiling height X, we use a BFS from the start cell and avoid
 * processing cells that have been filled with water.
 */

import java.util.*;
public class tides
{
	public static final int INFINITY = 1000000000;
	public static final int[] dr = {1, 0, -1, 0};
	public static final int[] dc = {0, 1, 0, -1};
	
	public static int[][] grid;
	
	public static void main(String[] args)
	{
		Scanner in = new Scanner(System.in);
		
		int n = in.nextInt();
		for(int i = 0; i < n; i++)
		{
			int r = in.nextInt();
			int c = in.nextInt();
			
			grid = new int[r][c];
			for(int j = 0; j < r; j++)
			{
				for(int k = 0; k < c; k++)
				{
					grid[j][k] = in.nextInt();
				}
			}
			
			// Binary search for the minimum ceiling height of a path through the cave
			int low = 0;
			int high = INFINITY;
			while(low < high)
			{
				int mid = (low + high + 1) / 2;
				
				if(check(mid))
				{
					low = mid;
				}
				else
				{
					high = mid - 1;
				}
			}
			
			// If no path was found, the binary search ends on zero
			System.out.println(low > 0 ? low : "impossible");
		}
	}
	
	// Run a BFS through the grid assuming that a particular height is required along the path
	public static boolean check(int height)
	{
		boolean[][] visited = new boolean[grid.length][grid[0].length];
		ArrayDeque<Integer> queue = new ArrayDeque<Integer>();
		
		queue.add(0);
		queue.add(0);
		queue.add(0);
		visited[0][0] = true;
		
		while(queue.size() > 0)
		{
			int row = queue.remove();
			int col = queue.remove();
			int dist = queue.remove();
			
			// Don't process this cell if it is already filled with water
			if(grid[row][col] - dist >= height)
			{
				if(row == grid.length - 1 && col == grid[0].length - 1)
				{
					return true;
				}
				
				for(int i = 0; i < dr.length; i++)
				{
					int nr = row + dr[i];
					int nc = col + dc[i];
					
					if(nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length && !visited[nr][nc])
					{
						visited[nr][nc] = true;
						queue.add(nr);
						queue.add(nc);
						queue.add(dist + 1);
					}
				}
			}
		}
		
		return false;
	}
}
