
#include <stdio.h>

#define TRUE  1
#define FALSE 0


int is_prime(int num)
{
   int k;

   for ( k = 2;  k <= (num / 2);  ++k )
      if ( (num % k) == 0 )
         return(FALSE);

   return(TRUE);
}


int main(void)
{
   int   data_set_count, k;
   int   num, prev_prime, next_prime;

   scanf("%d", &data_set_count);
   for ( k = 1;  k <= data_set_count;  ++k )
     {
      scanf("%d", &num);
      printf("%d ", num);

      if ( is_prime(num) )
         printf("0\n");
      else
        {
         /* find prime less than num */
         for ( prev_prime = (num - 1);  !is_prime(prev_prime);
                                                     --prev_prime )
	    ;

         /* find prime greater than num */
         for ( next_prime = (num + 1);  !is_prime(next_prime);
                                                     ++next_prime )
	    ;

         if ( (num - prev_prime) <= (next_prime - num) )
            printf("%d\n", num - prev_prime);
         else
            printf("%d\n", next_prime - num);

        }/* end else ( checking prime) */

     }/* end for ( k ) */

   return(0);

}

