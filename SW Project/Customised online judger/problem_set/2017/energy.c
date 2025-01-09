

/*
   UCF 2017 (Fall) Local Programming Contest
   Problem: energy
*/

#include <stdio.h>
#include <stdlib.h>

/* ************************************************************ */

int main(void)
{
   int   data_set_count, k;
   int   initial_rate, additional_rate,
         energy_used, charges;
   FILE  *in_fptr, *fopen();

   if ( (in_fptr = fopen("energy.in", "r")) == NULL )
     {
      printf("*** can't open input file *** \n");
      exit(0);
     }

   fscanf(in_fptr, "%d %d", &initial_rate, &additional_rate);

   fscanf(in_fptr, "%d", &data_set_count);
   for ( k = 1;  k <= data_set_count;  ++k )
     {
      fscanf(in_fptr, "%d", &energy_used);
      if ( energy_used <= 1000 )
         charges = energy_used * initial_rate;
      else
         charges = (1000 * initial_rate) +
                   ((energy_used - 1000) * additional_rate);
      printf("%d %d\n", energy_used, charges);
     }/* end for ( k ) */

   if ( fclose(in_fptr) == EOF )
     {
      printf("*** can't close input file *** \n");
      exit(0);
     }

   return(0);

}/* end main */

/* ************************************************************ */

