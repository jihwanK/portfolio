
import java.util.*;

public class breakice
{
   public static void main(String[] Args)
   {
      Scanner sc = new Scanner(System.in);
      int t = sc.nextInt();
      int cc = 0;
      while (t-->0)
      {
         int ans = 0;
         boolean updated;
         boolean completeRow;
         boolean completeCol;
         int row;
         int col;
         int n = sc.nextInt();
         int m = sc.nextInt();
         boolean[][] fallen = new boolean[n][n];
         for (int i = 0; i < m; i++)
         {
            row = sc.nextInt() - 1;
            col = sc.nextInt() - 1;
            if (fallen[row][col])
            {
               ans++;
            }
            else
            {
               fallen[row][col] = true;
               updated = true;
               while (updated)
               {
                  updated = false;

                  // Look for any blocks that might fall
                  for (row = 0; row < n; row++)
                  {
                     for (col = 0; col < n; col++)
                     {
                        // Check that this block has not fallen yet
                        if (!fallen[row][col])
                        {
                           // Check for an incomplete row
                           completeRow = true;
                           for (int col2 = 0; col2 < n; col2++)
                           {
                              if (fallen[row][col2])
                              {
                                 completeRow = false;
                              }
                           }
                           
                           // Check for an incomplete col
                           completeCol = true;
                           for (int row2 = 0; row2 < n; row2++)
                           {
                              if (fallen[row2][col])
                              {
                                 completeCol = false;
                              }
                           }
            
                           // Check if the block should fall
                           if (!completeCol && !completeRow)
                           {
                              fallen[row][col] = true;
                              updated = true;
                           }
                        }
                     }
                  }
               }
            }
         }

         // Print out the answer
         System.out.printf("Strategy #%d: %d%n%n", ++cc, ans);
      }
   }
}
