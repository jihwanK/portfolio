

/*
   UCF 2011 (Fall) Local Programming Contest
   Problem: coin
*/

#include <stdio.h>

#define TRUE  1
#define FALSE 0

/* ************************************************************ */

int main(void)
{
   int   data_set_count, k, coin_count, j;
   int   prev_amount, next_amount, good_denum;
   FILE  *in_fptr, *fopen();

   in_fptr = stdin;

   fscanf(in_fptr, "%d", &data_set_count);
   for ( k = 1;  k <= data_set_count;  ++k )
     {
      fscanf(in_fptr, "%d", &coin_count);
      fscanf(in_fptr, "%d", &prev_amount);
      good_denum = TRUE;

      for ( j = 2;  j <= coin_count;  ++j )
        {
         fscanf(in_fptr, "%d", &next_amount);
         if ( next_amount < (2 * prev_amount) )
            good_denum = FALSE;
         prev_amount = next_amount;
        }/* end for ( j ) */

      if ( good_denum )
         printf("0\n");
      else
         printf("1\n");

     }/* end for ( k ) */

   return(0);

}/* end main */

/* ************************************************************ */
