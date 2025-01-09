
import java.util.Scanner;


public class smart
{
   public boolean isPrime(int num)
   {
      int   k;

      for (k = 2; k <= num / 2; k++)
      {
         if (num % k == 0)
            return false;
      }

      return true;
   }


   public smart()
   {
      Scanner   scanner;
      int       numSets;
      int       k;
      int       num;
      int       i;
      int       j;

      scanner = new Scanner(System.in);

      numSets = scanner.nextInt();
      for (k = 0; k < numSets; k++)
      {
         num = scanner.nextInt();
         System.out.printf("%d ", num);
         if (isPrime(num))
            System.out.printf("0%n");
         else
         {
            for (i = num - 1; !isPrime(i); i--);

            for (j = num + 1; !isPrime(j); j++);

            if (num - i <= j - num)
               System.out.printf("%d%n", num - i);
            else
               System.out.printf("%d%n", j - num);
         }
      }
   }


   public static void main(String[] args)
   {
      new smart();
   }
}

