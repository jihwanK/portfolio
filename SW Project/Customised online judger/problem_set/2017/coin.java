
import java.util.Scanner;


public class coin
{
   public coin()
   {
      Scanner   scanner;
      int       numSets;
      int       k;
      int       coinCount;
      int       prevAmount;
      boolean   goodDenom;
      int       j;
      int       nextAmount;

      scanner = new Scanner(System.in);

      numSets = scanner.nextInt();
      for (k = 0; k < numSets; k++)
      {
         coinCount = scanner.nextInt();
         prevAmount = scanner.nextInt();

         goodDenom = true;

         for (j = 2; j <= coinCount; j++)
         {
            nextAmount = scanner.nextInt();

            if (nextAmount < 2 * prevAmount)
               goodDenom = false;

            prevAmount = nextAmount;
         }

         if (goodDenom)
            System.out.printf("0%n");
         else
            System.out.printf("1%n");
      }
   }


   public static void main(String[] args)
   {
      new coin();
   }
}

