import java.util.*;

public class game 
{
	public static void main(String[] args)
	{
		// Create a reader to read from the command line
		Scanner in = new Scanner(System.in);
		
		// Read in the first number which is the number of test cases
		int n = in.nextInt();
		
		// Loop through all of the test cases
		for(int i = 0; i < n; i++)
		{
			// Read in the number of items
			int num_items = in.nextInt();
			
			// Create an array to store the number of items needed
			int[] items = new int[num_items];
			
			// Create an array to store the probability that each item will 
			// drop
			float[] probability = new float[num_items];
			
			int size = 0;
			
			// Loop through the items
			for (int j = 0; j < num_items; j++)
			{
				// Read in the number of items and the probability that the 
				// items will drop
				items[j] = in.nextInt();
				probability[j] = in.nextFloat();
				
				size += items[j];
			}
			
			float[] prob = new float[size];
			int count = 0;
			for (int j = 0; j < num_items; j++)
			{
				for(int k = 0; k < items[j]; k++)
				{
					prob[count] = probability[j];
					count++;
				}
			}
			
			// Read in the number of attempts that the player has to retrieve items
			int attempts = in.nextInt();
			
			// Build a dynamic programming table to store the results of the probability,
			// where moving along the diagonal means that an item was obtained, and moving
			// along the second dimension means that the attempt failed to obtain an item
			double[][] dpTable = new double[size+1][attempts+1];
			
			for (int j = 0; j < size; j++)
			{
				Arrays.fill(dpTable[j], 0.0);
			}
			
			dpTable[0][0] = 1.0;
			
			for (int j = 0; j < size; j++)
			{
				for (int k = j; k < attempts; k++)
				{
					if (j == 0)
					{
						// Calculate the chance that the item is obtained
						dpTable[j+1][k+1] = dpTable[j][k] * prob[j];
						
						// Calculate the chance that the item is not obtained
						dpTable[j][k+1] = dpTable[j][k] * (1 - prob[j]);
					}
					else
					{
						// Calculate the chance that the item is obtained
						dpTable[j+1][k+1] = dpTable[j+1][k+1] + (dpTable[j][k] * prob[j]);
						
						// Calculate the chance that the item is not obtained
						dpTable[j][k+1] = dpTable[j][k+1] + (dpTable[j][k] * (1 - prob[j]));
					}
				}
			}
			
			// DEBUG: Used to print out the table in order to check the values
			//printTable(dpTable);
			// DEBUG: Prints a blank line to help with readability
			//System.out.println();
			
			// Create a value to store a final answer
			double answer = 0.0;
			
			// Loop through the last row in order to sum up all the ways that were
			// able to collect all the needed items
			for (int j = 0; j < attempts+1; j++)
			{
				answer += dpTable[size][j];
			}
			
			// Print the answer to 3 decimal points and add a new line
			System.out.printf("%.3f\n", answer);
		}
	}
	
	// This method takes in a table in order to print out the entire table
	public static void printTable(double[][] table)
	{
		for (int i = 0; i < table.length; i++)
		{
			for (int j = 0; j < table[i].length; j++)
			{
				System.out.print(table[i][j] + " ");
			}
			
			System.out.println();
		}
	}
}

/*
4
2
3 0.5
3 0.3
20
4
2 0.75
1 0.01
2 1.0
3 0.8
25
2
1 0.5
1 0.3 
2
2
50 .4
50 .3
250

*/
