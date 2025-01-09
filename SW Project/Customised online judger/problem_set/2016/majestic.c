
/*
   UCF 2016 (Fall) Local Programming Contest
   Problem: majestic
*/

#include <stdio.h>
#include <stdlib.h>

/* ************************************************** */

int main(void)
{
   FILE *in_fptr;
   int  data_set_count,
        stat1, stat2, stat3,
        count, k;

   if ( (in_fptr = fopen("majestic.in", "r")) == NULL )
   {
       printf("*** can't open input file *** \n");
       exit(-1);
   }

   fscanf(in_fptr, "%d", &data_set_count);

   for ( k = 1;  k <= data_set_count;  ++k )
   {
       fscanf(in_fptr, "%d %d %d", &stat1, &stat2, &stat3);
       printf("%d %d %d\n", stat1, stat2, stat3);

       count = 0;
       if ( stat1 >= 10 ) ++count;
       if ( stat2 >= 10 ) ++count;
       if ( stat3 >= 10 ) ++count;

       if ( count == 3 )      printf("triple-double\n\n");
       else if ( count == 2 ) printf("double-double\n\n");
       else if ( count == 1 ) printf("double\n\n");
       else                   printf("zilch\n\n");

   }/* end for ( k ) */

   if ( fclose(in_fptr) == EOF )
   {
       printf("*** can't close input file *** \n");
       exit(-1);
   }

   return(0);

}/* end main */

/* ************************************************** */
