import java.util.*;

public class jedi 
{
	public static int[] blasterTimes;
	public static int jediOne;
	public static int jediTwo;
	public static int[][][] memoTable;
	
	public static void main(String[] args)throws Exception
	{
		// Create a scanner that will read in the input from standard in
		Scanner in = new Scanner(System.in);
		
		// Read in the number of input cases that will be inside of the file
		int cases = in.nextInt();
		
		// Loop through all of the cases in the input
		for (int caseNumber = 1; caseNumber <= cases; caseNumber++)
		{
			// Read in the number of blaster shots that the mission has
			int numBlasters = in.nextInt();
			
			// Create a table to store the answers allowing for a faster lookup 
			// time during recursion
			memoTable = new int[numBlasters][101][101];
			
			// Create an array to store all the blaster shots
			blasterTimes = new int[numBlasters];
			
			// Loop through all the blaster shots in the input file
			for (int blasterShot = 0; blasterShot < numBlasters; blasterShot++)
			{
				// Read in the next blaster shot time
				blasterTimes[blasterShot] = in.nextInt();
				
				for (int i = 0; i < 101; i++)
				{
					// Fill the memo table with large values so that the answers will 
					// be overwritten with the smaller values during recursion
					Arrays.fill(memoTable[blasterShot][i], 1000);
				}
			}
			
			// Read in the number of Jedi in this mission
			int numJedi = in.nextInt();
			
			// Sort the array so the blaster times come in the chronological order
			Arrays.sort(blasterTimes);
			
			// Determine the number of jedi as that changes how the problem is 
			// solved
			if (numJedi == 1)
			{
				jediOne = in.nextInt();
				
				// Print the answer for this mission to the screen
				System.out.println("Mission #" + caseNumber + ": " + 
						numJediOne());
			}
			else
			{
				jediOne = in.nextInt();
				jediTwo = in.nextInt();
				
				// Print the answer for this mission to the screen
				System.out.println("Mission #" + caseNumber + ": " + 
						numJediTwo());
				
			}
			
			// Print a blank line after the mission
			System.out.println();
		}
		
		// Close the scanner that was reading the input from standard in
		in.close();
	}
	
	public static int numJediOne()
	{
		// This will keep track of the number of blaster shots that the jedi 
		// skipped
		int skipped = 0;
		
		// This will keep track of the next time the jedi can block a shot
		int nextBlock = 0;
		
		// Loop through all the blasters to determine how many shots the jedi 
		// can't block
		for (int currentBlaster = 0; currentBlaster < blasterTimes.length; 
				currentBlaster++)
		{
			// Check if the jedi can block the next shot
			if (nextBlock <= blasterTimes[currentBlaster])
			{
				// Increment the time for the next time the jedi can block a 
				// shot
				nextBlock = blasterTimes[currentBlaster] + jediOne;
			}
			else
			{
				// The jedi was unable to block the current blaster so the number 
				// of missed blaster shots increases
				skipped++;
			}
		}
		
		// Return the number of blaster shots that the jedi was unable to block 
		// this is the final answer for the mission
		return skipped;
	}
	
	public static int numJediTwo()
	{
		// Recursively choose the shots that the jedi block in order to find the 
		// smallest number of blaster shots that the jedi are unable to block
		return recurse(0, 0, 0);
	}
	
	public static int recurse(int blockOne, int blockTwo, int currentBlaster)
	{	
		// Base case where there are no more blaster shots left
		if (currentBlaster == blasterTimes.length)
		{
			// Since no blaster shots are left return that no more blaster
			// shots are unable to be blocked by the jedi
			return 0;
		}
		
		// Create a variable that will track the elapsed time between blaster shots
		int difference;
		
		// This checks that the array doesn't go out of bounds
		if (currentBlaster == 0)
		{
			// The difference in blaster times is based on 0 so just use the current 
			// blaster time
			difference = blasterTimes[currentBlaster];
		}
		else
		{
			// Subtract the previous blaster time from the current blaster time to 
			// determine the elapsed time
			difference = blasterTimes[currentBlaster] - blasterTimes[currentBlaster-1];
		}
		
		// Change the remaining block times based on the current blaster
		blockOne = Math.max(blockOne - difference, 0);
		blockTwo = Math.max(blockTwo - difference, 0);
		
		// Determine if both jedi can block a blaster shot
		if (blockOne == 0 && blockTwo == 0)
		{
			// If the value of the memo table is less than 1000 than an answer has 
			// already been found for this
			if (memoTable[currentBlaster][blockOne][blockTwo] < 1000)
			{
				// Return the answer the was found
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
			else
			{
				// Try both cases where jedi one blocks the shot and jedi two is waiting or 
				// have jedi two block the shot and jedi one waiting
				memoTable[currentBlaster][blockOne][blockTwo] = 
						Math.min(recurse(jediOne, blockTwo, currentBlaster + 1),
						recurse(blockOne, jediTwo, currentBlaster + 1));
				
				// Return the best value that is now recorded in the memo table
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
		}
		// This case means that only jedi one is able to block a shot
		else if (blockOne == 0)
		{
			// Determine if the answer has already been found
			if (memoTable[currentBlaster][blockOne][blockTwo] < 1000)
			{
				// The answer has already been found so return the best answer
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
			else
			{
				// Have jedi one block the shot
				memoTable[currentBlaster][blockOne][blockTwo] = 
					recurse(jediOne, blockTwo, currentBlaster + 1);
				
				// Return the missed shots based on jedi one blocking the shot
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
		}
		// This case means only jedi two can block the shot
		else if (blockTwo == 0)
		{
			// Determine if the answer has already been found
			if (memoTable[currentBlaster][blockOne][blockTwo] < 1000)
			{
				// The answer has already been found so return the best answer
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
			else
			{
				// Have jedi two block the shot
				memoTable[currentBlaster][blockOne][blockTwo] = 
						recurse(blockOne, jediTwo, currentBlaster + 1);
				
				// Return the missed shots based on jedi one blocking the shot
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
		}
		// Neither jedi can block the shot
		else
		{
			// Determine if the answer has already been found
			if (memoTable[currentBlaster][blockOne][blockTwo] < 1000)
			{
				// The answer has already been found so return the best answer
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
			else
			{
				// Both jedi are unable to block the shot so add 1 blaster shot that 
				// was unable to be blocked and move on to the next shot
				memoTable[currentBlaster][blockOne][blockTwo] = 
						recurse(blockOne, blockTwo, currentBlaster + 1) + 1;
				
				// Return the missed shots based on jedi one blocking the shot
				return memoTable[currentBlaster][blockOne][blockTwo];
			}
		}
	}
}
